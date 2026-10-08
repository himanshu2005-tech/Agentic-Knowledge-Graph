import torch
import gc
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from src.config import *
from src.utils import *

def load_model(model_id: str, label: str):
    log(f"Loading tokenizer for {label} ...")
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True,
                                               clean_up_tokenization_spaces=False)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    quant_cfg = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                    bnb_4bit_compute_dtype=torch.float16,
                                    llm_int8_enable_fp32_cpu_offload=True)
    log(f"Loading {label} (4-bit NF4) ...")
    model = AutoModelForCausalLM.from_pretrained(model_id, quantization_config=quant_cfg,
                                                  device_map="cuda:0", trust_remote_code=True,
                                                  low_cpu_mem_usage=True)
    model.eval()
    torch.cuda.empty_cache()
    torch.backends.cuda.matmul.allow_tf32 = True
    log(f"{label} loaded")
    return tokenizer, model


def unload_model(model, label: str):
    log(f"Unloading {label} ...")
    del model
    torch.cuda.empty_cache(); torch.cuda.synchronize(); gc.collect()
    log(f"{label} unloaded")


# ──────────────────────────────────────────────
# PROMPTS — deliberately dumb-simple, symmetric between raw/rag
# ──────────────────────────────────────────────
def is_gemma_tokenizer(tokenizer) -> bool:
    name = getattr(tokenizer, "name_or_path", "").lower()
    return "gemma" in name or "gemma" in tokenizer.__class__.__name__.lower()


def build_prompt(tokenizer, question: str, context: str = "") -> str:
    """One function for both raw and RAG. If context is empty string, this
    IS the raw prompt — guaranteeing the floor property described above."""
    use_rag = bool(context.strip())
    sys_inst = SYSTEM_INSTRUCTION + (RAG_INSTRUCTION_SUFFIX if use_rag else "")
    user_content = question
    if use_rag:
        user_content = f"Background facts:\n{context}\n\nQuestion: {question}"

    if is_gemma_tokenizer(tokenizer):
        # Gemma tokenizer has no system role — fold instruction into user turn
        messages = [{"role": "user", "content": f"{sys_inst}\n\n{user_content}"}]
    else:
        messages = [{"role": "system", "content": sys_inst},
                    {"role": "user", "content": user_content}]
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


# ──────────────────────────────────────────────
# INFERENCE + CLEANING
# ──────────────────────────────────────────────
def generate(tokenizer, model, prompt: str, max_new_tokens: int = MAX_NEW_TOKENS):
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True,
                       max_length=2048).to(model.device)
    with torch.no_grad():
        out_ids = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False,
                                  repetition_penalty=1.15, pad_token_id=tokenizer.pad_token_id,
                                  eos_token_id=tokenizer.eos_token_id, num_return_sequences=1)
    n_new = out_ids.shape[1] - inputs["input_ids"].shape[1]
    raw = tokenizer.decode(out_ids[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return clean_output(raw), n_new


def clean_output(text: str) -> str:
    cutoffs = [r"<\|user\|>", r"<\|system\|>", r"<\|assistant\|>", r"Human:", r"User:",
               r"Question:", r"Background facts:", r"```", r"<s>", r"\[INST\]"]
    for marker in cutoffs:
        m = re.search(marker, text, re.IGNORECASE)
        if m:
            text = text[:m.start()].strip()
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    seen, deduped = set(), []
    for s in sentences:
        s_norm = re.sub(r"\s+", " ", s.strip().lower())
        if s_norm not in seen and len(s_norm) > 10:
            seen.add(s_norm)
            deduped.append(s.strip())
    return " ".join(deduped[:4]).strip()


# ──────────────────────────────────────────────
# OPTIONAL AUTO-SCORING
# Add an "expected_answer" (short string or list of acceptable substrings)
# field to any question in questions.json to get automatic correctness
# scoring. Questions without it are left as "unscored" (manual review).
# ──────────────────────────────────────────────

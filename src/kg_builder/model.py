import torch
import logging
import time
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from .extraction import build_prompt, extract_triplets
from .canonicalization import force_seed_casing_in_text

logger = logging.getLogger(__name__)

def load_model(model_id: str):
    logger.info("Loading tokenizer ...")
    tokenizer = AutoTokenizer.from_pretrained(
        model_id, trust_remote_code=True,
        clean_up_tokenization_spaces=False,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    logger.info("Setting up 4-bit quantization config for RTX 3050 ...")
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )

    logger.info("Loading model weights in 4-bit mode entirely into VRAM ...")
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=quantization_config,
        device_map="auto",
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    )
    model.eval()
    torch.cuda.empty_cache()
    torch.backends.cuda.matmul.allow_tf32 = True
    logger.info(f"{model_id} loaded into VRAM successfully!")
    return tokenizer, model

def generate_and_extract(
    topic: str,
    tokenizer,
    model,
    max_new_tokens: int,
    top_k: int,
    temperature: float = 0.1,
    min_relations: int = 2,
    max_retries: int = 3
) -> tuple[list, float, float]:
    start_time = time.time()
    prompt_text = build_prompt(topic, tokenizer)
    inputs = tokenizer(prompt_text, return_tensors="pt").to(model.device)

    model_start = time.time()
    with torch.inference_mode():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=0.9,
            top_k=top_k,
            repetition_penalty=1.1,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
        )
    model_end = time.time()
    
    torch.cuda.empty_cache()

    prompt_len = inputs["input_ids"].shape[1]
    new_ids = output_ids[0][prompt_len:]
    raw_output = tokenizer.decode(new_ids, skip_special_tokens=True)
    raw_output = force_seed_casing_in_text(raw_output)

    candidates = extract_triplets(raw_output)
    
    total_end = time.time()
    
    model_time = model_end - model_start
    total_time = total_end - start_time
    
    return candidates, model_time, total_time

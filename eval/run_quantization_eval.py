import os
import sys
import json
import argparse
from tqdm import tqdm
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from eval.eval_metrics import quantization_delta
import src.rag_pipeline.agent as agent

def _load_model_variant(model_path: str, use_4bit: bool):
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    if use_4bit:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16
        )
        model = AutoModelForCausalLM.from_pretrained(model_path, quantization_config=bnb_config, device_map="auto")
    else:
        # FP16 load
        model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16, device_map="auto")
    model.eval()
    return tokenizer, model

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10, help="Number of queries to evaluate")
    args = parser.parse_args()

    gold_set_path = os.path.join(BASE_DIR, "eval", "gold_set.json")
    with open(gold_set_path, "r", encoding="utf-8") as f:
        gold_data = json.load(f)[:args.limit]

    print("Loading FP16 model (this will require ~6-8GB VRAM)...")
    try:
        # This might OOM on smaller cards!
        tokenizer_fp16, model_fp16 = _load_model_variant(agent.LOCAL_ANSWER_MODEL, use_4bit=False)
    except Exception as e:
        print(f"Failed to load FP16 model (Likely OOM): {e}")
        print("Run this on a machine with at least 12GB VRAM.")
        return

    print("Running FP16 generation...")
    fp16_answers = []
    for item in tqdm(gold_data):
        ans = agent.synthesize_answer_local(item["prompt"], [], [], tokenizer_fp16, model_fp16)
        fp16_answers.append(ans)

    del model_fp16
    torch.cuda.empty_cache()

    print("Loading 4-Bit model...")
    tokenizer_4bit, model_4bit = _load_model_variant(agent.LOCAL_ANSWER_MODEL, use_4bit=True)

    print("Running 4-Bit generation...")
    int4_answers = []
    for item in tqdm(gold_data):
        ans = agent.synthesize_answer_local(item["prompt"], [], [], tokenizer_4bit, model_4bit)
        int4_answers.append(ans)
        
    del model_4bit
    torch.cuda.empty_cache()

    # TODO: Replace this trivial length-based score with a real LLM-as-a-judge 
    # or Perplexity score in the future!
    print("\n--- QUANTIZATION DELTA RESULTS ---")
    total_delta = 0.0
    for i in range(len(gold_data)):
        fp16_score = len(fp16_answers[i])
        int4_score = len(int4_answers[i])
        delta = quantization_delta(fp16_score, int4_score)
        total_delta += delta
        print(f"Q{i+1}: Delta {delta} chars (FP16: {fp16_score}, 4Bit: {int4_score})")

    avg_delta = total_delta / len(gold_data)
    print(f"\nAverage Quantization Quality Loss (Proxy): {avg_delta} characters.")
    print("NOTE: Length is a trivial proxy. Implement Perplexity/LLM-Judge here for production.")

if __name__ == "__main__":
    main()

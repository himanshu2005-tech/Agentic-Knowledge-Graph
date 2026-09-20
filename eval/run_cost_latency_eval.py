import os
import sys
import json
import time
import argparse
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
from groq import Groq
import torch
from dotenv import load_dotenv

load_dotenv(override=True)

# Append root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from eval.eval_metrics import summarize_latency_cost, compare_configs
from src.rag_pipeline.agent import (
    load_local_model,
    load_knowledge_graph,
    RAG_KB_FILE,
    KG_MODEL,
    LOCAL_ANSWER_MODEL,
    answer_with_rag
)

def run_config_a_dual(question: str, client: Groq, tokenizer, model, all_triplets, existing_keys):
    """Full dual-model Agentic RAG Pipeline."""
    # Redirect stdout to avoid spam
    try:
        # Measure latency
        start_time = time.time()
        answer = answer_with_rag(question, client, KG_MODEL, tokenizer, model, all_triplets, existing_keys)
        latency = time.time() - start_time
    except Exception as e:
        print(f"Error in dual model: {e}")
        latency = 0.0
        
    return latency, 0  # Token tracking complex for dual model, return 0 for now

def run_config_b_70b_only(question: str, client: Groq):
    """Everything through Groq 70B directly."""
    start_time = time.time()
    tokens = 0
    try:
        response = client.chat.completions.create(
            model=KG_MODEL,
            messages=[
                {"role": "system", "content": "You are a factual assistant. Answer the user's question directly."},
                {"role": "user", "content": question}
            ],
            max_tokens=300,
            temperature=0.0
        )
        tokens = response.usage.total_tokens if response.usage else 0
    except Exception as e:
        pass
    latency = time.time() - start_time
    return latency, tokens

def run_config_c_3b_only(question: str, tokenizer, model):
    """Everything through Local 3B directly (No RAG)."""
    system_prompt = "You are a helpful assistant. Answer the question directly."
    user_content = f"Question: {question}"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=200).to(model.device)
    
    start_time = time.time()
    with torch.no_grad():
        outputs = model.generate(
            **inputs, 
            max_new_tokens=300, 
            do_sample=False, 
            repetition_penalty=1.15,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id
        )
    latency = time.time() - start_time
    # Token count proxy (output tokens roughly)
    tokens = outputs.shape[1] - inputs['input_ids'].shape[1]
    return latency, tokens

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10, help="Number of queries to evaluate")
    args = parser.parse_args()

    gold_set_path = os.path.join(BASE_DIR, "eval", "gold_set.json")
    with open(gold_set_path, "r", encoding="utf-8") as f:
        gold_data = json.load(f)[:args.limit]

    groq_client = Groq()
    local_tokenizer, local_model = load_local_model(LOCAL_ANSWER_MODEL)
    rag_triplets = load_knowledge_graph(RAG_KB_FILE)
    existing_keys = set([f"{t['subject'].lower()}|{t['relation'].lower()}|{t['object'].lower()}" for t in rag_triplets])

    a_lats, a_toks = [], []
    b_lats, b_toks = [], []
    c_lats, c_toks = [], []

    print(f"Running Cost/Latency evaluation on {len(gold_data)} queries...")
    for item in tqdm(gold_data):
        q = item["prompt"]
        
        # A: Dual Model
        lat, tok = run_config_a_dual(q, groq_client, local_tokenizer, local_model, rag_triplets, existing_keys)
        a_lats.append(lat)
        a_toks.append(tok)
        
        # B: 70B Only
        time.sleep(1) # rate limit
        lat, tok = run_config_b_70b_only(q, groq_client)
        b_lats.append(lat)
        b_toks.append(tok)
        
        # C: 3B Only
        lat, tok = run_config_c_3b_only(q, local_tokenizer, local_model)
        c_lats.append(lat)
        c_toks.append(tok)

    # Summarize metrics
    configs = {
        "Dual-Model (70B+3B)": summarize_latency_cost(a_lats, a_toks),
        "Single-Model (70B)": summarize_latency_cost(b_lats, b_toks),
        "Single-Model (3B Local)": summarize_latency_cost(c_lats, c_toks),
    }

    # Generate DataFrame
    df = compare_configs(configs)
    
    # Save CSV
    os.makedirs(os.path.join(BASE_DIR, "eval", "results"), exist_ok=True)
    out_csv = os.path.join(BASE_DIR, "eval", "results", "cost_latency", "cost_latency_results.csv")
    df.to_csv(out_csv)
    print(f"\nSaved CSV to: {out_csv}")
    print("\nResults:")
    print(df)

    # Generate Chart
    plt.figure(figsize=(10, 6))
    means = [configs[k]["mean_latency"] for k in configs]
    labels = list(configs.keys())
    
    # Simple bar chart
    plt.bar(labels, means, color=['#4285F4', '#EA4335', '#34A853'])
    plt.title('Mean Query Latency (Seconds) by Configuration')
    plt.ylabel('Mean Latency (s)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    out_png = os.path.join(BASE_DIR, "eval", "results", "cost_latency", "cost_latency_chart.png")
    plt.savefig(out_png)
    print(f"Saved Bar Chart to: {out_png}")

if __name__ == "__main__":
    main()

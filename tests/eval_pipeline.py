import os
import sys
import json
import time
import argparse
from tqdm import tqdm
from groq import Groq
import torch

# Append root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.rag_pipeline.agent import (
    load_local_model,
    load_knowledge_graph,
    RAG_KB_FILE,
    KG_MODEL,
    LOCAL_ANSWER_MODEL,
    answer_with_rag
)

def eval_model_a(question: str, tokenizer, model) -> str:
    """Baseline 3B (No Context)"""
    system_prompt = "You are a helpful, factual assistant. Answer the user's question directly and concisely."
    user_content = f"Question: {question}"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=200).to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs, 
            max_new_tokens=300, 
            do_sample=False, 
            repetition_penalty=1.15,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id
        )
    answer = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True).strip()
    
    # Clean up trailing artifacts
    for marker in ["<|user|>", "<|system|>", "<|assistant|>", "Human:", "User:", "Question:"]:
        idx = answer.find(marker)
        if idx != -1:
            answer = answer[:idx].strip()
            
    return answer

def eval_model_b(question: str, groq_client: Groq) -> str:
    """Baseline 120B/70B (No Context) via Groq API"""
    try:
        response = groq_client.chat.completions.create(
            model=KG_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful, factual assistant. Answer directly and concisely."},
                {"role": "user", "content": question}
            ],
            max_tokens=300,
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def eval_model_c(question: str, groq_client: Groq, tokenizer, model, all_triplets: list, existing_keys: set) -> str:
    """Agentic RAG Pipeline (KG + Web + 3B)"""
    try:
        return answer_with_rag(question, groq_client, KG_MODEL, tokenizer, model, all_triplets, existing_keys)
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100, help="Number of questions to run")
    args = parser.parse_args()

    # Setup
    with open('tests/eval_questions.json', 'r') as f:
        questions = json.load(f)[:args.limit]

    groq_client = Groq()
    local_tokenizer, local_model = load_local_model(LOCAL_ANSWER_MODEL)
    
    rag_triplets = load_knowledge_graph(RAG_KB_FILE)
    existing_keys = set([f"{t['subject'].lower()}|{t['relation'].lower()}|{t['object'].lower()}" for t in rag_triplets])

    results = []
    
    print(f"Starting quantitative evaluation across {len(questions)} questions...")
    for i, q in enumerate(tqdm(questions)):
        print(f"\n[{i+1}/{len(questions)}] Question: {q}")
        
        # Model A
        print("  Evaluating Model A (Local 3B Baseline)...")
        ans_a = eval_model_a(q, local_tokenizer, local_model)
        
        # Model B
        print("  Evaluating Model B (Groq 120B Baseline)...")
        ans_b = eval_model_b(q, groq_client)
        time.sleep(1) # Groq rate limit
        
        # Model C
        print("  Evaluating Model C (Agentic RAG)...")
        # Temporarily suppress stdout from the agent so it doesn't mess up tqdm
        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        try:
            ans_c = eval_model_c(q, groq_client, local_tokenizer, local_model, rag_triplets, existing_keys)
        finally:
            sys.stdout.close()
            sys.stdout = old_stdout
            
        results.append({
            "question": q,
            "system_a_3b_raw": ans_a,
            "system_b_120b_raw": ans_b,
            "system_c_rag": ans_c
        })
        
        # Save checkpoints incrementally
        with open('tests/evaluation_results.json', 'w') as f:
            json.dump(results, f, indent=4)

    print("\nEvaluation complete. Saved to tests/evaluation_results.json")

if __name__ == '__main__':
    main()

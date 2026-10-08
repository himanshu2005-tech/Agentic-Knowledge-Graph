import os
import sys
import json
import time
import argparse
import pandas as pd
from tqdm import tqdm
from groq import Groq
import torch
from dotenv import load_dotenv

load_dotenv(override=True)

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

def run_hybrid(question: str, client: Groq, tokenizer, model, all_triplets, existing_keys):
    """Full dual-model Agentic RAG Pipeline."""
    try:
        answer = answer_with_rag(question, client, KG_MODEL, tokenizer, model, all_triplets, existing_keys)
        return answer.strip()
    except Exception as e:
        return f"ERROR: {e}"

def run_cloud_70b(question: str, client: Groq):
    """Everything through Groq 70B directly."""
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
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: {e}"

def run_local_3b(question: str, tokenizer, model):
    """Everything through Local 3B directly (No RAG)."""
    system_prompt = "You are a helpful assistant. Answer the question directly."
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
    # Decode only the newly generated tokens
    output_ids = outputs[0][inputs['input_ids'].shape[1]:]
    return tokenizer.decode(output_ids, skip_special_tokens=True).strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=30, help="Number of queries to evaluate")
    args = parser.parse_args()

    questions_file = os.path.join(BASE_DIR, "data", "questions.json")
    if not os.path.exists(questions_file):
        print(f"File not found: {questions_file}")
        sys.exit(1)

    with open(questions_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        questions = data.get("questions", [])[:args.limit]

    groq_client = Groq()
    local_tokenizer, local_model = load_local_model(LOCAL_ANSWER_MODEL)
    rag_triplets = load_knowledge_graph(RAG_KB_FILE)
    existing_keys = set([f"{t['subject'].lower()}|{t['relation'].lower()}|{t['object'].lower()}" for t in rag_triplets])

    results = []

    print(f"\nRunning 3-Way Comparative Evaluation on {len(questions)} queries...")
    for item in tqdm(questions):
        q = item["question"]
        expected = str(item.get("expected_answer", ""))
        
        # We rewrite the question slightly to make it conversational and better test the NLP parsing
        rewritten_q = f"Can you tell me {q.lower()}?"
        if q.lower().startswith("what"):
            rewritten_q = f"I am trying to understand something. {q}"

        print(f"\n[Evaluating]: {rewritten_q}")
        
        # 1. Cloud 70B
        ans_cloud = run_cloud_70b(rewritten_q, groq_client)
        time.sleep(1) # rate limit
        
        # 2. Local 3B
        ans_local = run_local_3b(rewritten_q, local_tokenizer, local_model)
        
        # 3. Hybrid KG+Local
        # Suppress stdout temporarily to avoid massive spam during the loop
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        try:
            ans_hybrid = run_hybrid(rewritten_q, groq_client, local_tokenizer, local_model, rag_triplets, existing_keys)
        finally:
            sys.stdout.close()
            sys.stdout = original_stdout

        results.append({
            "Question": rewritten_q,
            "Expected_Answer": expected,
            "Cloud_70B_Answer": ans_cloud,
            "Local_3B_Answer": ans_local,
            "Hybrid_Answer": ans_hybrid
        })

    # Save Results
    df = pd.DataFrame(results)
    out_dir = os.path.join(BASE_DIR, "eval", "results", "accuracy")
    os.makedirs(out_dir, exist_ok=True)
    out_csv = os.path.join(out_dir, "comparative_answers.csv")
    df.to_csv(out_csv, index=False)
    
    print(f"\n✅ Completed! Saved side-by-side answers to: {out_csv}")

    # Calculate basic "does the answer contain the expected word" accuracy metric
    cloud_score = 0
    local_score = 0
    hybrid_score = 0
    
    for r in results:
        raw_expected = r["Expected_Answer"]
        
        # Parse list string representation back to list if needed
        import ast
        try:
            if raw_expected.startswith("[") and raw_expected.endswith("]"):
                expected_list = ast.literal_eval(raw_expected)
            else:
                expected_list = [raw_expected]
        except:
            expected_list = [raw_expected]
            
        ans_c = r["Cloud_70B_Answer"].lower().replace(" ", "")
        ans_l = r["Local_3B_Answer"].lower().replace(" ", "")
        ans_h = r["Hybrid_Answer"].lower().replace(" ", "")
        
        # For a match, ALL expected keywords must be found
        c_match = all(e.lower().replace(" ", "") in ans_c for e in expected_list)
        l_match = all(e.lower().replace(" ", "") in ans_l for e in expected_list)
        h_match = all(e.lower().replace(" ", "") in ans_h for e in expected_list)
        
        if c_match: cloud_score += 1
        if l_match: local_score += 1
        if h_match: hybrid_score += 1

    total = len(results)
    print("\n--- ROUGH ACCURACY SCORES (Keyword Match) ---")
    print(f"Cloud 70B : {cloud_score}/{total} ({(cloud_score/total)*100:.1f}%)")
    print(f"Local 3B  : {local_score}/{total} ({(local_score/total)*100:.1f}%)")
    print(f"Hybrid    : {hybrid_score}/{total} ({(hybrid_score/total)*100:.1f}%)")
    
    # Save a small text report
    with open(os.path.join(out_dir, "README.md"), "w") as f:
        f.write("# 3-Way Comparative Accuracy Benchmark\n\n")
        f.write("This folder contains the side-by-side exact textual answers generated by all 3 architectures on the 30-question dataset.\n\n")
        f.write(f"- **Cloud 70B** keyword match score: {cloud_score}/{total}\n")
        f.write(f"- **Local 3B** keyword match score: {local_score}/{total}\n")
        f.write(f"- **Hybrid** keyword match score: {hybrid_score}/{total}\n\n")
        f.write("Open `comparative_answers.csv` to read the actual paragraphs generated by each model to verify hallucinations vs grounded truth.")

if __name__ == "__main__":
    main()

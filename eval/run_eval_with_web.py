import os
import sys
import json
import time
import argparse
import pandas as pd
from tqdm import tqdm
from groq import Groq
from dotenv import load_dotenv

load_dotenv(override=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.rag_pipeline.agent import (
    load_knowledge_graph,
    RAG_KB_FILE,
    KG_MODEL,
    extract_topics_from_question,
    retrieve_ranked_facts,
    search_tavily
)

# Use a fast 8B model to simulate the Local 3B model (since system RAM is full)
SIMULATED_LOCAL_MODEL = "openai/gpt-oss-20b"

def synthesize_answer_simulated_local(question: str, facts: list, file_contexts: list, client: Groq):
    """Simulates synthesize_answer_local by strictly prompting Groq 8B."""
    context_blocks = []
    
    if facts:
        fact_str = "\n".join([f"- {f['subject']} {f['relation']} {f['object']}" for f in facts])
        context_blocks.append(f"--- KNOWLEDGE GRAPH FACTS ---\n{fact_str}")
        
    for ctx in file_contexts:
        context_blocks.append(ctx)
        
    combined_context = "\n\n".join(context_blocks)
    
    system_prompt = (
        "You are a strict, factual assistant. You must answer the user's question ONLY using the information provided in the context below. "
        "If the context does not contain the answer, you MUST refuse to answer and say exactly: "
        "'I'm sorry, but I cannot provide information about that based on the given facts.'\n\n"
        f"Context:\n{combined_context}"
    )

    try:
        response = client.chat.completions.create(
            model=SIMULATED_LOCAL_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            max_tokens=300,
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: {e}"

def run_hybrid_with_web(question: str, client: Groq, all_triplets):
    """Hybrid Pipeline that explicitly feeds raw Web Search into the 3B simulator."""
    try:
        topics = extract_topics_from_question(question, client, KG_MODEL)
        local_results, _ = retrieve_ranked_facts(question, topics, all_triplets)
        
        file_contexts = []
        if os.environ.get("TAVILY_API_KEY"):
            search_ctx, _ = search_tavily(question)
            if search_ctx:
                file_contexts.append(f"--- LIVE WEB RESULTS ---\n{search_ctx[:2000]}\n")
                
        answer = synthesize_answer_simulated_local(question, local_results, file_contexts, client)
        return answer.strip()
    except Exception as e:
        return f"ERROR: {e}"

def run_cloud_70b(question: str, client: Groq):
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

def run_local_3b_simulated(question: str, client: Groq):
    try:
        response = client.chat.completions.create(
            model=SIMULATED_LOCAL_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Answer the question directly."},
                {"role": "user", "content": question}
            ],
            max_tokens=300,
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: {e}"

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
    rag_triplets = load_knowledge_graph(RAG_KB_FILE)

    results = []
    print(f"\nRunning 3-Way Comparative Evaluation (WITH WEB CONTEXT + VRAM BYPASS) on {len(questions)} queries...")
    for item in tqdm(questions):
        q = item["question"]
        expected = str(item.get("expected_answer", ""))
        
        rewritten_q = f"Can you tell me {q.lower()}?"
        if q.lower().startswith("what"):
            rewritten_q = f"I am trying to understand something. {q}"

        print(f"\n[Evaluating]: {rewritten_q}")
        
        # 1. Cloud 70B
        ans_cloud = run_cloud_70b(rewritten_q, groq_client)
        time.sleep(0.5)
        
        # 2. Local 3B (Simulated via Groq 8B)
        ans_local = run_local_3b_simulated(rewritten_q, groq_client)
        time.sleep(0.5)
        
        # 3. Hybrid KG+Local+Web
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        try:
            ans_hybrid = run_hybrid_with_web(rewritten_q, groq_client, rag_triplets)
        finally:
            sys.stdout.close()
            sys.stdout = original_stdout
        
        time.sleep(0.5)

        results.append({
            "Question": rewritten_q,
            "Expected_Answer": expected,
            "Cloud_70B_Answer": ans_cloud,
            "Local_3B_Answer": ans_local,
            "Hybrid_Answer": ans_hybrid
        })

    df = pd.DataFrame(results)
    out_dir = os.path.join(BASE_DIR, "eval", "results", "accuracy")
    os.makedirs(out_dir, exist_ok=True)
    out_csv = os.path.join(out_dir, "comparative_answers_web.csv")
    df.to_csv(out_csv, index=False)
    
    print(f"\n✅ Completed! Saved side-by-side answers to: {out_csv}")
    
    cloud_score = 0
    local_score = 0
    hybrid_score = 0
    
    for r in results:
        raw_expected = r["Expected_Answer"]
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

if __name__ == "__main__":
    main()

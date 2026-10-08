import json
import os
import sys
from src.config import *
from src.utils import log
from src.pipeline import POMPipeline
from src.retriever import GATE_FAILURE_COUNTER

def score_answer(answer: str, expected) -> str:
    """Scores a single answer based on string matching."""
    ans_lower = answer.lower()
    
    is_no_knowledge = "i do not know" in ans_lower or "i don't know" in ans_lower or "i am unsure" in ans_lower
    
    if expected is None:
        return "Correct" if is_no_knowledge else "Incorrect"
        
    if isinstance(expected, list):
        if any(e.lower() in ans_lower for e in expected):
            return "Correct"
    else:
        if expected.lower() in ans_lower:
            return "Correct"
            
    if is_no_knowledge:
        return "No Knowledge"
        
    return "Incorrect"

def main():
    if not os.path.exists(QUESTIONS_PATH):
        log(f"Error: {QUESTIONS_PATH} not found.")
        sys.exit(1)
        
    with open(QUESTIONS_PATH, 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
        if isinstance(questions_data, dict) and "questions" in questions_data:
            questions = questions_data["questions"]
        else:
            questions = questions_data
        
    log(f"Loaded {len(questions)} questions from {QUESTIONS_PATH}")
    
    # Check expected answers
    if not any("expected_answer" in q for q in questions):
        log("\nNo 'expected_answer' fields found in questions.json. Running purely generation mode.\n")
    
    if os.path.exists(RESULTS_PATH):
        with open(RESULTS_PATH, 'r', encoding='utf-8') as f:
            results = json.load(f)
    else:
        results = {}
        
    for sys_key, label in SYSTEMS.items():
        if sys_key not in results:
            results[sys_key] = {}

        # Determine which model ID to load based on the label
        model_id = LLAMA_PATH if "Llama" in label else (QWEN_PATH if "Qwen" in label else GEMMA_PATH)
        
        # Initialize Pipeline
        pipeline = POMPipeline(model_id, label)
        
        for idx, q_obj in enumerate(questions):
            q_id = str(q_obj.get("id", idx))
            
            # Skip if already evaluated (resume capability)
            if q_id in results[sys_key] and "answer" in results[sys_key][q_id]:
                continue
                
            question_text = q_obj["question"]
            log(f"[{label}] Q{q_id}: {question_text}")
            
            answer, gate_passed, context_text = pipeline.ask(question_text)
            
            res_obj = {
                "question": question_text,
                "answer": answer
            }
            
            if "expected_answer" in q_obj:
                res_obj["score"] = score_answer(answer, q_obj["expected_answer"])
                
            if "RAG" in label:
                res_obj["gate_passed"] = gate_passed
                res_obj["context_retrieved"] = context_text
                
            results[sys_key][q_id] = res_obj
            
            # Save incrementally
            with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
                
        # LLM gets automatically unloaded when pipeline object is destroyed
        del pipeline

    # Print final gate failure stats
    log("=== GATE FALLBACK STATS ===")
    for sys_key, count in GATE_FAILURE_COUNTER.items():
        log(f"{sys_key}: {count} absolute fallbacks to raw knowledge")

if __name__ == "__main__":
    main()

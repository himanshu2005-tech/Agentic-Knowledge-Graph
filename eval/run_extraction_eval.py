import os
import sys
import json
import time
from tqdm import tqdm
from groq import Groq
from dotenv import load_dotenv

load_dotenv(override=True)

# Append root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.rag_pipeline.agent import generate_new_triplets, KG_MODEL
from eval.eval_metrics import precision_recall_f1, aggregate_prf1

def main():
    gold_set_path = os.path.join(BASE_DIR, "eval", "gold_set.json")
    if not os.path.exists(gold_set_path):
        print("Error: gold_set.json not found.")
        return

    with open(gold_set_path, "r", encoding="utf-8") as f:
        gold_data = json.load(f)

    # Configurable LIMIT
    LIMIT = 20
    eval_set = gold_data[:LIMIT]

    client = Groq()
    
    all_results = []
    
    print(f"Running Triplet Extraction Evaluation on {len(eval_set)} queries...")
    for item in tqdm(eval_set):
        prompt = item["prompt"]
        gold_triplets = [tuple(t) for t in item["gold_triplets"]]
        
        # In a real run we might extract topics first, but the eval says:
        # "call the actual generate_new_triplets() function against the 'prompt' field"
        # We will use the prompt as the topic for direct extraction evaluation.
        try:
            pred_triplets = generate_new_triplets(prompt, client, KG_MODEL, user_question=prompt)
            # Pred triplets is list[tuple].
        except Exception as e:
            print(f"Error extracting for prompt '{prompt}': {e}")
            pred_triplets = []

        scores = precision_recall_f1(gold_triplets, pred_triplets)
        
        result = {
            "prompt": prompt,
            "gold_triplets": gold_triplets,
            "pred_triplets": pred_triplets,
            **scores
        }
        all_results.append(result)
        time.sleep(2.0)  # Rate limiting

    # Aggregate
    macro_scores = aggregate_prf1(all_results)
    
    # Print results
    print("\n--- EXTRACTION EVALUATION RESULTS ---")
    for r in all_results:
        print(f"\nTopic: {r['prompt']}")
        print(f"  F1: {r['f1']:.3f} | Precision: {r['precision']:.3f} | Recall: {r['recall']:.3f}")
        print(f"  Gold : {len(r['gold_triplets'])} triplets")
        print(f"  Pred : {len(r['pred_triplets'])} triplets")
        
    print("\n" + "="*50)
    print(f"MACRO-AVERAGED SCORES (N={len(all_results)})")
    print(f"  Macro Precision : {macro_scores['macro_precision']:.3f}")
    print(f"  Macro Recall    : {macro_scores['macro_recall']:.3f}")
    print(f"  Macro F1        : {macro_scores['macro_f1']:.3f}")
    print("="*50)
    
    # Save to CSV
    os.makedirs(os.path.join(BASE_DIR, "eval", "results"), exist_ok=True)
    import pandas as pd
    df = pd.DataFrame([{
        "topic": r["prompt"], 
        "precision": r["precision"],
        "recall": r["recall"],
        "f1": r["f1"]
    } for r in all_results])
    
    out_path = os.path.join(BASE_DIR, "eval", "results", "extraction", "extraction_results.csv")
    df.to_csv(out_path, index=False)
    print(f"\nSaved detailed results to {out_path}")

if __name__ == "__main__":
    main()

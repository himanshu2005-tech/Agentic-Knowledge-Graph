import numpy as np
import pandas as pd
from typing import List, Dict, Any

def _normalize_triplet(triplet: tuple) -> tuple:
    """Normalize a triplet (subject, relation, object) to lowercase for fair comparison."""
    if len(triplet) == 3:
        s, r, o = triplet
    elif len(triplet) == 4:
        # In case the domain is included (domain, subject, relation, object)
        _, s, r, o = triplet
    else:
        return ()
    return (str(s).strip().lower(), str(r).strip().lower(), str(o).strip().lower())

def precision_recall_f1(gold_triplets: List[tuple], pred_triplets: List[tuple]) -> Dict[str, float]:
    """Calculate Precision, Recall, and F1 score for a single prediction vs gold standard."""
    gold_set = set(_normalize_triplet(t) for t in gold_triplets if _normalize_triplet(t))
    pred_set = set(_normalize_triplet(t) for t in pred_triplets if _normalize_triplet(t))
    
    if not gold_set and not pred_set:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0}
    if not gold_set or not pred_set:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
        
    true_positives = len(gold_set.intersection(pred_set))
    
    precision = true_positives / len(pred_set) if pred_set else 0.0
    recall = true_positives / len(gold_set) if gold_set else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {"precision": precision, "recall": recall, "f1": f1}

def aggregate_prf1(results: List[Dict[str, float]]) -> Dict[str, float]:
    """Calculate macro-averaged precision, recall, and F1 across multiple queries."""
    if not results:
        return {"macro_precision": 0.0, "macro_recall": 0.0, "macro_f1": 0.0}
    
    avg_p = sum(r["precision"] for r in results) / len(results)
    avg_r = sum(r["recall"] for r in results) / len(results)
    avg_f1 = sum(r["f1"] for r in results) / len(results)
    
    return {"macro_precision": avg_p, "macro_recall": avg_r, "macro_f1": avg_f1}

def summarize_latency_cost(latencies: List[float], token_counts: List[int] = None) -> Dict[str, float]:
    """Summarize latency and cost (token) metrics for a run."""
    if not latencies:
        return {"mean_latency": 0.0, "median_latency": 0.0, "p95_latency": 0.0, "total_tokens": 0}
        
    metrics = {
        "mean_latency": float(np.mean(latencies)),
        "median_latency": float(np.median(latencies)),
        "p95_latency": float(np.percentile(latencies, 95)),
        "total_tokens": sum(token_counts) if token_counts else 0
    }
    return metrics

def compare_configs(configs: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    """Format the latency/cost metrics across different configs into a DataFrame."""
    df = pd.DataFrame.from_dict(configs, orient='index')
    df.index.name = "Configuration"
    return df

def ablation_table(results: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    """
    Format ablation study results into a DataFrame, sorted by F1 score descending.
    Expected keys per result: 'micro_f1', 'mean_latency_sec', 'groundedness'
    """
    df = pd.DataFrame.from_dict(results, orient='index')
    df.index.name = "Ablation Variant"
    if "micro_f1" in df.columns:
        df = df.sort_values(by="micro_f1", ascending=False)
    return df

def quantization_delta(fp16_score: float, int4_score: float) -> float:
    """Calculate the absolute quality delta (loss) caused by 4-bit quantization."""
    return fp16_score - int4_score

def code_pass_rate(total: int, passed: int) -> float:
    """Calculate the code execution pass rate."""
    if total == 0:
        return 0.0
    return float(passed) / total

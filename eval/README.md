# RAG Evaluation Framework

This directory contains a rigorous, multi-tiered evaluation framework for the Agentic RAG pipeline. It is designed to produce quantitative metrics for academic/project reviews.

## Setup
Ensure you have the required dependencies installed:
```bash
pip install pandas matplotlib tqdm
```

## Tier 1 Benchmarks (End-to-End Metrics)

### 1. Triplet Extraction Quality (F1 Score)
**Script:** `python -m eval.run_extraction_eval`
- **What it does:** Runs the 70B extraction model against a set of queries and compares the extracted triplets to human-authored ground truth (`gold_set.json`).
- **Why it matters:** Validates that the Knowledge Graph construction isn't hallucinating noise.
- **Output:** `results/extraction_results.csv`

### 2. Cost & Latency Comparison
**Script:** `python -m eval.run_cost_latency_eval`
- **What it does:** Measures wall-clock latency for three configurations: Dual-Model (70B+3B), Single-Model (70B only), and Single-Model (3B only).
- **Why it matters:** Proves the efficiency claims of the dual-model architecture.
- **Output:** `results/cost_latency_results.csv` and `results/cost_latency_chart.png`

### 3. Ablation Study
**Script:** `python -m eval.run_ablation`
- **What it does:** Isolates specific pipeline components (e.g., turning off KG expansion, turning off code execution) to measure their direct impact on F1 quality and latency overhead.
- **Why it matters:** Empirically proves which features contribute most to the system's success.
- **Output:** `results/ablation_results.csv`

## Tier 2 Benchmarks (Component Proxies)

### 4. Quantization Delta
**Script:** `python -m eval.run_quantization_eval`
- **What it does:** Loads the local model in FP16 and 4-Bit NF4 formats, runs the same queries, and calculates a quality delta (currently using a placeholder length-based score; to be replaced with LLM-as-a-judge).
- **Why it matters:** Quantifies the exact quality trade-off made to achieve local execution.

### 5. Code Execution Pass Rate
**Script:** `python -m eval.run_code_eval`
- **What it does:** Scans the `codevault/` directory for generated `.py` scripts and executes them safely, measuring the pass/fail rate.
- **Why it matters:** Validates that the autonomous code generation feature actually produces working code.

## Modifying the Gold Set
To run a proper evaluation, you must populate `eval/gold_set.json` with human-authored ground-truth triplets. Do not auto-generate these with an LLM, as they serve as the validation anchor for the entire suite.

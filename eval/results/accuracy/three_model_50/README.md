# 50-question three-model evaluation

Same questions; raw 3B and KG-enhanced 3B use the same local model. The KG is read-only. Cloud is `openai/gpt-oss-120b` via Groq.

| Model | Correct | Accuracy |
|---|---:|---:|
| Raw 3B | 27/50 | 54.0% |
| 3B + KG | 37/50 | 74.0% |
| Cloud 120B | 39/50 | 78.0% |

## Accuracy by question type

| Model | Public (30) | KG-private (8) | KG facts (12) |
|---|---:|---:|---:|
| Raw 3B | 19/30 | 1/8 | 7/12 |
| 3B + KG | 17/30 | 8/8 | 12/12 |
| Cloud 120B | 26/30 | 3/8 | 10/12 |

Strict grounded 3B + KG: 17/50 (34.0%)
Retrieval recall@20: 70.0%
Valid citation rate: 36.0%

Full answers are in `all_answers.md`; machine-readable answers and evidence are in `answers.csv` and `results.json`.

**Ranking, best to worst (100-question run, the only one with all four models):**

| Rank | Model | Fully correct (of 100) | Rubric score | Token F1 |
|---|---|---|---|---|
| 1 | Fine-tuned Qwen 3B + KG | 91 | 92% | 0.875 |
| 2 | Raw Qwen 3B + KG | 84 | 85% | 0.228 |
| 3 | Cloud 120B (question only) | 29 | 35% | 0.106 |
| 4 | Raw Qwen 3B | 8 | 12% | 0.084 |

**Caveats:**

- **Rank 1 vs 2 is not settled.** The fine-tuned model beats raw + KG by 11 wins to 4 losses, but p = 0.118. That is a promising edge, not a proven one. Fine-tuning does clearly improve refusals: it correctly refuses 10 of 11 unanswerable questions, against 2 of 11 for raw + KG.
- **The token F1 gap is exaggerated.** Fine-tuned scores 0.875 against 0.228 mainly because it copies the gold answers' phrasing. The rubric score (92% vs 85%) is the fairer comparison.
- **The cloud model is not a fair comparison.** It got only the question, with no evidence. It also returned 11 empty outputs, so its 35% is a lower bound.
- **Fine-tuned may be inflated.** Its test questions may overlap its training data. I couldn't rule that out.

**On the 50-question benchmark (no fine-tuned model):** cloud 78% > Qwen + KG 74% > raw Qwen 54%. The first two are statistically indistinguishable (p = 0.82).

The ranking depends on the setting. With evidence supplied, the KG-assisted models win. When the model has to answer from the question alone and the topic is public knowledge, the cloud model leads. On questions the graph covers, the KG models win clearly.
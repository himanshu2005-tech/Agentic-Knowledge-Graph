# Actual 3B: raw vs RAG evaluation

This is a deterministic, paired evaluation of the same local model. No Groq or web expansion was used.

- Questions: 8
- Raw 3B: 4/8 (50%)
- RAG + 3B: 8/8 (100%)
- Strict grounded RAG: 5/8 (62%)
- Accuracy delta: +50.0 percentage points
- Retrieval recall@8: 88%
- Valid citation rate: 62%

| ID | Category | Raw | RAG | Retrieved answer | Confidence |
|---|---|---:|---:|---:|---:|
| private-1 | knowledge-only | FAIL | PASS | YES | 0.468 |
| private-2 | multi-hop | FAIL | PASS | YES | 0.668 |
| private-3 | knowledge-only | FAIL | PASS | YES | 0.661 |
| domain-1 | domain | PASS | PASS | YES | 0.468 |
| domain-2 | domain | PASS | PASS | YES | 0.665 |
| public-1 | public-fact | FAIL | PASS | YES | 0.668 |
| public-2 | public-fact | PASS | PASS | YES | 0.665 |
| negative-1 | retrieval-stress | PASS | PASS | NO | 0.689 |

Scoring uses normalized expected-answer containment. Inspect the CSV/JSON for full answers and evidence; this small benchmark is diagnostic, not statistically conclusive.

Strict grounded accuracy requires the expected answer to appear in the response, the retrieved evidence, and a valid `[F#]` citation. The uncited Pascal and OCaml answers therefore fail this stricter measure, as does JavaScript because its retrieved evidence did not contain Brendan Eich.

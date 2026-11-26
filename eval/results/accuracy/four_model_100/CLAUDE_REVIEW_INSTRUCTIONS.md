# Independent evaluation instructions for Claude

Evaluate the accompanying 100-question, four-configuration experiment independently. Do not accept the repository's automatic scores as ground truth; recompute and critique them.

## Files

- `README.md`: summarized metrics and all answers in readable Markdown.
- `results.json`: exact machine-readable answers and recorded metrics.
- `answers.csv`: one row per question with all four answers.
- `test_100.jsonl`: original held-out prompts, evidence, expected answers, and categories.
- `run_100_question_four_model_eval.py`: evaluator implementation.
- `MANIFEST.json`: file descriptions and SHA-256 checksums.

## Compared configurations

1. **Raw 3B:** receives only the question.
2. **Raw 3B + KG:** receives the question and the held-out evidence block.
3. **Fine-tuned 3B + KG:** receives the same evidence as raw 3B + KG.
4. **Cloud 120B:** receives only the question.

The evidence blocks are controlled evaluation contexts derived from the held-out dataset. They isolate evidence-synthesis ability; they do not test live retrieval from `rag_knowledge.txt`.

## Requested analysis

1. Verify that there are exactly 100 aligned questions and four answers per question.
2. Recompute normalized exact match, token-overlap F1, refusal recall, and false-refusal count.
3. Grade every answer for:
   - factual correctness relative to the supplied evidence and expected answer;
   - completeness;
   - unsupported additions or hallucinations;
   - correct refusal when evidence is insufficient;
   - citation correctness for evidence-conditioned configurations.
4. Use a documented ordinal rubric, for example:
   - `2`: correct, complete, and supported;
   - `1`: substantially correct but incomplete or containing a minor unsupported detail;
   - `0`: incorrect, unsupported, misleading, or an inappropriate refusal.
5. For KG configurations, treat the supplied evidence as authoritative for this experiment. Do not reward outside knowledge that contradicts it.
6. Do not compare the cloud and raw question-only models as though they received the evidence. Explicitly discuss this asymmetry.
7. Identify cases where lexical F1 disagrees with semantic correctness.
8. Report per-configuration totals, per-category totals, hallucination counts, refusal precision/recall, and pairwise wins/ties/losses.
9. Quote representative answers, including both successes and failures.
10. Give separate verdicts for:
    - standalone factual answering;
    - evidence-conditioned synthesis;
    - readiness for the intended KG pipeline.

## Reproducibility cautions

- This evaluation contains 36 extractive, 28 grounded-QA, 25 multi-hop, and 11 unanswerable examples.
- Keyword and token-overlap measures are diagnostic proxies, not human semantic judgments.
- Fine-tuned 3B + KG was trained for evidence-conditioned answering; standalone fine-tuned performance is not measured here.
- Do not claim that this evaluates live retrieval quality.
- Flag suspected train/test leakage or templated memorization if answer wording appears copied rather than derived.

Return a concise executive verdict followed by the detailed score breakdown and a list of disputed or ambiguous cases.

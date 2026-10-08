# 30-question model comparison

Charts in this directory are generated from `eval/results/accuracy/comparative_answers.csv`.

The scorer lowercases each answer, removes spaces, punctuation, Markdown, and unusual Unicode spacing, then checks whether every expected answer appears in the normalized response. For the AWK question, all three expected inventor names are required.

## Results

| Model | Correct | Accuracy |
|---|---:|---:|
| Cloud 70B | 29/30 | 96.7% |
| Raw Local 3B | 18/30 | 60.0% |
| 3B + Knowledge Graph | 19/30 | 63.3% |

Run `python eval/codex-accuracy/plot_30_question_analysis.py` from the project root to reproduce all charts and `scored_results.csv`.

This is a normalized expected-answer match, not a semantic or human-judged quality score. It should not be interpreted as measuring factual precision beyond the expected answer strings.

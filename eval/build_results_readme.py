"""Build the human-readable evaluation README from committed JSON results."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THREE_MODEL = ROOT / "eval/results/accuracy/three_model_50/results.json"
ADAPTER = ROOT / "finetune/results/grounded_v2_100_comparison.json"
OUTPUT = ROOT / "eval/results/README.md"


def pct(value: float) -> str:
    return f"{value:.1%}"


def block(value: str) -> str:
    # Indented Markdown is robust even when model output itself contains fences.
    lines = (value or "—").strip().splitlines()
    return "\n".join(f"    {line}" if line else "    " for line in lines)


def main() -> None:
    benchmark = json.loads(THREE_MODEL.read_text(encoding="utf-8"))
    adapter = json.loads(ADAPTER.read_text(encoding="utf-8"))
    metrics = benchmark["metrics"]
    rows = benchmark["answers"]
    adapted_rows = adapter["answers"]

    categories: dict[str, list[dict]] = defaultdict(list)
    for row in adapted_rows:
        categories[row["kind"]].append(row)

    lines = [
        "# Model Evaluation: Metrics and Complete Answers",
        "",
        "> Generated from the repository's saved evaluation JSON. This document does not rerun models or alter scores.",
        "",
        "## Executive verdict",
        "",
        "The new fine-tuned 3B adapter is the strongest tested **evidence-conditioned answer model**. On 100 held-out examples, mean token F1 increased from **0.2281** to **0.8747**, normalized exact matches increased from **1/100** to **74/100**, and correct insufficient-evidence refusals increased from **2/11** to **10/11**.",
        "",
        "On the separate 50-question system benchmark, the 120B cloud model scored **39/50 (78%)**, the original 3B+KG system scored **37/50 (74%)**, and raw 3B scored **27/50 (54%)**. The fine-tuned 3B+KG combination has not yet been rerun on that benchmark and therefore has no directly comparable 50-question score.",
        "",
        "## Configuration ranking",
        "",
        "1. **Fine-tuned 3B + KG — provisional production choice.** Expected to combine improved synthesis with retrieval, but the combined 50-question result is still pending.",
        "2. **120B cloud — strongest measured general baseline.** 39/50 overall and 26/30 on public questions.",
        "3. **Original 3B + KG — strongest measured graph-specific configuration.** 20/20 on graph-specific questions, though strict grounded correctness was 17/50.",
        "4. **Fine-tuned 3B alone — strongest measured evidence-conditioned local model.** 0.8747 mean token F1 on the held-out v2 sample.",
        "5. **Raw 3B — weakest configuration.** 27/50 on the system benchmark and 0.2281 token F1 on the held-out adapter comparison.",
        "",
        "## 50-question system benchmark",
        "",
        "| Configuration | Correct | Accuracy | Public | Profile-specific | KG facts |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for key, label in (("raw_3b", "Raw 3B"), ("kg_3b", "Original 3B + KG"), ("cloud_120b", "120B cloud")):
        item = metrics[key]
        lines.append(
            f"| {label} | {item['correct']}/{item['total']} | {pct(item['accuracy'])} | "
            f"{item['public']['correct']}/{item['public']['total']} | "
            f"{item['kg-private']['correct']}/{item['kg-private']['total']} | "
            f"{item['kg-fact']['correct']}/{item['kg-fact']['total']} |"
        )
    lines += [
        "",
        f"- Strict grounded correctness for original 3B+KG: **{metrics['kg_3b']['strict_grounded']['correct']}/{metrics['kg_3b']['strict_grounded']['total']} ({pct(metrics['kg_3b']['strict_grounded']['accuracy'])})**",
        f"- Retrieval recall@k: **{pct(metrics['retrieval']['recall_at_k'])}**",
        f"- Valid citation rate: **{pct(metrics['retrieval']['valid_citation_rate'])}**",
        f"- Cloud model: `{metrics['cloud_model']}`",
        "",
        "## 100-example held-out adapter comparison",
        "",
        "| Metric | Raw 3B | Fine-tuned 3B |",
        "|---|---:|---:|",
        f"| Mean token F1 | {adapter['base']['mean_token_f1']:.4f} | **{adapter['adapted']['mean_token_f1']:.4f}** |",
        f"| Refusal recall | {pct(adapter['base']['refusal_accuracy'])} | **{pct(adapter['adapted']['refusal_accuracy'])}** |",
        f"| Citation identifier validity | {pct(adapter['base']['citation_validity'])} | {pct(adapter['adapted']['citation_validity'])} |",
        f"| Raw-triplet-free rate | {pct(adapter['base']['raw_triplet_free_rate'])} | {pct(adapter['adapted']['raw_triplet_free_rate'])} |",
        "| Normalized exact matches | 1/100 | **74/100** |",
        "| Citation presence | 0/100 | **87/100** |",
        "",
        "### Category-level mean token F1",
        "",
        "| Category | Examples | Raw 3B | Fine-tuned 3B |",
        "|---|---:|---:|---:|",
        "| Extractive answer | 36 | 0.3004 | **0.8307** |",
        "| Grounded QA | 28 | 0.2123 | **0.9071** |",
        "| Multi-hop | 25 | 0.1662 | **0.8866** |",
        "| Unanswerable | 11 | 0.1722 | **0.9091** |",
        "",
        "The paired mean-F1 improvement is **+0.6466** with a bootstrap 95% interval of **+0.5849 to +0.7047** on this 100-example sample.",
        "",
        "## Complete 50-question answers",
        "",
        "Each entry shows the saved expected concepts and the exact outputs from all three configurations.",
        "",
    ]
    for index, row in enumerate(rows, 1):
        expected = row.get("expected", [])
        expected_text = ", ".join(expected) if isinstance(expected, list) else str(expected)
        lines += [
            "<details>",
            f"<summary><strong>Q{index}. {row['question']}</strong> — {row.get('category', 'unknown')}</summary>",
            "",
            f"**Expected concepts:** {expected_text}",
            "",
            f"**Raw 3B — {'PASS' if row.get('raw_3b_correct') else 'FAIL'}**",
            "",
            block(row.get("raw_3b_answer", "")),
            "",
            f"**Original 3B + KG — {'PASS' if row.get('kg_3b_correct') else 'FAIL'}**",
            "",
            block(row.get("kg_3b_answer", "")),
            "",
            f"**120B cloud — {'PASS' if row.get('cloud_120b_correct') else 'FAIL'}**",
            "",
            block(row.get("cloud_120b_answer", "")),
            "",
            f"**Retrieval:** route `{row.get('retrieval_route', '—')}`, confidence `{row.get('retrieval_confidence', '—')}`, expected evidence found `{row.get('retrieval_contains_expected', '—')}`.",
            "",
            "</details>",
            "",
        ]

    lines += [
        "## Complete 100-example raw-versus-adapter answers",
        "",
        "These examples test answer synthesis from supplied evidence; they do not test retrieval or general world knowledge.",
        "",
    ]
    for index, row in enumerate(adapted_rows, 1):
        lines += [
            "<details>",
            f"<summary><strong>A{index}. {row['question']}</strong> — {row['kind']}</summary>",
            "",
            "**Expected answer**",
            "",
            block(row["expected"]),
            "",
            "**Raw 3B**",
            "",
            block(row["base"]),
            "",
            "**Fine-tuned 3B**",
            "",
            block(row["adapted"]),
            "",
            "</details>",
            "",
        ]

    lines += [
        "## Interpretation and limitations",
        "",
        "- The two evaluations use different datasets and metrics; their numerical scores must not be compared as though they came from one benchmark.",
        "- Token F1 and concept-containment scoring are lexical proxies, not semantic or expert human judgments.",
        "- Citation validity checks whether emitted identifiers exist in the prompt; it does not prove that the cited passage entails the claim.",
        "- The adapter comparison uses the first 100 examples from a 1,007-example held-out file. A complete evaluation remains desirable.",
        "- Three answerable examples received false refusals, and one unanswerable example was answered incorrectly.",
        "- The eight profile-specific questions in the 50-question run depended on an earlier/local graph state that is absent from the current committed graph snapshot.",
        "- The correct next comparison is a read-only rerun of the same 50 questions with the new adapter loaded into the 3B+KG pipeline.",
        "",
        "## Source artifacts",
        "",
        "- `eval/results/accuracy/three_model_50/results.json`",
        "- `finetune/results/grounded_v2_100_comparison.json`",
        "- `finetune/checkpoints/qwen3b-grounded-v2/final_metrics.json`",
        "- `finetune/checkpoints/qwen3b-grounded-v2/best-adapter/`",
        "",
    ]
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT} ({len(lines)} generated lines, {OUTPUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()

"""Compare saved cloud/raw answers with the new fine-tuned 3B on the same 50 questions."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import torch
from peft import PeftModel

from eval.run_50_question_three_model_eval import local_generate, matches
from src.rag_pipeline.agent import load_local_model


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter", default="finetune/checkpoints/qwen3b-grounded-v2/best-adapter")
    parser.add_argument("--source", default="eval/results/accuracy/three_model_50/results.json")
    parser.add_argument("--output-dir", default="eval/results/accuracy/fine_tuned_three_way")
    parser.add_argument("--runtime", choices=("auto", "gpu-4bit", "cpu-int8"), default="auto")
    parser.add_argument("--max-new-tokens", type=int, default=80)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    source = json.loads((root / args.source).read_text(encoding="utf-8"))
    output_dir = root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = output_dir / "checkpoint.json"
    completed = json.loads(checkpoint.read_text(encoding="utf-8")) if args.resume and checkpoint.exists() else []
    by_id = {row["id"]: row for row in completed}

    tokenizer, base = load_local_model(str(root / "local_qwen_3b"), runtime=args.runtime)
    model = PeftModel.from_pretrained(base, str(root / args.adapter))
    model.eval()
    rows = []
    started = time.perf_counter()
    for index, original in enumerate(source["answers"], 1):
        if original["id"] in by_id:
            rows.append(by_id[original["id"]])
            continue
        answer, latency = local_generate(
            tokenizer,
            model,
            [
                {"role": "system", "content": "Answer accurately and concisely in one sentence."},
                {"role": "user", "content": original["question"]},
            ],
            args.max_new_tokens,
        )
        expected = original["expected"].split(" | ")
        row = {
            "id": original["id"], "category": original["category"],
            "question": original["question"], "expected": original["expected"],
            "raw_3b_answer": original["raw_3b_answer"],
            "raw_3b_correct": original["raw_3b_correct"],
            "fine_tuned_3b_answer": answer,
            "fine_tuned_3b_correct": matches(answer, expected),
            "fine_tuned_3b_ms": latency,
            "cloud_120b_answer": original["cloud_120b_answer"],
            "cloud_120b_correct": original["cloud_120b_correct"],
        }
        rows.append(row)
        checkpoint.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[{index:02d}/50] tuned={'PASS' if row['fine_tuned_3b_correct'] else 'FAIL'} {original['question']}", flush=True)

    rows.sort(key=lambda row: int(row["id"]))
    keys = ("raw_3b", "fine_tuned_3b", "cloud_120b")
    metrics = {}
    for key in keys:
        correct = sum(row[f"{key}_correct"] for row in rows)
        metrics[key] = {"correct": correct, "total": len(rows), "accuracy": correct / len(rows)}
        for category in ("public", "kg-private", "kg-fact"):
            selected = [row for row in rows if row["category"] == category]
            passed = sum(row[f"{key}_correct"] for row in selected)
            metrics[key][category] = {"correct": passed, "total": len(selected), "accuracy": passed / len(selected)}
    metrics["fine_tuned_mean_latency_ms"] = sum(row["fine_tuned_3b_ms"] for row in rows) / len(rows)
    metrics["runtime_seconds"] = time.perf_counter() - started
    result = {"metrics": metrics, "answers": rows}
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    labels = {"raw_3b": "Raw 3B", "fine_tuned_3b": "Fine-tuned 3B", "cloud_120b": "Cloud 120B"}
    report = [
        "# Same-question answer comparison: cloud vs raw 3B vs fine-tuned 3B", "",
        "> All three configurations answer the same 50 questions. No KG evidence is supplied in this comparison. The fine-tuned model is therefore tested outside its intended evidence-conditioned pipeline.", "",
        "## Metrics", "", "| Model | Overall | Public | Profile-specific | KG facts |", "|---|---:|---:|---:|---:|",
    ]
    for key in keys:
        item = metrics[key]
        report.append(
            f"| {labels[key]} | {item['correct']}/{item['total']} ({item['accuracy']:.1%}) | "
            f"{item['public']['correct']}/{item['public']['total']} | {item['kg-private']['correct']}/{item['kg-private']['total']} | "
            f"{item['kg-fact']['correct']}/{item['kg-fact']['total']} |"
        )
    report += ["", "## Complete answer differences", ""]
    for row in rows:
        report += [
            "<details>", f"<summary><strong>{row['id']}. {row['question']}</strong> — expected: {row['expected']}</summary>", "",
            f"**Raw 3B — {'PASS' if row['raw_3b_correct'] else 'FAIL'}**", "", *(f"    {line}" for line in row['raw_3b_answer'].splitlines()), "",
            f"**Fine-tuned 3B — {'PASS' if row['fine_tuned_3b_correct'] else 'FAIL'}**", "", *(f"    {line}" for line in row['fine_tuned_3b_answer'].splitlines()), "",
            f"**Cloud 120B — {'PASS' if row['cloud_120b_correct'] else 'FAIL'}**", "", *(f"    {line}" for line in row['cloud_120b_answer'].splitlines()), "",
            "</details>", "",
        ]
    (output_dir / "README.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(metrics, indent=2), flush=True)


if __name__ == "__main__":
    main()

"""100-question comparison: raw 3B, raw 3B+KG, tuned 3B+KG, cloud 120B."""
from __future__ import annotations

import argparse
import json
import random
import re
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from eval.run_50_question_three_model_eval import cloud_generate, local_generate
from src.rag_pipeline.agent import load_local_model
from src.rag_pipeline.settings import Settings


REFUSAL = "i do not have enough verified evidence to answer"


def tokens(value: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", value.lower())


def token_f1(reference: str, prediction: str) -> float:
    expected, actual = Counter(tokens(reference)), Counter(tokens(prediction))
    overlap = sum((expected & actual).values())
    if not expected or not actual or not overlap:
        return 0.0
    precision, recall = overlap / sum(actual.values()), overlap / sum(expected.values())
    return 2 * precision * recall / (precision + recall)


def normalized_exact(reference: str, prediction: str) -> bool:
    return tokens(reference) == tokens(prediction)


def summarize(rows: list[dict], key: str) -> dict:
    f1s = [token_f1(row["expected"], row[key]) for row in rows]
    refusal_rows = [row for row in rows if REFUSAL in row["expected"].lower()]
    answerable = [row for row in rows if REFUSAL not in row["expected"].lower()]
    return {
        "examples": len(rows),
        "mean_token_f1": round(sum(f1s) / len(f1s), 4),
        "normalized_exact_matches": sum(normalized_exact(row["expected"], row[key]) for row in rows),
        "refusal_recall": round(sum(REFUSAL in row[key].lower() for row in refusal_rows) / max(1, len(refusal_rows)), 4),
        "false_refusals": sum(REFUSAL in row[key].lower() for row in answerable),
    }


def paired_comparison(rows: list[dict], challenger: str, baseline: str) -> dict:
    differences = [
        token_f1(row["expected"], row[challenger]) - token_f1(row["expected"], row[baseline])
        for row in rows
    ]
    generator = random.Random(42)
    bootstrap = sorted(
        sum(generator.choice(differences) for _ in differences) / len(differences)
        for _ in range(10_000)
    )
    return {
        "mean_f1_delta": round(sum(differences) / len(differences), 4),
        "bootstrap_95_ci": [round(bootstrap[249], 4), round(bootstrap[9749], 4)],
        "wins": sum(value > 0 for value in differences),
        "ties": sum(value == 0 for value in differences),
        "losses": sum(value < 0 for value in differences),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", default="finetune/data_v2/test.jsonl")
    parser.add_argument("--kg-results", default="finetune/results/grounded_v2_100_comparison.json")
    parser.add_argument("--output-dir", default="eval/results/accuracy/four_model_100")
    parser.add_argument("--runtime", choices=("auto", "gpu-4bit", "cpu-int8"), default="gpu-4bit")
    parser.add_argument("--max-new-tokens", type=int, default=128)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    load_dotenv(root / ".env")
    settings = Settings()
    output = root / args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output / "checkpoint.json"
    test_rows = [json.loads(line) for line in (root / args.test).read_text(encoding="utf-8").splitlines() if line.strip()][:100]
    kg_saved = json.loads((root / args.kg_results).read_text(encoding="utf-8"))["answers"]
    if [row["id"] for row in test_rows] != [row["id"] for row in kg_saved]:
        raise RuntimeError("KG evaluation rows do not align with the first 100 held-out examples")

    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8")) if args.resume and checkpoint_path.exists() else []
    completed = {row["id"]: row for row in checkpoint}
    tokenizer, model = load_local_model(str(settings.local_model_path), runtime=args.runtime)
    cloud = Groq(api_key=settings.groq_api_key.get_secret_value()) if settings.groq_api_key else Groq()
    rows: list[dict] = []
    for index, (source, kg) in enumerate(zip(test_rows, kg_saved), 1):
        if source["id"] in completed:
            rows.append(completed[source["id"]])
            continue
        user_content = source["messages"][-2]["content"]
        question = user_content.split("Question:", 1)[-1].strip()
        started = time.perf_counter()
        raw_answer, raw_ms = local_generate(
            tokenizer, model,
            [{"role": "system", "content": "Answer accurately and concisely in one sentence."}, {"role": "user", "content": question}],
            args.max_new_tokens,
        )
        cloud_answer, cloud_ms = cloud_generate(cloud, settings.kg_model, question)
        row = {
            "id": source["id"], "kind": source["metadata"]["kind"], "question": question,
            "expected": source["messages"][-1]["content"],
            "raw_3b": raw_answer, "raw_3b_ms": raw_ms,
            "raw_3b_kg": kg["base"],
            "fine_tuned_3b_kg": kg["adapted"],
            "cloud_120b": cloud_answer, "cloud_120b_ms": cloud_ms,
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
        }
        rows.append(row)
        checkpoint_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[{index:03d}/100] rawF1={token_f1(row['expected'], raw_answer):.2f} cloudF1={token_f1(row['expected'], cloud_answer):.2f} {question}", flush=True)

    models = ("raw_3b", "raw_3b_kg", "fine_tuned_3b_kg", "cloud_120b")
    metrics = {key: summarize(rows, key) for key in models}
    for key in models:
        metrics[key]["by_kind"] = {}
        grouped: dict[str, list[dict]] = defaultdict(list)
        for row in rows:
            grouped[row["kind"]].append(row)
        for kind, selected in sorted(grouped.items()):
            metrics[key]["by_kind"][kind] = summarize(selected, key)
    metrics["raw_3b"]["mean_generation_ms"] = round(sum(row["raw_3b_ms"] for row in rows) / len(rows), 2)
    metrics["cloud_120b"]["mean_generation_ms"] = round(sum(row["cloud_120b_ms"] for row in rows) / len(rows), 2)
    metrics["paired_fine_tuned_3b_kg"] = {
        baseline: paired_comparison(rows, "fine_tuned_3b_kg", baseline)
        for baseline in ("raw_3b", "raw_3b_kg", "cloud_120b")
    }
    metrics["generated_at"] = datetime.now(timezone.utc).isoformat()
    metrics["design"] = {
        "raw_3b": "question only", "raw_3b_kg": "question plus held-out evidence",
        "fine_tuned_3b_kg": "question plus identical held-out evidence", "cloud_120b": "question only",
    }
    result = {"metrics": metrics, "answers": rows}
    (output / "results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    labels = {
        "raw_3b": "Raw 3B", "raw_3b_kg": "Raw 3B + KG",
        "fine_tuned_3b_kg": "Fine-tuned 3B + KG", "cloud_120b": "Cloud 120B",
    }
    report = [
        "# 100-question four-model evaluation", "",
        "> Same held-out questions and expected answers. Both KG configurations receive the same evidence. Raw 3B and cloud 120B receive only the question.", "",
        "## Overall metrics", "", "| Configuration | Mean token F1 | Exact matches | Refusal recall | False refusals |", "|---|---:|---:|---:|---:|",
    ]
    for key in models:
        item = metrics[key]
        report.append(f"| {labels[key]} | {item['mean_token_f1']:.4f} | {item['normalized_exact_matches']}/100 | {item['refusal_recall']:.1%} | {item['false_refusals']} |")
    report += ["", "## Paired fine-tuned 3B + KG improvement", "", "| Baseline | Mean F1 delta | Bootstrap 95% interval | Wins / ties / losses |", "|---|---:|---:|---:|"]
    for baseline in ("raw_3b", "raw_3b_kg", "cloud_120b"):
        item = metrics["paired_fine_tuned_3b_kg"][baseline]
        report.append(f"| {labels[baseline]} | {item['mean_f1_delta']:+.4f} | [{item['bootstrap_95_ci'][0]:+.4f}, {item['bootstrap_95_ci'][1]:+.4f}] | {item['wins']} / {item['ties']} / {item['losses']} |")
    report += ["", "## Category-level mean token F1", "", "| Configuration | Extractive | Grounded QA | Multi-hop | Unanswerable |", "|---|---:|---:|---:|---:|"]
    for key in models:
        kinds = metrics[key]["by_kind"]
        report.append(f"| {labels[key]} | {kinds['extractive_answer']['mean_token_f1']:.4f} | {kinds['grounded_qa']['mean_token_f1']:.4f} | {kinds['multi_hop']['mean_token_f1']:.4f} | {kinds['unanswerable']['mean_token_f1']:.4f} |")
    report += ["", "## Complete answers", ""]
    for index, row in enumerate(rows, 1):
        report += ["<details>", f"<summary><strong>Q{index}. {row['question']}</strong> — {row['kind']}</summary>", "", "**Expected**", "", *(f"    {line}" for line in row["expected"].splitlines()), ""]
        for key in models:
            report += [f"**{labels[key]}**", "", *(f"    {line}" for line in row[key].splitlines()), ""]
        report += ["</details>", ""]
    report += [
        "## Interpretation limits", "",
        "- Token F1 and exact match are lexical measures; inspect the answers for semantic correctness.",
        "- The held-out evidence blocks act as controlled KG context. This isolates synthesis quality but does not measure live retrieval recall.",
        "- Cloud and raw standalone models are permitted to use memorized knowledge, whereas KG models are trained or prompted to rely on supplied evidence.",
    ]
    (output / "README.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(metrics, indent=2), flush=True)


if __name__ == "__main__":
    main()

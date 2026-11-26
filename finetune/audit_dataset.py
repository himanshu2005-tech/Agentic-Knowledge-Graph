from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from transformers import AutoTokenizer

from .train_qlora import ChatDataset


def normalized_question(row: dict) -> str:
    question = row["messages"][1]["content"].rsplit("Question:", 1)[-1]
    return re.sub(r"[^a-z0-9]+", "", question.lower())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("finetune/data_v2"))
    parser.add_argument("--model", default="local_qwen_3b")
    parser.add_argument("--max-length", type=int, default=384)
    args = parser.parse_args()
    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    report = {"splits": {}, "cross_split_question_overlap": {}, "errors": []}
    question_sets = {}
    for split in ("train", "validation", "test"):
        path = args.data / f"{split}.jsonl"
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        dataset = ChatDataset(path, tokenizer, args.max_length)
        encoded_lengths, supervised_lengths = [], []
        sources, kinds = Counter(), Counter()
        seen_ids = set()
        for index, row in enumerate(rows):
            if row["id"] in seen_ids: report["errors"].append(f"duplicate id in {split}: {row['id']}")
            seen_ids.add(row["id"])
            sources[row["metadata"]["source"]] += 1
            kinds[row["metadata"]["kind"]] += 1
            item = dataset[index]
            encoded_lengths.append(len(item["input_ids"]))
            supervised = sum(label != -100 for label in item["labels"])
            supervised_lengths.append(supervised)
            if supervised == 0: report["errors"].append(f"no supervised tokens: {row['id']}")
            available = set(re.findall(r"\[F(\d+)\]", row["messages"][1]["content"]))
            emitted = set(re.findall(r"\[F(\d+)\]", row["messages"][2]["content"]))
            if not emitted.issubset(available): report["errors"].append(f"invalid citation: {row['id']}")
        question_sets[split] = {normalized_question(row) for row in rows}
        report["splits"][split] = {
            "rows": len(rows), "sources": dict(sources), "kinds": dict(kinds),
            "max_encoded_tokens": max(encoded_lengths),
            "mean_encoded_tokens": round(sum(encoded_lengths) / len(encoded_lengths), 2),
            "min_supervised_tokens": min(supervised_lengths),
        }
    for left, right in (("train", "validation"), ("train", "test"), ("validation", "test")):
        report["cross_split_question_overlap"][f"{left}-{right}"] = len(question_sets[left] & question_sets[right])
    output = args.data / "audit.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["errors"] or any(report["cross_split_question_overlap"].values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

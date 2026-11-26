from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import unicodedata
from collections import Counter
from pathlib import Path

from datasets import load_dataset

from .build_dataset import SYSTEM


SOURCES = {
    "squad_v2": {
        "repo": "rajpurkar/squad_v2",
        "config": "squad_v2",
        "revision": "3ffb306f725f7d2ce8394bc1873b24868140c412",
        "license": "CC BY-SA 4.0",
        "url": "https://huggingface.co/datasets/rajpurkar/squad_v2",
    },
    "hotpot_qa": {
        "repo": "hotpotqa/hotpot_qa",
        "config": "distractor",
        "revision": "1908d6afbbead072334abe2965f91bd2709910ab",
        "license": "CC BY-SA 4.0",
        "url": "https://huggingface.co/datasets/hotpotqa/hotpot_qa",
    },
    "halueval_qa": {
        "repo": "pminervini/HaluEval",
        "config": "qa",
        "revision": "12a856119f03975a94509091e8cada3e6be6ead7",
        "license": "Apache-2.0",
        "url": "https://huggingface.co/datasets/pminervini/HaluEval",
    },
}


def clean(value: str, limit: int) -> str:
    value = unicodedata.normalize("NFKC", str(value))
    value = re.sub(r"<[^>]+>", " ", value)
    value = "".join(char for char in value if char in "\n\t" or ord(char) >= 32)
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value).strip()
    return value[:limit].strip()


def answer_window(context: str, answer: str, limit: int = 850) -> str:
    context = clean(context, 100_000)
    if len(context) <= limit:
        return context
    position = context.lower().find(answer.lower()) if answer else -1
    if position < 0:
        return context[:limit]
    start = max(0, position - limit // 2)
    end = min(len(context), start + limit)
    start = max(0, end - limit)
    return context[start:end].strip()


def record(
    source: str, source_id: str, question: str, evidence: list[str], answer: str, kind: str,
    citation_count: int | None = None,
) -> dict | None:
    question = clean(question, 400)
    answer = clean(answer, 600)
    cleaned_evidence = [clean(item, 1600) for item in evidence if clean(item, 1600)]
    evidence = []
    remaining = 900
    for item in cleaned_evidence:
        if remaining <= 0:
            break
        clipped = item[:remaining].strip()
        if clipped:
            evidence.append(clipped)
            remaining -= len(clipped)
    if not question or not answer or not evidence:
        return None
    cited = "\n".join(f"[F{i}] {item}" for i, item in enumerate(evidence, 1))
    if "[F" not in answer and "not have enough verified evidence" not in answer.lower():
        supported = min(citation_count or len(evidence), len(evidence))
        answer = answer.rstrip(". ") + ". " + " ".join(f"[F{i}]" for i in range(1, supported + 1))
    return {
        "id": f"{source}:{source_id}",
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Evidence:\n{cited}\n\nQuestion: {question}"},
            {"role": "assistant", "content": answer},
        ],
        "metadata": {"kind": kind, "source": source, "source_id": source_id},
    }


def sample_squad(limit: int, seed: int) -> list[dict]:
    meta = SOURCES["squad_v2"]
    dataset = load_dataset(meta["repo"], meta["config"], split="train", revision=meta["revision"])
    answerable, unanswerable = [], []
    for row in dataset:
        target = answerable if row["answers"]["text"] else unanswerable
        target.append(row)
    rng = random.Random(seed)
    rng.shuffle(answerable); rng.shuffle(unanswerable)
    unanswerable_count = min(len(unanswerable), limit // 4)
    chosen = answerable[:limit - unanswerable_count] + unanswerable[:unanswerable_count]
    rng.shuffle(chosen)
    rows = []
    for row in chosen:
        if row["answers"]["text"]:
            answer = row["answers"]["text"][0]
            kind = "extractive_answer"
        else:
            answer = "I do not have enough verified evidence to answer."
            kind = "unanswerable"
        context = answer_window(row["context"], answer if row["answers"]["text"] else "")
        item = record("squad_v2", row["id"], row["question"], [context], answer, kind)
        if item: rows.append(item)
    return rows


def sample_halueval(limit: int, seed: int) -> list[dict]:
    meta = SOURCES["halueval_qa"]
    dataset = load_dataset(meta["repo"], meta["config"], split="data", revision=meta["revision"])
    indices = list(range(len(dataset)))
    random.Random(seed + 1).shuffle(indices)
    rows = []
    for index in indices[:limit]:
        row = dataset[index]
        source_id = hashlib.sha256(f"{index}|{row['question']}".encode()).hexdigest()[:16]
        item = record("halueval_qa", source_id, row["question"], [row["knowledge"]], row["right_answer"], "grounded_qa")
        if item: rows.append(item)
    return rows


def sample_hotpot(limit: int, seed: int) -> list[dict]:
    meta = SOURCES["hotpot_qa"]
    dataset = load_dataset(meta["repo"], meta["config"], split="train", revision=meta["revision"])
    indices = list(range(len(dataset)))
    random.Random(seed + 2).shuffle(indices)
    rows = []
    for index in indices:
        row = dataset[index]
        supporting = {(title, sentence_id) for title, sentence_id in zip(row["supporting_facts"]["title"], row["supporting_facts"]["sent_id"])}
        evidence = []
        distractors = []
        for title, sentences in zip(row["context"]["title"], row["context"]["sentences"]):
            selected = [sentence for sentence_id, sentence in enumerate(sentences) if (title, sentence_id) in supporting]
            if selected:
                evidence.append(f"{title}: {' '.join(selected)}")
            elif sentences and len(distractors) < 1:
                distractors.append(f"{title}: {sentences[0]}")
        supporting_count = len(evidence)
        evidence.extend(distractors)
        item = record(
            "hotpot_qa", row["id"], row["question"], evidence[:4], row["answer"], "multi_hop",
            citation_count=supporting_count,
        )
        if item: rows.append(item)
        if len(rows) >= limit: break
    return rows


def fingerprint(item: dict) -> str:
    user = item["messages"][1]["content"].lower()
    user = re.sub(r"[^a-z0-9]+", "", user)
    return hashlib.sha256(user.encode()).hexdigest()


def write(rows: list[dict], output: Path, seed: int) -> None:
    deduplicated = {}
    rejection_counts = Counter()
    for item in rows:
        key = fingerprint(item)
        if key in deduplicated:
            rejection_counts["exact_normalized_duplicate"] += 1
            continue
        deduplicated[key] = item
    rows = list(deduplicated.values())
    split_rows = {"train": [], "validation": [], "test": []}
    for item in rows:
        question = item["messages"][1]["content"].rsplit("Question:", 1)[-1]
        question_group = re.sub(r"[^a-z0-9]+", "", question.lower())
        bucket = int(hashlib.sha256(question_group.encode()).hexdigest()[:8], 16) % 100
        split = "train" if bucket < 90 else "validation" if bucket < 95 else "test"
        split_rows[split].append(item)
    for values in split_rows.values():
        random.Random(seed).shuffle(values)
    output.mkdir(parents=True, exist_ok=True)
    for split, values in split_rows.items():
        with (output / f"{split}.jsonl").open("w", encoding="utf-8") as handle:
            for item in values:
                handle.write(json.dumps(item, ensure_ascii=False) + "\n")
    manifest = {
        "created_by": "finetune.build_public_dataset",
        "seed": seed,
        "sources": SOURCES,
        "requested_rows": Counter(item["metadata"]["source"] for item in rows),
        "rejections": dict(rejection_counts),
        "splits": {name: len(values) for name, values in split_rows.items()},
        "total": len(rows),
        "cleaning": [
            "Unicode NFKC normalization", "HTML/control-character removal", "whitespace normalization",
            "field length limits", "empty-record removal", "normalized exact deduplication",
            "deterministic normalized-question-group split",
        ],
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, default=dict), encoding="utf-8")
    print(json.dumps(manifest, indent=2, default=dict))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("finetune/data_v2"))
    parser.add_argument("--squad", type=int, default=9000)
    parser.add_argument("--hotpot", type=int, default=5500)
    parser.add_argument("--halueval", type=int, default=5500)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    rows = []
    rows.extend(sample_squad(args.squad, args.seed))
    rows.extend(sample_hotpot(args.hotpot, args.seed))
    rows.extend(sample_halueval(args.halueval, args.seed))
    write(rows, args.output, args.seed)


if __name__ == "__main__":
    main()

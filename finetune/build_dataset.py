from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from collections import defaultdict
from pathlib import Path

from src.rag_pipeline.stores.file import FileKnowledgeStore


SYSTEM = (
    "You are the final answer model in an evidence-aware knowledge graph system. "
    "Answer only from the supplied evidence. Never combine details belonging to different entities. "
    "Translate graph facts into clear natural language instead of repeating raw triples. "
    "If the evidence does not identify the requested entity or support the requested claim, say exactly: "
    "I do not have enough verified evidence to answer."
)


def humanize(value: str) -> str:
    value = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", value)
    value = re.sub(r"[_-]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def evidence_line(index: int, subject: str, relation: str, obj: str) -> str:
    return f"[F{index}] {subject} {relation} {obj}"


def natural_fact(subject: str, relation: str, obj: str) -> str:
    subject_text = humanize(subject)
    object_text = humanize(obj)
    relation_text = humanize(relation).lower()
    templates = {
        "isa": f"{subject_text} is a {object_text}",
        "created": f"{subject_text} created {object_text}",
        "invented": f"{subject_text} invented {object_text}",
        "developed": f"{subject_text} developed {object_text}",
        "holdsposition": f"{subject_text} holds the position of {object_text}",
        "holdsqualification": f"{subject_text} holds a {object_text} qualification",
        "locatedin": f"{subject_text} is located in {object_text}",
        "specializesin": f"{subject_text} specializes in {object_text}",
        "hasresearchinterest": f"{subject_text}'s research interests include {object_text}",
        "authored": f"{subject_text} authored {object_text}",
        "hasexperience": f"{subject_text} has {object_text} of experience",
    }
    compact = re.sub(r"[^a-z]", "", relation.lower())
    return templates.get(compact, f"{subject_text} {relation_text} {object_text}")


def example(question: str, evidence: list[str], answer: str, kind: str, key: str) -> dict:
    user = "Evidence:\n" + "\n".join(evidence) + f"\n\nQuestion: {question}"
    return {
        "id": hashlib.sha256(f"{kind}|{key}|{question}".encode()).hexdigest()[:16],
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
            {"role": "assistant", "content": answer},
        ],
        "metadata": {"kind": kind, "group": key},
    }


def build_examples(store: FileKnowledgeStore, seed: int) -> list[dict]:
    rng = random.Random(seed)
    sourced = [fact for fact in store.all_facts() if fact.sources]
    by_subject: dict[str, list] = defaultdict(list)
    for fact in sourced:
        by_subject[fact.subject].append(fact)

    examples: list[dict] = []
    for subject, facts in sorted(by_subject.items()):
        unique = {(fact.relation.lower(), fact.object.lower()): fact for fact in facts}
        facts = list(unique.values())[:8]
        for fact in facts:
            evidence = [evidence_line(1, fact.subject, fact.relation, fact.object)]
            answer = natural_fact(fact.subject, fact.relation, fact.object) + ". [F1]"
            examples.append(example(
                f"What verified information is available about {humanize(subject)}?",
                evidence, answer, "single_fact", subject,
            ))
        if len(facts) >= 2:
            evidence = [evidence_line(i, fact.subject, fact.relation, fact.object) for i, fact in enumerate(facts, 1)]
            bullets = "\n".join(
                f"- {natural_fact(fact.subject, fact.relation, fact.object)}. [F{i}]"
                for i, fact in enumerate(facts, 1)
            )
            answer = f"{humanize(subject)}\n\nVerified information\n{bullets}"
            examples.append(example(
                f"Give me a structured profile of {humanize(subject)}.",
                evidence, answer, "profile", subject,
            ))

    subjects = list(by_subject)
    for index in range(min(160, max(40, len(sourced) * 2))):
        requested = f"Example Person {index + 1}"
        distractors = rng.sample(sourced, k=min(3, len(sourced))) if sourced else []
        evidence = [
            evidence_line(i, fact.subject, fact.relation, fact.object)
            for i, fact in enumerate(distractors, 1)
        ] or ["[F1] ExampleCampus locatedIn ExampleState"]
        examples.append(example(
            f"Who is {requested}?", evidence,
            "I do not have enough verified evidence to answer.",
            "insufficient_identity", requested,
        ))

    for index in range(min(120, len(subjects) * 3)):
        target = subjects[index % len(subjects)] if subjects else f"Target{index}"
        target_facts = by_subject.get(target, [])[:2]
        others = [fact for fact in sourced if fact.subject != target]
        distractors = rng.sample(others, k=min(2, len(others)))
        combined = target_facts + distractors
        rng.shuffle(combined)
        evidence = [evidence_line(i, fact.subject, fact.relation, fact.object) for i, fact in enumerate(combined, 1)]
        target_lines = []
        for i, fact in enumerate(combined, 1):
            if fact.subject == target:
                target_lines.append(f"- {natural_fact(fact.subject, fact.relation, fact.object)}. [F{i}]")
        if target_lines:
            examples.append(example(
                f"Who is {humanize(target)}? Use only facts about that person or entity.",
                evidence, f"{humanize(target)}\n\n" + "\n".join(target_lines),
                "entity_isolation", target,
            ))

    # Synthetic structural examples teach formatting without memorizing real-world claims.
    roles = ["Professor", "Research Engineer", "Program Chair", "Student"]
    skills = ["Machine Learning", "Network Security", "Data Analytics", "Distributed Computing"]
    for index in range(120):
        name = f"Sample Person {index + 1}"
        role = roles[index % len(roles)]
        skill = skills[index % len(skills)]
        evidence = [
            f"[F1] SamplePerson{index + 1} holdsPosition {role.replace(' ', '')}",
            f"[F2] SamplePerson{index + 1} specializesIn {skill.replace(' ', '')}",
        ]
        answer = f"{name}\n\nRole\n- {role}. [F1]\n\nExpertise\n- {skill}. [F2]"
        examples.append(example(f"Who is {name}?", evidence, answer, "structured_synthetic", name))

    rng.shuffle(examples)
    return examples


def write_splits(examples: list[dict], output: Path, seed: int) -> None:
    output.mkdir(parents=True, exist_ok=True)
    groups: dict[str, list[dict]] = defaultdict(list)
    for item in examples:
        groups[item["metadata"]["group"]].append(item)
    group_names = sorted(groups)
    random.Random(seed).shuffle(group_names)
    train_cut = max(1, int(len(group_names) * 0.80))
    val_cut = max(train_cut + 1, int(len(group_names) * 0.90))
    split_groups = {
        "train": set(group_names[:train_cut]),
        "validation": set(group_names[train_cut:val_cut]),
        "test": set(group_names[val_cut:]),
    }
    manifest = {"seed": seed, "total": len(examples), "splits": {}}
    for split, allowed in split_groups.items():
        rows = [item for item in examples if item["metadata"]["group"] in allowed]
        with (output / f"{split}.jsonl").open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        manifest["splits"][split] = len(rows)
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge", type=Path, default=Path("data/rag/rag_knowledge.txt"))
    parser.add_argument("--provenance", type=Path, default=Path("data/rag/fact_provenance.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("finetune/data"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    store = FileKnowledgeStore(args.knowledge, args.provenance)
    write_splits(build_examples(store, args.seed), args.output, args.seed)


if __name__ == "__main__":
    main()

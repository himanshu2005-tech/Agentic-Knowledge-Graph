"""Paired 50-question evaluation: raw 3B, 3B+KG, and Groq 120B.

The benchmark is read-only: it never expands or modifies the knowledge graph.
Progress is checkpointed after every question so interrupted cloud runs resume.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import torch
from dotenv import load_dotenv
from groq import Groq

from src.rag_pipeline.agent import load_local_model
from src.rag_pipeline.retrieval import HybridRetriever
from src.rag_pipeline.settings import Settings
from src.rag_pipeline.stores.file import FileKnowledgeStore


EXTRA_CASES = [
    ("31", "kg-private", "What academic position does Prasanna Kumar hold?", ["AssociateProfessor"]),
    ("32", "kg-private", "Which courses does Prasanna Kumar teach?", ["DataStructures", "Algorithms"]),
    ("33", "kg-private", "Whom does Prasanna Kumar supervise?", ["PhDStudents"]),
    ("34", "kg-private", "What are Prasanna Kumar's research interests?", ["MachineLearning", "DistributedSystems"]),
    ("35", "kg-private", "What paper did Prasanna Kumar publish?", ["DeepLearningForIoT"]),
    ("36", "kg-private", "What award did Prasanna Kumar receive?", ["BestTeacherAward2022"]),
    ("37", "kg-private", "Where does Prasanna Kumar reside?", ["Chennai"]),
    ("38", "kg-private", "Which professional organizations is Prasanna Kumar a member of?", ["IEEE", "ACM"]),
    ("39", "kg-fact", "Which languages did Pascal influence?", ["Modula2", "Ada"]),
    ("40", "kg-fact", "Which company developed Turbo Pascal?", ["Borland"]),
    ("41", "kg-fact", "Which two core mechanisms does Prolog support?", ["Backtracking", "Unification"]),
    ("42", "kg-fact", "Name two areas where OCaml is used.", ["CompilerConstruction", "FormalVerification"]),
    ("43", "kg-fact", "Which simulation product is included in MATLAB?", ["Simulink"]),
    ("44", "kg-fact", "Which partitioning technique does Quicksort use?", ["Partitioning"]),
    ("45", "kg-fact", "Is Quicksort a stable sorting algorithm?", ["notstable"]),
    ("46", "kg-fact", "Name two areas where Lua is used.", ["GameDevelopment", "EmbeddedSystems"]),
    ("47", "kg-fact", "What does clean cooking reduce?", ["IndoorAirPollution"]),
    ("48", "kg-fact", "What does water sanitation improve?", ["PublicHealth"]),
    ("49", "kg-fact", "What does rural electrification improve?", ["EducationOutcomes"]),
    ("50", "kg-fact", "What does deforestation contribute to?", ["ClimateChange"]),
]


def normalize(value: str) -> str:
    return unicodedata.normalize("NFKD", value)


def concept_tokens(value: str) -> set[str]:
    """Tokenize both natural text and CamelCase gold concepts fairly."""
    value = normalize(value)
    return {
        token.lower()
        for token in re.findall(r"[A-Z]+(?=[A-Z][a-z]|\d|\b)|[A-Z]?[a-z]+|\d+", value)
    }


def matches(answer: str, expected: list[str]) -> bool:
    answer_tokens = concept_tokens(answer)
    for item in expected:
        if item.lower() == "notstable":
            if not {"not", "stable"}.issubset(answer_tokens):
                return False
        elif not concept_tokens(item).issubset(answer_tokens):
            return False
    return True


def load_cases(root: Path) -> list[dict]:
    source = json.loads((root / "data" / "questions.json").read_text(encoding="utf-8"))["questions"]
    cases = []
    for item in source:
        expected = item["expected_answer"]
        cases.append({
            "id": str(item["id"]),
            "category": "public",
            "question": item["question"],
            "expected": expected if isinstance(expected, list) else [expected],
        })
    cases.extend(
        {"id": case_id, "category": category, "question": question, "expected": expected}
        for case_id, category, question, expected in EXTRA_CASES
    )
    if len(cases) != 50:
        raise RuntimeError(f"Expected exactly 50 cases, found {len(cases)}")
    return cases


def local_generate(tokenizer, model, messages: list[dict], max_new_tokens: int) -> tuple[str, float]:
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2500).to(model.device)
    started = time.perf_counter()
    with torch.inference_mode():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            repetition_penalty=1.1,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    answer = tokenizer.decode(
        output[0][inputs["input_ids"].shape[1] :], skip_special_tokens=True
    ).strip()
    return answer, round((time.perf_counter() - started) * 1000, 2)


def cloud_generate(client: Groq, model_name: str, question: str, attempts: int = 5) -> tuple[str, float]:
    for attempt in range(attempts):
        started = time.perf_counter()
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "Answer accurately and concisely in one sentence."},
                    {"role": "user", "content": question},
                ],
                temperature=0,
                max_completion_tokens=160,
                reasoning_effort="low",
            )
            message = response.choices[0].message
            answer = (message.content or "") or getattr(message, "reasoning_content", "") or ""
            return answer.strip(), round((time.perf_counter() - started) * 1000, 2)
        except Exception:
            if attempt == attempts - 1:
                raise
            time.sleep(min(2 ** attempt, 16))
    raise RuntimeError("unreachable")


def write_checkpoint(path: Path, rows: list[dict]) -> None:
    path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")


def aggregate(rows: list[dict], model_key: str, subset: str | None = None) -> tuple[int, int, float]:
    selected = rows if subset is None else [row for row in rows if row["category"] == subset]
    passed = sum(bool(row[f"{model_key}_correct"]) for row in selected)
    return passed, len(selected), passed / len(selected) if selected else 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", choices=("auto", "gpu-4bit", "cpu-int8"), default="auto")
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--max-new-tokens", type=int, default=80)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--refresh-kg", action="store_true", help="Reuse raw/cloud answers and rerun KG answers")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    output_dir = root / "eval" / "results" / "accuracy" / "three_model_50"
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output_dir / "checkpoint.json"
    cases = load_cases(root)
    rows: list[dict] = []
    if args.resume and checkpoint_path.exists():
        rows = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    completed_ids = {row["id"] for row in rows}

    load_dotenv(root / ".env")
    settings = Settings(enable_embeddings=True)
    client = Groq()
    store = FileKnowledgeStore(settings.rag_kb_path, settings.provenance_path)
    retriever = HybridRetriever(store, settings.embedding_model, True)
    tokenizer, model = load_local_model(str(settings.local_model_path), runtime=args.runtime)

    for index, case in enumerate(cases, 1):
        existing = next((row for row in rows if row["id"] == case["id"]), None)
        if existing and not args.refresh_kg:
            continue
        question = case["question"]
        print(f"[{index:02d}/50] {question}", flush=True)
        if existing:
            raw_answer, raw_ms = existing["raw_3b_answer"], existing["raw_3b_ms"]
        else:
            raw_answer, raw_ms = local_generate(
                tokenizer,
                model,
                [
                    {"role": "system", "content": "Answer accurately and concisely in one sentence."},
                    {"role": "user", "content": question},
                ],
                args.max_new_tokens,
            )
        retrieval = retriever.retrieve(question, top_k=args.top_k, threshold=settings.confidence_threshold)
        evidence = "\n".join(
            f"[F{i}] {hit.fact.text}" for i, hit in enumerate(retrieval.hits, 1)
        )
        kg_answer, kg_ms = local_generate(
            tokenizer,
            model,
            [
                {
                    "role": "system",
                    "content": (
                        "Answer only from the supplied evidence, in one concise sentence. "
                        "Include every relevant person or item needed for a complete answer. "
                        "Cite the supporting facts with [F#]. If evidence is insufficient, say so."
                    ),
                },
                {"role": "user", "content": f"Evidence:\n{evidence}\n\nQuestion: {question}"},
            ],
            args.max_new_tokens,
        )
        if existing:
            cloud_answer, cloud_ms = existing["cloud_120b_answer"], existing["cloud_120b_ms"]
        else:
            cloud_answer, cloud_ms = cloud_generate(client, settings.kg_model, question)
        expected = case["expected"]
        evidence_text = " ".join(hit.fact.text for hit in retrieval.hits)
        citations = [int(value) for value in re.findall(r"\[F(\d+)\]", kg_answer)]
        citations_valid = bool(citations) and all(1 <= value <= len(retrieval.hits) for value in citations)
        row = {
            **case,
            "expected": " | ".join(expected),
            "raw_3b_answer": raw_answer,
            "kg_3b_answer": kg_answer,
            "cloud_120b_answer": cloud_answer,
            "raw_3b_correct": matches(raw_answer, expected),
            "kg_3b_correct": matches(kg_answer, expected),
            "cloud_120b_correct": matches(cloud_answer, expected),
            "retrieval_contains_expected": matches(evidence_text, expected),
            "kg_citations_valid": citations_valid,
            "kg_strict_grounded_correct": matches(kg_answer, expected)
            and matches(evidence_text, expected)
            and citations_valid,
            "retrieval_confidence": retrieval.confidence,
            "retrieval_route": retrieval.route,
            "evidence": " || ".join(hit.fact.text for hit in retrieval.hits),
            "raw_3b_ms": raw_ms,
            "kg_3b_ms": kg_ms,
            "cloud_120b_ms": cloud_ms,
        }
        if existing:
            rows[rows.index(existing)] = row
        else:
            rows.append(row)
        write_checkpoint(checkpoint_path, rows)
        print(
            "  scores: raw=%s kg=%s cloud=%s"
            % (row["raw_3b_correct"], row["kg_3b_correct"], row["cloud_120b_correct"]),
            flush=True,
        )

    rows.sort(key=lambda row: int(row["id"]))
    # Always re-grade checkpoints with the current Unicode/CamelCase-aware scorer.
    for row in rows:
        expected = row["expected"].split(" | ")
        row["raw_3b_correct"] = matches(row["raw_3b_answer"], expected)
        row["kg_3b_correct"] = matches(row["kg_3b_answer"], expected)
        row["cloud_120b_correct"] = matches(row["cloud_120b_answer"], expected)
        row["retrieval_contains_expected"] = matches(row["evidence"], expected)
        row["kg_strict_grounded_correct"] = (
            row["kg_3b_correct"]
            and row["retrieval_contains_expected"]
            and row["kg_citations_valid"]
        )
    metrics = {}
    for key in ("raw_3b", "kg_3b", "cloud_120b"):
        passed, total, accuracy = aggregate(rows, key)
        metrics[key] = {"correct": passed, "total": total, "accuracy": accuracy}
        for category in ("public", "kg-private", "kg-fact"):
            p, t, a = aggregate(rows, key, category)
            metrics[key][category] = {"correct": p, "total": t, "accuracy": a}
    grounded = sum(row["kg_strict_grounded_correct"] for row in rows)
    metrics["kg_3b"]["strict_grounded"] = {
        "correct": grounded,
        "total": len(rows),
        "accuracy": grounded / len(rows),
    }
    metrics["retrieval"] = {
        "recall_at_k": sum(row["retrieval_contains_expected"] for row in rows) / len(rows),
        "valid_citation_rate": sum(row["kg_citations_valid"] for row in rows) / len(rows),
    }
    metrics["generated_at"] = datetime.now(timezone.utc).isoformat()
    metrics["cloud_model"] = settings.kg_model
    metrics["question_count"] = len(rows)

    csv_path = output_dir / "answers.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (output_dir / "results.json").write_text(
        json.dumps({"metrics": metrics, "answers": rows}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    report = [
        "# 50-question three-model evaluation",
        "",
        "Same questions; raw 3B and KG-enhanced 3B use the same local model. The KG is read-only. Cloud is `openai/gpt-oss-120b` via Groq.",
        "",
        "| Model | Correct | Accuracy |",
        "|---|---:|---:|",
    ]
    for key, label in (("raw_3b", "Raw 3B"), ("kg_3b", "3B + KG"), ("cloud_120b", "Cloud 120B")):
        item = metrics[key]
        report.append(f"| {label} | {item['correct']}/{item['total']} | {item['accuracy']:.1%} |")
    report.extend([
        "",
        "## Accuracy by question type",
        "",
        "| Model | Public (30) | KG-private (8) | KG facts (12) |",
        "|---|---:|---:|---:|",
    ])
    for key, label in (("raw_3b", "Raw 3B"), ("kg_3b", "3B + KG"), ("cloud_120b", "Cloud 120B")):
        item = metrics[key]
        report.append(
            f"| {label} | {item['public']['correct']}/30 | "
            f"{item['kg-private']['correct']}/8 | {item['kg-fact']['correct']}/12 |"
        )
    report.extend([
        "",
        f"Strict grounded 3B + KG: {grounded}/{len(rows)} ({grounded / len(rows):.1%})",
        f"Retrieval recall@{args.top_k}: {metrics['retrieval']['recall_at_k']:.1%}",
        f"Valid citation rate: {metrics['retrieval']['valid_citation_rate']:.1%}",
        "",
        "Full answers are in `all_answers.md`; machine-readable answers and evidence are in `answers.csv` and `results.json`.",
    ])
    (output_dir / "README.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    answer_report = [
        "# All answers: raw 3B vs 3B + KG vs cloud 120B",
        "",
        "The expected concept and all three verbatim model answers are retained below.",
        "",
    ]
    for row in rows:
        answer_report.extend([
            f"## {row['id']}. {row['question']}",
            "",
            f"Expected: `{row['expected']}`  ",
            f"Category: `{row['category']}`",
            "",
            f"- Raw 3B ({'PASS' if row['raw_3b_correct'] else 'FAIL'}): {row['raw_3b_answer']}",
            f"- 3B + KG ({'PASS' if row['kg_3b_correct'] else 'FAIL'}): {row['kg_3b_answer']}",
            f"- Cloud 120B ({'PASS' if row['cloud_120b_correct'] else 'FAIL'}): {row['cloud_120b_answer']}",
            "",
        ])
    (output_dir / "all_answers.md").write_text("\n".join(answer_report), encoding="utf-8")
    print(json.dumps(metrics, indent=2), flush=True)


if __name__ == "__main__":
    main()

"""Evaluate the real local 3B model with and without retrieved evidence.

This benchmark intentionally avoids Groq/web expansion and never writes to the
knowledge base. It isolates the value added by retrieval and grounded prompting.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import torch

from src.rag_pipeline.agent import load_local_model
from src.rag_pipeline.retrieval import HybridRetriever
from src.rag_pipeline.settings import Settings
from src.rag_pipeline.stores.file import FileKnowledgeStore


CASES = [
    {
        "id": "private-1",
        "category": "knowledge-only",
        "question": "Who supervises PhD students?",
        "expected": ["Prasanna Kumar"],
    },
    {
        "id": "private-2",
        "category": "multi-hop",
        "question": "Which university awarded Prasanna Kumar an MTech?",
        "expected": ["Anna University"],
    },
    {
        "id": "private-3",
        "category": "knowledge-only",
        "question": "Where does Prasanna Kumar reside?",
        "expected": ["Chennai"],
    },
    {
        "id": "domain-1",
        "category": "domain",
        "question": "What does clean cooking reduce?",
        "expected": ["indoor air pollution"],
    },
    {
        "id": "domain-2",
        "category": "domain",
        "question": "What is the average-case time complexity of Quicksort?",
        "expected": ["n log n", "nlogn"],
    },
    {
        "id": "public-1",
        "category": "public-fact",
        "question": "Who invented Pascal?",
        "expected": ["Niklaus Wirth"],
    },
    {
        "id": "public-2",
        "category": "public-fact",
        "question": "Who developed OCaml?",
        "expected": ["Xavier Leroy"],
    },
    {
        "id": "negative-1",
        "category": "retrieval-stress",
        "question": "Who invented JavaScript?",
        "expected": ["Brendan Eich"],
    },
]


@dataclass
class Result:
    id: str
    category: str
    question: str
    expected: str
    raw_answer: str
    rag_answer: str
    raw_correct: bool
    rag_correct: bool
    retrieval_contains_answer: bool
    citations_valid: bool
    retrieval_confidence: float
    retrieval_route: str
    retrieval_ms: float
    raw_generation_ms: float
    rag_generation_ms: float
    evidence: str


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def is_correct(answer: str, expected: list[str]) -> bool:
    compact = normalize(answer)
    return any(normalize(candidate) in compact for candidate in expected)


def citations_are_valid(answer: str, evidence_count: int) -> bool:
    citations = [int(value) for value in re.findall(r"\[F(\d+)\]", answer)]
    return bool(citations) and all(1 <= value <= evidence_count for value in citations)


def generate(tokenizer, model, messages: list[dict], max_new_tokens: int) -> tuple[str, float]:
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
    elapsed_ms = (time.perf_counter() - started) * 1000
    answer = tokenizer.decode(
        output[0][inputs["input_ids"].shape[1] :], skip_special_tokens=True
    ).strip()
    return answer, round(elapsed_ms, 2)


def run(args: argparse.Namespace) -> dict:
    settings = Settings(enable_embeddings=not args.no_embeddings)
    store = FileKnowledgeStore(settings.rag_kb_path, settings.provenance_path)
    retriever = HybridRetriever(store, settings.embedding_model, settings.enable_embeddings)
    tokenizer, model = load_local_model(str(settings.local_model_path), runtime=args.runtime)
    cases = CASES[: args.limit] if args.limit else CASES
    results: list[Result] = []

    for index, case in enumerate(cases, 1):
        question = case["question"]
        print(f"\n[{index}/{len(cases)}] {question}")
        raw_answer, raw_ms = generate(
            tokenizer,
            model,
            [
                {
                    "role": "system",
                    "content": "Answer the question accurately and concisely in one sentence.",
                },
                {"role": "user", "content": question},
            ],
            args.max_new_tokens,
        )
        retrieval = retriever.retrieve(
            question, top_k=args.top_k, threshold=settings.confidence_threshold
        )
        facts = [hit.fact for hit in retrieval.hits]
        evidence = "\n".join(f"[F{i}] {fact.text}" for i, fact in enumerate(facts, 1))
        rag_answer, rag_ms = generate(
            tokenizer,
            model,
            [
                {
                    "role": "system",
                    "content": (
                        "Answer only from the supplied evidence, in one concise sentence. "
                        "Cite factual claims with [F#]. If the evidence is insufficient, say so."
                    ),
                },
                {"role": "user", "content": f"Evidence:\n{evidence}\n\nQuestion: {question}"},
            ],
            args.max_new_tokens,
        )
        expected = case["expected"]
        evidence_text = " ".join(fact.text for fact in facts)
        result = Result(
            id=case["id"],
            category=case["category"],
            question=question,
            expected=" | ".join(expected),
            raw_answer=raw_answer,
            rag_answer=rag_answer,
            raw_correct=is_correct(raw_answer, expected),
            rag_correct=is_correct(rag_answer, expected),
            retrieval_contains_answer=is_correct(evidence_text, expected),
            citations_valid=citations_are_valid(rag_answer, len(facts)),
            retrieval_confidence=retrieval.confidence,
            retrieval_route=retrieval.route,
            retrieval_ms=retrieval.latency_ms,
            raw_generation_ms=raw_ms,
            rag_generation_ms=rag_ms,
            evidence=" || ".join(fact.text for fact in facts),
        )
        results.append(result)
        print(f"  raw={'PASS' if result.raw_correct else 'FAIL'} rag={'PASS' if result.rag_correct else 'FAIL'}")

    raw_passes = sum(row.raw_correct for row in results)
    rag_passes = sum(row.rag_correct for row in results)
    retrieval_passes = sum(row.retrieval_contains_answer for row in results)
    valid_citations = sum(row.citations_valid for row in results)
    grounded_passes = sum(
        row.rag_correct and row.retrieval_contains_answer and row.citations_valid
        for row in results
    )
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_path": str(settings.local_model_path),
        "runtime": args.runtime,
        "embeddings_enabled": settings.enable_embeddings,
        "question_count": len(results),
        "raw_correct": raw_passes,
        "raw_accuracy": raw_passes / len(results),
        "rag_correct": rag_passes,
        "rag_accuracy": rag_passes / len(results),
        "strict_grounded_correct": grounded_passes,
        "strict_grounded_accuracy": grounded_passes / len(results),
        "accuracy_delta_points": (rag_passes - raw_passes) * 100 / len(results),
        "retrieval_recall_at_k": retrieval_passes / len(results),
        "valid_citation_rate": valid_citations / len(results),
        "mean_raw_generation_ms": sum(row.raw_generation_ms for row in results) / len(results),
        "mean_rag_generation_ms": sum(row.rag_generation_ms for row in results) / len(results),
    }
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "actual_3b_rag_eval.csv"
    json_path = output_dir / "actual_3b_rag_eval.json"
    md_path = output_dir / "actual_3b_rag_eval.md"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(results[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(row) for row in results)
    json_path.write_text(
        json.dumps({"summary": summary, "results": [asdict(row) for row in results]}, indent=2),
        encoding="utf-8",
    )
    lines = [
        "# Actual 3B: raw vs RAG evaluation",
        "",
        "This is a deterministic, paired evaluation of the same local model. No Groq or web expansion was used.",
        "",
        f"- Questions: {len(results)}",
        f"- Raw 3B: {raw_passes}/{len(results)} ({summary['raw_accuracy']:.0%})",
        f"- RAG + 3B: {rag_passes}/{len(results)} ({summary['rag_accuracy']:.0%})",
        f"- Strict grounded RAG: {grounded_passes}/{len(results)} ({summary['strict_grounded_accuracy']:.0%})",
        f"- Accuracy delta: {summary['accuracy_delta_points']:+.1f} percentage points",
        f"- Retrieval recall@{args.top_k}: {summary['retrieval_recall_at_k']:.0%}",
        f"- Valid citation rate: {summary['valid_citation_rate']:.0%}",
        "",
        "| ID | Category | Raw | RAG | Retrieved answer | Confidence |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in results:
        lines.append(
            f"| {row.id} | {row.category} | {'PASS' if row.raw_correct else 'FAIL'} | "
            f"{'PASS' if row.rag_correct else 'FAIL'} | "
            f"{'YES' if row.retrieval_contains_answer else 'NO'} | {row.retrieval_confidence:.3f} |"
        )
    lines.extend([
        "",
        "Scoring uses normalized expected-answer containment. Inspect the CSV/JSON for full answers and evidence; this small benchmark is diagnostic, not statistically conclusive.",
    ])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", choices=("auto", "gpu-4bit", "cpu-int8"), default="auto")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--max-new-tokens", type=int, default=96)
    parser.add_argument("--no-embeddings", action="store_true")
    parser.add_argument("--output-dir", default="eval/results/accuracy")
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


REFUSAL = "i do not have enough verified evidence to answer"


def tokens(value: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", value.lower())


def token_f1(reference: str, prediction: str) -> float:
    expected = Counter(tokens(reference))
    actual = Counter(tokens(prediction))
    overlap = sum((expected & actual).values())
    if not expected or not actual or not overlap:
        return 0.0
    precision = overlap / sum(actual.values())
    recall = overlap / sum(expected.values())
    return 2 * precision * recall / (precision + recall)


def generate(model, tokenizer, messages: list[dict], max_new_tokens: int) -> str:
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=384).to(model.device)
    with torch.inference_mode():
        output = model.generate(
            **inputs, max_new_tokens=max_new_tokens, do_sample=False,
            pad_token_id=tokenizer.pad_token_id, eos_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()


def metrics(rows: list[dict], predictions: list[str]) -> dict:
    refusal_rows = [i for i, row in enumerate(rows) if REFUSAL in row["messages"][-1]["content"].lower()]
    citations_valid = 0
    raw_triplet_free = 0
    for row, prediction in zip(rows, predictions):
        available = set(re.findall(r"\[F\d+\]", row["messages"][-2]["content"]))
        emitted = set(re.findall(r"\[F\d+\]", prediction))
        citations_valid += int(emitted.issubset(available))
        raw_triplet_free += int(not re.search(
            r"\b(?:holdsQualification|holdsPosition|locatedIn|specializesIn|hasSkill|isPartOf)\b",
            prediction,
        ))
    return {
        "examples": len(rows),
        "mean_token_f1": round(sum(token_f1(row["messages"][-1]["content"], prediction) for row, prediction in zip(rows, predictions)) / len(rows), 4),
        "refusal_accuracy": round(sum(REFUSAL in predictions[i].lower() for i in refusal_rows) / max(1, len(refusal_rows)), 4),
        "citation_validity": round(citations_valid / len(rows), 4),
        "raw_triplet_free_rate": round(raw_triplet_free / len(rows), 4),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="local_qwen_3b")
    parser.add_argument("--adapter", default="finetune/checkpoints/qwen3b-kg-qlora/best-adapter")
    parser.add_argument("--test", type=Path, default=Path("finetune/data/test.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("finetune/results/adapter_comparison.json"))
    parser.add_argument("--max-examples", type=int, default=0)
    parser.add_argument("--max-new-tokens", type=int, default=128)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.test.read_text(encoding="utf-8").splitlines() if line.strip()]
    if args.max_examples:
        rows = rows[:args.max_examples]
    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    tokenizer.pad_token = tokenizer.pad_token or tokenizer.eos_token
    quantization = BitsAndBytesConfig(
        load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16,
    )
    base = AutoModelForCausalLM.from_pretrained(
        args.model, local_files_only=True, quantization_config=quantization,
        device_map={"": 0}, torch_dtype=torch.float16,
    )
    base_predictions = [generate(base, tokenizer, row["messages"][:-1], args.max_new_tokens) for row in rows]
    adapted = PeftModel.from_pretrained(base, args.adapter)
    adapted_predictions = [generate(adapted, tokenizer, row["messages"][:-1], args.max_new_tokens) for row in rows]
    result = {
        "base": metrics(rows, base_predictions),
        "adapted": metrics(rows, adapted_predictions),
        "answers": [
            {
                "id": row["id"], "kind": row["metadata"]["kind"],
                "question": row["messages"][-2]["content"].split("Question:", 1)[-1].strip(),
                "expected": row["messages"][-1]["content"],
                "base": base_prediction, "adapted": adapted_prediction,
            }
            for row, base_prediction, adapted_prediction in zip(rows, base_predictions, adapted_predictions)
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"base": result["base"], "adapted": result["adapted"]}, indent=2))


if __name__ == "__main__":
    main()

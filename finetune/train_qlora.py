from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import torch
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from torch.utils.data import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    Trainer,
    TrainingArguments,
    set_seed,
)


class ChatDataset(Dataset):
    def __init__(self, path: Path, tokenizer, max_length: int):
        self.rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        messages = self.rows[index]["messages"]
        prompt = self.tokenizer.apply_chat_template(messages[:-1], tokenize=False, add_generation_prompt=True)
        full = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
        prompt_ids = self.tokenizer(prompt, add_special_tokens=False)["input_ids"]
        full_ids = self.tokenizer(full, add_special_tokens=False)["input_ids"]
        answer_ids = full_ids[len(prompt_ids):]
        if len(answer_ids) >= self.max_length:
            answer_ids = answer_ids[:self.max_length - 1]
        prompt_budget = self.max_length - len(answer_ids)
        if len(prompt_ids) > prompt_budget:
            # Preserve both the system instruction and the question at the end.
            head = min(96, prompt_budget // 3)
            prompt_ids = prompt_ids[:head] + prompt_ids[-(prompt_budget - head):]
        input_ids = prompt_ids + answer_ids
        labels = [-100] * len(prompt_ids) + answer_ids
        return {"input_ids": input_ids, "attention_mask": [1] * len(input_ids), "labels": labels}


class Collator:
    def __init__(self, pad_token_id: int):
        self.pad_token_id = pad_token_id

    def __call__(self, rows):
        length = max(len(row["input_ids"]) for row in rows)
        def pad(values, fill): return values + [fill] * (length - len(values))
        return {
            "input_ids": torch.tensor([pad(row["input_ids"], self.pad_token_id) for row in rows]),
            "attention_mask": torch.tensor([pad(row["attention_mask"], 0) for row in rows]),
            "labels": torch.tensor([pad(row["labels"], -100) for row in rows]),
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="local_qwen_3b")
    parser.add_argument("--train", type=Path, default=Path("finetune/data/train.jsonl"))
    parser.add_argument("--validation", type=Path, default=Path("finetune/data/validation.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("finetune/checkpoints/qwen3b-kg-qlora"))
    parser.add_argument("--max-length", type=int, default=384)
    parser.add_argument("--epochs", type=float, default=2.0)
    parser.add_argument("--max-steps", type=int, default=-1)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--gradient-accumulation", type=int, default=8)
    parser.add_argument("--eval-steps", type=int, default=250)
    parser.add_argument("--save-steps", type=int, default=250)
    parser.add_argument("--max-eval-samples", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError("QLoRA training requires a CUDA GPU in this Windows configuration")
    set_seed(args.seed)
    args.output.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    tokenizer.pad_token = tokenizer.pad_token or tokenizer.eos_token
    quantization = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16,
    )
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        local_files_only=True,
        quantization_config=quantization,
        device_map={"": 0},
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
    )
    model.config.use_cache = False
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    model = get_peft_model(model, LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    ))
    model.print_trainable_parameters()
    train = ChatDataset(args.train, tokenizer, args.max_length)
    validation = ChatDataset(args.validation, tokenizer, args.max_length)
    if args.max_eval_samples and len(validation.rows) > args.max_eval_samples:
        validation.rows = validation.rows[:args.max_eval_samples]
    steps_per_epoch = math.ceil(len(train) / args.gradient_accumulation)
    training_args = TrainingArguments(
        output_dir=str(args.output),
        num_train_epochs=args.epochs,
        max_steps=args.max_steps,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=args.gradient_accumulation,
        gradient_checkpointing=True,
        learning_rate=args.learning_rate,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        fp16=True,
        optim="paged_adamw_8bit",
        logging_steps=5,
        eval_strategy="steps",
        eval_steps=min(args.eval_steps, max(10, steps_per_epoch // 2)),
        save_strategy="steps",
        save_steps=min(args.save_steps, max(10, steps_per_epoch // 2)),
        save_total_limit=3,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        report_to="none",
        dataloader_num_workers=0,
        remove_unused_columns=False,
        seed=args.seed,
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train,
        eval_dataset=validation,
        data_collator=Collator(tokenizer.pad_token_id),
    )
    trainer.train(resume_from_checkpoint=True if args.resume else None)
    trainer.save_model(str(args.output / "best-adapter"))
    tokenizer.save_pretrained(args.output / "best-adapter")
    metrics = trainer.evaluate()
    (args.output / "final_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()

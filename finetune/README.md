# Local 3B evidence-grounding fine-tune

This directory builds an auditable instruction dataset and trains a QLoRA adapter for the local Qwen2.5-Coder-3B-Instruct checkpoint.

The dataset teaches evidence-only answering, entity isolation, readable profile formatting, citations, and refusal when evidence is insufficient. Real-world examples are included only when the graph fact has retained source provenance. Synthetic examples teach behavior without adding real-world claims.

## Build the dataset

```powershell
python -m finetune.build_dataset
```

Outputs are written to `finetune/data/train.jsonl`, `validation.jsonl`, `test.jsonl`, and `manifest.json`. Splits are grouped by entity to reduce train/test leakage.

## Smoke-test training

```powershell
python -m finetune.train_qlora --max-steps 2 --output finetune/checkpoints/smoke
```

## Full training

```powershell
python -m finetune.train_qlora --epochs 2
```

The output is a LoRA adapter, not another multi-gigabyte copy of the base model. Keep the original `local_qwen_3b` folder and load the adapter with PEFT for inference.

Do not judge the adapter from training loss alone. Compare the base and adapted model on `finetune/data/test.jsonl` and the existing 30/50-question evaluations before adopting it.

## Evaluate base versus adapter

```powershell
python -m finetune.evaluate_adapter
```

The application automatically loads `finetune/checkpoints/qwen3b-kg-qlora/best-adapter` when it exists. Override that location with `LOCAL_ADAPTER_PATH`.

## Larger public v2 dataset

Download pinned, license-recorded subsets of SQuAD 2.0, HotpotQA, and HaluEval, then clean and audit them:

```powershell
python -m finetune.build_public_dataset
python -m finetune.audit_dataset
```

Validated approximately 12-hour RTX 3050 command:

```powershell
python -m finetune.train_qlora `
  --train finetune/data_v2/train.jsonl `
  --validation finetune/data_v2/validation.jsonl `
  --output finetune/checkpoints/qwen3b-grounded-v2 `
  --max-length 384 `
  --max-steps 1900 `
  --gradient-accumulation 8 `
  --learning-rate 1e-4 `
  --eval-steps 250 `
  --save-steps 250 `
  --max-eval-samples 256
```

Resume after interruption by adding `--resume` to the same command.

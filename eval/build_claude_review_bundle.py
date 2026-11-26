"""Build a secret-free review bundle for independent Claude evaluation."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "eval/results/accuracy/four_model_100"
RESULTS = BUNDLE / "results.json"
TEST = ROOT / "finetune/data_v2/test.jsonl"
SCRIPT = ROOT / "eval/run_100_question_four_model_eval.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    source_rows = [json.loads(line) for line in TEST.read_text(encoding="utf-8").splitlines() if line.strip()][:100]
    if len(result["answers"]) != 100 or len(source_rows) != 100:
        raise RuntimeError("Expected exactly 100 result and source rows")
    if [row["id"] for row in result["answers"]] != [row["id"] for row in source_rows]:
        raise RuntimeError("Result and source IDs are not aligned")

    test_subset = BUNDLE / "test_100.jsonl"
    test_subset.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in source_rows), encoding="utf-8")

    csv_path = BUNDLE / "answers.csv"
    fields = ["id", "kind", "question", "expected", "raw_3b", "raw_3b_kg", "fine_tuned_3b_kg", "cloud_120b", "raw_3b_ms", "cloud_120b_ms"]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: row.get(key, "") for key in fields} for row in result["answers"])

    evaluator_copy = BUNDLE / SCRIPT.name
    shutil.copy2(SCRIPT, evaluator_copy)
    included = [
        BUNDLE / "README.md", RESULTS, csv_path, test_subset, evaluator_copy,
        BUNDLE / "CLAUDE_REVIEW_INSTRUCTIONS.md",
    ]
    manifest = {
        "schema_version": 1,
        "question_count": 100,
        "answer_count": 400,
        "models": ["raw_3b", "raw_3b_kg", "fine_tuned_3b_kg", "cloud_120b"],
        "files": [
            {"name": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in included
        ],
        "excluded": [".env", "API keys", "model weights", "training checkpoints", "full datasets"],
    }
    manifest_path = BUNDLE / "MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    included.append(manifest_path)

    archive = BUNDLE / "claude_review_bundle.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as handle:
        for path in included:
            handle.write(path, arcname=path.name)
    print(f"Created {archive} ({archive.stat().st_size:,} bytes)")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()

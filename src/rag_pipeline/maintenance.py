from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Callable


Triple = tuple[str, str, str, str]


def purge_file_graph_records(
    knowledge_path: Path,
    provenance_path: Path,
    should_remove: Callable[[Triple], bool],
) -> dict[str, object]:
    """Atomically purge matching file-store records after creating backups."""
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backups: list[str] = []
    removed_facts = 0
    removed_provenance = 0

    for path in (knowledge_path, provenance_path):
        backup = path.with_name(f"{path.name}.{stamp}.bak")
        shutil.copy2(path, backup)
        backups.append(str(backup))

    fact_lines = knowledge_path.read_text(encoding="utf-8").splitlines()
    kept_facts: list[str] = []
    for line in fact_lines:
        try:
            domain = line.split("[domain=", 1)[1].split("]", 1)[0]
            subject, relation, obj = [part.strip() for part in line.rsplit("(", 1)[1].rstrip(")").split(",", 2)]
            remove = should_remove((domain, subject, relation, obj))
        except (IndexError, ValueError):
            remove = False
        if remove:
            removed_facts += 1
        else:
            kept_facts.append(line)

    provenance_lines = provenance_path.read_text(encoding="utf-8").splitlines()
    kept_provenance: list[str] = []
    for line in provenance_lines:
        try:
            triple = json.loads(line)["triple"]
            remove = should_remove((triple["domain"], triple["subject"], triple["relation"], triple["object"]))
        except (json.JSONDecodeError, KeyError, TypeError):
            remove = False
        if remove:
            removed_provenance += 1
        else:
            kept_provenance.append(line)

    knowledge_path.write_text("\n".join(kept_facts) + "\n", encoding="utf-8")
    provenance_path.write_text("\n".join(kept_provenance) + "\n", encoding="utf-8")
    return {
        "removed_facts": removed_facts,
        "removed_provenance": removed_provenance,
        "backups": backups,
    }

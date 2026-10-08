from __future__ import annotations

import json
import re
import threading
from collections.abc import Sequence
from pathlib import Path

from ..domain import Fact, RetrievalHit, Source

TRIPLE_RE = re.compile(
    r"\[domain=([A-Za-z0-9_ -]+)\]\s*\(\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*([^)]+?)\s*\)"
)


def tokenize(text: str) -> set[str]:
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
    return {
        token.lower().rstrip("s")
        for token in re.findall(r"[A-Za-z0-9]+", text)
        if len(token) > 2
    }


class FileKnowledgeStore:
    """Zero-infrastructure store retaining compatibility with the legacy text KB."""

    def __init__(self, kb_path: Path, provenance_path: Path):
        self.kb_path = Path(kb_path)
        self.provenance_path = Path(provenance_path)
        self._lock = threading.RLock()
        self._facts: dict[str, Fact] = {}
        self.reload()

    def reload(self) -> None:
        provenance = self._load_provenance()
        facts: dict[str, Fact] = {}
        if self.kb_path.exists():
            for line in self.kb_path.read_text(encoding="utf-8").splitlines():
                match = TRIPLE_RE.fullmatch(line.strip())
                if not match:
                    continue
                seed = Fact(*[part.strip() for part in match.groups()])
                record = provenance.get(seed.id, {})
                source_records = record.get("provenance", {}).get("sources", [])
                sources = tuple(
                    Source(
                        url=item.get("url", ""), title=item.get("title", ""),
                        excerpt=item.get("excerpt", ""), provider=record.get("provenance", {}).get("provider") or "",
                        score=item.get("search_score"),
                    )
                    for item in source_records if item.get("url")
                )
                extraction = record.get("extraction", {})
                facts[seed.id] = Fact(
                    domain=seed.domain, subject=seed.subject, relation=seed.relation, object=seed.object,
                    sources=sources,
                    confidence=float(extraction.get("confidence", 0.8 if sources else 0.5)),
                    verification_status=extraction.get("verification_status", "unverified"),
                )
        with self._lock:
            self._facts = facts

    def _load_provenance(self) -> dict[str, dict]:
        records: dict[str, dict] = {}
        if not self.provenance_path.exists():
            return records
        for line in self.provenance_path.read_text(encoding="utf-8").splitlines():
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("fact_id"):
                records[record["fact_id"]] = record
        return records

    def health(self) -> dict:
        return {"backend": "file", "status": "healthy", "facts": self.count()}

    def count(self) -> int:
        with self._lock:
            return len(self._facts)

    def all_facts(self) -> list[Fact]:
        with self._lock:
            return list(self._facts.values())

    def upsert_facts(self, facts: Sequence[Fact]) -> int:
        self.kb_path.parent.mkdir(parents=True, exist_ok=True)
        self.provenance_path.parent.mkdir(parents=True, exist_ok=True)
        inserted = 0
        with self._lock:
            with self.kb_path.open("a", encoding="utf-8") as handle, self.provenance_path.open("a", encoding="utf-8") as provenance:
                for fact in facts:
                    if fact.id in self._facts:
                        continue
                    handle.write(f"[domain={fact.domain}] ({fact.subject}, {fact.relation}, {fact.object})\n")
                    provenance.write(json.dumps({
                        "schema_version": 1,
                        "fact_id": fact.id,
                        "triple": {
                            "domain": fact.domain, "subject": fact.subject,
                            "relation": fact.relation, "object": fact.object,
                        },
                        "provenance": {
                            "provider": fact.sources[0].provider if fact.sources else None,
                            "retrieved_at": fact.created_at,
                            "sources": [
                                {
                                    "url": source.url, "title": source.title,
                                    "excerpt": source.excerpt, "search_score": source.score,
                                }
                                for source in fact.sources
                            ],
                        },
                        "extraction": {
                            "verification_status": fact.verification_status,
                            "confidence": fact.confidence,
                        },
                    }, ensure_ascii=False) + "\n")
                    self._facts[fact.id] = fact
                    inserted += 1
        return inserted

    def lexical_search(self, query: str, limit: int = 20) -> list[RetrievalHit]:
        query_tokens = tokenize(query)
        if not query_tokens:
            return []
        hits = []
        with self._lock:
            values = tuple(self._facts.values())
        for fact in values:
            subject_tokens = tokenize(fact.subject)
            object_tokens = tokenize(fact.object)
            fact_tokens = subject_tokens | object_tokens | tokenize(fact.relation) | tokenize(fact.domain)
            overlap = query_tokens & fact_tokens
            if not overlap:
                continue
            score = len(overlap) / max(len(query_tokens), 1)
            if subject_tokens & query_tokens:
                score += 0.35
            if object_tokens & query_tokens:
                score += 0.15
            hits.append(RetrievalHit(fact=fact, score=min(score, 1.0), lexical_score=min(score, 1.0), reasons=("lexical",)))
        return sorted(hits, key=lambda hit: hit.score, reverse=True)[:limit]

    def graph_expand(self, entity_names: Sequence[str], limit: int = 20) -> list[RetrievalHit]:
        entities = {token for name in entity_names for token in tokenize(name)}
        if not entities:
            return []
        hits = []
        with self._lock:
            values = tuple(self._facts.values())
        for fact in values:
            if entities & (tokenize(fact.subject) | tokenize(fact.object)):
                hits.append(RetrievalHit(fact=fact, score=0.35, graph_score=0.35, reasons=("graph-neighbor",)))
        return hits[:limit]

    def close(self) -> None:
        return None

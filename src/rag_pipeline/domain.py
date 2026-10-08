from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True, slots=True)
class Source:
    url: str
    title: str = ""
    excerpt: str = ""
    provider: str = ""
    retrieved_at: str = field(default_factory=utc_now)
    score: float | None = None


@dataclass(frozen=True, slots=True)
class Fact:
    domain: str
    subject: str
    relation: str
    object: str
    sources: tuple[Source, ...] = ()
    confidence: float = 0.5
    verification_status: str = "unverified"
    created_at: str = field(default_factory=utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        canonical = "|".join(
            value.strip().lower()
            for value in (self.domain, self.subject, self.relation, self.object)
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @property
    def text(self) -> str:
        return f"{self.subject} {self.relation} {self.object}"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["id"] = self.id
        return payload


@dataclass(frozen=True, slots=True)
class RetrievalHit:
    fact: Fact
    score: float
    lexical_score: float = 0.0
    semantic_score: float = 0.0
    graph_score: float = 0.0
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    query: str
    hits: tuple[RetrievalHit, ...]
    confidence: float
    route: str
    latency_ms: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "confidence": self.confidence,
            "route": self.route,
            "latency_ms": self.latency_ms,
            "hits": [
                {
                    "fact": hit.fact.to_dict(),
                    "score": hit.score,
                    "lexical_score": hit.lexical_score,
                    "semantic_score": hit.semantic_score,
                    "graph_score": hit.graph_score,
                    "reasons": list(hit.reasons),
                }
                for hit in self.hits
            ],
        }

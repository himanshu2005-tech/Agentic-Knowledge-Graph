from __future__ import annotations

import logging
import re
import time
from collections import defaultdict
from collections.abc import Sequence
from difflib import SequenceMatcher

from .domain import Fact, RetrievalHit, RetrievalResult
from .stores.base import KnowledgeStore

logger = logging.getLogger(__name__)


def _entity_tokens(value: str) -> set[str]:
    # Split CamelCase while treating a leading initial (``SBaghavathi``) as a
    # separate token. Initials are then ignored so user spelling variants can
    # still be compared with the meaningful parts of the person's name.
    tokens = re.findall(r"[A-Z]+(?=[A-Z][a-z]|\d|\b)|[A-Z]?[a-z]+|\d+", value)
    return {token.lower() for token in tokens if len(token) > 2}


def _entity_coverage(required: set[str], available: set[str]) -> float:
    if not required:
        return 0.0
    matched = 0
    for token in required:
        if token in available or any(
            len(token) >= 6
            and len(candidate) >= 6
            and SequenceMatcher(None, token, candidate).ratio() >= 0.82
            for candidate in available
        ):
            matched += 1
    return matched / len(required)


class EmbeddingReranker:
    def __init__(self, model_name: str, enabled: bool = True):
        self.model_name = model_name
        self.enabled = enabled
        self._model = None

    def _load(self):
        if not self.enabled:
            return None
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name, device="cpu")
            except Exception as exc:
                logger.warning("Embedding reranker unavailable; continuing with lexical/graph retrieval: %s", exc)
                self.enabled = False
        return self._model

    def scores(self, query: str, facts: Sequence[Fact]) -> list[float]:
        model = self._load()
        if model is None or not facts:
            return [0.0] * len(facts)
        embeddings = model.encode([query, *[fact.text for fact in facts]], normalize_embeddings=True)
        query_vector = embeddings[0]
        return [max(0.0, float(query_vector @ vector)) for vector in embeddings[1:]]


class HybridRetriever:
    """Reciprocal-rank fusion over indexed lexical, graph, and semantic signals."""

    def __init__(self, store: KnowledgeStore, embedding_model: str, enable_embeddings: bool = True):
        self.store = store
        self.reranker = EmbeddingReranker(embedding_model, enable_embeddings)

    def retrieve(self, query: str, entities: Sequence[str] = (), top_k: int = 12, threshold: float = 0.60) -> RetrievalResult:
        started = time.perf_counter()
        lexical = self.store.lexical_search(query, limit=max(top_k * 3, 20))
        graph = self.store.graph_expand(entities, limit=max(top_k * 2, 20)) if entities else []
        candidates: dict[str, Fact] = {}
        ranks: dict[str, dict[str, int]] = defaultdict(dict)
        raw: dict[str, dict[str, float]] = defaultdict(dict)
        for channel, hits in (("lexical", lexical), ("graph", graph)):
            for rank, hit in enumerate(hits, start=1):
                candidates[hit.fact.id] = hit.fact
                ranks[hit.fact.id][channel] = rank
                raw[hit.fact.id][channel] = hit.score

        facts = list(candidates.values())
        semantic_scores = self.reranker.scores(query, facts)
        if any(score > 0 for score in semantic_scores):
            semantic_rank = sorted(range(len(facts)), key=lambda idx: semantic_scores[idx], reverse=True)
            for rank, index in enumerate(semantic_rank, start=1):
                fact_id = facts[index].id
                ranks[fact_id]["semantic"] = rank
                raw[fact_id]["semantic"] = semantic_scores[index]

        fused = []
        for fact in facts:
            channel_ranks = ranks[fact.id]
            rrf = sum(1.0 / (60 + rank) for rank in channel_ranks.values())
            normalized_rrf = min(rrf * 20, 1.0)
            evidence_quality = fact.confidence * (1.0 if fact.sources else 0.8)
            score = 0.75 * normalized_rrf + 0.25 * evidence_quality
            fused.append(RetrievalHit(
                fact=fact, score=round(score, 4),
                lexical_score=round(raw[fact.id].get("lexical", 0.0), 4),
                semantic_score=round(raw[fact.id].get("semantic", 0.0), 4),
                graph_score=round(raw[fact.id].get("graph", 0.0), 4),
                reasons=tuple(sorted(channel_ranks)),
            ))
        fused.sort(key=lambda hit: hit.score, reverse=True)
        selected = tuple(fused[:top_k])
        if not selected:
            confidence = 0.0
        else:
            top_strength = selected[0].score
            depth = min(len(selected) / 5.0, 1.0)
            diversity = min(len({hit.fact.domain for hit in selected}) / 3.0, 1.0)
            confidence = round(min(1.0, 0.65 * top_strength + 0.25 * depth + 0.10 * diversity), 3)
        # A generic high-scoring fact must not satisfy a query about an unknown
        # named entity. Cap confidence when no retrieved fact covers any entity.
        meaningful_entities = [_entity_tokens(entity) for entity in entities]
        meaningful_entities = [tokens for tokens in meaningful_entities if tokens]
        if meaningful_entities and selected:
            # A named-person identity is considered covered only by sourced
            # evidence. Legacy unsourced LLM facts must not unlock a confident
            # answer about a real person. Non-person KG concepts may still use
            # curated local facts without web provenance.
            requires_sourced_identity = bool(re.search(r"\bwho\s+(?:is|was)\b", query, re.IGNORECASE))
            selected_tokens = [
                _entity_tokens(f"{hit.fact.subject} {hit.fact.object}")
                for hit in selected
                if hit.fact.sources or not requires_sourced_identity
            ]
            entity_covered = any(
                _entity_coverage(entity, fact_tokens) >= 0.60
                for entity in meaningful_entities
                for fact_tokens in selected_tokens
            )
            if not entity_covered:
                confidence = min(confidence, 0.35)
        route = "local" if confidence >= threshold else "expand"
        return RetrievalResult(
            query=query, hits=selected, confidence=confidence, route=route,
            latency_ms=round((time.perf_counter() - started) * 1000, 2),
        )

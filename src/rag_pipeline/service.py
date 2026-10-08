from __future__ import annotations

import json
import logging
import re
import threading
from collections.abc import Sequence
from difflib import SequenceMatcher
from pathlib import Path

import torch
from groq import Groq

from .agent import (
    extract_topics_from_question,
    filter_grounded_triplets,
    generate_new_triplets,
    load_local_model,
    search_tavily,
    select_relevant_sources,
)
from .domain import Fact, RetrievalResult, Source, utc_now
from .observability import ROUTES
from .retrieval import HybridRetriever
from .settings import Settings
from .stores.base import KnowledgeStore

logger = logging.getLogger(__name__)


def person_from_question(question: str) -> str | None:
    match = re.search(
        r"\bwho\s+(?:is|was)\s+(.+?)(?=\s+from\b|\s+(?:at|in)\s+[A-Z]|[?.!,]|$)",
        question.strip(), re.IGNORECASE,
    )
    if not match:
        return None
    name = re.sub(r"[^A-Za-z0-9]", "", match.group(1))
    return name if len(name) >= 4 else None


def facts_for_person(question: str, facts: Sequence[Fact]) -> list[Fact]:
    """Keep only sourced facts directly attached to the requested person."""
    person = person_from_question(question)
    if not person:
        return list(facts)
    requested = person.lower()
    selected = []
    for fact in facts:
        subject = re.sub(r"[^a-z0-9]", "", fact.subject.lower())
        same_person = subject == requested or (
            len(subject) >= 8 and len(requested) >= 8
            and SequenceMatcher(None, requested, subject).ratio() >= 0.82
        )
        if same_person and fact.sources:
            selected.append(fact)
    return selected


def evidence_covers_question(question: str, facts: Sequence[Fact]) -> bool:
    """Reject a locally confident result when it misses an explicitly requested facet."""
    question_tokens = set(re.findall(r"[a-z0-9]+", question.lower()))
    evidence = " ".join(fact.text.lower() for fact in facts)
    required_facets = {
        "qualification": ("qualification", "qualifications", "degree", "degrees", "education"),
        "research": ("research", "researches", "interest", "interests"),
        "publication": ("publication", "publications", "paper", "papers"),
        "experience": ("experience", "experienced"),
    }
    evidence_markers = {
        "qualification": ("phd", "doctorate", "mtech", "btech", "be", "degree", "qualification"),
        "research": ("research", "machinelearning", "security", "analytics", "computing"),
        "publication": ("published", "publication", "paper", "authored", "bookchapter"),
        "experience": ("experience", "years"),
    }
    for facet, request_words in required_facets.items():
        if question_tokens.intersection(request_words) and not any(
            marker in evidence for marker in evidence_markers[facet]
        ):
            return False
    return bool(facts)


def extract_explicit_credentials(topic: str, sources: Sequence[dict]) -> list[tuple]:
    """Capture plainly stated degrees that a generative extraction pass may omit."""
    topic_tokens = set(re.findall(r"[A-Z]?[a-z]+", re.sub(r"(?<=[a-z])(?=[A-Z])", " ", topic)))
    blocked = {"amrita", "university", "vidyapeetham", "campus", "school", "college", "department"}
    if len(topic_tokens) < 2 or {token.lower() for token in topic_tokens}.intersection(blocked):
        return []
    text = " ".join(str(source.get("content", "")) for source in sources)
    compact = re.sub(r"[^a-z0-9]", "", text.lower())
    credentials: list[tuple] = []
    patterns = (
        ("phd", "PhD"),
        ("mtech", "MTech"),
        ("btech", "BTech"),
    )
    for marker, canonical in patterns:
        if marker in compact:
            credentials.append(("Education", topic, "holdsQualification", canonical))
    if "mtech" in compact and re.search(r"gold\s+medal", text, re.IGNORECASE):
        credentials.append(("Education", topic, "receivedForMTech", "GoldMedal"))
    return credentials


class LocalSynthesizer:
    """Thread-safe, lazy local model runtime for API and worker processes."""

    def __init__(self, model_path: Path, runtime: str = "auto"):
        self.model_path = str(model_path)
        self.runtime = runtime
        self._tokenizer = None
        self._model = None
        self._load_lock = threading.Lock()
        self._generate_lock = threading.Lock()

    @property
    def loaded(self) -> bool:
        return self._model is not None

    def _ensure_loaded(self) -> None:
        if self.loaded:
            return
        with self._load_lock:
            if not self.loaded:
                self._tokenizer, self._model = load_local_model(self.model_path, runtime=self.runtime)

    def answer(self, question: str, facts: Sequence[Fact], max_new_tokens: int = 512) -> str:
        self._ensure_loaded()
        evidence = "\n".join(f"[F{idx}] {fact.text}" for idx, fact in enumerate(facts, 1))
        messages = [
            {
                "role": "system",
                "content": (
                    "Answer only from the supplied evidence. Never combine details belonging to different people. "
                    "Never infer a person's location, affiliation, role, or qualifications from facts about a campus "
                    "or another person. Translate graph facts into polished natural language; never print raw triples "
                    "such as 'X holdsQualification Y' and never explain graph inference steps. For a person profile, "
                    "use this compact structure: the person's name as a heading, a one-sentence summary, then only "
                    "the applicable sections Role, Affiliation, Qualifications, Expertise, and Location as short bullet "
                    "lists. Omit sections unsupported by evidence. Cite each bullet with [F#]. If the evidence cannot "
                    "identify the requested person, say exactly: 'I do not have enough verified evidence to answer.'"
                ),
            },
            {"role": "user", "content": f"Evidence:\n{evidence}\n\nQuestion: {question}"},
        ]
        prompt = self._tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self._tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2500).to(self._model.device)
        with self._generate_lock, torch.inference_mode():
            output = self._model.generate(
                **inputs, max_new_tokens=max_new_tokens, do_sample=False, repetition_penalty=1.1,
                pad_token_id=self._tokenizer.pad_token_id, eos_token_id=self._tokenizer.eos_token_id,
            )
        return self._tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()


class RAGService:
    def __init__(self, settings: Settings, store: KnowledgeStore, runtime: str = "auto"):
        self.settings = settings
        self.store = store
        self.retriever = HybridRetriever(store, settings.embedding_model, settings.enable_embeddings)
        self.synthesizer = LocalSynthesizer(settings.local_model_path, runtime)
        self.groq = Groq(api_key=settings.groq_api_key.get_secret_value()) if settings.groq_api_key else None
        self._feedback_lock = threading.Lock()

    def retrieve(self, question: str, entities: Sequence[str] = ()) -> RetrievalResult:
        result = self.retriever.retrieve(
            question, entities=entities, top_k=self.settings.retrieval_top_k,
            threshold=self.settings.confidence_threshold,
        )
        ROUTES.labels(result.route).inc()
        return result

    def graph_view(self, query: str = "", domain: str = "", offset: int = 0, limit: int = 200) -> dict:
        facts, total, domains = self.store.graph_page(
            query=query.strip(), domain=domain.strip(), offset=offset, limit=limit
        )
        nodes: dict[str, dict] = {}
        edges = []
        for fact in facts:
            for entity, role in ((fact.subject, "subject"), (fact.object, "object")):
                key = entity.strip().lower()
                node = nodes.setdefault(key, {
                    "id": key, "label": entity, "domains": set(), "degree": 0,
                })
                node["domains"].add(fact.domain)
                node["degree"] += 1
            edges.append({
                "id": fact.id,
                "source": fact.subject.strip().lower(),
                "target": fact.object.strip().lower(),
                "label": fact.relation,
                "domain": fact.domain,
                "confidence": fact.confidence,
                "verification_status": fact.verification_status,
                "source_count": len({source.url for source in fact.sources}),
            })
        serialized_nodes = [
            {**node, "domains": sorted(node["domains"])} for node in nodes.values()
        ]
        serialized_nodes.sort(key=lambda node: (-node["degree"], node["label"].lower()))
        return {
            "nodes": serialized_nodes,
            "edges": edges,
            "domains": domains,
            "pagination": {
                "offset": offset, "limit": limit, "returned": len(facts),
                "total_facts": total, "has_more": offset + len(facts) < total,
            },
        }

    def _expand(self, question: str, entities: Sequence[str]) -> int:
        if self.groq is None:
            return 0
        inserted = 0
        for topic in entities or [question]:
            # Persist only facts grounded in web evidence. The cloud model extracts;
            # it is not itself treated as a factual source.
            readable_topic = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", topic).strip()
            web_query = f'"{readable_topic}" {question} official profile biography qualifications'
            triples: list[tuple] = []
            web_sources: list[dict] = []
            if self.settings.tavily_api_key:
                context, web_sources = search_tavily(
                    web_query,
                    api_key=self.settings.tavily_api_key.get_secret_value(),
                )
                if context:
                    triples = generate_new_triplets(
                        topic, self.groq, self.settings.kg_model, user_question=question, search_context=context
                    )
                    triples.extend(extract_explicit_credentials(topic, web_sources))
                    triples = list(dict.fromkeys(triples))
                    triples = filter_grounded_triplets(triples, web_sources)
            facts = []
            for domain, subject, relation, obj in triples:
                matched_sources = select_relevant_sources(subject, obj, web_sources)
                sources = tuple(
                    Source(
                        url=item["url"], title=item["title"], excerpt=item["content"][:1200],
                        provider="tavily", score=item.get("score"),
                    )
                    for item in matched_sources
                )
                facts.append(Fact(
                    domain=domain, subject=subject, relation=relation, object=obj, sources=sources,
                    confidence=min(0.95, 0.65 + 0.05 * len(sources)),
                    verification_status="web_grounded_unverified",
                    metadata={"model": self.settings.kg_model, "question": question, "query": web_query},
                ))
            inserted += self.store.upsert_facts(facts)
        return inserted

    def answer(self, question: str) -> dict:
        entities = extract_topics_from_question(question, self.groq, self.settings.kg_model) if self.groq else []
        requested_person = person_from_question(question)
        expansion_entities = [requested_person] if requested_person else entities
        retrieval = self.retrieve(question, entities)
        expanded = 0
        retrieved_facts = facts_for_person(question, [hit.fact for hit in retrieval.hits])
        if retrieval.route == "expand" or not evidence_covers_question(question, retrieved_facts):
            expanded = self._expand(question, expansion_entities)
            if expanded:
                retrieval = self.retrieve(question, entities)
        # Do not let generic near-matches become evidence for an unresolved entity.
        eligible_facts = facts_for_person(question, [hit.fact for hit in retrieval.hits])
        facts = eligible_facts if retrieval.route == "local" else []
        eligible_ids = {fact.id for fact in eligible_facts}
        evidence_hits = [hit for hit in retrieval.hits if hit.fact.id in eligible_ids]
        if requested_person and not facts:
            retrieval = RetrievalResult(
                query=retrieval.query, hits=tuple(), confidence=min(retrieval.confidence, 0.35),
                route="expand", latency_ms=retrieval.latency_ms,
            )
            evidence_hits = []
        unique_sources = {source.url for fact in facts for source in fact.sources}
        answer_confidence = min(
            retrieval.confidence,
            0.40 + min(len(facts), 5) * 0.08 + min(len(unique_sources), 2) * 0.10,
        ) if facts else min(retrieval.confidence, 0.35)
        answer = self.synthesizer.answer(question, facts) if facts else "I do not have enough verified evidence to answer."
        return {
            "answer": answer,
            "confidence": round(answer_confidence, 3),
            "route": retrieval.route,
            "expanded_facts": expanded,
            "evidence": [
                {
                    "label": f"F{idx}", "fact": hit.fact.to_dict(), "score": hit.score,
                    "reasons": list(hit.reasons),
                }
                for idx, hit in enumerate(evidence_hits, 1)
            ],
        }

    def submit_feedback(self, question: str, verdict: str, note: str, fact_ids: Sequence[str]) -> dict:
        record = {
            "schema_version": 1, "submitted_at": utc_now(), "question": question,
            "verdict": verdict, "note": note, "fact_ids": list(fact_ids),
        }
        self.settings.feedback_path.parent.mkdir(parents=True, exist_ok=True)
        with self._feedback_lock, self.settings.feedback_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record

    def health(self) -> dict:
        return {
            "status": "healthy", "store": self.store.health(),
            "local_model_loaded": self.synthesizer.loaded,
            "expansion_configured": self.groq is not None,
        }

    def close(self) -> None:
        self.store.close()

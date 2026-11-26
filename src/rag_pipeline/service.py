from __future__ import annotations

import json
import logging
import re
import threading
from datetime import datetime, timezone
from collections.abc import Callable, Sequence
from difflib import SequenceMatcher
from pathlib import Path

import torch
from groq import Groq
from transformers import StoppingCriteria, StoppingCriteriaList

from .agent import (
    _LANG_EXT_MAP,
    evaluate_code_need,
    extract_topics_from_question,
    filter_grounded_triplets,
    generate_code_for_vault,
    generate_new_triplets,
    load_local_model,
    search_tavily,
    select_relevant_sources,
)
from .domain import Fact, RetrievalHit, RetrievalResult, Source, utc_now
from .observability import ROUTES
from .retrieval import HybridRetriever
from .settings import Settings
from .stores.base import KnowledgeStore

logger = logging.getLogger(__name__)

Emit = Callable[..., None]


def _no_emit(stage: str, message: str, **data) -> None:
    return None

# Must stay identical to finetune/build_dataset.py SYSTEM; the LoRA adapter was trained on it.
SYNTHESIS_SYSTEM_PROMPT = (
    "You are the final answer model in an evidence-aware knowledge graph system. "
    "Answer only from the supplied evidence. Never combine details belonging to different entities. "
    "Translate graph facts into clear natural language instead of repeating raw triples. "
    "If the evidence does not identify the requested entity or support the requested claim, say exactly: "
    "I do not have enough verified evidence to answer."
)
NO_EVIDENCE_ANSWER = "I do not have enough verified evidence to answer."
# The adapter was trained on 2-4 facts per prompt and writes roughly one bullet per fact.
MAX_SYNTHESIS_FACTS = 8
RATE_LIMIT_MAX_WAIT_S = 15.0
GENERATION_MAX_SECONDS = 60.0


_SMALL_TALK_WORDS = {
    "hi", "hii", "hello", "hey", "yo", "hola", "namaste", "thanks", "thank", "you", "ok", "okay",
    "good", "morning", "afternoon", "evening", "night", "bye", "goodbye", "there", "sup", "cool", "great",
}
SMALL_TALK_ANSWER = (
    "Hello! I answer questions from the knowledge graph and cite the facts I use. "
    "Try asking about a person, an algorithm, or a programming language."
)


_CODE_HINT = re.compile(
    r"\b(code|coding|implement\w*|program|script|function|snippet|class|sql|query|html|css|javascript|"
    r"typescript|python|java|numpy|pytorch|api|write|build|create)\b|c\+\+",
    re.IGNORECASE,
)


def looks_like_code_request(question: str) -> bool:
    """Cheap pre-filter so ordinary questions do not pay for the cloud code classifier."""
    return bool(_CODE_HINT.search(question))


def is_small_talk(question: str) -> bool:
    """Greetings must not trigger web expansion, which would otherwise persist junk facts."""
    words = re.findall(r"[a-z]+", question.lower())
    return bool(words) and all(word in _SMALL_TALK_WORDS for word in words)


def evidence_text(fact: Fact) -> str:
    """Render boolean-valued facts as plain statements; the 3B model drops a bare 'False'."""
    value = fact.object.strip().lower()
    if value in {"true", "false", "yes", "no"}:
        predicate = re.sub(r"^is", "", fact.relation, flags=re.IGNORECASE) or fact.relation
        negation = "not " if value in {"false", "no"} else ""
        return f"{fact.subject} is {negation}{predicate}"
    return fact.text


_CITATION_RE = re.compile(r"\[?F(\d+)\]?")


def truncate_citation_loop(text: str) -> str:
    """Cut the text where the model restarts enumerating the evidence (F1, F2, ... then F1, F2 again)."""
    matches = [m for m in _CITATION_RE.finditer(text) if m.group(0).startswith("[")]
    labels = [int(m.group(1)) for m in matches]
    for i in range(3, len(labels) - 1):
        if labels[i] == labels[0] and labels[i + 1] == labels[1] and max(labels[:i]) >= 3:
            return text[:matches[i].start()].rstrip()
    return text


def clean_answer(text: str, fact_count: int) -> str:
    """Strip the degenerate tails a small greedy model produces after its real answer."""
    text = text.strip()
    if text.startswith(NO_EVIDENCE_ANSWER.rstrip(".")):
        return NO_EVIDENCE_ANSWER
    for match in _CITATION_RE.finditer(text):
        if match.group(0).startswith("[") and int(match.group(1)) > fact_count:
            text = text[:match.start()]
            break
    return collapse_repeats(truncate_citation_loop(text)) or NO_EVIDENCE_ANSWER


class DegenerationStop(StoppingCriteria):
    def __init__(self, tokenizer, prompt_length: int, fact_count: int):
        self.tokenizer = tokenizer
        self.prompt_length = prompt_length
        self.fact_count = fact_count

    def __call__(self, input_ids, scores, **kwargs) -> bool:
        if input_ids.shape[1] - self.prompt_length < 12:
            return False
        text = self.tokenizer.decode(input_ids[0][self.prompt_length:], skip_special_tokens=True).strip()
        if text.startswith(NO_EVIDENCE_ANSWER.rstrip(".")) and len(text) >= len(NO_EVIDENCE_ANSWER):
            return True
        if any(m.group(0).startswith("[") and int(m.group(1)) > self.fact_count for m in _CITATION_RE.finditer(text)):
            return True
        return truncate_citation_loop(text) != text


def collapse_repeats(text: str) -> str:
    """Drop repeated sentences, the failure mode of a small greedy-decoded model stuck in a loop."""
    seen: set[str] = set()
    lines = []
    for line in text.strip().splitlines():
        kept = []
        for sentence in re.split(r"(?<=[.!?])\s+", line):
            key = re.sub(r"\[F\d+\]|[^a-z0-9]", "", sentence.lower())
            if key and key in seen:
                continue
            if key:
                seen.add(key)
            kept.append(sentence)
        if kept or not line.strip():
            lines.append(" ".join(kept).rstrip())
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


_HONORIFIC_SUFFIXES = {"sir", "madam", "maam", "mam"}
_HONORIFIC_PREFIXES = {"dr", "prof", "professor"}
_NAME_STOPWORDS = {
    "tell", "me", "about", "who", "is", "was", "what", "do", "does", "you", "know", "the", "of", "from",
    "at", "in", "our", "my", "and", "please", "details", "info", "information", "on", "give", "describe",
}


def _name_key(words: Sequence[str], capitalize: bool = False) -> str | None:
    parts = [re.sub(r"[^A-Za-z0-9]", "", word) for word in words]
    parts = [p for p in parts if p and p.lower() not in _HONORIFIC_SUFFIXES | _HONORIFIC_PREFIXES]
    if capitalize:
        parts = [p[0].upper() + p[1:] for p in parts]
    name = "".join(parts)
    return name if len(name) >= 4 else None


def person_from_question(question: str) -> str | None:
    match = re.search(
        r"\bwho\s+(?:is|was)\s+(?:(?:dr|prof|mr|mrs|ms)\.?\s+)?(.+?)(?=\s+from\b|\s+(?:at|in)\s+[A-Z]|[?.!,]|$)",
        question.strip(), re.IGNORECASE,
    )
    # "What are Prasanna Kumar's research interests?" - a multi-word capitalized possessive names a person.
    match = match or re.search(r"\b((?:[A-Z][a-z]+\.?\s+)+[A-Z][a-z]+)['’]s\b", question)
    if match and (name := _name_key(match.group(1).split())):
        return name
    # "Tell me about saravanan sir ..." / "Dr. Priya from ..." - an honorific names a person.
    words = re.findall(r"[A-Za-z][A-Za-z.']*", question)
    lowered = [word.lower().strip(".'") for word in words]
    for index, word in enumerate(lowered):
        if word in _HONORIFIC_SUFFIXES and index > 0:
            start = index
            while start > 0 and index - start < 3 and lowered[start - 1] not in _NAME_STOPWORDS | _HONORIFIC_PREFIXES:
                start -= 1
            return _name_key(words[start:index], capitalize=True)
        if word in _HONORIFIC_PREFIXES:
            end = index + 1
            while end < len(words) and end - index <= 3 and lowered[end] not in _NAME_STOPWORDS | _HONORIFIC_SUFFIXES:
                if end > index + 1 and not words[end][0].isupper():
                    break
                end += 1
            return _name_key(words[index + 1:end], capitalize=True)
    return None


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
    blocked = {
        "amrita", "university", "vidyapeetham", "campus", "school", "college", "department",
        "research", "interests", "interest", "qualification", "qualifications", "education",
        "publications", "experience", "profile", "biography",
    }
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

    def __init__(self, model_path: Path, adapter_path: Path | None = None, runtime: str = "auto"):
        self.model_path = str(model_path)
        self.adapter_path = Path(adapter_path) if adapter_path else None
        self.adapter_loaded = False
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
                if self.adapter_path and (self.adapter_path / "adapter_config.json").exists():
                    from peft import PeftModel
                    self._model = PeftModel.from_pretrained(self._model, str(self.adapter_path))
                    self.adapter_loaded = True
                    logger.info("Loaded local fine-tuning adapter from %s", self.adapter_path)

    def warm_up(self) -> None:
        try:
            self._ensure_loaded()
        except Exception:
            logger.exception("Local model warm-up failed; it will be retried on the first question")

    def answer(self, question: str, facts: Sequence[Fact], max_new_tokens: int = 384) -> str:
        self._ensure_loaded()
        evidence = "\n".join(f"[F{idx}] {evidence_text(fact)}" for idx, fact in enumerate(facts, 1))
        messages = [
            {"role": "system", "content": SYNTHESIS_SYSTEM_PROMPT},
            {"role": "user", "content": f"Evidence:\n{evidence}\n\nQuestion: {question}"},
        ]
        prompt = self._tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self._tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2500).to(self._model.device)
        prompt_length = inputs["input_ids"].shape[1]
        with self._generate_lock, torch.inference_mode():
            output = self._model.generate(
                **inputs, max_new_tokens=max_new_tokens, do_sample=False, repetition_penalty=1.1,
                no_repeat_ngram_size=10, max_time=GENERATION_MAX_SECONDS,
                stopping_criteria=StoppingCriteriaList([DegenerationStop(self._tokenizer, prompt_length, len(facts))]),
                pad_token_id=self._tokenizer.pad_token_id, eos_token_id=self._tokenizer.eos_token_id,
            )
        return clean_answer(self._tokenizer.decode(output[0][prompt_length:], skip_special_tokens=True), len(facts))


class RAGService:
    def __init__(self, settings: Settings, store: KnowledgeStore, runtime: str = "auto"):
        self.settings = settings
        self.store = store
        self.retriever = HybridRetriever(store, settings.embedding_model, settings.enable_embeddings)
        self.synthesizer = LocalSynthesizer(settings.local_model_path, settings.local_adapter_path, runtime)
        self.groq = (
            Groq(api_key=settings.groq_api_key.get_secret_value(), timeout=30.0, max_retries=1)
            if settings.groq_api_key else None
        )
        self._feedback_lock = threading.Lock()
        self._topics_lock = threading.Lock()
        self._topics_cache: dict[str, list[str]] = {}

    def warm_up(self) -> None:
        """Load the embedding and local answer models so the first question is not slowed by loading."""
        self.retriever.reranker._load()
        self.synthesizer.warm_up()

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

    def codevault_page(
        self, query: str = "", language: str = "", offset: int = 0, limit: int = 100
    ) -> dict:
        """Return a bounded, metadata-only page from the local Code Vault."""
        root = self.settings.codevault_path.resolve()
        root.mkdir(parents=True, exist_ok=True)
        query_key = query.strip().lower()
        language_key = language.strip().lower()
        files = []
        languages: dict[str, int] = {}
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            file_language = relative.split("/", 1)[0] if "/" in relative else "other"
            languages[file_language] = languages.get(file_language, 0) + 1
            if language_key and file_language.lower() != language_key:
                continue
            if query_key and query_key not in relative.lower():
                continue
            stat = path.stat()
            files.append({
                "path": relative,
                "name": path.name,
                "language": file_language,
                "extension": path.suffix.lower(),
                "size": stat.st_size,
                "modified_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            })
        files.sort(key=lambda item: (item["language"], item["name"].lower()))
        total = len(files)
        page = files[offset:offset + limit]
        return {
            "files": page,
            "languages": [
                {"name": name, "files": count} for name, count in sorted(languages.items())
            ],
            "pagination": {
                "offset": offset, "limit": limit, "returned": len(page), "total_files": total,
                "has_more": offset + len(page) < total,
            },
        }

    def codevault_file(self, relative_path: str) -> dict:
        """Read one text file while preventing traversal outside the vault."""
        root = self.settings.codevault_path.resolve()
        candidate = (root / relative_path).resolve()
        if candidate == root or root not in candidate.parents or not candidate.is_file():
            raise FileNotFoundError("Code Vault file not found")
        size = candidate.stat().st_size
        if size > 2 * 1024 * 1024:
            raise ValueError("File is too large to preview (2 MB maximum)")
        try:
            content = candidate.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("Binary files cannot be previewed") from exc
        relative = candidate.relative_to(root).as_posix()
        return {"path": relative, "name": candidate.name, "size": size, "content": content}

    def _expand(self, question: str, entities: Sequence[str], emit: Emit = _no_emit) -> int:
        if self.groq is None or not self.settings.tavily_api_key:
            emit("web_skipped", "Web search is not configured, so only local facts can be used")
            return 0
        inserted = 0
        for topic in entities or [question]:
            # Persist only facts grounded in web evidence. The cloud model extracts;
            # it is not itself treated as a factual source.
            readable_topic = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", topic).strip()
            web_query = f'"{readable_topic}" {question} official profile biography qualifications'
            triples: list[tuple] = []
            web_sources: list[dict] = []
            emit("web", f'Searching the web for "{readable_topic}"')
            if self.settings.tavily_api_key:
                context, web_sources = search_tavily(
                    web_query,
                    api_key=self.settings.tavily_api_key.get_secret_value(),
                )
                if not context:
                    emit("web_result", f'No relevant web sources found for "{readable_topic}"', sources=0)
                if context:
                    emit(
                        "web_result", f"Found {len(web_sources)} relevant web source{'s' if len(web_sources) != 1 else ''}",
                        sources=len(web_sources), urls=[item["url"] for item in web_sources[:5]],
                    )
                    emit("extract", "Extracting facts from the sources with the 120B model")
                    triples = generate_new_triplets(
                        topic, self.groq, self.settings.kg_model, user_question=question, search_context=context,
                        max_rate_limit_wait=RATE_LIMIT_MAX_WAIT_S,
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
            added = self.store.upsert_facts(facts)
            inserted += added
            if web_sources:
                emit(
                    "facts_added",
                    f"Added {added} source-verified fact{'s' if added != 1 else ''} to the knowledge graph" if added
                    else "No new facts could be verified against the sources",
                    facts=added,
                )
        return inserted

    def _topics(self, question: str) -> list[str]:
        """Topic extraction samples at temperature 1; cache per question so repeats route the same way."""
        if self.groq is None:
            return []
        key = re.sub(r"\s+", " ", question.strip().lower())
        with self._topics_lock:
            cached = self._topics_cache.get(key)
        if cached is None:
            cached = extract_topics_from_question(question, self.groq, self.settings.kg_model)
            with self._topics_lock:
                if len(self._topics_cache) >= 512:
                    self._topics_cache.clear()
                self._topics_cache[key] = cached
        return list(cached)

    def _retrieve_for_answer(self, question: str, entities: Sequence[str], person: str | None) -> RetrievalResult:
        """For person questions, guarantee the person's own sourced facts are retrieved.

        Generic context (e.g. many campus facts) otherwise fills every top-k slot and crowds them out.
        """
        base = self.retrieve(question, entities)
        if not person:
            return base
        person_facts = facts_for_person(question, [hit.fact for hit in self.store.graph_expand([person], limit=200)])
        if not person_facts:
            return base
        ranked = {hit.fact.id: hit for hit in base.hits}
        person_hits = sorted(
            (ranked.get(fact.id) or RetrievalHit(
                fact=fact, score=round(0.5 + 0.3 * fact.confidence, 4), graph_score=0.35, reasons=("person-match",),
            ) for fact in person_facts),
            key=lambda hit: hit.score, reverse=True,
        )
        person_ids = {hit.fact.id for hit in person_hits}
        hits = tuple([*person_hits, *(hit for hit in base.hits if hit.fact.id not in person_ids)][:self.settings.retrieval_top_k])
        confidence = round(max(base.confidence, min(0.9, 0.6 + 0.05 * len(person_facts))), 3)
        return RetrievalResult(query=base.query, hits=hits, confidence=confidence, route="local", latency_ms=base.latency_ms)

    def _answer_code(self, question: str, emit: Emit) -> dict | None:
        """Serve implementation requests from the Code Vault, generating the file with the 120B model if needed."""
        if self.groq is None or not looks_like_code_request(question):
            return None
        emit("code_check", "Checking whether the question asks for code")
        # The classifier samples at temperature 1; cache it so a repeated question reuses the same vault file.
        key = "code:" + re.sub(r"\s+", " ", question.strip().lower())
        with self._topics_lock:
            decision = self._topics_cache.get(key)
        if decision is None:
            decision = evaluate_code_need(question, [], self.groq, self.settings.kg_model)
            with self._topics_lock:
                self._topics_cache[key] = decision
        needs_code, language, flavor, concept = decision
        language = re.sub(r"[^a-z0-9+#]", "", language.lower())
        if not needs_code or not language:
            return None
        ext = _LANG_EXT_MAP.get(language, ".txt")
        safe_flavor = re.sub(r"[^A-Za-z0-9]", "", flavor.capitalize()) if flavor else ""
        root = self.settings.codevault_path.resolve()
        path = root / language / (f"{concept}_{safe_flavor}{ext}" if safe_flavor else f"{concept}{ext}")
        relative = path.relative_to(root).as_posix()
        readable = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", concept)
        if path.is_file():
            emit("code_vault", f"Found an existing implementation in the Code Vault ({relative})")
        else:
            emit("code_generate", f"Generating {language} code for {readable} with the 120B model")
            created = generate_code_for_vault(
                concept, question, language, flavor, self.groq.with_options(timeout=180.0, max_retries=0),
                self.settings.kg_model, set(), [],
            )
            if not created or not path.is_file():
                emit("code_failed", "Code generation failed; the cloud model did not return a file")
                return {
                    "answer": "I couldn't generate that code right now. Please try again in a moment.",
                    "confidence": 0.0, "route": "code", "expanded_facts": 0, "evidence": [],
                }
            emit("code_saved", f"Saved to the Code Vault as {relative}")
        content = path.read_text(encoding="utf-8", errors="replace")
        flavor_text = f" ({flavor})" if flavor else ""
        return {
            "answer": (
                f"Here is a {language} implementation of {readable}{flavor_text}. "
                f"It is saved in the Code Vault as {relative}.\n\n```{language}\n{content.rstrip()}\n```"
            ),
            "confidence": 0.0, "route": "code", "expanded_facts": 0, "evidence": [],
            "code": {"path": relative, "language": language, "size": path.stat().st_size},
        }

    def answer(self, question: str, emit: Emit = _no_emit) -> dict:
        if is_small_talk(question):
            return {"answer": SMALL_TALK_ANSWER, "confidence": 1.0, "route": "chat", "expanded_facts": 0, "evidence": []}
        code_result = self._answer_code(question, emit)
        if code_result is not None:
            return code_result
        emit("graph", "Checking the knowledge graph")
        entities = self._topics(question)
        requested_person = person_from_question(question)
        expansion_entities = [requested_person] if requested_person else entities
        retrieval = self._retrieve_for_answer(question, entities, requested_person)
        expanded = 0
        retrieved_facts = facts_for_person(question, [hit.fact for hit in retrieval.hits])
        confidence_pct = round(retrieval.confidence * 100)
        if retrieval.route == "expand" or not evidence_covers_question(question, retrieved_facts):
            emit(
                "insufficient",
                f"Not enough information in the knowledge graph ({len(retrieved_facts)} matching facts, "
                f"{confidence_pct}% confidence)",
                facts=len(retrieved_facts), confidence=retrieval.confidence,
            )
            expanded = self._expand(question, expansion_entities, emit)
            if expanded:
                emit("graph", "Re-checking the knowledge graph with the new facts")
                retrieval = self._retrieve_for_answer(question, entities, requested_person)
        else:
            emit(
                "graph_hit",
                f"Found {len(retrieved_facts)} relevant facts in the knowledge graph ({confidence_pct}% confidence)",
                facts=len(retrieved_facts), confidence=retrieval.confidence,
            )
        # Do not let generic near-matches become evidence for an unresolved entity.
        eligible_facts = facts_for_person(question, [hit.fact for hit in retrieval.hits])[:MAX_SYNTHESIS_FACTS]
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
        if facts:
            emit("synthesize", f"Writing the answer with the local 3B model from {len(facts)} verified facts")
        else:
            emit("no_evidence", "No verified evidence was found for this question")
        answer = self.synthesizer.answer(question, facts) if facts else NO_EVIDENCE_ANSWER
        if answer == NO_EVIDENCE_ANSWER:
            # A refusal used no evidence; never show high confidence or sources next to it.
            answer_confidence = min(answer_confidence, 0.35)
            evidence_hits = []
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
            "local_adapter_loaded": self.synthesizer.adapter_loaded,
            "expansion_configured": self.groq is not None,
        }

    def close(self) -> None:
        self.store.close()

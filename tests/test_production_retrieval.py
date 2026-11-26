from pathlib import Path

from src.rag_pipeline.domain import Fact, Source
from src.rag_pipeline.retrieval import HybridRetriever
from src.rag_pipeline.service import (
    clean_answer,
    collapse_repeats,
    evidence_covers_question,
    evidence_text,
    extract_explicit_credentials,
    facts_for_person,
    is_small_talk,
    person_from_question,
    truncate_citation_loop,
)
from src.rag_pipeline.stores.file import FileKnowledgeStore


def test_evidence_text_renders_boolean_facts_as_statements():
    assert evidence_text(Fact("CS", "Quicksort", "isstable", "False")) == "Quicksort is not stable"
    assert evidence_text(Fact("CS", "MergeSort", "isStable", "true")) == "MergeSort is Stable"
    assert evidence_text(Fact("CS", "Quicksort", "uses", "Recursion")) == "Quicksort uses Recursion"


def test_collapse_repeats_removes_generation_loops():
    looped = "Tony Hoare\n\n- [F1] Tony Hoare invented Quicksort. [F2] It is fast. [F1] Tony Hoare invented Quicksort. [F2] It is fast."
    assert collapse_repeats(looped) == "Tony Hoare\n\n- [F1] Tony Hoare invented Quicksort. [F2] It is fast."
    clean = "Niklaus Wirth\n\n- Invented Pascal. [F1]\n- Born in Switzerland. [F2]"
    assert collapse_repeats(clean) == clean


def test_possessive_person_questions_are_person_scoped():
    assert person_from_question("What are Prasanna Kumar's research interests?") == "PrasannaKumar"
    assert person_from_question("What is Dijkstra's algorithm?") is None
    assert person_from_question("Explain how Quicksort works.") is None
    facts = [
        Fact("CS", "PrasannaKumar", "hasresearchinterest", "DataMining", sources=(Source(url="https://a.example"),)),
        Fact("CS", "PrasannaKumarAcharya", "hasresearchinterest", "NanoTechnology", sources=(Source(url="https://b.example"),)),
    ]
    assert facts_for_person("What are Prasanna Kumar's research interests?", facts) == [facts[0]]


def test_honorific_questions_are_person_scoped():
    assert person_from_question("Tell me about saravanan sir from amrita chennai campus") == "Saravanan"
    assert person_from_question("Tell me about Priya madam") == "Priya"
    assert person_from_question("What does Dr. Ramesh Kumar teach?") == "RameshKumar"
    assert person_from_question("Prof Anand from Amrita") == "Anand"
    assert person_from_question("who is saravanan sir?") == "saravanan"
    assert person_from_question("Who is Dr. Sriram Devanathan from Amrita?") == "SriramDevanathan"
    assert person_from_question("Who is Prof. Anand?") == "Anand"
    assert person_from_question("What is a binary search tree?") is None


def test_person_facts_are_not_crowded_out_by_generic_context(tmp_path: Path):
    from src.rag_pipeline.service import RAGService
    from src.rag_pipeline.settings import Settings

    store = FileKnowledgeStore(tmp_path / "facts.txt", tmp_path / "provenance.jsonl")
    source = (Source(url="https://www.amrita.edu/faculty/s-saravanan-chennai"),)
    campus = [Fact("Education", f"Campus{i}Chennai", "isPartOf", "AmritaChennaiCampus", sources=source) for i in range(20)]
    person = Fact("Education", "Saravanan", "isA", "AssistantProfessor", sources=source, confidence=0.8)
    store.upsert_facts([*campus, person])
    settings = Settings(_env_file=None, RAG_ENABLE_EMBEDDINGS=False, RAG_RETRIEVAL_TOP_K=5)
    service = RAGService(settings, store)
    question = "Tell me about saravanan sir from amrita chennai campus"
    result = service._retrieve_for_answer(question, ["AmritaChennaiCampus"], "Saravanan")
    assert result.route == "local"
    assert result.hits[0].fact.id == person.id


def test_chat_stream_emits_pipeline_steps_then_answer():
    import json

    from fastapi.testclient import TestClient

    from src.rag_pipeline import api

    class FakeService:
        def answer(self, question, emit):
            emit("graph", "Checking the knowledge graph")
            emit("insufficient", "Not enough information")
            emit("web", 'Searching the web for "X"')
            return {"answer": "ok", "confidence": 0.8, "route": "local", "expanded_facts": 2, "evidence": []}

    api.app.state.service = FakeService()
    with TestClient(api.app).stream("POST", "/v1/chat/stream", json={"question": "Who is X?"}) as response:
        body = "".join(response.iter_text())
    events = [json.loads(chunk[len("data: "):]) for chunk in body.split("\n\n") if chunk.startswith("data: ")]
    assert [event["stage"] for event in events] == ["graph", "insufficient", "web", "done"]
    assert events[-1]["result"]["answer"] == "ok"


def test_code_requests_are_served_from_the_code_vault(tmp_path: Path, monkeypatch):
    from src.rag_pipeline import service as service_module
    from src.rag_pipeline.settings import Settings

    assert service_module.looks_like_code_request("Give me code for neural network using just numpy")
    assert not service_module.looks_like_code_request("What is photosynthesis?")

    vault = tmp_path / "codevault"
    (vault / "python").mkdir(parents=True)
    (vault / "python" / "NeuralNetwork_Numpy.py").write_text("import numpy as np\n", encoding="utf-8")
    monkeypatch.setattr(service_module, "evaluate_code_need", lambda *a: (True, "python", "Numpy", "NeuralNetwork"))
    store = FileKnowledgeStore(tmp_path / "facts.txt", tmp_path / "provenance.jsonl")
    settings = Settings(_env_file=None, RAG_ENABLE_EMBEDDINGS=False, GROQ_API_KEY="test-key")
    settings.codevault_path = vault
    svc = service_module.RAGService(settings, store)
    stages = []
    result = svc.answer("Give me code for neural network using just numpy", emit=lambda stage, message, **_: stages.append(stage))
    assert result["route"] == "code"
    assert result["code"]["path"] == "python/NeuralNetwork_Numpy.py"
    assert "```python\nimport numpy as np\n```" in result["answer"]
    assert stages == ["code_check", "code_vault"]


def test_credentials_are_not_attributed_to_generic_topics():
    sources = [{"content": "She holds a PhD and an MTech."}]
    assert extract_explicit_credentials("ResearchInterests", sources) == []


def test_small_talk_detection():
    assert is_small_talk("hello")
    assert is_small_talk("Hi there!")
    assert is_small_talk("thank you")
    assert not is_small_talk("hello world program in python")
    assert not is_small_talk("Who invented Pascal?")
    assert not is_small_talk("???")


def test_clean_answer_drops_refusal_tails_and_invented_citations():
    rambling = "I do not have enough verified evidence to answer. [F1] PascalLanguage isA Language. [F9] Wirth."
    assert clean_answer(rambling, 8) == "I do not have enough verified evidence to answer."
    invented = "Niklaus Wirth\n\n- Created Pascal. [F2]\n- Born in Winterthur. [F9] Wirt. [F10] Wurth."
    assert clean_answer(invented, 8) == "Niklaus Wirth\n\n- Created Pascal. [F2]\n- Born in Winterthur."


def test_truncate_citation_loop_cuts_restarted_enumeration():
    looped = "Tony Hoare\n\n- [F1] Invented it. [F2] Developed it. [F3] Sorts. [F1] Invented Quiksort. [F2] Developd it."
    assert truncate_citation_loop(looped) == "Tony Hoare\n\n- [F1] Invented it. [F2] Developed it. [F3] Sorts."
    normal = "Quicksort partitions arrays [F2] and recurses [F5]. It was invented by Tony Hoare [F1]. It is in place [F3]."
    assert truncate_citation_loop(normal) == normal


def test_file_store_round_trip_and_hybrid_routing(tmp_path: Path):
    store = FileKnowledgeStore(tmp_path / "facts.txt", tmp_path / "provenance.jsonl")
    facts = [
        Fact("Physics", "QuantumMechanics", "studies", "AtomicSystems", confidence=0.9),
        Fact("Physics", "QuantumMechanics", "includes", "WaveParticleDuality", confidence=0.9),
        Fact("Programming", "Python", "isA", "Language", confidence=0.9),
    ]
    assert store.upsert_facts(facts) == 3
    assert store.upsert_facts(facts) == 0

    result = HybridRetriever(store, "unused", enable_embeddings=False).retrieve(
        "Explain quantum mechanics", entities=["QuantumMechanics"], top_k=5, threshold=0.50
    )
    assert result.route == "local"
    assert result.confidence >= 0.50
    assert [hit.fact.subject for hit in result.hits] == ["QuantumMechanics", "QuantumMechanics"]


def test_file_store_preserves_source_metadata(tmp_path: Path):
    source = Source(url="https://example.com/evidence", title="Evidence")
    fact = Fact("Science", "Earth", "orbits", "Sun", sources=(source,))
    store = FileKnowledgeStore(tmp_path / "facts.txt", tmp_path / "provenance.jsonl")
    store.upsert_facts([fact])
    reloaded = FileKnowledgeStore(tmp_path / "facts.txt", tmp_path / "provenance.jsonl")
    saved = reloaded.all_facts()[0]
    assert saved.sources[0].url == "https://example.com/evidence"


def test_graph_page_is_filtered_paginated_and_reports_domains(tmp_path: Path):
    store = FileKnowledgeStore(tmp_path / "facts.txt", tmp_path / "provenance.jsonl")
    store.upsert_facts([
        Fact("Programming", "GuidoVanRossum", "created", "Python"),
        Fact("Programming", "BrendanEich", "created", "JavaScript"),
        Fact("Science", "Earth", "orbits", "Sun"),
    ])
    facts, total, domains = store.graph_page(query="created", domain="Programming", offset=1, limit=1)
    assert total == 2
    assert len(facts) == 1
    assert facts[0].subject == "GuidoVanRossum"
    assert domains == [{"name": "Programming", "facts": 2}, {"name": "Science", "facts": 1}]


def test_low_evidence_routes_to_expansion(tmp_path: Path):
    store = FileKnowledgeStore(tmp_path / "facts.txt", tmp_path / "provenance.jsonl")
    result = HybridRetriever(store, "unused", enable_embeddings=False).retrieve("Unknown subject")
    assert result.route == "expand"
    assert result.confidence == 0.0


def test_unknown_named_entity_cannot_be_satisfied_by_generic_facts(tmp_path: Path):
    store = FileKnowledgeStore(tmp_path / "facts.txt", tmp_path / "provenance.jsonl")
    store.upsert_facts([
        Fact("Education", "AmritapuriCampus", "locatedIn", "Kerala", confidence=0.9),
        Fact("Education", "ChennaiCampus", "locatedIn", "TamilNadu", confidence=0.9),
        Fact("Education", "ComputerScience", "isA", "Department", confidence=0.9),
    ])
    result = HybridRetriever(store, "unused", enable_embeddings=False).retrieve(
        "What are Baghavathi Priya's qualifications and campus?",
        entities=["BaghavathiPriya"],
        top_k=10,
        threshold=0.60,
    )
    assert result.route == "expand"
    assert result.confidence <= 0.35


def test_unsourced_person_facts_cannot_unlock_confident_identity_answer(tmp_path: Path):
    store = FileKnowledgeStore(tmp_path / "facts.txt", tmp_path / "provenance.jsonl")
    store.upsert_facts([
        Fact("Education", "PrasannaKumar", "isA", "Professor", confidence=0.95),
        Fact("Education", "PrasannaKumar", "obtainedDegree", "PhD", confidence=0.95),
    ])
    result = HybridRetriever(store, "unused", enable_embeddings=False).retrieve(
        "Who is Prasanna Kumar from Amrita Chennai?", entities=["PrasannaKumar"], threshold=0.50
    )
    assert result.route == "expand"
    assert result.confidence <= 0.35


def test_minor_person_name_misspelling_matches_verified_subject(tmp_path: Path):
    store = FileKnowledgeStore(tmp_path / "facts.txt", tmp_path / "provenance.jsonl")
    source = Source(url="https://www.amrita.edu/faculty/s-baghavathi-priya", title="Official profile")
    store.upsert_facts([
        Fact("Education", "SBaghavathiPriya", "isA", "AssociateProfessor", confidence=0.9, sources=(source,)),
        Fact("Education", "SBaghavathiPriya", "earned", "PhD", confidence=0.9, sources=(source,)),
        Fact("Education", "SBaghavathiPriya", "earned", "MTechGoldMedal", confidence=0.9, sources=(source,)),
    ])
    result = HybridRetriever(store, "unused", enable_embeddings=False).retrieve(
        "Who is Bhagavati Priya and what are her qualifications?",
        entities=["BhagavatiPriya"],
        top_k=10,
        threshold=0.50,
    )
    assert result.route == "local"
    assert result.confidence >= 0.50


def test_requested_qualifications_require_degree_evidence():
    profile_only = [Fact("Education", "SBaghavathiPriya", "isA", "AssociateProfessor")]
    with_degree = profile_only + [Fact("Education", "SBaghavathiPriya", "earned", "PhD")]
    question = "Who is Bhagavati Priya and what are her qualifications?"
    assert not evidence_covers_question(question, profile_only)
    assert evidence_covers_question(question, with_degree)


def test_explicit_official_credentials_survive_incomplete_llm_extraction():
    sources = [{"content": "She received a gold medal in M.Tech degree and a Ph.D. from JNTUH."}]
    assert extract_explicit_credentials("BhagavatiPriya", sources) == [
        ("Education", "BhagavatiPriya", "holdsQualification", "PhD"),
        ("Education", "BhagavatiPriya", "holdsQualification", "MTech"),
        ("Education", "BhagavatiPriya", "receivedForMTech", "GoldMedal"),
    ]
    assert extract_explicit_credentials("AmritaVishwaVidyapeethamChennaiCampus", sources) == []


def test_person_profile_context_excludes_other_people_and_generic_campus_facts():
    source = Source(url="https://www.amrita.edu/faculty/madhumita", title="Official profile")
    facts = [
        Fact("Education", "MadhumitaKarthikeyan", "holdsPosition", "Professor", sources=(source,)),
        Fact("Education", "MadhunalaHimanshu", "locatedIn", "Chennai", sources=(source,)),
        Fact("Education", "ChennaiCampus", "locatedIn", "TamilNadu", sources=(source,)),
    ]
    question = "Who is Madhumita Karthikeyan from Amrita Vishwa Vidyapeetham Chennai?"
    assert person_from_question(question) == "MadhumitaKarthikeyan"
    assert facts_for_person(question, facts) == [facts[0]]

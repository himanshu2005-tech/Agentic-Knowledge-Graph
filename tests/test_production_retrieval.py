from pathlib import Path

from src.rag_pipeline.domain import Fact, Source
from src.rag_pipeline.retrieval import HybridRetriever
from src.rag_pipeline.service import (
    evidence_covers_question,
    extract_explicit_credentials,
    facts_for_person,
    person_from_question,
)
from src.rag_pipeline.stores.file import FileKnowledgeStore


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

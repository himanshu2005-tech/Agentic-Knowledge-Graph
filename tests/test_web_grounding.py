from src.rag_pipeline.agent import (
    filter_grounded_triplets,
    rank_web_sources,
    select_relevant_sources,
)


def test_first_party_academic_source_ranks_above_aggregator():
    query = '"Baghavathi Priya" Amrita Chennai qualifications official profile'
    results = [
        {
            "title": "Faculty profile mirror",
            "url": "https://people.example.com/baghavathi-priya",
            "content": "Baghavathi Priya teaches at Amrita Chennai and has academic qualifications.",
            "score": 0.92,
        },
        {
            "title": "Dr. S. Baghavathi Priya",
            "url": "https://www.amrita.edu/faculty/s-baghavathi-priya/",
            "content": "Baghavathi Priya is Associate Professor at Amrita Chennai. She received a Ph.D.",
            "score": 0.84,
        },
        {
            "title": "Priya Bhagavathy",
            "url": "https://example.edu/people/priya-bhagavathy",
            "content": "Priya Bhagavathy has an academic profile at another university.",
            "score": 0.99,
        },
    ]
    ranked = rank_web_sources(query, results)
    assert ranked[0]["url"].startswith("https://www.amrita.edu/")
    assert ranked[0]["authority_score"] == 1.0
    assert all("example.com" not in source["url"] for source in ranked)


def test_irrelevant_generic_campus_page_is_filtered_out():
    results = [{
        "title": "Amrita campuses",
        "url": "https://www.amrita.edu/about",
        "content": "The university has campuses in Chennai, Amritapuri, Bengaluru, and Coimbatore.",
        "score": 0.9,
    }]
    assert rank_web_sources("Baghavathi Priya qualifications research", results) == []


def test_requested_campus_must_appear_in_person_source():
    results = [{
        "title": "Madhumitha Karthikeyan",
        "url": "https://example.edu/madhumitha",
        "content": "Madhumitha Karthikeyan studies at Amrita Vishwa Vidyapeetham in Coimbatore.",
        "score": 0.9,
    }]
    query = '"Madhumita Karthikeyan" Amrita Vishwa Vidyapeetham Chennai'
    assert rank_web_sources(query, results) == []


def test_unsupported_extracted_triples_are_rejected():
    sources = [{
        "title": "Dr. S. Baghavathi Priya",
        "url": "https://www.amrita.edu/faculty/s-baghavathi-priya/",
        "content": "S. Baghavathi Priya is an Associate Professor at the Chennai campus.",
        "score": 0.9,
    }]
    triples = [
        ("Education", "SBaghavathiPriya", "holdsPosition", "AssociateProfessor"),
        ("Education", "SBaghavathiPriya", "worksAt", "AmritapuriCampus"),
    ]
    assert select_relevant_sources("SBaghavathiPriya", "AssociateProfessor", sources)
    assert filter_grounded_triplets(triples, sources) == [triples[0]]


def test_minor_name_typo_and_phd_abbreviation_still_match_official_evidence():
    sources = [{
        "title": "Dr. S. Baghavathi Priya",
        "url": "https://www.amrita.edu/faculty/s-baghavathi-priya/",
        "content": (
            "S. Baghavathi Priya is an Associate Professor at Chennai. "
            "She received her Ph.D. from Jawaharlal Nehru Technological University Hyderabad."
        ),
        "score": 0.9,
    }]
    assert select_relevant_sources("BhagavathiPriya", "PhD", sources)
    assert select_relevant_sources("BhagavatiPriya", "PhD", sources)
    ranked = rank_web_sources('"Bhagavathi Priya" qualifications', sources)
    assert ranked[0]["url"].startswith("https://www.amrita.edu/")

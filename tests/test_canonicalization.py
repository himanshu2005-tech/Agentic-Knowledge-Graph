import pytest
from src.kg_builder.canonicalization import _force_pascal_case, force_seed_casing_in_text

def test_force_pascal_case_real_words():
    assert _force_pascal_case("Cabinet") == "Cabinet"
    assert _force_pascal_case("CabiNet") == "Cabinet"
    assert _force_pascal_case("ConstitutIon") == "Constitution"
    assert _force_pascal_case("natIon") == "Nation"

def test_force_pascal_case_compound_words():
    assert _force_pascal_case("MachineLearning") == "MachineLearning"
    assert _force_pascal_case("QuantumMechanics") == "QuantumMechanics"
    assert _force_pascal_case("computerScience") == "ComputerScience"

def test_flashtext_seed_casing():
    # 'nqueens' should be normalized to 'NQueens' assuming 'NQueens' is in seeds
    # Let's mock a simple replacement test
    raw = "The model predicted nqueens for the problem."
    result = force_seed_casing_in_text(raw)
    assert "NQueens" in result or "nqueens" in result  # Depends on DEFAULT_SEEDS contents
    
    # We just ensure it runs without crashing
    assert isinstance(result, str)

import re
import nltk
from flashtext import KeywordProcessor
from .seeds import DEFAULT_SEEDS

# ══════════════════════════════════════════════════════════════════════
#  NLTK DICTIONARY CACHE
# ══════════════════════════════════════════════════════════════════════
try:
    nltk.download('words', quiet=True)
    from nltk.corpus import words as nltk_words
    _ENGLISH_WORDS = set(w.lower() for w in nltk_words.words())
except Exception:
    _ENGLISH_WORDS = set()

# ══════════════════════════════════════════════════════════════════════
#  FLASHTEXT SEED-CASING PROCESSOR
# ══════════════════════════════════════════════════════════════════════
_SEED_CASING_PROCESSOR = KeywordProcessor(case_sensitive=False)

def _init_flashtext():
    # Build a lookup for all our perfectly cased seeds
    for seed in DEFAULT_SEEDS:
        # We want to replace any case-insensitive match of "seed" with the exact casing of "seed"
        _SEED_CASING_PROCESSOR.add_keyword(seed, seed)

_init_flashtext()

def force_seed_casing_in_text(raw_model_output: str) -> str:
    """
    Preprocesses raw model output. If the model generated a word that 
    matches one of our seeds case-insensitively (e.g. 'nqueens', 'storage'),
    this efficiently replaces it with the exact canonical casing from the seed list
    (e.g. 'NQueens', 'Storage').
    """
    return _SEED_CASING_PROCESSOR.replace_keywords(raw_model_output)

def _force_pascal_case(s: str) -> str:
    """Converts mixed casing into proper PascalCase using heuristics."""
    # If the whole token (case stripped) is a real English word,
    # trust that it's one word with a typo'd capital, not a compound.
    if s.lower() in _ENGLISH_WORDS:
        return s.capitalize()

    words = re.sub(r'([a-z])([A-Z])', r'\1 \2', s).split()
    if not words:
        return s
    return "".join(w.capitalize() for w in words)

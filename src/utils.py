import re
from datetime import datetime

def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def camel_split(s: str) -> str:
    """Splits CamelCase or PascalCase into lowercase words."""
    return re.sub(r'(?<!^)(?=[A-Z])', ' ', s).lower()

def is_meaningful_line(line: str) -> bool:
    """Checks if a retrieved text is meaningful and not just a single word."""
    words = line.split()
    return len(words) >= 3

def clean_output(text: str) -> str:
    """Clean up artifacts from raw generation."""
    # Remove thoughts or tags if any accidentally leaked
    text = re.sub(r'<[^>]*>', '', text)
    # Basic whitespace cleanup
    text = ' '.join(text.split())
    # Sometimes models output Question/Answer prefixes
    text = text.replace('Answer: ', '').replace('Response: ', '')
    return text.strip()

def _casing_quality_score(s: str) -> int:
    """Used for normalising knowledge base casing."""
    score = 0
    for w in s.split():
        if not w:
            continue
        if w[0].isupper() and w[1:].islower():
            score += 2
        elif w.islower():
            score += 1
        interior_caps = sum(1 for c in w[1:] if c.isupper())
        score -= interior_caps * 3
    return score

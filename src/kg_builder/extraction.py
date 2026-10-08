import re

_TRIPLET_RE = re.compile(
    r"\[domain=([A-Za-z0-9_ -]+)\]\s*\(\s*([A-Za-z][A-Za-z0-9]{1,19})\s*,\s*([A-Za-z][A-Za-z]{1,34})\s*,\s*([A-Za-z][A-Za-z0-9]{1,19})\s*\)"
)

from .validators import CANONICAL_RELATIONS, is_valid_node, is_valid_relation

# Relations where subject should be a person/org and object should be a creation/concept
_CREATOR_RELATIONS = frozenset({
    "developed", "invented", "discovered", "founded", "created", "designed", "wrote", "painted",
    "composed", "directed", "built",
})

# Known algorithm/tool/concept suffixes that should NOT be in the subject position of creator relations
_NON_CREATOR_SUFFIXES = frozenset({
    "sort", "search", "tree", "algorithm", "protocol", "cache", "hash", "model",
    "network", "graph", "list", "queue", "stack", "heap", "table", "filter",
    "pattern", "structure", "function", "method", "process", "system", "framework",
    "language", "database", "server", "api", "library",
})

def _is_likely_non_creator(node: str) -> bool:
    """Check if a node looks like an algorithm/tool/concept (not a person/org)."""
    lower = node.lower()
    for suffix in _NON_CREATOR_SUFFIXES:
        if lower.endswith(suffix):
            return True
    return False

def extract_triplets(text: str) -> list:
    """Extracts raw (domain, subject, relation, object) tuples from generated text.
    
    Includes post-generation quality filters:
    - Rejects self-referential triples (X, rel, X)
    - Rejects reversed creator relations (Algorithm, developed, Person)
    - Rejects nodes with fewer than 2 characters
    """
    results = []
    for m in _TRIPLET_RE.finditer(text):
        d = m.group(1).strip()
        s = m.group(2).strip()
        r = m.group(3).strip()
        e = m.group(4).strip()
        
        if is_valid_node(s) and is_valid_node(e) and is_valid_relation(r):
            r_can = CANONICAL_RELATIONS.get(r.lower(), r.lower())
            
            # Quality Filter 1: Reject self-referential triples
            if s.lower() == e.lower():
                continue
            
            # Quality Filter 2: Reject reversed creator relations
            # e.g., (TimSort, developed, Python) where TimSort is clearly not a creator
            if r_can in _CREATOR_RELATIONS and _is_likely_non_creator(s):
                continue
            
            # Quality Filter 3: Reject ultra-short nodes (1 char)
            if len(s) < 2 or len(e) < 2:
                continue
            
            results.append((d, s, r_can, e))
    return results

def build_prompt(topic: str, tokenizer, use_chat_template: bool = False) -> str:
    examples = f"""\
Topic: DNA
[domain=Biology] (DNA, isA, Molecule)
[domain=Biology] (DNA, contains, Nucleotide)
[domain=Biology] (DNA, encodes, Protein)
[domain=Biology] (DNA, isPartOf, Chromosome)
[domain=Biology] (JamesWatson, discovered, DNAStructure)
[domain=Biology] (Chromosome, isPartOf, Nucleus)

Topic: BinarySearchTree
[domain=Computer Science] (BinarySearchTree, isA, DataStructure)
[domain=Computer Science] (BinarySearchTree, supports, Search)
[domain=Computer Science] (BinarySearchTree, has, Root)
[domain=Computer Science] (BinarySearchTree, contains, Nodes)
[domain=Computer Science] (InorderTraversal, isPartOf, BinarySearchTree)

Topic: Photosynthesis
[domain=Biology] (Photosynthesis, isA, BiologicalProcess)
[domain=Biology] (Photosynthesis, requires, Sunlight)
[domain=Biology] (Photosynthesis, produces, Oxygen)
[domain=Biology] (Photosynthesis, requires, CarbonDioxide)
[domain=Biology] (Chloroplast, performs, Photosynthesis)

Topic: {topic}
"""
    if use_chat_template and hasattr(tokenizer, 'apply_chat_template'):
        try:
            system = (
                "You are an enterprise-grade Knowledge Graph extraction engine producing "
                "encyclopedic-quality triples. Every triple you generate must be a universally "
                "accepted fact verifiable in textbooks or Wikipedia.\n\n"
                "STRICT RULES:\n"
                "1. Format: [domain=DomainName] (Subject, relation, Object)\n"
                "2. Entities MUST be atomic PascalCase with no spaces (e.g., 'MachineLearning', NOT 'machine learning').\n"
                "3. Relations MUST be standard verbs: isA, isPartOf, has, contains, solves, developed, "
                "invented, discovered, causes, produces, requires, includes, supports, connects, "
                "controls, influences, studies, involves, represents, enables, performs, measures, etc.\n"
                "4. DIRECTION MATTERS: (Creator, developed, Creation) is CORRECT. "
                "(Creation, developed, Creator) is WRONG. The subject performs the action on the object.\n"
                "5. NO hallucination: If you are not 100% certain a fact is true, omit it entirely.\n"
                "6. NO self-referential triples: (X, isA, X) is FORBIDDEN.\n"
                "7. NO placeholder or generic entities. Use specific, real names.\n"
                "8. Generate 8-15 high-quality triples per topic.\n"
                "9. Output ONLY the triples. No markdown, no explanations, no conversational text."
            )
            messages = [
                {"role": "system", "content": system},
                {"role": "user",   "content": examples.strip()},
            ]
            return tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        except Exception:
            pass
    return examples


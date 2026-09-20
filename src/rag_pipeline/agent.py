"""
Agentic RAG Pipeline — Dual-Model Knowledge Graph Expansion

Dual-model architecture:
  - 70B (Groq API): Topic extraction + fact generation (heavy knowledge work)
  - 3B (Local Qwen): Answer synthesis from retrieved facts (lightweight, no API needed)

Usage:
    python -m src.rag_pipeline
"""

import os
import re
import gc
import sys
import time
import json
import hashlib
import logging
import subprocess
import argparse
import threading
import ctypes
from datetime import datetime, timezone
import torch
from dotenv import load_dotenv
import requests
from groq import Groq
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TextIteratorStreamer

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════════════════════════════

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KG_MODEL = "openai/gpt-oss-120b"       # Heavy model: topic extraction + fact generation
LOCAL_ANSWER_MODEL = os.path.join(BASE_DIR, "local_qwen_3b")  # Local 3B model for answer synthesis
MIN_FACTS_THRESHOLD = 1   # If 0 facts found locally, trigger on-demand generation
MAX_RETRIES = 3
CPU_INT8_MIN_AVAILABLE_GB = 10

# File paths
CRAWLER_KB_FILE = os.path.join(BASE_DIR, "data", "kg", "knowledge_base.txt")   # Pre-built by background crawler
RAG_KB_FILE = os.path.join(BASE_DIR, "data", "rag", "rag_knowledge.txt")       # On-demand facts go here
PROVENANCE_FILE = os.path.join(BASE_DIR, "data", "rag", "fact_provenance.jsonl")
FEEDBACK_FILE = os.path.join(BASE_DIR, "data", "rag", "answer_feedback.jsonl")
REVIEW_QUEUE_FILE = os.path.join(BASE_DIR, "data", "rag", "fact_review_queue.jsonl")


# ══════════════════════════════════════════════════════════════════════
#  TRIPLET EXTRACTION (self-contained, no kg_builder dependency)
# ══════════════════════════════════════════════════════════════════════

_TRIPLET_LINE_RE = re.compile(
    r"\[domain=([A-Za-z0-9_ -]+)\]\s*\(\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*([^)]+?)\s*\)"
)

_EXTRACT_RE = re.compile(
    r"\[domain=([A-Za-z0-9_ -]+)\]\s*\(\s*([A-Za-z][A-Za-z0-9]{1,19})\s*,\s*([A-Za-z][A-Za-z]{1,34})\s*,\s*([A-Za-z][A-Za-z0-9]{1,19})\s*\)"
)

# Canonical relation mapping
CANONICAL_RELATIONS = {
    "isa": "isA", "is_a": "isA", "typeof": "isA", "type": "isA",
    "ispartof": "isPartOf", "is_part_of": "isPartOf", "partof": "isPartOf",
    "has": "has", "hasa": "has", "contains": "contains",
    "developed": "developed", "invented": "invented", "discovered": "discovered",
    "founded": "founded", "created": "created", "designed": "designed",
    "wrote": "wrote", "composed": "composed",
    "causes": "causes", "produces": "produces", "requires": "requires",
    "includes": "includes", "supports": "supports", "connects": "connects",
    "controls": "controls", "influences": "influences", "studies": "studies",
    "involves": "involves", "represents": "represents", "enables": "enables",
    "performs": "performs", "measures": "measures", "solves": "solves",
    "affects": "affects", "governs": "governs", "originated": "originated",
    "precedes": "precedes", "follows": "follows", "generates": "generates",
    "analyzes": "analyzes", "regulates": "regulates", "enforces": "enforces",
    "interprets": "interprets", "maintains": "maintains", "stores": "stores",
    "encodes": "encodes", "emits": "emits", "orbits": "orbits",
    "surrounds": "surrounds", "reduces": "reduces", "modifies": "modifies",
    "forms": "forms", "creates": "creates", "determines": "determines",
    "develops": "develops", "trains": "trains", "teaches": "teaches",
    "plays": "plays", "painted": "painted", "directed": "directed",
    "built": "built",
}


def extract_triplets_from_text(text: str) -> list[tuple]:
    """Extract (domain, subject, relation, object) tuples from raw LLM output."""
    results = []
    for m in _EXTRACT_RE.finditer(text):
        d = m.group(1).strip()
        s = m.group(2).strip()
        r = m.group(3).strip()
        o = m.group(4).strip()

        # Normalize relation
        r_can = CANONICAL_RELATIONS.get(r.lower(), r.lower())

        # Skip self-referential
        if s.lower() == o.lower():
            continue
        # Skip ultra-short nodes
        if len(s) < 2 or len(o) < 2:
            continue

        results.append((d, s, r_can, o))
    return results


# ══════════════════════════════════════════════════════════════════════
#  KNOWLEDGE GRAPH LOADING
# ══════════════════════════════════════════════════════════════════════

def load_knowledge_graph(filepath: str) -> list[dict]:
    """Load all triplets from a knowledge base file into a list of dicts."""
    triplets = []
    if not os.path.exists(filepath):
        return triplets

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            m = _TRIPLET_LINE_RE.match(line)
            if m:
                triplets.append({
                    "domain": m.group(1).strip(),
                    "subject": m.group(2).strip(),
                    "relation": m.group(3).strip(),
                    "object": m.group(4).strip(),
                    "raw": line,
                })
    return triplets


# ══════════════════════════════════════════════════════════════════════
#  TOOL 1: SEARCH LOCAL KNOWLEDGE GRAPH
# ══════════════════════════════════════════════════════════════════════

def search_local_kg(topics: list[str], triplets: list[dict]) -> list[dict]:
    """Search the local knowledge graph for triplets matching any of the topics.

    Performs case-insensitive substring matching on subject AND object fields.
    Returns deduplicated results.
    """
    results = []
    seen_raw = set()

    for t in triplets:
        subj_lower = t["subject"].lower()
        obj_lower = t["object"].lower()

        for topic in topics:
            topic_lower = topic.lower().replace(" ", "")
            topic_singular = topic_lower.rstrip('s') # Handle basic plural mismatches

            # Avoid matching generic topics against file paths
            obj_matches = False
            if t["relation"].lower() != "hascontextfile":
                obj_matches = (topic_lower in obj_lower) or (topic_singular in obj_lower)

            if (topic_lower in subj_lower) or (topic_singular in subj_lower) or obj_matches:
                if t["raw"] not in seen_raw:
                    results.append(t)
                    seen_raw.add(t["raw"])
                break

    return results


def _search_tokens(text: str) -> set[str]:
    """Normalize prose and PascalCase entities for lexical KG ranking."""
    spaced = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
    return {
        token.lower().rstrip("s")
        for token in re.findall(r"[A-Za-z0-9]+", spaced)
        if len(token) > 2 and token.lower() not in {"what", "with", "from", "that", "this", "give", "information", "about", "does"}
    }


def retrieve_ranked_facts(question: str, topics: list[str], triplets: list[dict], top_k: int = 20) -> tuple[list[dict], float]:
    """Rank KG facts by query/entity overlap and return a routing confidence score."""
    query_tokens = _search_tokens(question)
    topic_tokens = _search_tokens(" ".join(topics))
    ranked = []
    for fact in triplets:
        subject_tokens = _search_tokens(fact["subject"])
        object_tokens = _search_tokens(fact["object"])
        relation_tokens = _search_tokens(fact["relation"])
        fact_tokens = subject_tokens | object_tokens | relation_tokens | _search_tokens(fact["domain"])
        overlap = query_tokens & fact_tokens
        topic_overlap = topic_tokens & (subject_tokens | object_tokens)
        if not overlap and not topic_overlap:
            continue
        score = len(overlap) * 1.0 + len(topic_overlap) * 1.5
        if subject_tokens & query_tokens:
            score += 1.0
        if fact["relation"].lower() in {"isa", "ispartof", "has", "contains"}:
            score += 0.15
        ranked_fact = dict(fact)
        ranked_fact["retrieval_score"] = round(score, 3)
        ranked.append(ranked_fact)

    ranked.sort(key=lambda fact: fact["retrieval_score"], reverse=True)
    selected = ranked[:top_k]
    if not selected or not topic_tokens:
        return selected, 0.0
    covered_topics = set().union(*[
        topic_tokens & (_search_tokens(fact["subject"]) | _search_tokens(fact["object"]))
        for fact in selected
    ])
    coverage = len(covered_topics) / len(topic_tokens)
    strength = min(selected[0]["retrieval_score"] / 4.0, 1.0)
    evidence_depth = min(len(selected) / 4.0, 1.0)
    confidence = round(0.5 * coverage + 0.35 * strength + 0.15 * evidence_depth, 3)
    return selected, confidence


def print_evidence(facts: list[dict], provenance_index: dict[str, dict]) -> None:
    """Show the exact KG facts and web sources used for the final answer."""
    if not facts:
        return
    print("\nEvidence used:")
    for index, fact in enumerate(facts, start=1):
        fact_id = _fact_id(fact["domain"], fact["subject"], fact["relation"], fact["object"])
        source_urls = [
            source["url"] for source in provenance_index.get(fact_id, {}).get("provenance", {}).get("sources", [])
            if source.get("url")
        ]
        source_text = f" | Sources: {', '.join(source_urls)}" if source_urls else " | Source: local knowledge graph"
        print(f"  [F{index}] {fact['subject']} {fact['relation']} {fact['object']}{source_text}")


# ══════════════════════════════════════════════════════════════════════
#  TOOL 1.5: TAVILY WEB SEARCH
# ══════════════════════════════════════════════════════════════════════

def search_tavily(query: str) -> tuple[str, list[dict]]:
    """Fetch web evidence and retain its URLs for fact-level provenance.

    The text context is for the LLM; the structured source list is persisted with
    every fact accepted from this web-grounded generation pass.
    """
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "", []

    url = "https://api.tavily.com/search"
    headers = {"Content-Type": "application/json"}
    data = {
        "api_key": api_key,
        "query": query,
        "search_depth": "advanced",
        "include_answer": False,
        "max_results": 5
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        raw_results = response.json().get("results", [])
        sources = []
        for index, result in enumerate(raw_results, start=1):
            source_url = (result.get("url") or "").strip()
            content = (result.get("content") or "").strip()
            if not source_url or not content:
                continue
            sources.append({
                "id": index,
                "title": (result.get("title") or source_url).strip(),
                "url": source_url,
                "content": content,
                "score": result.get("score"),
            })
        context = "\n\n".join(
            f"[source={source['id']}] {source['title']}\nURL: {source['url']}\n{source['content']}"
            for source in sources
        )
        return context, sources
    except Exception as e:
        logger.error(f"Tavily search failed: {e}")
        return "", []


# ══════════════════════════════════════════════════════════════════════
#  TOOL 2: ON-DEMAND TRIPLET GENERATION
# ══════════════════════════════════════════════════════════════════════

def generate_new_triplets(topic: str, client, model_name: str, user_question: str = "", search_context: str = "") -> list[tuple]:
    """Generate new triplets for a topic using the 70B model via Groq API.
    Includes the user's original question as context for relevance."""
    context_hint = ""
    if search_context:
        context_hint = f"\n\nCRITICAL CONTEXT: You must extract facts ONLY from the following LIVE WEB SEARCH RESULTS. Do not use your internal knowledge.\n---\n{search_context}\n---\nRelevant to user question: '{user_question}'"
    elif user_question:
        context_hint = f"\n\nCRITICAL CONTEXT: The user asked: \"{user_question}\". Generate facts highly relevant to this question."

    system_prompt = (
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
        "8. Generate 10-20 high-quality triples per topic.\n"
        "9. Output ONLY the triples. No markdown, no explanations, no conversational text.\n"
        "10. RELATIONAL COMPLETENESS: Ensure that generated entities are explicitly linked back to the main Topic via relational triplets (e.g., if Topic is 'Amrita', you MUST generate (Amrita, hasCampus, CoimbatoreCampus))."
        f"{context_hint}"
    )

    user_prompt = f"""\
Topic: DNA
[domain=Biology] (DNA, isA, Molecule)
[domain=Biology] (DNA, contains, Nucleotide)
[domain=Biology] (DNA, encodes, Protein)
[domain=Biology] (DNA, isPartOf, Chromosome)
[domain=Biology] (JamesWatson, discovered, DNAStructure)
[domain=Biology] (Chromosome, isPartOf, Nucleus)

Topic: BinarySearchTree
[domain=ComputerScience] (BinarySearchTree, isA, DataStructure)
[domain=ComputerScience] (BinarySearchTree, supports, Search)
[domain=ComputerScience] (BinarySearchTree, has, Root)
[domain=ComputerScience] (BinarySearchTree, contains, Nodes)
[domain=ComputerScience] (InorderTraversal, isPartOf, BinarySearchTree)

Topic: Photosynthesis
[domain=Biology] (Photosynthesis, isA, BiologicalProcess)
[domain=Biology] (Photosynthesis, requires, Sunlight)
[domain=Biology] (Photosynthesis, produces, Oxygen)
[domain=Biology] (Photosynthesis, requires, CarbonDioxide)
[domain=Biology] (Chloroplast, performs, Photosynthesis)
Topic: {topic}
"""

    raw_output = ""
    for attempt in range(MAX_RETRIES):
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=1,
                max_completion_tokens=500,
                top_p=1,
                reasoning_effort="low",
                stream=False,
            )
            raw_output = (completion.choices[0].message.content or "") or getattr(completion.choices[0].message, "reasoning_content", "") or ""
            break
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate limit" in error_msg.lower():
                match = re.search(r"try again in (?:(\d+)m)?([\d\.]+)s", error_msg)
                if match:
                    mins = int(match.group(1)) if match.group(1) else 0
                    secs = float(match.group(2))
                    wait_time = (mins * 60) + secs + 2.0
                else:
                    wait_time = 60.0
                logger.warning(f"Rate limit hit! Sleeping {wait_time:.1f}s... (Attempt {attempt+1}/{MAX_RETRIES})")
                time.sleep(wait_time)
            else:
                logger.error(f"Groq API Error: {e}")
                break

    triplets = extract_triplets_from_text(raw_output)

    return triplets


# ══════════════════════════════════════════════════════════════════════
#  TOOL 3: INTELLIGENT CODE VAULT (70B EVALUATES + GENERATES)
# ══════════════════════════════════════════════════════════════════════

# Map of language identifiers to file extensions
_LANG_EXT_MAP = {
    "python": ".py", "py": ".py",
    "javascript": ".js", "js": ".js",
    "typescript": ".ts", "ts": ".ts",
    "java": ".java",
    "c": ".c", "cpp": ".cpp", "c++": ".cpp",
    "csharp": ".cs", "c#": ".cs",
    "go": ".go", "golang": ".go",
    "rust": ".rs",
    "ruby": ".rb",
    "sql": ".sql",
    "html": ".html",
    "css": ".css",
    "shell": ".sh", "bash": ".sh",
    "r": ".r",
    "kotlin": ".kt",
    "swift": ".swift",
    "scala": ".scala",
    "lua": ".lua",
    "matlab": ".m",
    "markdown": ".md", "md": ".md",
    "text": ".txt", "txt": ".txt",
    "arduino": ".ino", "ino": ".ino",
    "openscad": ".scad", "scad": ".scad",
    "verilog": ".v", "vhdl": ".vhdl",
    "autocad": ".lsp", "autolisp": ".lsp", "lsp": ".lsp",
    "svg": ".svg",
    "json": ".json",
    "yaml": ".yml", "yml": ".yml",
    "xml": ".xml",
    "toml": ".toml",
    "csv": ".csv",
    "ini": ".ini",
    "webassembly": ".wat", "wat": ".wat",
    "assembly": ".asm", "asm": ".asm",
    "supercollider": ".scd",
    "gdscript": ".gd", "godot": ".gd",
    "latex": ".tex", "tex": ".tex",
    "terraform": ".tf", "tf": ".tf",
}


def evaluate_code_need(question: str, topics: list[str], client, model_name: str) -> tuple[bool, str, str]:
    """Ask the 70B model whether the question requires an implementation/code.
    Returns (needs_code: bool, language: str, flavor: str).
    Flavor helps differentiate implementations (e.g. PyTorch vs Raw Python)."""

    system_prompt = (
        "You are a classifier. Given a user question, decide if it requires writing "
        "code or an implementation file (script, program, query, config, etc.).\n\n"
        "Respond with EXACTLY one line in this format:\n"
        "  YES | <language> | <flavor> | <ConceptName>\n"
        "  or\n"
        "  NO\n\n"
        "Examples:\n"
        "  Question: 'Give me code for a neural network in PyTorch' → YES | python | PyTorch | NeuralNetwork\n"
        "  Question: 'Give me a raw python neural network' → YES | python | Raw | NeuralNetwork\n"
        "  Question: 'Write a SQL query to find duplicate rows' → YES | sql | None | DuplicateRowsQuery\n"
        "  Question: 'What is photosynthesis?' → NO\n"
        "  Question: 'Implement quicksort in C++' → YES | cpp | None | QuickSort\n"
        "  Question: 'Create a REST API in Express' → YES | javascript | Express | RestApi\n"
        "  Question: 'Write a playable Snake game using HTML5 Canvas and JS' → YES | html | Canvas | SnakeGame\n"
        "  Question: 'Write a README file for the backend' → YES | markdown | None | BackendReadme\n"
        "  Question: 'Write code to blink an LED on an Arduino' → YES | arduino | None | BlinkLed\n"
        "  Question: 'Create a 3D model of a cube in OpenSCAD' → YES | openscad | None | CubeModel\n"
        "  Question: 'Write an AutoLISP script to draw a staircase in AutoCAD' → YES | autocad | AutoLISP | Staircase\n"
        "  Question: 'Design a scalable vector logo of a rocket' → YES | svg | None | RocketLogo\n\n"
        "The <flavor> is strictly OPTIONAL. If the user does not specify a specific framework or variation, output 'None'.\n"
        "The <ConceptName> MUST be a single PascalCase word describing the algorithm or structure (e.g., 'TransformerModel').\n"
        "Respond with ONLY the piped string. Nothing else."
    )

    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
            temperature=1,
            max_completion_tokens=100,
            top_p=1,
            reasoning_effort="low",
            stream=False,
        )
        _msg = completion.choices[0].message
        response = (((_msg.content or "") or getattr(_msg, "reasoning_content", "") or "")).strip().lower()
    except Exception as e:
        print(f"   ⚠️ Code evaluation failed: {e}")
        return False, "", "", ""

    if response.startswith("yes"):
        _raw = ((_msg.content or "") or getattr(_msg, "reasoning_content", "") or "")
        parts = [p.strip() for p in _raw.split("|")]

        lang = parts[1].lower() if len(parts) > 1 else "python"
        flavor = parts[2] if len(parts) > 2 else ""
        concept = parts[3] if len(parts) > 3 else "GeneratedCode"

        # Filter out hallucinated fillers if the model gets confused
        if flavor.lower() in ("yes", "no", "none", "and", "or", "in", "with", "using"):
            flavor = ""

        # Clean concept to ensure PascalCase and no weird chars
        concept = re.sub(r"[^A-Za-z0-9]", "", concept)
        if not concept:
            concept = "GeneratedCode"

        return True, lang, flavor, concept
    return False, "", "", ""


def generate_code_for_vault(topic: str, user_question: str, language: str, flavor: str,
                            client, model_name: str,
                            existing_keys: set, all_triplets: list[dict]) -> int:
    """Make a DEDICATED 70B call to generate implementation code for a topic.
    Supports any programming language and specific flavors (e.g. PyTorch). Saves the result to codevault/.
    Returns the number of new vault files created (0 or 1)."""

    ext = _LANG_EXT_MAP.get(language.lower(), ".txt")
    lang_display = language.capitalize()
    flavor_display = f" using {flavor.capitalize()}" if flavor else ""

    if ext in [".md", ".txt"]:
        system_prompt = (
            f"You are a technical writer. The user wants a {lang_display} document{flavor_display}.\n"
            f"Output ONLY the complete {lang_display} content. Do not wrap it in triple-backtick fences.\n"
            f"The content should be well-structured, clear, and comprehensive."
        )
    else:
        system_prompt = (
            f"You are a senior {lang_display} engineer. The user wants working {lang_display} code{flavor_display}.\n"
            f"Output ONLY a single, complete {lang_display} file. No explanations, no markdown headings, "
            f"no triple-backtick fences — just raw source code.\n"
            f"The code must be production-ready, well-commented, and directly runnable."
        )

    if ext in [".md", ".txt"]:
        user_prompt = (
            f"Write a complete {lang_display} document for: {user_question}\n"
            f"Focus on the topic '{topic}'{flavor_display}.\n"
            f"Output ONLY the document text."
        )
    else:
        user_prompt = (
            f"Write a complete {lang_display} implementation for: {user_question}\n"
            f"Focus on the topic '{topic}'{flavor_display}.\n"
            f"Output ONLY raw {lang_display} source code. No markdown. No explanations."
        )

    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=1,
            max_completion_tokens=6000,
            top_p=1,
            reasoning_effort="medium",
            stream=False,
        )
        _code_msg = completion.choices[0].message
        raw_code = ((_code_msg.content or "") or getattr(_code_msg, "reasoning_content", "") or "").strip()
    except Exception as e:
        print(f"   ⚠️ Code generation failed: {e}")
        return 0

    if not raw_code:
        return 0

    # Strip markdown fences if the model wrapped them anyway
    fence_match = re.search(r"```(?:\w+)?\s*(.*?)\s*```", raw_code, re.DOTALL)
    if fence_match:
        raw_code = fence_match.group(1).strip()

    # Save to codevault
    safe_topic = re.sub(r"[^A-Za-z0-9]", "", topic) or "GeneratedCode"
    if flavor:
        safe_flavor = re.sub(r"[^A-Za-z0-9]", "", flavor.capitalize())
        filename = f"{safe_topic}_{safe_flavor}{ext}"
        topic_display = f"{topic} ({flavor.capitalize()})"
    else:
        filename = f"{safe_topic}{ext}"
        topic_display = topic

    vault_dir = os.path.join(BASE_DIR, "codevault", language.lower())
    os.makedirs(vault_dir, exist_ok=True)
    filepath = os.path.join(vault_dir, filename)

    # Language-appropriate comment header
    if ext in (".py", ".r", ".sh", ".rb", ".lua", ".yaml", ".yml", ".toml", ".ini", ".tf", ".gd"):
        header = f"# Auto-generated Code Vault for '{topic_display}' [{lang_display}]\n\n"
    elif ext in (".tex",):
        header = f"% Auto-generated Code Vault for '{topic_display}' [{lang_display}]\n\n"
    elif ext in (".asm", ".wat"):
        header = f"; Auto-generated Code Vault for '{topic_display}' [{lang_display}]\n\n"
    elif ext in (".html", ".md", ".txt"):
        header = f"<!-- Auto-generated Code Vault for '{topic_display}' [{lang_display}] -->\n\n"
    elif ext in (".svg", ".xml"):
        header = ""  # XML strict parsing crashes if a comment precedes <?xml ?>
    elif ext in (".lsp", ".gcode", ".scad"):
        header = f"// Auto-generated Code Vault for '{topic_display}' [{lang_display}]\n\n"
    elif ext == ".sql":
        header = f"-- Auto-generated Code Vault for '{topic_display}' [{lang_display}]\n\n"
    else:
        header = f"// Auto-generated Code Vault for '{topic_display}' [{lang_display}]\n\n"

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(header + raw_code + "\n")
        print(f"   💾 Code Vault saved: {filepath} [{lang_display}]")
    except Exception as e:
        print(f"   ⚠️ Failed to save Code Vault file: {e}")
        return 0

    # Inject hasContextFile triplet into RAG KB and in-memory graph
    # Store with the specific filename so it's tied to this flavor
    triplet_line = f"[domain=CodeVault] ({safe_topic}, hasContextFile, {filepath})"
    key = f"{safe_topic.lower()}|hascontextfile|{filepath.lower()}"
    if key not in existing_keys:
        existing_keys.add(key)
        with open(RAG_KB_FILE, "a", encoding="utf-8") as f:
            f.write(triplet_line + "\n")
        all_triplets.append({
            "domain": "CodeVault",
            "subject": safe_topic,
            "relation": "hasContextFile",
            "object": filepath,
            "raw": triplet_line,
        })

    return 1


# ══════════════════════════════════════════════════════════════════════
#  TOOL 5: CODE EXECUTION (INTERPRETER PATTERN)
# ══════════════════════════════════════════════════════════════════════

def execute_code_safely(filepath: str, timeout: int = 10) -> tuple[bool, str]:
    """Execute a Python file in a sandboxed subprocess with a hard timeout.
    Returns (success: bool, output: str).
    Only Python files are supported."""

    if not filepath.endswith(".py"):
        return False, "Only Python (.py) files can be executed."

    if not os.path.exists(filepath):
        return False, f"File not found: {filepath}"

    try:
        result = subprocess.run(
            [sys.executable, filepath],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.dirname(filepath),
        )

        output = ""
        if result.stdout:
            output += result.stdout.strip()
        if result.stderr:
            # Append stderr but label it
            stderr_clean = result.stderr.strip()
            if stderr_clean:
                output += f"\n[STDERR]: {stderr_clean}" if output else f"[STDERR]: {stderr_clean}"

        if result.returncode == 0:
            return True, output if output else "(Program completed successfully with no output)"
        else:
            return False, output if output else f"(Program exited with code {result.returncode})"

    except subprocess.TimeoutExpired:
        return False, f"⏱️ Execution timed out after {timeout} seconds (possible infinite loop)."
    except Exception as e:
        return False, f"Execution error: {e}"


def should_execute_code(question: str, concept: str, client, model_name: str) -> bool:
    """Ask the 70B model whether the user wants to SEE the output of running
    the code, or just the source code itself."""

    system_prompt = (
        "You are a classifier. Given a user question and the code concept that was generated, "
        "decide if the user wants to SEE THE OUTPUT of running the code, or just the source code itself.\n\n"
        "Respond with EXACTLY one word: YES or NO.\n\n"
        "YES means: the user wants a computed result, a printed answer, or program output.\n"
        "NO means: the user wants the code architecture, implementation pattern, or just the source.\n\n"
        "Examples:\n"
        "  Question: 'Calculate the 100th prime number in Python' → YES\n"
        "  Question: 'Write a Python script to sort [5,3,8,1] and print it' → YES\n"
        "  Question: 'Implement a neural network using PyTorch' → NO\n"
        "  Question: 'Give me a REST API implementation in Python' → NO\n"
        "  Question: 'What is 2^32? Write Python to compute it' → YES\n"
        "  Question: 'Implement the A* pathfinding algorithm' → NO\n\n"
        "Respond with ONLY 'YES' or 'NO'. Nothing else."
    )

    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Question: {question}\nCode concept: {concept}"},
            ],
            temperature=1,
            max_completion_tokens=20,
            top_p=1,
            reasoning_effort="low",
            stream=False,
        )
        _exec_msg = completion.choices[0].message
        response = ((_exec_msg.content or "") or getattr(_exec_msg, "reasoning_content", "") or "").strip().lower()
        return response.startswith("yes")
    except Exception as e:
        print(f"   ⚠️ Execution classification failed: {e}")
        return False


def _fact_id(domain: str, subject: str, relation: str, obj: str) -> str:
    """Return a stable identifier for a canonical triple."""
    canonical = f"{domain.lower()}|{subject.lower()}|{relation.lower()}|{obj.lower()}"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _select_relevant_sources(subject: str, obj: str, sources: list[dict]) -> list[dict]:
    """Keep sources mentioning a triple entity; fall back to all supplied evidence."""
    entity_terms = {
        token.lower() for token in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)|\d+", f"{subject} {obj}")
        if len(token) > 2
    }
    relevant = [
        source for source in sources
        if entity_terms.intersection((source["title"] + " " + source["content"]).lower().split())
    ]
    return relevant or sources


def append_provenance_records(
    triplets: list[tuple],
    sources: list[dict],
    query: str,
    model_name: str,
    filepath: str = PROVENANCE_FILE,
) -> None:
    """Append immutable JSONL provenance for accepted facts.

    Facts are kept in the legacy text KB for retrieval compatibility; this sidecar
    stores the evidence needed to audit or cite every generated fact.
    """
    if not triplets:
        return
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    with open(filepath, "a", encoding="utf-8") as f:
        for domain, subject, relation, obj in triplets:
            matched_sources = _select_relevant_sources(subject, obj, sources)
            record = {
                "schema_version": 1,
                "fact_id": _fact_id(domain, subject, relation, obj),
                "triple": {
                    "domain": domain,
                    "subject": subject,
                    "relation": relation,
                    "object": obj,
                },
                "provenance": {
                    "query": query,
                    "retrieved_at": retrieved_at,
                    "provider": "tavily" if sources else None,
                    "sources": [
                        {
                            "title": source["title"],
                            "url": source["url"],
                            "excerpt": source["content"][:1200],
                            "search_score": source.get("score"),
                        }
                        for source in matched_sources
                    ],
                },
                "extraction": {
                    "method": "web_grounded_llm" if sources else "llm_generated",
                    "model": model_name,
                    "verification_status": "web_grounded_unverified" if sources else "unverified",
                },
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_provenance_index(filepath: str = PROVENANCE_FILE) -> dict[str, dict]:
    """Load the newest provenance record for each fact without changing the KG."""
    records = {}
    if not os.path.exists(filepath):
        return records
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)
                if record.get("fact_id"):
                    records[record["fact_id"]] = record
            except json.JSONDecodeError:
                logger.warning("Skipping malformed provenance record")
    return records


def append_feedback_record(
    question: str,
    verdict: str,
    note: str,
    facts: list[dict],
    provenance_index: dict[str, dict],
    feedback_path: str = FEEDBACK_FILE,
    review_queue_path: str = REVIEW_QUEUE_FILE,
) -> dict:
    """Persist answer feedback and queue disputed facts for human review.

    Feedback never edits or deletes KG facts. Negative feedback creates a separate
    review task so a curator can inspect the linked web evidence before changing
    a fact's verification status.
    """
    fact_ids = []
    source_urls = []
    for fact in facts:
        fact_id = _fact_id(fact["domain"], fact["subject"], fact["relation"], fact["object"])
        fact_ids.append(fact_id)
        for source in provenance_index.get(fact_id, {}).get("provenance", {}).get("sources", []):
            if source.get("url"):
                source_urls.append(source["url"])
    source_urls = list(dict.fromkeys(source_urls))
    submitted_at = datetime.now(timezone.utc).isoformat()
    feedback_id = hashlib.sha256(f"{submitted_at}|{question}|{verdict}|{note}".encode("utf-8")).hexdigest()
    record = {
        "schema_version": 1,
        "feedback_id": feedback_id,
        "submitted_at": submitted_at,
        "question": question,
        "verdict": verdict,
        "note": note,
        "fact_ids": fact_ids,
        "source_urls": source_urls,
    }
    os.makedirs(os.path.dirname(feedback_path), exist_ok=True)
    with open(feedback_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    if verdict in {"incorrect", "incomplete"}:
        review_task = {
            "schema_version": 1,
            "feedback_id": feedback_id,
            "created_at": submitted_at,
            "status": "pending",
            "priority": "high" if verdict == "incorrect" else "medium",
            "reason": verdict,
            "note": note,
            "question": question,
            "fact_ids": fact_ids,
            "source_urls": source_urls,
        }
        with open(review_queue_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(review_task, ensure_ascii=False) + "\n")
    return record


def collect_answer_feedback(question: str, facts: list[dict], provenance_index: dict[str, dict]) -> str | None:
    """Collect optional human judgement immediately after an answer is shown."""
    try:
        choice = input("\nWas this answer [c]orrect, [i]ncorrect, [n]complete, or [s]kip? ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return None
    verdicts = {"c": "correct", "i": "incorrect", "n": "incomplete"}
    if choice not in verdicts:
        return None
    note = input("Optional feedback note (press Enter to skip): ").strip()
    append_feedback_record(question, verdicts[choice], note, facts, provenance_index)
    return verdicts[choice]


def append_triplets_to_file(triplets: list[tuple], filepath: str, existing_keys: set = None) -> list[str]:
    """Append new triplets to a knowledge base file, skipping duplicates. Creates parent dirs if needed."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if existing_keys is None:
        existing_keys = set()
    lines = []
    with open(filepath, "a", encoding="utf-8") as f:
        for domain, s, r, o in triplets:
            key = f"{s.lower()}|{r.lower()}|{o.lower()}"
            if key in existing_keys:
                continue  # Skip duplicate
            existing_keys.add(key)
            line = f"[domain={domain}] ({s}, {r}, {o})"
            f.write(line + "\n")
            lines.append(line)
    return lines


# ══════════════════════════════════════════════════════════════════════
#  TOOL 3: EXTRACT TOPICS FROM USER QUESTION
# ══════════════════════════════════════════════════════════════════════

def extract_topics_from_question(question: str, client=None, model_name: str = "") -> list[str]:
    """Use the LLM to extract key topics/entities from a user question."""
    if client is None:
        words = re.sub(r"[^A-Za-z0-9\s]", "", question).strip().split()
        return [word.capitalize() for word in words if len(word) > 4][:3]

    system_prompt = (
        "You are a topic extraction engine. Given a user question, extract the 1-3 most "
        "important topics or entities that should be searched in a Knowledge Graph.\n\n"
        "RULES:\n"
        "1. Output ONLY the topics, one per line.\n"
        "2. Use PascalCase with no spaces (e.g., 'MachineLearning', 'QuantumMechanics').\n"
        "3. Be specific: prefer 'BubbleSort' over 'Sorting'.\n"
        "4. DO NOT include programming languages (like Python, JavaScript, C++) as topics. Focus purely on the domain concepts, algorithms, models, or data structures.\n"
        "5. No explanations, no numbering, no markdown."
    )

    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
            temperature=1,
            max_completion_tokens=200,
            top_p=1,
            reasoning_effort="low",
            stream=False,
        )
        msg = completion.choices[0].message
        # Reasoning models (like openai/gpt-oss-120b) may put the answer in
        # reasoning_content when content is empty — handle both.
        raw = (msg.content or "") or getattr(msg, "reasoning_content", "") or ""

        topics = []
        for line in raw.strip().split("\n"):
            # Strip markdown bullets and numbering
            line = re.sub(r"^[-*0-9.]+\s*", "", line).strip()
            # If it's a conversational sentence (more than 3 words or too long), skip it
            if not line or len(line.split()) > 3 or len(line) > 40:
                continue

            # Sanitize to PascalCase
            clean_topic = re.sub(r"[^A-Za-z0-9]", "", line)
            if clean_topic:
                topics.append(clean_topic)

        if not topics:
            raise ValueError("No valid topics parsed from LLM")

        return topics[:3]
    except Exception as e:
        logger.error(f"Topic extraction failed/fallback: {e}")
        # Fallback heuristic: just grab longest words from question
        words = re.sub(r"[^A-Za-z0-9\s]", "", question).strip().split()
        return [w.capitalize() for w in words if len(w) > 4][:3]


def available_windows_memory_gb() -> float | None:
    """Return available physical memory on Windows without adding a dependency."""
    if os.name != "nt":
        return None

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    memory = MEMORYSTATUSEX()
    memory.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)):
        return round(memory.ullAvailPhys / (1024 ** 3), 1)
    return None


def select_windows_runtime(preference: str = "auto") -> tuple[str, str]:
    """Choose an always-quantized local runtime for the current Windows machine."""
    if preference not in {"auto", "gpu-4bit", "cpu-int8"}:
        raise ValueError("runtime must be one of: auto, gpu-4bit, cpu-int8")
    if preference == "gpu-4bit":
        if not torch.cuda.is_available():
            raise RuntimeError("gpu-4bit was requested but no CUDA-capable NVIDIA GPU is available")
        return "gpu-4bit", "CUDA available; selecting 4-bit NF4 quantization"
    if preference == "cpu-int8":
        return "cpu-int8", "CPU mode requested; selecting dynamic INT8 quantization"
    if torch.cuda.is_available():
        return "gpu-4bit", "CUDA-capable NVIDIA GPU detected; selecting 4-bit NF4 quantization"
    available_gb = available_windows_memory_gb()
    if available_gb is not None and available_gb < CPU_INT8_MIN_AVAILABLE_GB:
        return "cpu-int8", f"CPU-only; {available_gb:.1f} GB RAM available (the 3B model may be slow or run out of memory)"
    detail = f"{available_gb:.1f} GB RAM available" if available_gb is not None else "available RAM unknown"
    return "cpu-int8", f"CPU-only; {detail}; selecting dynamic INT8 quantization"


def load_local_model(model_path: str, runtime: str = "auto"):
    """Load the local 3B model with 4-bit quantization for answer synthesis."""
    selected_runtime, hardware_note = select_windows_runtime(runtime)
    print(f"   Hardware: {hardware_note}")
    print(f"\n🔧 Loading local answer model from: {model_path}")
    print(f"   (Please be patient! Moving 3 Billion parameters into GPU VRAM takes 10-20 seconds. Do not press Ctrl+C...)")
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True,
                                               clean_up_tokenization_spaces=False)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    if selected_runtime == "gpu-4bit":
        quant_cfg = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            llm_int8_enable_fp32_cpu_offload=True,
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            quantization_config=quant_cfg,
            device_map="cuda:0",
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            offload_folder="offload_cache",
        )
    else:
        # Dynamic quantization is CPU-native and works without CUDA/bitsandbytes.
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float32,
            trust_remote_code=True,
            low_cpu_mem_usage=False,
        )
        model = torch.quantization.quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)
    model.eval()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    print(f"   ✅ Local model loaded successfully!")
    return tokenizer, model


def synthesize_answer_local(question: str, facts: list[dict], file_contexts: list[str], tokenizer, model, execution_output: str = "", needs_code: bool = False) -> str:
    """Synthesize a natural language answer using the LOCAL 3B model with real-time streaming."""
    if not facts and not file_contexts:
        msg = "I don't have enough information in my Knowledge Graph to answer this question."
        print(f"\n{'─' * 70}\n🤖 Agent: {msg}\n{'─' * 70}")
        return msg

    fact_lines = []
    for index, f in enumerate(facts[:20], start=1):
        fact_lines.append(f"[F{index}] {f['subject']} {f['relation']} {f['object']}")
    facts_text = "\n".join(fact_lines)

    vault_text = ""
    if file_contexts and needs_code:
        vault_text = "\n\nCODE VAULT FILES (Dense Context):\n" + "\n".join(file_contexts)
        system_prompt = (
            "You are a factual assistant. The user requested an implementation, and a "
            "Code Vault file was successfully found and will be attached below.\n\n"
            "CRITICAL INSTRUCTION: Keep your response EXTREMELY BRIEF (1-2 sentences max). "
            "Just acknowledge that the requested code is provided in the attached Code Vault below. "
            "Do NOT try to explain the code. Do NOT output any python or code blocks yourself. "
            "Just say 'Here is the code you requested from the vault.' or something similar."
        )
    elif file_contexts and not needs_code:
        vault_text = "\n\nCODE VAULT FILES (Dense Context):\n" + "\n".join(file_contexts)
        system_prompt = (
            "You are an advanced factual assistant. You answer questions by grounding your response "
            "STRICTLY in the Knowledge Graph facts and Code Vault files provided below.\n\n"
            "RULES:\n"
            "1. Do NOT inject your own internal knowledge for rankings or statistics. You may use basic logical deduction to connect obvious entities (e.g. if the user asks about 'Amrita', recognize that 'CoimbatoreCampus' is part of it if present in the context).\n"
            "2. Ensure that your core factual claims do not contradict the provided facts.\n"
            "3. Answer accurately, theoretically, and conversationally, as the user is asking a conceptual question, NOT asking you to generate code."
        )
    else:
        system_prompt = (
            "You are a strict, factual assistant. You answer questions by grounding your response "
            "ONLY in the Knowledge Graph facts provided below.\n\n"
            "RULES:\n"
            "1. Do NOT inject your own internal knowledge, rankings, or statistics. You must only state facts explicitly provided in the context. However, you may use basic logical deduction to recognize obvious entity aliases or relationships.\n"
            "2. However, you MUST ensure that your core factual claims do not contradict the provided facts.\n"
            "3. Cite every factual sentence with one or more fact labels such as [F1].\n"
            "4. Answer accurately and conversationally, but do not hallucinate."
        )

    exec_text = ""
    if execution_output:
        exec_text = f"\n\n--- PROGRAM EXECUTION OUTPUT ---\n{execution_output}\n--- END EXECUTION OUTPUT ---\n"

    user_content = f"Background facts:\n{facts_text}{vault_text}{exec_text}\n\nQuestion: {question}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True,
                       max_length=2500).to(model.device)

    # ── Streaming: print tokens to terminal as they are generated ──
    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

    generation_kwargs = dict(
        **inputs,
        max_new_tokens=800,
        do_sample=False,
        repetition_penalty=1.15,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
        streamer=streamer,
    )

    # Run generation in a background thread so we can stream from the main thread
    gen_thread = threading.Thread(target=lambda: model.generate(**generation_kwargs))
    gen_thread.start()

    # Print the streaming header
    print(f"\n{'─' * 70}")
    sys.stdout.write("🤖 Agent: ")
    sys.stdout.flush()

    answer_chunks = []
    for chunk in streamer:
        sys.stdout.write(chunk)
        sys.stdout.flush()
        answer_chunks.append(chunk)

    gen_thread.join()
    print(f"\n{'─' * 70}")

    answer = "".join(answer_chunks).strip()

    # Clean up trailing artifacts
    for marker in ["<|user|>", "<|system|>", "<|assistant|>", "Human:", "User:", "Question:"]:
        idx = answer.find(marker)
        if idx != -1:
            answer = answer[:idx].strip()

    return answer if answer else "Failed to generate answer."


# ══════════════════════════════════════════════════════════════════════
#  MAIN AGENT LOOP
# ══════════════════════════════════════════════════════════════════════

def run_agent(kg_model: str = KG_MODEL, local_model_path: str = LOCAL_ANSWER_MODEL, runtime: str = "auto"):
    """Run the local KG → 120B → web → local 3B RAG pipeline."""
    load_dotenv(override=True)

    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        print("\n[ERROR] GROQ_API_KEY environment variable not set!")
        print("Add GROQ_API_KEY to your .env file before running the 120B fallback.")
        return
    groq_client = Groq()

    # Load local 3B model for answer synthesis
    local_tokenizer, local_model = load_local_model(local_model_path, runtime=runtime)

    # Load ONLY the on-demand RAG KB
    print("\n" + "=" * 70)
    print("  AGENTIC RAG PIPELINE — Dual-Model Knowledge Graph")
    print("=" * 70)

    print(f"\n📂 Loading on-demand RAG Knowledge:   {RAG_KB_FILE}")
    rag_triplets = load_knowledge_graph(RAG_KB_FILE)
    print(f"   Loaded {len(rag_triplets)} facts from previous RAG sessions.")

    # Use only RAG facts for in-memory graph
    all_triplets = rag_triplets
    # Build deduplication index
    existing_keys = set()
    for t in all_triplets:
        key = f"{t['subject'].lower()}|{t['relation'].lower()}|{t['object'].lower()}"
        existing_keys.add(key)
    print(f"\n✅ Total facts in memory: {len(all_triplets)} ({len(existing_keys)} unique)")
    print(f"   🧠 Knowledge Model (70B): {kg_model} [Groq API]")
    print(f"   💬 Answer Model   (3B):  {local_model_path} [Local GPU]")
    print(f"\nType your question and press Enter. Type 'quit' or 'exit' to stop.\n")
    print("-" * 70)

    while True:
        try:
            question = input("\n🧠 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye!")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("\nGoodbye!")
            break

        # ── Step 1: Extract Topics (70B via Groq) ──
        topics = extract_topics_from_question(question, groq_client, kg_model)

        time.sleep(1.0)  # Rate limit

        # ── Step 2: Search Local Graph ──
        local_results, local_confidence = retrieve_ranked_facts(question, topics, all_triplets)
        print(f"   Local retrieval confidence: {local_confidence:.0%}")

        # ── Step 3: On-Demand Expansion (70B via Groq) ──
        new_facts_generated = 0
        topics_needing_expansion = []
        data_source = "[Local Graph]"

        if local_confidence < 0.60:
            topics_needing_expansion = topics

        if topics_needing_expansion:
            newly_generated_dicts = []
            for topic in topics_needing_expansion:
                # Ask the 120B model from its own knowledge first. Web search is
                # only used as a fallback when that produces no valid triplets.
                web_sources = []
                search_ctx = ""
                new_triplets = generate_new_triplets(topic, groq_client, kg_model, user_question=question)
                data_source = "[120B LLM]"
                if not new_triplets and os.environ.get("TAVILY_API_KEY"):
                    search_ctx, web_sources = search_tavily(f"{topic} {question}")
                    if web_sources:
                        new_triplets = generate_new_triplets(
                            topic, groq_client, kg_model, user_question=question, search_context=search_ctx
                        )
                        data_source = "[Web + 120B LLM]"
                if new_triplets:
                    # Write to the SEPARATE RAG file (not the crawler's file!)
                    written_lines = append_triplets_to_file(new_triplets, RAG_KB_FILE, existing_keys)
                    new_facts_generated += len(written_lines)

                    # Add only deduplicated ones to in-memory graph
                    accepted_triplets = []
                    for line in written_lines:
                        m = _TRIPLET_LINE_RE.match(line)
                        if m:
                            accepted_triplets.append((
                                m.group(1).strip(), m.group(2).strip(),
                                m.group(3).strip(), m.group(4).strip(),
                            ))
                            fact_dict = {
                                "domain": m.group(1).strip(),
                                "subject": m.group(2).strip(),
                                "relation": m.group(3).strip(),
                                "object": m.group(4).strip(),
                                "raw": line,
                            }
                            all_triplets.append(fact_dict)
                            newly_generated_dicts.append(fact_dict)

                    append_provenance_records(
                        accepted_triplets,
                        sources=web_sources,
                        query=f"{topic} {question}",
                        model_name=kg_model,
                    )

                    time.sleep(2.0)  # Rate limit protection

            # Re-search with expanded graph
            local_results, local_confidence = retrieve_ranked_facts(question, topics, all_triplets)

            # GUARANTEE: Force newly generated facts into the context even if keyword matching fails
            for gen_fact in newly_generated_dicts:
                if gen_fact not in local_results:
                    local_results.append(gen_fact)

        # ── Step 3b: Intelligent Code Vault (70B Evaluates) ──
        vault_files_created = 0
        vault_path = None  # Will be set if code evaluation identifies a vault target
        needs_code, detected_lang, detected_flavor, concept_name = evaluate_code_need(question, topics, groq_client, kg_model)

        if needs_code:
            primary_topic = concept_name

            if primary_topic:
                safe_primary = primary_topic
                ext = _LANG_EXT_MAP.get(detected_lang.lower(), ".txt")

                if detected_flavor:
                    safe_flavor = re.sub(r"[^A-Za-z0-9]", "", detected_flavor.capitalize())
                    vault_path = os.path.join(BASE_DIR, "codevault", detected_lang.lower(), f"{safe_primary}_{safe_flavor}{ext}")
                    print_flavor = f" ({detected_flavor.capitalize()})"
                else:
                    vault_path = os.path.join(BASE_DIR, "codevault", detected_lang.lower(), f"{safe_primary}{ext}")
                    print_flavor = ""

                # ── Interactive Overwrite Prompt ──
                skip_generation = False
                if os.path.exists(vault_path):
                    ans = input(f"   ⚠️ Vault file '{os.path.basename(vault_path)}' already exists. Overwrite? (y/n): ").strip().lower()
                    if ans != 'y':
                        print(f"   → Skipping generation. Using existing file.")
                        skip_generation = True

                if not skip_generation:
                    print(f"   → YES — Generating {detected_lang.upper()} Code Vault for '{primary_topic}'{print_flavor}...")
                    vault_files_created = generate_code_for_vault(
                        primary_topic, question, detected_lang, detected_flavor, groq_client, kg_model,
                        existing_keys, all_triplets
                    )
                    if vault_files_created:
                        # Re-search so the hasContextFile triplet is picked up
                        local_results = search_local_kg(topics, all_triplets)
                    time.sleep(2.0)
                else:
                    # Ensure the hasContextFile triplet is searchable for hydration
                    local_results = search_local_kg(topics, all_triplets)
        else:
            pass

        # ── Step 4: Hydrate Code Vault & Synthesize Answer (Local 3B) ──
        # Hydrate Code Vaults
        file_contexts = []
        raw_code_blocks = []  # Keep track of raw code to append to final answer
        vault_python_paths = []  # Track Python vault files for potential execution
        for t in local_results:
            if t["relation"].lower() == "hascontextfile":
                filepath = t["object"]
                if os.path.exists(filepath):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Truncate to ~1500 chars to avoid memory overflow on 3B model
                            truncated_content = content[:1500] + ("\n...[TRUNCATED]" if len(content) > 1500 else "")
                            file_contexts.append(f"--- FILE: {filepath} ---\n{truncated_content}\n")
                            raw_code_blocks.append((os.path.basename(filepath), content))
                            if filepath.endswith(".py"):
                                vault_python_paths.append(filepath)
                    except Exception as e:
                        pass
                else:
                    pass

        # Fallback: if Code Vault evaluation identified a Python vault file but KG search
        # didn't find the hasContextFile triplet (topic name mismatch), inject it directly.
        if needs_code and vault_path is not None and os.path.exists(vault_path):
            if vault_path not in [t["object"] for t in local_results if t["relation"].lower() == "hascontextfile"]:
                try:
                    with open(vault_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        truncated_content = content[:1500] + ("\n...[TRUNCATED]" if len(content) > 1500 else "")
                        file_contexts.append(f"--- FILE: {vault_path} ---\n{truncated_content}\n")
                        raw_code_blocks.append((os.path.basename(vault_path), content))
                        if vault_path.endswith(".py"):
                            vault_python_paths.append(vault_path)
                except Exception as e:
                    pass

        # ── Step 4b: Code Execution (Interpreter Pattern) ──
        execution_output = ""
        if vault_python_paths and needs_code:
            time.sleep(1.0)  # Rate limit
            if should_execute_code(question, concept_name, groq_client, kg_model):
                for py_path in vault_python_paths:
                    success, output = execute_code_safely(py_path)
                    if success:
                        execution_output += f"[{os.path.basename(py_path)}]:\n{output}\n"
                    else:
                        execution_output += f"[{os.path.basename(py_path)} — FAILED]:\n{output}\n"

        answer = synthesize_answer_local(question, local_results, file_contexts, local_tokenizer, local_model, execution_output, needs_code)

        provenance_index = load_provenance_index()
        print_evidence(local_results, provenance_index)
        feedback_verdict = collect_answer_feedback(question, local_results, provenance_index)

        # Answer was already streamed to the terminal by synthesize_answer_local.
        # No need to print it again.
        exec_status = ""
        if execution_output:
            exec_status = " | ⚡ code executed"
        print(f"   📊 Stats ({data_source}): {len(local_results)} facts | {len(file_contexts)} vault files | {new_facts_generated} new facts generated | {len(all_triplets)} total in graph{exec_status}")

    # Cleanup
    del local_model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()


def main():
    parser = argparse.ArgumentParser(description="Agentic RAG Pipeline — Dual-Model Knowledge Graph")
    parser.add_argument("--kg-model", type=str, default=KG_MODEL, help="Groq model for topic extraction and fact generation")
    parser.add_argument("--local-model", type=str, default=LOCAL_ANSWER_MODEL, help="Path to local 3B model for answer synthesis")
    parser.add_argument("--runtime", choices=["auto", "gpu-4bit", "cpu-int8"], default="auto", help="Quantized local runtime (default: auto-detect Windows hardware)")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )

    run_agent(kg_model=args.kg_model, local_model_path=args.local_model, runtime=args.runtime)


if __name__ == "__main__":
    main()

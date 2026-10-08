"""
Agentic RAG Pipeline — On-Demand Knowledge Graph Expansion

This agent answers user questions by:
1. Extracting key topics from the question (via LLM).
2. Searching the local knowledge_base.txt for relevant triplets.
3. If insufficient facts are found, generating new triplets on-the-fly
   using the 70B model and appending them to the graph.
4. Synthesizing a grounded answer from the retrieved facts.

Usage:
    python -m src.kg_builder.rag_agent
"""

import os
import re
import time
import logging
import argparse
from groq import Groq

from .config import settings
from .extraction import extract_triplets
from .canonicalization import force_seed_casing_in_text

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════════════════════════════

MODEL_NAME = "llama-3.3-70b-versatile"
MIN_FACTS_THRESHOLD = 3   # If fewer facts found locally, trigger on-demand generation
MAX_RETRIES = 3


# ══════════════════════════════════════════════════════════════════════
#  KNOWLEDGE GRAPH LOADING
# ══════════════════════════════════════════════════════════════════════

_TRIPLET_LINE_RE = re.compile(
    r"\[domain=([A-Za-z0-9_ -]+)\]\s*\(\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*([^)]+?)\s*\)"
)


def load_knowledge_graph(filepath: str) -> list[dict]:
    """Load all triplets from knowledge_base.txt into a list of dicts."""
    triplets = []
    if not os.path.exists(filepath):
        logger.warning(f"Knowledge base file not found: {filepath}")
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
    Returns deduplicated results ordered by relevance (exact match > partial).
    """
    results = []
    seen_raw = set()

    for t in triplets:
        subj_lower = t["subject"].lower()
        obj_lower = t["object"].lower()

        for topic in topics:
            topic_lower = topic.lower().replace(" ", "")
            # Check if the topic matches either the subject or object
            if topic_lower in subj_lower or topic_lower in obj_lower:
                if t["raw"] not in seen_raw:
                    results.append(t)
                    seen_raw.add(t["raw"])
                break  # No need to check other topics for this triplet

    return results


# ══════════════════════════════════════════════════════════════════════
#  TOOL 2: ON-DEMAND TRIPLET GENERATION
# ══════════════════════════════════════════════════════════════════════

def generate_new_triplets(
    topic: str,
    client: Groq,
    model_name: str,
    user_question: str = "",
) -> list[tuple]:
    """Generate new triplets for a topic using the 70B model via Groq API.

    Includes the user's original question as context so the LLM generates
    facts relevant to what the user actually asked about.
    Returns list of (domain, subject, relation, object) tuples.
    """
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
        "10. Focus on facts that are RELEVANT to the user's question context."
    )

    # Build context hint from the user question
    context_hint = ""
    if user_question:
        context_hint = f"\n(Context: The user asked: \"{user_question}\". Generate facts relevant to this question.)\n"

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
{context_hint}
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
                temperature=0.05,
                max_completion_tokens=500,
                top_p=1,
                stream=False,
            )
            raw_output = completion.choices[0].message.content or ""
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

    raw_output = force_seed_casing_in_text(raw_output)
    return extract_triplets(raw_output)


def append_triplets_to_file(triplets: list[tuple], filepath: str, existing_keys: set = None) -> list[str]:
    """Append new triplets to the knowledge_base.txt file, skipping duplicates.

    Args:
        existing_keys: Set of "subject|relation|object" keys already in the graph.
    Returns the list of formatted lines that were actually written (deduplicated).
    """
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

def extract_topics_from_question(question: str, client: Groq, model_name: str) -> list[str]:
    """Use the LLM to extract key topics/entities from a user question.

    Returns a list of PascalCase topic strings.
    """
    system_prompt = (
        "You are a topic extraction engine. Given a user question, extract the 1-3 most "
        "important topics or entities that should be searched in a Knowledge Graph.\n\n"
        "RULES:\n"
        "1. Output ONLY the topics, one per line.\n"
        "2. Use PascalCase with no spaces (e.g., 'MachineLearning', 'QuantumMechanics').\n"
        "3. Be specific: prefer 'BubbleSort' over 'Sorting'.\n"
        "4. No explanations, no numbering, no markdown."
    )

    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
            temperature=0.0,
            max_completion_tokens=100,
            top_p=1,
            stream=False,
        )
        raw = completion.choices[0].message.content or ""
        # Parse one topic per line, strip whitespace
        topics = [line.strip() for line in raw.strip().split("\n") if line.strip()]
        return topics
    except Exception as e:
        logger.error(f"Topic extraction failed: {e}")
        # Fallback: use the raw question words as topics
        words = question.strip().split()
        return [w.capitalize() for w in words if len(w) > 3][:3]


# ══════════════════════════════════════════════════════════════════════
#  ANSWER SYNTHESIS
# ══════════════════════════════════════════════════════════════════════

def synthesize_answer(
    question: str,
    facts: list[dict],
    client: Groq,
    model_name: str,
) -> str:
    """Synthesize a natural language answer from retrieved Knowledge Graph facts."""
    if not facts:
        return "I don't have enough information in my Knowledge Graph to answer this question."

    # Format facts as readable context
    fact_lines = []
    for f in facts[:50]:  # Cap at 50 facts to stay within context limits
        fact_lines.append(f"- {f['subject']} {f['relation']} {f['object']} (Domain: {f['domain']})")
    facts_text = "\n".join(fact_lines)

    system_prompt = (
        "You are a strictly factual assistant. You answer questions using ONLY the "
        "Knowledge Graph facts provided below. These facts are the absolute truth. "
        "Prioritize these facts over your own prior knowledge.\n\n"
        "Answer accurately and concisely in 2-4 sentences. Do not use markdown, "
        "bullet points, or numbered lists. Do not repeat yourself. "
        "If the facts don't contain the answer, say 'I do not have enough information.'"
    )

    user_prompt = f"KNOWLEDGE GRAPH FACTS:\n{facts_text}\n\nQUESTION: {question}"

    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_completion_tokens=300,
            top_p=1,
            stream=False,
        )
        return completion.choices[0].message.content or "Failed to generate answer."
    except Exception as e:
        logger.error(f"Answer synthesis failed: {e}")
        return f"Error generating answer: {e}"


# ══════════════════════════════════════════════════════════════════════
#  MAIN AGENT LOOP
# ══════════════════════════════════════════════════════════════════════

def run_agent(model_name: str = MODEL_NAME):
    """Run the interactive Agentic RAG pipeline."""
    # Initialize Groq client
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        print("\n[ERROR] GROQ_API_KEY environment variable not set!")
        print("Set it with: $env:GROQ_API_KEY=\"your_key_here\"")
        return

    client = Groq(api_key=api_key)
    kg_file = settings.output_file

    # Load the knowledge graph
    print("\n" + "=" * 70)
    print("  AGENTIC RAG PIPELINE — On-Demand Knowledge Graph")
    print("=" * 70)
    print(f"\nLoading Knowledge Graph from: {kg_file}")

    triplets = load_knowledge_graph(kg_file)
    # Build deduplication index from existing triplets
    existing_keys = set()
    for t in triplets:
        key = f"{t['subject'].lower()}|{t['relation'].lower()}|{t['object'].lower()}"
        existing_keys.add(key)
    print(f"Loaded {len(triplets)} facts into memory ({len(existing_keys)} unique).")
    print(f"Model: {model_name}")
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

        # ── Step 1: Extract Topics ──
        print(f"\n📌 Extracting topics from your question...")
        topics = extract_topics_from_question(question, client, model_name)
        print(f"   Topics identified: {', '.join(topics)}")

        # Small delay for rate limiting
        time.sleep(1.0)

        # ── Step 2: Search Local Graph ──
        print(f"\n🔍 Searching local Knowledge Graph ({len(triplets)} facts)...")
        local_results = search_local_kg(topics, triplets)
        print(f"   Found {len(local_results)} relevant facts locally.")

        # ── Step 3: On-Demand Expansion (check PER-TOPIC coverage) ──
        new_facts_generated = 0
        topics_needing_expansion = []

        for topic in topics:
            topic_facts = search_local_kg([topic], triplets)
            print(f"   → '{topic}': {len(topic_facts)} facts found")
            if len(topic_facts) < MIN_FACTS_THRESHOLD:
                topics_needing_expansion.append(topic)

        if topics_needing_expansion:
            print(f"\n⚡ Topics with insufficient coverage: {', '.join(topics_needing_expansion)}")
            print(f"   Generating new knowledge on-the-fly...")

            for topic in topics_needing_expansion:
                new_triplets = generate_new_triplets(topic, client, model_name, user_question=question)
                if new_triplets:
                    written_lines = append_triplets_to_file(new_triplets, kg_file, existing_keys)
                    new_facts_generated += len(written_lines)
                    print(f"   ✅ Generated {len(written_lines)} new facts for '{topic}' ({len(new_triplets) - len(written_lines)} duplicates skipped)")

                    # Add only the deduplicated ones to in-memory graph
                    for line in written_lines:
                        m = _TRIPLET_LINE_RE.match(line)
                        if m:
                            triplets.append({
                                "domain": m.group(1).strip(),
                                "subject": m.group(2).strip(),
                                "relation": m.group(3).strip(),
                                "object": m.group(4).strip(),
                                "raw": line,
                            })

                    time.sleep(2.0)  # Rate limit protection

            # Re-search with expanded graph
            print(f"\n🔍 Re-searching expanded graph ({len(triplets)} total facts)...")
            local_results = search_local_kg(topics, triplets)
            print(f"   Found {len(local_results)} relevant facts after expansion.")
        else:
            print(f"   ✅ All topics have sufficient local coverage. No expansion needed.")

        # ── Step 4: Synthesize Answer ──
        print(f"\n💬 Synthesizing answer from {len(local_results)} facts...")
        time.sleep(1.0)  # Rate limit
        answer = synthesize_answer(question, local_results, client, model_name)

        print(f"\n{'─' * 70}")
        print(f"🤖 Agent: {answer}")
        print(f"{'─' * 70}")
        print(f"   📊 Stats: {len(local_results)} facts used | {new_facts_generated} new facts generated | {len(triplets)} total in graph")


def main():
    parser = argparse.ArgumentParser(description="Agentic RAG Pipeline — On-Demand Knowledge Graph")
    parser.add_argument("--model", type=str, default=MODEL_NAME, help="Groq model name")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )

    run_agent(model_name=args.model)


if __name__ == "__main__":
    main()

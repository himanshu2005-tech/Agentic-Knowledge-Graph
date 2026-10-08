import time
import os
import logging
from groq import Groq
from .extraction import extract_triplets
from .canonicalization import force_seed_casing_in_text

logger = logging.getLogger(__name__)

def load_model(model_id: str):
    logger.info(f"Initializing Groq client for model {model_id}...")
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        logger.warning("GROQ_API_KEY environment variable not set! API call will fail unless you set it.")
    client = Groq(api_key=api_key)
    return client, model_id

def generate_and_extract(
    topic: str,
    client: Groq,
    model_name: str,
    max_new_tokens: int,
    top_k: int,
    temperature: float = 1.0,
    min_relations: int = 2,
    max_retries: int = 3
) -> tuple[list, float, float]:
    start_time = time.time()
    
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
        "8. Generate 8-15 high-quality triples per topic.\n"
        "9. Output ONLY the triples. No markdown, no explanations, no conversational text."
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

    model_start = time.time()
    import re
    raw_output = ""
    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_completion_tokens=max_new_tokens,
                top_p=1,
                stream=False
            )
            raw_output = completion.choices[0].message.content or ""
            break  # Success! Break out of retry loop
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate limit" in error_msg.lower():
                # Extract wait time, e.g., "try again in 3m21.312s" or "try again in 10s"
                match = re.search(r"try again in (?:(\d+)m)?([\d\.]+)s", error_msg)
                if match:
                    mins = int(match.group(1)) if match.group(1) else 0
                    secs = float(match.group(2))
                    wait_time = (mins * 60) + secs + 2.0  # +2s buffer
                else:
                    wait_time = 60.0  # Default to 60s if we can't parse it
                
                logger.warning(f"Rate limit hit! Sleeping for {wait_time:.1f} seconds... (Attempt {attempt+1}/{max_retries})")
                time.sleep(wait_time)
            else:
                logger.error(f"Groq API Error: {e}")
                break  # Break on non-rate-limit errors
        
    model_end = time.time()

    raw_output = force_seed_casing_in_text(raw_output)
    candidates = extract_triplets(raw_output)
    
    total_end = time.time()
    
    model_time = model_end - model_start
    total_time = total_end - start_time
    
    return candidates, model_time, total_time

import os
import time
import heapq
import itertools
import argparse
import logging
import numpy as np
from .config import settings
from sentence_transformers import SentenceTransformer
from .persistence import (
    NodeRegistry, load_set_from_file, load_triplet_counts,
    count_triplets, load_domain_queues, bootstrap_domain_queues,
    save_domain_queues, save_triplet_counts, append_to_file
)
from .validators import check_functional_conflict, build_functional_index, update_functional_index, is_placeholder_name
from .wikidata import _load_wikidata_cache, _save_wikidata_cache, wikidata_verify_triple
from .api_model import load_model, generate_and_extract
from .seeds import DEFAULT_SEEDS, TOPIC_DOMAINS

def setup_logging():
    settings.setup_dirs()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
        handlers=[
            logging.FileHandler(settings.stats_log_file),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)

# Import domain categories from the top-level config
from src.config import DOMAIN_CATEGORIES, BEAM_EMBED_MODEL


def route_to_domain(node_vec, domain_embeddings):
    """Find the best-matching domain for a node vector. Returns (domain_name, similarity)."""
    best_domain = None
    best_sim = -1.0
    for domain, d_vec in domain_embeddings.items():
        sim = float(np.dot(node_vec, d_vec))
        if sim > best_sim:
            best_sim = sim
            best_domain = domain
    return best_domain, best_sim


def run_bfs(resume: bool = False, batch_size: int = 50, max_triplets: int = 500000, 
            patience: int = 20, use_wikidata: bool = False, model_name: str = "llama-3.3-70b-versatile"):
    
    logger.info("=" * 70)
    logger.info("  ROUND-ROBIN DOMAIN SCHEDULER — Knowledge Graph Builder")
    logger.info("=" * 70)
    
    tokenizer, model = load_model(model_name)
    
    # Load embedding model and compute domain vectors
    logger.info(f"Loading embedding model: {BEAM_EMBED_MODEL}")
    embedder = SentenceTransformer(BEAM_EMBED_MODEL)
    
    domain_embeddings = {}
    for domain, description in DOMAIN_CATEGORIES.items():
        domain_embeddings[domain] = embedder.encode(description, normalize_embeddings=True)
    logger.info(f"Computed core vectors for {len(domain_embeddings)} domains.")
    
    domain_names = list(DOMAIN_CATEGORIES.keys())
    
    polysemy_terms = load_set_from_file(settings.polysemy_log_file)
    registry = NodeRegistry(polysemy_terms)
    if resume:
        registry.load_from_file(settings.output_file)
    
    visited = load_set_from_file(settings.visited_file) if resume else set()
    blacklist = load_set_from_file(settings.blacklist_file) if resume else set()
    triplet_counts = load_triplet_counts(settings.triplet_set_file) if resume else {}
    
    subj_idx, obj_idx = build_functional_index(triplet_counts)
    
    # Load or bootstrap domain queues
    domain_queues = load_domain_queues(settings.queue_file, visited, blacklist, domain_names) if resume else {d: [] for d in domain_names}
    
    total_queued = sum(len(q) for q in domain_queues.values())
    if total_queued == 0:
        if len(registry.get_all_canonical_nodes()) == 0:
            logger.info("Registry empty. Seeding from DEFAULT_SEEDS...")
            for s in DEFAULT_SEEDS:
                domain = TOPIC_DOMAINS.get(s, "General")
                registry.canonicalize(s, domain)
        logger.info("Routing seeds into domain queues via embedding similarity...")
        domain_queues = bootstrap_domain_queues(registry, visited, blacklist, embedder, domain_embeddings)
    
    total_queued = sum(len(q) for q in domain_queues.values())
    logger.info(f"Starting Round-Robin with {total_queued} nodes across {sum(1 for q in domain_queues.values() if q)} active domains.")
    
    wikidata_cache = _load_wikidata_cache() if use_wikidata else {}
    
    total_triplets = count_triplets(triplet_counts)
    nodes_processed = 0
    bad_streak = 0
    
    # Domain stats tracking
    domain_stats = {d: {"processed": 0, "triplets": 0} for d in domain_names}
    
    # Round-robin cycle through all domains
    domain_cycle = itertools.cycle(domain_names)
    empty_passes = 0  # Track how many consecutive domains had empty queues
    
    while total_triplets < max_triplets and bad_streak < patience:
        # Find next non-empty domain
        domain = next(domain_cycle)
        
        if not domain_queues.get(domain):
            empty_passes += 1
            if empty_passes >= len(domain_names):
                logger.info("All domain queues are empty. Stopping.")
                break
            continue
        
        empty_passes = 0
        
        neg_sim, depth, current_node = heapq.heappop(domain_queues[domain])
        if current_node in visited or current_node in blacklist:
            continue
            
        logger.info(f"[{domain}] Processing [{depth}] (sim={-neg_sim:.3f}): {current_node}")
        visited.add(current_node)
        append_to_file(settings.visited_file, current_node)
        
        # Generate triplets
        raw_triplets, model_time, total_time = generate_and_extract(
            current_node, tokenizer, model, 
            settings.max_new_tokens, settings.top_k, settings.temperature,
            min_relations=2, max_retries=3
        )
        
        # Rate limit protection (Groq free tier)
        time.sleep(2.1)
        
        valid_extracted = 0
        for extracted_domain, s, r, o in raw_triplets:
            is_ph, ph_reason = is_placeholder_name(s)
            if not is_ph:
                is_ph, ph_reason = is_placeholder_name(o, relation=r, is_object=True)
            if is_ph:
                append_to_file(settings.filtered_file, f"[FILTERED] {ph_reason} | ({s}, {r}, {o})")
                continue
                
            s_can = registry.canonicalize(s, extracted_domain)
            o_can = registry.canonicalize(o, extracted_domain)
            
            conflict, reason = check_functional_conflict(s_can, r, o_can, subj_idx, obj_idx)
            if conflict:
                append_to_file(settings.quarantine_file, f"{s_can} | {r} | {o_can} ({reason})")
                continue
                
            if use_wikidata:
                s_can, o_can = wikidata_verify_triple(s_can, r, o_can, wikidata_cache)
                
            triplet_key = f"{s_can},{r},{o_can}"
            if triplet_key not in triplet_counts:
                triplet_counts[triplet_key] = 1
                total_triplets += 1
                valid_extracted += 1
                
                update_functional_index(s_can, r, o_can, subj_idx, obj_idx)
                
                append_to_file(settings.output_file, f"[domain={extracted_domain}] ({s_can}, {r}, {o_can})")
                
                # Route new object into the best-matching domain queue
                if o_can not in visited and o_can not in blacklist:
                    o_vec = embedder.encode(o_can, normalize_embeddings=True)
                    best_domain, sim = route_to_domain(o_vec, domain_embeddings)
                    heapq.heappush(domain_queues[best_domain], (-sim, depth + 1, o_can))
            else:
                triplet_counts[triplet_key] += 1
                
        if valid_extracted == 0:
            bad_streak += 1
            logger.warning(f"No valid triplets for {current_node}. Bad streak: {bad_streak}")
        else:
            bad_streak = 0
            domain_stats[domain]["triplets"] += valid_extracted
            
        domain_stats[domain]["processed"] += 1
        nodes_processed += 1
        
        # Periodic checkpoint + stats
        if nodes_processed % batch_size == 0:
            logger.info("=" * 50)
            logger.info(f"CHECKPOINT — {total_triplets} total triplets, {nodes_processed} nodes processed")
            for d in domain_names:
                qsize = len(domain_queues.get(d, []))
                proc = domain_stats[d]["processed"]
                trips = domain_stats[d]["triplets"]
                if proc > 0 or qsize > 0:
                    logger.info(f"  [{d}] processed={proc}, triplets={trips}, queue={qsize}")
            logger.info("=" * 50)
            save_domain_queues(settings.queue_file, domain_queues)
            save_triplet_counts(settings.triplet_set_file, triplet_counts)
            if use_wikidata:
                _save_wikidata_cache(wikidata_cache)
                
    # Final save
    save_domain_queues(settings.queue_file, domain_queues)
    save_triplet_counts(settings.triplet_set_file, triplet_counts)
    if use_wikidata:
        _save_wikidata_cache(wikidata_cache)
    
    # Final report
    logger.info("=" * 70)
    logger.info("  FINAL DOMAIN REPORT")
    logger.info("=" * 70)
    for d in domain_names:
        proc = domain_stats[d]["processed"]
        trips = domain_stats[d]["triplets"]
        qsize = len(domain_queues.get(d, []))
        logger.info(f"  [{d:25s}] processed={proc:4d}  triplets={trips:5d}  remaining={qsize:5d}")
    logger.info(f"  TOTAL: {total_triplets} triplets from {nodes_processed} nodes.")
    logger.info("=" * 70)

def main():
    parser = argparse.ArgumentParser(description="Knowledge Graph Builder — Round-Robin Domain Scheduler")
    parser.add_argument("--reset", action="store_true", help="Reset all progress and start from scratch (disables auto-resume)")
    parser.add_argument("--batch-size", type=int, default=50, help="Checkpoint frequency")
    parser.add_argument("--wikidata", action="store_true", help="Enable Wikidata verification")
    parser.add_argument("--model", type=str, default="llama-3.3-70b-versatile", help="Model name to use")
    args = parser.parse_args()
    
    setup_logging()
    
    # Enable wikidata if either arg or config is set
    use_wikidata = args.wikidata or settings.enable_wikidata_verification
    
    # Auto-resume if the file exists and we aren't explicitly resetting
    auto_resume = os.path.exists(settings.output_file) and not args.reset
    if auto_resume:
        logger.info(f"Found existing {settings.output_file}. Auto-resuming...")
        
    try:
        run_bfs(resume=auto_resume, batch_size=args.batch_size, use_wikidata=use_wikidata, model_name=args.model)
    except KeyboardInterrupt:
        logger.info("Interrupted by user. Shutting down gracefully.")

if __name__ == "__main__":
    main()

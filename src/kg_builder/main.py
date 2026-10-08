import os
import time
import argparse
import logging
from collections import deque
from .config import settings
from .persistence import (
    NodeRegistry, load_set_from_file, load_triplet_counts,
    count_triplets, load_queue, bootstrap_from_registry,
    save_queue, save_triplet_counts, append_to_file
)
from .validators import check_functional_conflict, build_functional_index, update_functional_index, is_placeholder_name
from .wikidata import _load_wikidata_cache, _save_wikidata_cache, wikidata_verify_triple
from .model import load_model, generate_and_extract
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

def run_bfs(resume: bool = False, batch_size: int = 50, max_triplets: int = 500000, 
            patience: int = 5, use_wikidata: bool = False):
    
    logger.info("Initializing BFS Knowledge Graph Builder...")
    
    tokenizer, model = load_model(settings.model_path)
    
    polysemy_terms = load_set_from_file(settings.polysemy_log_file)
    registry = NodeRegistry(polysemy_terms)
    if resume:
        registry.load_from_file(settings.output_file)
    
    visited = load_set_from_file(settings.visited_file) if resume else set()
    blacklist = load_set_from_file(settings.blacklist_file) if resume else set()
    triplet_counts = load_triplet_counts(settings.triplet_set_file) if resume else {}
    
    subj_idx, obj_idx = build_functional_index(triplet_counts)
    
    queue = load_queue(settings.queue_file, visited, blacklist) if resume else deque()
    if not queue:
        if len(registry.get_all_canonical_nodes()) == 0:
            logger.info("Registry empty. Seeding from DEFAULT_SEEDS...")
            for s in DEFAULT_SEEDS:
                domain = TOPIC_DOMAINS.get(s, "General")
                registry.canonicalize(s, domain)
        queue = bootstrap_from_registry(registry, visited, blacklist)
    
    logger.info(f"Starting BFS with {len(queue)} nodes in queue.")
    
    wikidata_cache = _load_wikidata_cache() if use_wikidata else {}
    
    total_triplets = count_triplets(triplet_counts)
    nodes_processed = 0
    bad_streak = 0
    
    while queue and total_triplets < max_triplets and bad_streak < patience:
        current_node, depth = queue.popleft()
        if current_node in visited or current_node in blacklist:
            continue
            
        logger.info(f"Processing node [{depth}]: {current_node}")
        visited.add(current_node)
        append_to_file(settings.visited_file, current_node)
        
        # generate
        raw_triplets, model_time, total_time = generate_and_extract(
            current_node, tokenizer, model, 
            settings.max_new_tokens, settings.top_k, settings.temperature,
            min_relations=2, max_retries=3
        )
        
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
                
                if o_can not in visited and o_can not in blacklist:
                    queue.append((o_can, depth + 1))
            else:
                triplet_counts[triplet_key] += 1
                
        if valid_extracted == 0:
            bad_streak += 1
            logger.warning(f"No valid triplets for {current_node}. Bad streak: {bad_streak}")
        else:
            bad_streak = 0
            
        nodes_processed += 1
        
        if nodes_processed % batch_size == 0:
            logger.info("Saving checkpoints...")
            save_queue(settings.queue_file, queue)
            save_triplet_counts(settings.triplet_set_file, triplet_counts)
            if use_wikidata:
                _save_wikidata_cache(wikidata_cache)
                
    # Final save
    save_queue(settings.queue_file, queue)
    save_triplet_counts(settings.triplet_set_file, triplet_counts)
    if use_wikidata:
        _save_wikidata_cache(wikidata_cache)
        
    logger.info("BFS completed.")

def main():
    parser = argparse.ArgumentParser(description="Knowledge Graph Builder")
    parser.add_argument("--resume", action="store_true", help="Resume from previous state")
    parser.add_argument("--batch-size", type=int, default=50, help="Checkpoint frequency")
    parser.add_argument("--wikidata", action="store_true", help="Enable Wikidata verification")
    args = parser.parse_args()
    
    setup_logging()
    
    # Enable wikidata if either arg or config is set
    use_wikidata = args.wikidata or settings.enable_wikidata_verification
    
    try:
        run_bfs(resume=args.resume, batch_size=args.batch_size, use_wikidata=use_wikidata)
    except KeyboardInterrupt:
        logger.info("Interrupted by user. Shutting down gracefully.")

if __name__ == "__main__":
    main()

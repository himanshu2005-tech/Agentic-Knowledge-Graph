import os
import json
import heapq
from typing import Union, Tuple, Optional
import logging
from collections import deque
from .canonicalization import _force_pascal_case

logger = logging.getLogger(__name__)


def save_queue(path: str, queue) -> None:
    """Persist the legacy `(node, depth)` queue atomically."""
    temp_path = path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as handle:
        for node, depth in queue:
            handle.write(f"{node}\t{depth}\n")
    os.replace(temp_path, path)


def load_queue(path: str, visited: set | None = None, blacklist: set | None = None):
    """Load a legacy queue while excluding visited or blocked nodes."""
    visited = visited or set()
    blacklist = blacklist or set()
    queue = deque()
    if not os.path.exists(path):
        return queue
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            parts = line.rstrip("\n").split("\t")
            if not parts or not parts[0] or parts[0] in visited or parts[0] in blacklist:
                continue
            queue.append((parts[0], int(parts[1]) if len(parts) > 1 else 0))
    return queue

class NodeRegistry:
    """Manages canonical forms and discovery domains for nodes."""
    
    def __init__(self, polysemous_terms: set):
        self._registry: dict[Union[str, Tuple[str, str]], str] = {}
        self.polysemous_terms = polysemous_terms

    def load_from_file(self, filepath: str):
        """Loads registry state from an existing knowledge_base.txt"""
        if not os.path.exists(filepath):
            return
            
        count = 0
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                
                parts = line.split(']')
                if len(parts) < 2: continue
                
                domain_part = parts[0].strip()
                if not domain_part.startswith('[domain='): continue
                domain = domain_part.replace('[domain=', '')
                
                rest = parts[1].strip()
                if not (rest.startswith('(') and rest.endswith(')')): continue
                rest = rest[1:-1]
                
                parts_t = rest.split(',')
                if len(parts_t) == 3:
                    s, _, o = [x.strip() for x in parts_t]
                    for node in (s, o):
                        key = node.lower().rstrip('s')
                        if key in self.polysemous_terms:
                            reg_key = (domain.lower(), key)
                        else:
                            reg_key = key
                            
                        if reg_key not in self._registry:
                            self._registry[reg_key] = node
                            count += 1
        logger.info(f"Loaded {count} nodes into NodeRegistry.")

    def is_known(self, raw: str, domain: str) -> bool:
        key = raw.strip().lower().rstrip('s')
        reg_key = (domain.lower(), key) if key in self.polysemous_terms else key
        return reg_key in self._registry

    def canonicalize(self, raw: str, domain: str) -> str:
        """Returns the canonical form of a node. Registers it if new."""
        key = raw.strip().lower().rstrip("s")
        reg_key = (domain.lower(), key) if key in self.polysemous_terms else key
            
        if reg_key in self._registry:
            existing = self._registry[reg_key]
            # Clean up poisoned KB entries (e.g. "legaldocument" -> "LegalDocument")
            if existing.islower() and len(existing) > 5:
                existing = existing.capitalize()
                self._registry[reg_key] = existing
            return existing
            
        canonical = _force_pascal_case(raw.strip())
            
        self._registry[reg_key] = canonical
        return canonical
        
    def get_all_canonical_nodes(self) -> list:
        return list(self._registry.values())


def load_set_from_file(path: str) -> set:
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())

def append_to_file(path: str, line: str):
    with open(path, "a", encoding='utf-8') as f:
        f.write(line + "\n")

def count_triplets(triplet_counts: dict) -> int:
    return sum(triplet_counts.values())

def load_triplet_counts(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return {}

def save_triplet_counts(path: str, counts: dict):
    temp_path = path + ".tmp"
    with open(temp_path, "w", encoding='utf-8') as f:
        json.dump(counts, f, indent=2)
    os.replace(temp_path, path)

def save_domain_queues(path: str, domain_queues: dict):
    temp_path = path + ".tmp"
    with open(temp_path, "w", encoding='utf-8') as f:
        for domain, queue in domain_queues.items():
            for neg_sim, depth, node in list(queue):
                f.write(f"{node}\t{depth}\t{neg_sim}\t{domain}\n")
    os.replace(temp_path, path)

def load_domain_queues(path: str, visited: set, blacklist: set, domain_names: list) -> dict:
    domain_queues = {d: [] for d in domain_names}
    if not os.path.exists(path):
        return domain_queues
    skipped = 0
    loaded = 0
    with open(path, "r", encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            node = parts[0]
            depth = int(parts[1]) if len(parts) > 1 else 0
            neg_sim = float(parts[2]) if len(parts) > 2 else 0.0
            domain = parts[3] if len(parts) > 3 else domain_names[0]
            if node in visited or node in blacklist:
                skipped += 1
                continue
            if domain not in domain_queues:
                domain_queues[domain] = []
            heapq.heappush(domain_queues[domain], (neg_sim, depth, node))
            loaded += 1
    logger.info(f"Restored {loaded} nodes across {sum(1 for q in domain_queues.values() if q)} domains, skipped {skipped}.")
    return domain_queues

def bootstrap_domain_queues(registry: NodeRegistry, visited: set, blacklist: set,
                            embedder, domain_embeddings: dict) -> dict:
    """Route all seeds into domain queues using embedding similarity."""
    import numpy as np
    domain_queues = {d: [] for d in domain_embeddings}
    count = 0
    for node in registry.get_all_canonical_nodes():
        if node in visited or node in blacklist:
            continue
        node_vec = embedder.encode(node, normalize_embeddings=True)
        best_domain = None
        best_sim = -1.0
        for domain, d_vec in domain_embeddings.items():
            sim = float(np.dot(node_vec, d_vec))
            if sim > best_sim:
                best_sim = sim
                best_domain = domain
        heapq.heappush(domain_queues[best_domain], (-best_sim, 0, node))
        count += 1
    for domain, q in domain_queues.items():
        if q:
            logger.info(f"  [{domain}]: {len(q)} seeds")
    logger.info(f"Bootstrapped {count} seeds across {sum(1 for q in domain_queues.values() if q)} domains")
    return domain_queues


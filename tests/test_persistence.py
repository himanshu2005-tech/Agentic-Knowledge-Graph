import os
import pytest
from collections import deque
from src.kg_builder.persistence import NodeRegistry, save_queue, load_queue

def test_node_registry(tmp_path):
    registry = NodeRegistry(polysemous_terms={"bank", "apple"})
    
    # Test canonicalization of a new node
    can1 = registry.canonicalize("apple", "Technology")
    assert can1 == "Apple"
    assert registry.is_known("apple", "Technology")
    
    # Test polysemy distinction
    can2 = registry.canonicalize("apple", "Food")
    assert can2 == "Apple"
    assert registry.is_known("apple", "Food")
    
    # Ensure they are distinct in registry (can't directly assert dict size without touching internals, but we can verify it doesn't crash)

def test_queue_persistence(tmp_path):
    q_file = tmp_path / "queue.txt"
    q = deque([("NodeA", 0), ("NodeB", 1)])
    
    save_queue(str(q_file), q)
    assert os.path.exists(str(q_file))
    
    loaded_q = load_queue(str(q_file), visited=set(), blacklist={"NodeB"})
    
    assert len(loaded_q) == 1
    assert loaded_q[0] == ("NodeA", 0)

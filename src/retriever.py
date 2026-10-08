import os
import re
import pickle
import numpy as np
import networkx as nx
from pathlib import Path
from collections import defaultdict
import math
from sentence_transformers import SentenceTransformer, CrossEncoder
from src.config import *
from src.utils import *

GATE_FAILURE_COUNTER = __import__('collections').Counter()

def normalize_kb(kb_path: str):
    log("Scanning KB for casing conflicts ...")
    pattern = re.compile(r"\(([^,]+),\s*([^,]+),\s*([^)]+)\)")
    node_groups = defaultdict(list)
    with open(kb_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        m = pattern.search(line.strip())
        if m:
            for node in (m.group(1).strip(), m.group(3).strip()):
                key = node.lower().rstrip("s")
                if node not in node_groups[key]:
                    node_groups[key].append(node)

    CANON = {}
    conflict_count = 0
    unresolvable = []
    for key, variants in node_groups.items():
        if len(variants) > 1 and len({v.lower() for v in variants}) == 1:
            conflict_count += 1
            best = max(variants, key=_casing_quality_score)
            if _casing_quality_score(best) < 0:
                unresolvable.append(key)
            for v in variants:
                if v != best:
                    CANON[v] = best

    log(f"  Found {conflict_count} conflicts -> fixing {len(CANON)} variants ...")
    if unresolvable:
        log(f"  WARNING: {len(unresolvable)} conflict groups have no clean variant.")

    if CANON:
        fixed = []
        for line in lines:
            for old, new in CANON.items():
                if old in line:
                    line = line.replace(old, new)
            fixed.append(line)
        with open(kb_path, "w", encoding="utf-8") as f:
            f.writelines(fixed)
    log(f"KB normalized (checked {len(lines)} lines)")


# ──────────────────────────────────────────────
# GRAPH + EMBEDDINGS (unchanged retrieval-side logic from v5.0)
# ──────────────────────────────────────────────
def load_knowledge_graph(kb_path: str, graphml_path: str) -> nx.DiGraph:
    if Path(graphml_path).exists():
        if os.path.getmtime(kb_path) > os.path.getmtime(graphml_path):
            log("KB newer than graphml cache. Rebuilding ...")
            os.remove(graphml_path)
        else:
            log(f"Loading graph from {graphml_path} ...")
            G = nx.read_graphml(graphml_path)
            log(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
            return G
    log(f"Parsing KB from {kb_path} ...")
    G = nx.DiGraph()
    pattern = re.compile(r"\(([^,]+),\s*([^,]+),\s*([^)]+)\)")
    with open(kb_path, "r", encoding="utf-8") as f:
        for line in f:
            m = pattern.search(line.strip())
            if m:
                s, r, o = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
                G.add_node(s); G.add_node(o)
                G.add_edge(s, o, relation=r)
    log(f"Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    nx.write_graphml(G, graphml_path)
    return G


def camel_split(s: str) -> str:
    s = re.sub(r'(?<=[a-z])([A-Z])', r' \1', s)
    s = re.sub(r'(?<=[A-Z])([A-Z])(?=[a-z])', r' \1', s)
    return re.sub(r'\s+', ' ', s).strip()


def build_triple_texts(G: nx.DiGraph):
    texts, triples = [], []
    placeholders = {"location", "person", "date", "time", "organization", "object",
                     "city", "country", "name", "year", "number", "event", "company"}
    for u, v, data in G.edges(data=True):
        if u.strip().lower() in placeholders or v.strip().lower() in placeholders:
            continue
        rel = data.get("relation", "relatedTo")
        texts.append(f"{camel_split(u)} {camel_split(rel)} {camel_split(v)}")
        triples.append((u, rel, v))
    return texts, triples


def load_or_build_embeddings(G, embed_model, cache_path, kb_path):
    if Path(cache_path).exists():
        if os.path.getmtime(kb_path) > os.path.getmtime(cache_path):
            log("KB newer than embeddings cache. Rebuilding ...")
            os.remove(cache_path)
        else:
            log("Loading triple embeddings from cache ...")
            with open(cache_path, "rb") as f:
                data = pickle.load(f)
            if "texts" not in data:
                data["texts"] = [f"{camel_split(u)} {camel_split(r)} {camel_split(v)}"
                                  for u, r, v in data["triples"]]
                with open(cache_path, "wb") as f:
                    pickle.dump(data, f)
            log(f"  {len(data['triples'])} triples loaded")
            return data["embeddings"], data["triples"], data["texts"]

    log("Building triple embeddings (first run ~30-60s) ...")
    texts, triples = build_triple_texts(G)
    embeddings = embed_model.encode(texts, batch_size=512, show_progress_bar=True,
                                     convert_to_numpy=True, normalize_embeddings=True)
    with open(cache_path, "wb") as f:
        pickle.dump({"embeddings": embeddings, "triples": triples, "texts": texts}, f)
    log(f"  Embedded {len(triples)} triples -> saved to {cache_path}")
    return embeddings, triples, texts


# ──────────────────────────────────────────────
# HYBRID RETRIEVAL (unchanged from v5.0 — hub-discount + co-occurrence bonus
# you already designed are kept, since the bug was downstream of this)
# ──────────────────────────────────────────────
STOPWORDS = {
    "what", "how", "does", "is", "the", "a", "an", "and", "or", "in", "of",
    "to", "for", "with", "are", "from", "do", "have", "has", "be", "it", "its",
    "this", "that", "which", "why", "where", "when", "who", "between", "related",
    "did", "was", "were", "by", "at", "on", "as", "up", "if", "so", "but",
}

GENERIC_RELATIONS = frozenset([
    "relatedto", "involves", "isrelatedto", "associatedwith",
    "isassociatedwith", "istypeof", "ispartof", "isa", "partof",
])


def content_tokens(text: str) -> set:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower())
            if t not in STOPWORDS and len(t) > 2}


def lexical_match_score(query_tokens, u, rel, v, G=None):
    subj_tokens = content_tokens(camel_split(u))
    rel_tokens = content_tokens(camel_split(rel))
    obj_tokens = content_tokens(camel_split(v))
    triple_tokens = subj_tokens | rel_tokens | obj_tokens

    entity_overlap = query_tokens & (subj_tokens | obj_tokens)
    relation_overlap = query_tokens & rel_tokens
    exact_overlap = query_tokens & triple_tokens

    co_occurrence_bonus = 0.0
    if entity_overlap and relation_overlap:
        co_occurrence_bonus = 0.5 if rel.replace(" ", "").lower() in GENERIC_RELATIONS else 3.0

    hub_discount = 0.0
    if G is not None:
        u_deg = G.degree(u) if G.has_node(u) else 1
        v_deg = G.degree(v) if G.has_node(v) else 1
        if (query_tokens & subj_tokens) and u_deg > 5:
            hub_discount += math.log10(u_deg) * 0.75
        if (query_tokens & obj_tokens) and v_deg > 5:
            hub_discount += math.log10(v_deg) * 0.75

    score = (1.25 * len(entity_overlap) + 0.90 * len(relation_overlap)
             + 0.35 * len(exact_overlap) + co_occurrence_bonus - hub_discount)
    return max(0.0, score), len(entity_overlap)


def keyword_score(query: str, texts: list) -> np.ndarray:
    q_tokens = content_tokens(camel_split(query))
    if not q_tokens:
        return np.zeros(len(texts))
    scores = np.zeros(len(texts))
    for i, text in enumerate(texts):
        scores[i] = len(q_tokens & content_tokens(text)) / (len(q_tokens) + 1e-9)
    return scores


def load_reranker():
    try:
        log(f"Loading reranker ({CROSS_ENCODER_MODEL}) ...")
        reranker = CrossEncoder(CROSS_ENCODER_MODEL)
        reranker.model.eval()
        log("Reranker loaded")
        return reranker
    except Exception as exc:
        log(f"Reranker unavailable ({exc}); falling back to embedding-only retrieval.")
        return None


def mmr_rerank(candidate_embs, candidate_indices, rel_scores, k, lambda_):
    selected, remaining = [], list(range(len(candidate_indices)))
    while len(selected) < k and remaining:
        if not selected:
            best = remaining[int(np.argmax([rel_scores[i] for i in remaining]))]
        else:
            sel_embs = candidate_embs[selected]
            mmr_scores = []
            for i in remaining:
                relevance = lambda_ * rel_scores[i]
                redundancy = (1 - lambda_) * float((candidate_embs[i] @ sel_embs.T).max())
                mmr_scores.append(relevance - redundancy)
            best = remaining[int(np.argmax(mmr_scores))]
        selected.append(best)
        remaining.remove(best)
    return [candidate_indices[i] for i in selected]


def is_meaningful_line(line: str) -> bool:
    return len([w for w in line.split() if len(w) > 1]) >= MIN_WORDS_PER_LINE


def triples_to_sentences(triples_list) -> str:
    return "\n".join(f"{camel_split(u)} {camel_split(rel).lower()} {camel_split(v)}."
                      for u, rel, v in triples_list)


def calculate_graph_rag_boost(G, query_tokens, u, v):
    if G is None or not query_tokens:
        return 0.0
    if not hasattr(G, "_node_lowercase_map"):
        G._node_lowercase_map = {n.lower(): n for n in G.nodes()}
    query_nodes = {G._node_lowercase_map[t] for t in query_tokens if t in G._node_lowercase_map}
    if not query_nodes:
        return 0.0
    if u in query_nodes and v in query_nodes:
        return 1.50
    boost = 0.0
    for qn in query_nodes:
        qn_deg = G.degree(qn) if G.has_node(qn) else 1
        neighbor_boost = 0.5 if qn_deg <= 5 else max(0.0, 0.5 - math.log10(qn_deg) * 0.25)
        if u in G:
            if u == qn:
                boost = max(boost, 1.0)
            elif G.has_edge(qn, u) or G.has_edge(u, qn):
                boost = max(boost, neighbor_boost)
        if v in G:
            if v == qn:
                boost = max(boost, 1.0)
            elif G.has_edge(qn, v) or G.has_edge(v, qn):
                boost = max(boost, neighbor_boost)
    return boost


def retrieve_context(query, embed_model, reranker, triple_embeddings, all_triples,
                      triple_texts, mmr_k, G=None):
    """Returns (context, n_used, avg_sim, reason, gate_scores).
    reason: 'ok' | 'no_candidates' | 'quality_gate'
    On 'quality_gate' or 'no_candidates', context is '' — caller MUST treat
    this identically to a raw prompt. That's the floor guarantee.
    """
    query_tokens = content_tokens(camel_split(query))
    if not query_tokens:
        return "", 0, 0.0, "no_candidates", {}

    q_emb = embed_model.encode(query, convert_to_numpy=True, normalize_embeddings=True)
    sem_scores = triple_embeddings @ q_emb
    kw_scores = keyword_score(query, triple_texts)

    lexical_scores = np.zeros(len(all_triples), dtype=np.float32)
    lexical_anchor = np.zeros(len(all_triples), dtype=np.float32)
    for i, (u, rel, v) in enumerate(all_triples):
        score, entity_hits = lexical_match_score(query_tokens, u, rel, v, G=G)
        lexical_scores[i] = score
        lexical_anchor[i] = entity_hits

    hybrid = 0.55 * sem_scores + 0.25 * kw_scores + 0.20 * lexical_scores
    if G is not None:
        graph_boosts = np.array([calculate_graph_rag_boost(G, query_tokens, u, v)
                                  for u, rel, v in all_triples], dtype=np.float32)
        hybrid += 0.30 * graph_boosts
    for i, (_, rel, _) in enumerate(all_triples):
        if rel.replace(" ", "").lower() in GENERIC_RELATIONS:
            hybrid[i] -= GENERIC_PENALTY

    sorted_idx = np.argsort(hybrid)[::-1]
    candidates = sorted_idx[:TOP_K].tolist()
    if not candidates:
        return "", 0, 0.0, "no_candidates", {}

    k_actual = min(mmr_k, len(candidates))
    if reranker is not None:
        cand_texts = [triple_texts[i] for i in candidates]
        pair_scores = np.asarray(reranker.predict([(query, t) for t in cand_texts],
                                                    show_progress_bar=False), dtype=np.float32)
        cand_embs = triple_embeddings[candidates]
        final_idx = mmr_rerank(cand_embs, candidates, pair_scores, k=k_actual, lambda_=MMR_LAMBDA)
        best_rerank = float(np.max(pair_scores))
    else:
        cand_embs = triple_embeddings[candidates]
        rel_scores = cand_embs @ q_emb
        final_idx = mmr_rerank(cand_embs, candidates, rel_scores, k=k_actual, lambda_=MMR_LAMBDA)
        best_rerank = 0.0

    selected_triples = [all_triples[i] for i in final_idx]
    selected_embs = triple_embeddings[final_idx]
    avg_sim = float(np.mean(selected_embs @ q_emb)) if len(selected_embs) else 0.0
    selected_lex = lexical_scores[final_idx]
    best_lex = float(np.max(selected_lex)) if len(selected_lex) else 0.0
    max_entity_hits = int(np.max(lexical_anchor[final_idx])) if len(final_idx) else 0

    context = triples_to_sentences(selected_triples)
    meaningful = sum(1 for line in context.splitlines() if is_meaningful_line(line))
    structure_score = min(1.0, 0.5 + (meaningful - 1) * 0.25) if meaningful > 0 else 0.0

    norm_semantic = max(0.0, min(1.0, avg_sim / 0.8))
    norm_lexical = max(0.0, min(1.0, best_lex / 4.0))
    norm_rerank = max(0.0, min(1.0, (best_rerank + 5) / 15.0)) if reranker is not None else norm_semantic

    confidence = (norm_semantic * GATE_WEIGHTS["semantic"] + norm_rerank * GATE_WEIGHTS["rerank"]
                  + norm_lexical * GATE_WEIGHTS["lexical"] + structure_score * GATE_WEIGHTS["structure"])

    # Extra hard rule (new in v6): even if weighted confidence clears, a triple
    # that shares ZERO entity tokens with the question can't be trusted — it's
    # topically adjacent, not on-target (this is exactly the Islamabad/
    # Afghanistan failure mode: capital-city triples, zero entity anchor).
    if max_entity_hits == 0:
        confidence = min(confidence, GATE_CONFIDENCE_THRESHOLD - 0.01)

    gate_scores = {"avg_sim": round(avg_sim, 3), "best_lex": round(best_lex, 3),
                   "best_rerank": round(best_rerank, 3), "confidence": round(confidence, 3),
                   "max_entity_hits": max_entity_hits}

    log(f"  [GATE] '{query[:45]}' | Conf:{confidence:.3f} Sem:{norm_semantic:.2f} "
        f"Rnk:{norm_rerank:.2f} Lex:{norm_lexical:.2f} Struct:{structure_score:.2f} "
        f"EntHits:{max_entity_hits}")

    if confidence < GATE_CONFIDENCE_THRESHOLD:
        GATE_FAILURE_COUNTER["confidence_too_low"] += 1
        log(f"  [GATE_REJECT] confidence {confidence:.2f} < {GATE_CONFIDENCE_THRESHOLD} -> "
            f"falls back to RAW prompt for this question")
        return "", 0, avg_sim, "quality_gate", gate_scores

    return context, len(selected_triples), avg_sim, "ok", gate_scores


# ──────────────────────────────────────────────
# MODEL LOADING
# ──────────────────────────────────────────────

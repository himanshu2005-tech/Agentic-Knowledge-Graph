"""Validation and Filtering Logic."""

import re
import logging

logger = logging.getLogger(__name__)

CANONICAL_RELATIONS = {
    "is": "is", "has": "has", "isa": "isA", "ispartof": "isPartOf", 
    "haspart": "hasPart", "istypeof": "isTypeOf", "iskindof": "isKindOf",
    "issubclassof": "isSubclassOf", "isrelatedto": "isRelatedTo",
    "belongsto": "belongsTo", "consistsof": "consistsOf",
    "comprisesof": "comprisesOf", "composedof": "composedOf",
    "contains": "contains", "produces": "produces", "causes": "causes", 
    "enables": "enables", "requires": "requires", "includes": "includes", 
    "generates": "generates", "performs": "performs", "stores": "stores", 
    "converts": "converts", "transmits": "transmits", "regulates": "regulates", 
    "encodes": "encodes", "consumes": "consumes", "activates": "activates",
    "connects": "connects", "controls": "controls", "defines": "defines", 
    "determines": "determines", "follows": "follows", "governs": "governs", 
    "impacts": "impacts", "involves": "involves", "leads": "leads", 
    "maintains": "maintains", "models": "models", "modifies": "modifies", 
    "orbits": "orbits", "processes": "processes", "reduces": "reduces",
    "releases": "releases", "responds": "responds", "transforms": "transforms", 
    "triggers": "triggers", "studies": "studies", "surrounds": "surrounds", 
    "hosts": "hosts", "extends": "extends", "applies": "applies", 
    "represents": "represents", "classifies": "classifies", "rotates": "rotates", 
    "revolves": "revolves", "affects": "affects", "creates": "creates",
    "builds": "builds", "allows": "allows", "makes": "makes", "carries": "carries", 
    "drives": "drives", "powers": "powers", "shapes": "shapes", "supports": "supports", 
    "inhibits": "inhibits", "binds": "binds", "synthesizes": "synthesizes",
    "breaks": "breaks", "measures": "measures", "monitors": "monitors", 
    "flows": "flows", "depends": "depends", "derives": "derives", "forms": "forms", 
    "interacts": "interacts", "absorbs": "absorbs", "emits": "emits",
    "reflects": "reflects", "attracts": "attracts", "exhibits": "exhibits", 
    "limits": "limits", "operates": "operates", "selects": "selects", 
    "serves": "serves", "solves": "solves", "underlies": "underlies", 
    "validates": "validates", "heats": "heats", "cools": "cools", "grows": "grows",
    "influences": "influences", "inspired": "inspired", "inspires": "inspires", 
    "invented": "invented", "invents": "invents", "discovered": "discovered", 
    "discovers": "discovers", "founded": "founded", "originates": "originates", 
    "originated": "originated", "developed": "developed", "develops": "develops", 
    "evolved": "evolved", "evolves": "evolves", "wrote": "wrote", "writes": "writes",
    "composed": "composed", "composedfor": "composedFor", "composes": "composes",
    "directs": "directs", "directed": "directed", "painted": "painted", 
    "performed": "performed", "played": "played", "plays": "plays", "won": "won", 
    "wins": "wins", "defeated": "defeated", "defeats": "defeats",
    "ruled": "ruled", "rules": "rules", "fought": "fought", "trades": "trades", 
    "traded": "traded", "migrated": "migrated", "colonized": "colonized", 
    "opposed": "opposed", "replaced": "replaced", "preceded": "preceded", 
    "precedes": "precedes", "succeeded": "succeeded", "succeeds": "succeeds", 
    "symbolizes": "symbolizes", "celebrates": "celebrates", "practiced": "practiced",
    "believes": "believes", "worships": "worships", "narrates": "narrates", 
    "portrays": "portrays", "criticizes": "criticizes", "analyzes": "analyzes", 
    "interprets": "interprets", "translates": "translates", "categorizes": "categorizes", 
    "ranks": "ranks", "trains": "trains", "teaches": "teaches", "learns": "learns", 
    "publishes": "publishes", "broadcasts": "broadcasts", "records": "records", 
    "exports": "exports", "imports": "imports", "invades": "invades", 
    "defends": "defends", "negotiates": "negotiates", "elects": "elects", 
    "enforces": "enforces", "prohibits": "prohibits", "permits": "permits", 
    "funds": "funds", "employs": "employs", "manages": "manages", "owns": "owns", 
    "sells": "sells", "buys": "buys", "invests": "invests", "competes": "competes", 
    "cooperates": "cooperates", "merges": "merges", "acquires": "acquires",
    "prevented": "prevented", "destroyed": "destroyed", "protected": "protected",
    "declared": "declared", "established": "established", "abolished": "abolished",
    "reformed": "reformed", "unified": "unified",
}

RELATION_PREFIXES = frozenset(CANONICAL_RELATIONS.keys())

_BAD_SUBSTRINGS = [
    'ofthe', 'onthe', 'anda', 'orthe', 'withthe', 'inthe', 'atthe',
    'bythe', 'forthe', 'fromthe', 'tothe', 'andthe', 'ofan', 'ofa',
    'approximately', 'however', 'therefore', 'although', 'because',
    'various', 'several', 'multiple', 'different', 'certain',
    'example', 'following', 'canbe', 'maybe', 'willbe'
]

def normalize_node(n: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_]', '', n)

def is_valid_node(raw: str) -> bool:
    if len(raw) < 2 or len(raw) > 30:
        return False
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', raw):
        return False
    low = raw.lower()
    for bad in _BAD_SUBSTRINGS:
        if bad in low:
            return False
    # Avoid fully uppercase acronyms longer than 5 chars
    if raw.isupper() and len(raw) > 5:
        return False
    return True

def is_valid_relation(raw: str) -> bool:
    if len(raw) < 2 or len(raw) > 20:
        return False
    return raw.lower() in CANONICAL_RELATIONS

_PLACEHOLDER_NAMES = frozenset({
    "johndoe", "janedoe", "directorname", "authorname", "ceoname",
    "personname", "artistname", "actorname", "singername", "writername",
    "countryb", "countrya", "languagea", "languageb", "citya", "cityb",
    "companyname", "brandname", "productname", "teamname",
})

_PLACEHOLDER_BASES = frozenset({
    "author", "book", "episode", "role", "director", "artist",
    "song", "movie", "person", "country", "language", "style",
    "city", "company", "character", "player", "singer", "actor",
    "writer", "film", "show", "track", "album", "band",
    "soundtrack", "rocker", "jazzartist",
})

_GENERIC_AS_VALUE = frozenset({
    "director", "episode", "movie", "song", "book", "film",
    "show", "author", "artist", "singer", "opera", "play",
    "poem", "novel", "story", "music", "album",
})

_SPECIFIC_VALUE_RELATIONS = frozenset({
    "wrote", "wrotebook", "wrotework", "directed", "directedby",
    "composed", "composedby", "composedsong", "composedwork",
    "composedmusic", "painted", "invented", "discovered",
    "founded", "foundedby",
})

def is_placeholder_name(node: str, relation: str = "", is_object: bool = False) -> tuple[bool, str]:
    l = node.lower()
    if l in _PLACEHOLDER_NAMES:
        return True, "placeholder"
    
    for base in _PLACEHOLDER_BASES:
        if l == base or l == f"some{base}" or l == f"a{base}":
            return True, "placeholder"

    if is_object and relation.lower() in _SPECIFIC_VALUE_RELATIONS:
        if l in _GENERIC_AS_VALUE:
            return True, "generic_value"
            
    return False, ""

_FUNCTIONAL_SUBJ_RELS = frozenset({
    "capitalcity", "iscapitalof", "bornin", "diedin", 
    "foundedby", "inventedby", "discoveredby"
})

_FUNCTIONAL_OBJ_RELS = frozenset({
    "capital", "spouse", "mother", "father"
})

def build_functional_index(triplet_counts: dict) -> tuple[dict, dict]:
    subj_idx = {}
    obj_idx = {}
    for triplet in triplet_counts:
        parts = triplet.split(",")
        if len(parts) == 3:
            s, r, o = parts
            r_lower = r.lower()
            if r_lower in _FUNCTIONAL_SUBJ_RELS:
                if s not in subj_idx: subj_idx[s] = {}
                if r_lower not in subj_idx[s]: subj_idx[s][r_lower] = set()
                subj_idx[s][r_lower].add(o)
                
            if r_lower in _FUNCTIONAL_OBJ_RELS:
                if o not in obj_idx: obj_idx[o] = {}
                if r_lower not in obj_idx[o]: obj_idx[o][r_lower] = set()
                obj_idx[o][r_lower].add(s)
    return subj_idx, obj_idx

def update_functional_index(s: str, r: str, o: str, subj_idx: dict, obj_idx: dict):
    r_lower = r.lower()
    if r_lower in _FUNCTIONAL_SUBJ_RELS:
        if s not in subj_idx: subj_idx[s] = {}
        if r_lower not in subj_idx[s]: subj_idx[s][r_lower] = set()
        subj_idx[s][r_lower].add(o)
        
    if r_lower in _FUNCTIONAL_OBJ_RELS:
        if o not in obj_idx: obj_idx[o] = {}
        if r_lower not in obj_idx[o]: obj_idx[o][r_lower] = set()
        obj_idx[o][r_lower].add(s)

def check_functional_conflict(s, r, o, subj_idx, obj_idx) -> tuple[bool, str]:
    r_lower = r.lower()
    
    # 1:1 or N:1 functional constraints
    if r_lower in _FUNCTIONAL_SUBJ_RELS:
        if s in subj_idx and r_lower in subj_idx[s]:
            existing = subj_idx[s][r_lower]
            if o not in existing and len(existing) > 0:
                return True, f"Functional Conflict: {s} already has {r} {list(existing)[0]}"
                
    if r_lower in _FUNCTIONAL_OBJ_RELS:
        if o in obj_idx and r_lower in obj_idx[o]:
            existing = obj_idx[o][r_lower]
            if s not in existing and len(existing) > 0:
                return True, f"Functional Conflict: {o} already is {r} of {list(existing)[0]}"

    return False, ""

"""Wikidata Verification Logic."""

import urllib.request
import urllib.parse
import json
import logging
import os
import re
import time
logger = logging.getLogger(__name__)

def _camel_to_label(s: str) -> str:
    """Convert CamelCase to space-separated label for Wikidata lookup."""
    result = re.sub(r'([a-z])([A-Z])', r'\1 \2', s)
    result = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', result)
    return result.strip()

def _load_wikidata_cache() -> dict:
    if not os.path.exists(WIKIDATA_CACHE_FILE):
        return {}
    try:
        with open(WIKIDATA_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_wikidata_cache(cache: dict):
    tmp = WIKIDATA_CACHE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)
    os.replace(tmp, WIKIDATA_CACHE_FILE)

def _sparql_query(sparql: str) -> list | None:
    """Execute a SPARQL query against Wikidata. Returns list of result bindings, or None on error."""
    url = WIKIDATA_ENDPOINT + "?" + urllib.parse.urlencode({
        "query": sparql,
        "format": "json",
    })
    req = urllib.request.Request(url, headers={
        "User-Agent": "KGBuilder/1.0 (himanshu.madhunala1@gmail.com)",
        "Accept": "application/sparql-results+json",
    })
    for attempt in range(3):
        try:
            time.sleep(1.0)  # Speed limit to avoid Wikidata 429 rate limit
            with urllib.request.urlopen(req, timeout=WIKIDATA_TIMEOUT) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("results", {}).get("bindings", [])
        except Exception as e:
            code = getattr(e, 'code', None)
            if code in (429, 502, 503, 504):
                wait_time = 60
                logger.info(f"  [WIKIDATA] HTTP Error {code}. Waiting {wait_time}s... (Attempt {attempt+1}/3)")
                time.sleep(wait_time)
            else:
                logger.info(f"  [WIKIDATA] Query failed: {type(e).__name__}: {e}")
                return None
    logger.info("  [WIKIDATA] Max retries reached. Failing query.")
    return None

def _wikidata_lookup(entity_label: str, property_id: str, cache: dict) -> list | None:
    """Look up property values for an entity in Wikidata. Returns value labels or None."""
    cache_key = f"{property_id}|{entity_label.lower()}"
    if cache_key in cache:
        return cache[cache_key]

    safe_label = entity_label.replace('"', '\\"')
    sparql = (
        'SELECT ?valueLabel WHERE { '
        f'?entity rdfs:label "{safe_label}"@en . '
        f'?entity wdt:{property_id} ?value . '
        'SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . } '
        '} LIMIT 10'
    )
    bindings = _sparql_query(sparql)
    if bindings is None:
        # Error occurred, do not cache the failure
        return None
    if not bindings:
        cache[cache_key] = None
        return None

    values = [b["valueLabel"]["value"] for b in bindings if "valueLabel" in b]
    cache[cache_key] = values if values else None
    return cache[cache_key]

def _fuzzy_label_match(claimed: str, verified: str) -> bool:
    """Check if a claimed label loosely matches a verified Wikidata label."""
    c = claimed.lower().strip()
    v = verified.lower().strip()
    if c == v:
        return True
    if len(c) >= 4 and (c in v or v in c):
        return True
    # Remove common geographical suffixes and retry
    for suf in ("city", "state", "island", "islands", "republic", "kingdom"):
        cs = c.replace(suf, "").strip()
        vs = v.replace(suf, "").strip()
        if cs and vs and cs == vs:
            return True
    return False

def wikidata_verify_triple(s: str, r: str, o: str, cache: dict) -> tuple[str, str]:
    """Verify a triple against Wikidata (DISABLED FOR SPEED)."""
    return ("UNKNOWN", "Verification disabled to prevent HTTP 429 rate limits")


# ══════════════════════════════════════════════════════════════════════
#  PLACEHOLDER / GENERIC-NAME FILTER
# ══════════════════════════════════════════════════════════════════════
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


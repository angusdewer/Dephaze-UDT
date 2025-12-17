# ============================================================
# DEPHAZE UDT — REAL WIKI PROVIDER
# EXTERNAL EVIDENCE SOURCE — SAFE MODE BOUNDARY
# ============================================================
# Role:
#   Deterministic, alias-seeded multi-fetcher for Wikipedia.
#
# Purpose:
#   - Provide external textual evidence
#   - Expand ontological ambiguity into parallel branches
#   - Feed Gödel structural extraction (NOT semantics)
#
# This is NOT:
#   - a knowledge base
#   - a scraper
#   - a popularity search
#   - an AI model
#
# This IS:
#   - an explicit, external evidence provider
#   - ontology-aware alias expansion
#   - deterministic control flow
#
# SAFE MODE BOUNDARY:
#   - This module touches the external world
#   - Dephaze CORE remains fully SAFE MODE
#   - All effects are explicit and auditable
# ============================================================

import requests


# ------------------------------------------------------------
# Wikipedia API configuration
# ------------------------------------------------------------

WIKI_API = "https://en.wikipedia.org/w/api.php"

HEADERS = {
    # REQUIRED by Wikipedia API policy
    "User-Agent": "DephazeUDT/1.1 (contact: dewerangus@gmail.com)"
}


# ------------------------------------------------------------
# Alias expansion (ONTOLOGICAL, NOT SEARCH)
# ------------------------------------------------------------

def expand_aliases(query: str):
    """
    Deterministic structural alias expansion.

    Purpose:
      - Open parallel ontology branches
      - NOT popularity or relevance optimization
    """
    aliases = []
    q = query.strip().lower()

    # original query
    aliases.append(q)

    # slash-based ambiguity (AC/DC, input/output, etc.)
    if "/" in q:
        parts = [p.strip() for p in q.split("/") if p.strip()]
        if len(parts) == 2:
            a, b = parts
            aliases.append(f"{a} {b}")
            aliases.append(f"{a} and {b}")

            # known structural physics pattern
            if a == "ac" and b == "dc":
                aliases.append("alternating current")
                aliases.append("direct current")
                aliases.append("alternating current direct current")

    # uppercase acronym heuristic (handled safely)
    if q.isupper() or q.replace("/", "").isupper():
        aliases.append(q.lower())

    # deduplicate while preserving order
    seen = set()
    out = []
    for a in aliases:
        if a not in seen:
            seen.add(a)
            out.append(a)

    return out


# ------------------------------------------------------------
# RealWiki provider
# ------------------------------------------------------------

class RealWiki:
    """
    Explicit Wikipedia evidence provider.

    NOT cached.
    NOT ranked.
    NOT learned.
    """

    def __init__(self, lang="en", max_results=3):
        self.lang = lang
        self.max_results = max_results

    # --------------------------------------------------
    # Search titles (multiple, not best-hit)
    # --------------------------------------------------

    def search_all(self, query: str):
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": self.max_results,
            "format": "json",
        }
        r = requests.get(
            WIKI_API,
            params=params,
            headers=HEADERS,
            timeout=5,
        )
        r.raise_for_status()
        data = r.json()
        return [item["title"] for item in data.get("query", {}).get("search", [])]

    # --------------------------------------------------
    # Fetch extract (intro only)
    # --------------------------------------------------

    def fetch_extract(self, title: str):
        params = {
            "action": "query",
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "titles": title,
            "format": "json",
        }
        r = requests.get(
            WIKI_API,
            params=params,
            headers=HEADERS,
            timeout=5,
        )
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
        for page in pages.values():
            return page.get("extract", "")
        return ""

    # --------------------------------------------------
    # Alias-seeded multi fetch
    # --------------------------------------------------

    def search_and_fetch_all(self, query: str):
        """
        Expand aliases → fetch multiple candidate pages.

        Returns:
          List of dicts with:
            - title
            - extract
            - alias_source
        """
        results = []
        seen_titles = set()

        for alias in expand_aliases(query):
            try:
                titles = self.search_all(alias)
            except Exception:
                continue

            for title in titles:
                if title in seen_titles:
                    continue

                extract = self.fetch_extract(title)
                if not extract:
                    continue

                seen_titles.add(title)
                results.append(
                    {
                        "title": title,
                        "extract": extract,
                        "alias_source": alias,
                    }
                )

        return results

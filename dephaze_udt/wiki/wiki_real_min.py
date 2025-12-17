# ============================================================
# DEPHAZE UDT — REAL WIKI PROVIDER (MINIMAL)
# LEGACY / FALLBACK IMPLEMENTATION
# ============================================================
# Role:
#   Minimal, deterministic Wikipedia fetcher.
#
# Purpose:
#   - Lightweight external evidence lookup
#   - Mobile / demo / offline-adjacent usage
#
# This is NOT:
#   - ontology expansion
#   - alias-based branching
#   - multi-source evidence
#   - governance-controlled ingestion
#
# This IS:
#   - a minimal, single-hit evidence fetcher
#   - deterministic control flow
#   - explicit external boundary
#
# NOTE:
#   For full ontology-safe ingestion, use:
#     wiki/wiki_real.py
# ============================================================

import requests


class RealWiki:
    """
    Minimal Wikipedia provider (single-hit).
    """

    def __init__(self, lang="en", timeout=5.0):
        self.lang = lang
        self.timeout = timeout

    def search_and_fetch(self, query: str):
        """
        Search Wikipedia and fetch intro extract of top result.

        Returns:
          (title, extract) or (None, None)
        """
        url = f"https://{self.lang}.wikipedia.org/w/api.php"

        # --- search ---
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
        }
        r = requests.get(url, params=params, timeout=self.timeout)
        data = r.json()
        hits = data.get("query", {}).get("search", [])
        if not hits:
            return None, None

        title = hits[0]["title"]

        # --- extract ---
        params = {
            "action": "query",
            "prop": "extracts",
            "titles": title,
            "exintro": True,
            "explaintext": True,
            "format": "json",
        }
        r = requests.get(url, params=params, timeout=self.timeout)
        pages = r.json().get("query", {}).get("pages", {})
        page = next(iter(pages.values()), {})
        extract = page.get("extract")

        return title, extract

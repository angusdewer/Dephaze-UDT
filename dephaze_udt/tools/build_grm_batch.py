# ============================================================
# DEPHAZE TOOLS — GRM BATCH BUILDER (OFFLINE)
# ============================================================
# Role:
#   Offline utility for building a GRM snapshot from
#   external, explicit data sources (e.g. Wikipedia).
#
# IMPORTANT:
#   - This is NOT part of Dephaze UDT runtime
#   - This script is executed manually
#   - Output is a frozen GRM snapshot (JSON)
#
# This is NOT:
#   - training
#   - learning
#   - background ingestion
#   - an automated crawler
#
# This IS:
#   - an explicit, auditable world snapshot builder
#
# SAFE MODE:
#   - Dephaze core remains SAFE MODE compliant
#   - External data usage is fully explicit here
# ============================================================

import dephaze
from grm_merge import GRMMerger
from grm_normalize import normalize_grm
from grm_persistence import save_grm
import requests


# ============================================================
# Explicit external provider
# ============================================================

class RealWiki:
    """
    Explicit Wikipedia provider.

    Used ONLY in offline tooling.
    """
    HEADERS = {
        "User-Agent": "DephazeUDT/1.0 (contact: dewerangus@gmail.com)"
    }

    def __init__(self, lang="en", timeout=5.0):
        self.lang = lang
        self.timeout = timeout

    def search_and_fetch(self, query: str):
        try:
            api = f"https://{self.lang}.wikipedia.org/w/api.php"

            r = requests.get(
                api,
                headers=self.HEADERS,
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "format": "json",
                },
                timeout=self.timeout,
            )
            hits = r.json().get("query", {}).get("search", [])
            if not hits:
                return None, None

            title = hits[0]["title"]

            r = requests.get(
                api,
                headers=self.HEADERS,
                params={
                    "action": "query",
                    "prop": "extracts",
                    "titles": title,
                    "exintro": True,
                    "explaintext": True,
                    "format": "json",
                },
                timeout=self.timeout,
            )
            pages = r.json().get("query", {}).get("pages", {})
            extract = next(iter(pages.values()), {}).get("extract")

            return title, extract

        except Exception:
            return None, None


# ============================================================
# Domain seed (EXPLICIT)
# ============================================================

PROMPTS = [
    "cat", "dog", "mouse", "lion", "tiger",
    "horse", "cow", "sheep", "wolf", "fox",
]


# ============================================================
# Build process
# ============================================================

udt = dephaze.DephazeUDT(wiki=RealWiki())
merger = GRMMerger()

for p in PROMPTS:
    print("Processing:", p)
    bundle = udt.forward(p, use_wiki=True)

    if not bundle.wiki_title:
        print("  ⚠ skipped (no wiki)")
        continue

    canonical_id = f"wiki:{bundle.wiki_title}"

    merger.get_or_create(
        canonical_id=canonical_id,
        label=bundle.wiki_title,
        source="wikipedia",
    )

    for m in bundle.godel.mentions:
        merger.get_or_create(
            canonical_id=canonical_id,
            label=bundle.wiki_title,
            alias=m,
            source="mention",
        )


# ============================================================
# Normalize and persist
# ============================================================

normalize_grm(merger.nodes)
save_grm(merger.nodes, "grm_animals_v1.json")

print("\nSaved GRM snapshot: grm_animals_v1.json")
print("Total nodes:", len(merger.nodes))

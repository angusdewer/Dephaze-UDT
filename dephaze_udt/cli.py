# ============================================================
# DEPHAZE UDT — FINAL CLI (HEADLESS ENTRY POINT)
# SAFE MODE — DETERMINISTIC — NO LLM
# ============================================================
# Role:
#   Canonical command-line interface for Dephaze UDT.
#
# Purpose:
#   - Deterministic structural analysis from shell / CI
#   - Scriptable, reproducible execution
#   - Noise-safe, governance-controlled Wiki usage
#
# This is NOT:
#   - an AI model
#   - an LLM wrapper
#   - a crawler
#   - a server
#
# This IS:
#   - a headless structural analyzer
#   - ontology-first, phase-space driven
#   - SAFE MODE compliant
#
# Invariants (SAFE MODE):
#   - No learning
#   - No background processes
#   - Explicit external boundary (Wiki)
# ============================================================

from __future__ import annotations
import argparse
import json
import requests
import re
from typing import Optional, Tuple

from core.dephaze import DephazeUDT, WikiProvider


# ============================================================
# REAL WIKI PROVIDER (MINIMAL, GOVERNED)
# ============================================================

class RealWiki(WikiProvider):
    """
    Minimal, deterministic Wikipedia provider for CLI usage.
    """

    HEADERS = {
        "User-Agent": "DephazeUDT/1.0 (contact: dewerangus@gmail.com)"
    }

    def __init__(self, lang: str = "en", timeout: float = 5.0):
        self.lang = lang
        self.timeout = timeout

    def search_and_fetch(self, query: str) -> Tuple[Optional[str], Optional[str]]:
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
            r.raise_for_status()
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
            r.raise_for_status()
            pages = r.json().get("query", {}).get("pages", {})
            page = next(iter(pages.values()), {})
            return title, page.get("extract")

        except Exception:
            return None, None


# ============================================================
# NOISE + STRUCTURAL HEURISTICS
# ============================================================

KNOWN_MORPHEMES = (
    "ion", "energy", "quantum", "theory", "field", "mass",
    "relativity", "particle", "wave", "space", "time"
)


def looks_like_real_term(s: str) -> bool:
    """
    Conservative structural filter against noise / spam.
    """
    s = s.strip()
    if not s:
        return False

    sl = s.lower()

    # multi-word phrase
    if " " in sl:
        return True

    # Proper noun (Einstein)
    if s[0].isupper() and any(c.islower() for c in s[1:]):
        return True

    # scientific morphemes
    for m in KNOWN_MORPHEMES:
        if sl.endswith(m):
            return True

    # reject keyboard smash (no vowels)
    if not any(v in sl for v in "aeiou"):
        return False

    return True


def normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


# ============================================================
# WIKI GOVERNANCE POLICY (FINAL)
# ============================================================

def wiki_allowed(label: str, xi: float, known: set[str], history_len: int) -> bool:
    """
    Decide whether Wiki lookup is allowed for this prompt.

    Deterministic, coherence-driven policy.
    """
    s = (label or "").strip()
    if not s:
        return False

    sl = s.lower()

    if sl in known:
        return False

    if len(sl) < 3:
        return False

    if not any(c.isalpha() for c in sl):
        return False

    if not looks_like_real_term(s):
        return False

    # A-mode: first iteration allowed
    if history_len <= 1:
        return True

    # xi refinement window
    if xi > 0.70:
        return False
    if xi < 0.40:
        return False

    return True


def wiki_result_matches(prompt: str, title: str) -> bool:
    """
    Conservative match between prompt and Wiki title.
    """
    if not title:
        return False

    p = prompt.lower()
    t = title.lower()

    # direct containment
    if t in p or p in t:
        return True

    # sentence → entity match
    for w in [w for w in t.split() if len(w) > 2]:
        if w in p:
            return True

    return False


# ============================================================
# CLI ENTRY POINT
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dephaze UDT – Deterministic Structural Analyzer (SAFE MODE)"
    )
    parser.add_argument("prompt", type=str)
    parser.add_argument("--no-wiki", action="store_true")
    args = parser.parse_args()

    known = set()

    udt = DephazeUDT(
        history_size=32,
        n_samples=64,
        strict_anchor=True,
        anchors={},
        atlas=None,
        wiki=None,
    )

    # PASS 1 — STRUCTURAL ONLY
    bundle = udt.forward(args.prompt, use_wiki=False)

    # PASS 2 — CONDITIONAL WIKI
    if (not args.no_wiki) and wiki_allowed(
        args.prompt,
        bundle.lambda_result.xi,
        known,
        bundle.sigma_audit["history_len"],
    ):
        wiki = RealWiki()
        title, extract = wiki.search_and_fetch(args.prompt)
        if wiki_result_matches(args.prompt, title):
            udt.wiki = wiki
            bundle = udt.forward(args.prompt, use_wiki=True)

    # OUTPUT (MINIMAL, MACHINE-READABLE)
    print("=== Dephaze UDT – Structural Output ===")
    print(f"Prompt: {bundle.prompt}")

    print("\nSigma audit:")
    for k, v in bundle.sigma_audit.items():
        print(f"  {k}: {v}")

    if bundle.wiki_title:
        print("\nWiki attachment:")
        print(f"  title  : {bundle.wiki_title}")
        print(f"  extract: {bundle.wiki_extract[:300]}")

    print("\n=== END ===")


if __name__ == "__main__":
    main()

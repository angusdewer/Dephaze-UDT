# ============================================================
# DEPHAZE GRM — SUBJECT NORMALIZATION (ALIAS FILTER)
# SAFE MODE FREEZE
# ============================================================
# Role:
#   Deterministic alias normalization for GRM nodes.
#
# Purpose:
#   - Remove non-entity aliases (geo, political, vague terms)
#   - Keep entity-relevant, compact identifiers
#   - Prevent alias explosion in GRM
#
# This is NOT:
#   - entity resolution
#   - fuzzy matching
#   - NLP / NER
#   - a learning system
#
# This IS:
#   - a strict, rule-based alias filter
#   - deterministic and reproducible
#   - SAFE MODE compliant
#
# Invariants (SAFE MODE):
#   - Rules are fixed
#   - No adaptive behavior
#   - In-place normalization only
#
# Modifying filters changes GRM semantics
# and breaks reproducibility guarantees.
# ============================================================

from typing import Dict, List
from grm_merge import GRMNode


# ------------------------------------------------------------
# Hard filters (CLOSED)
# ------------------------------------------------------------

GEO_STOPWORDS = {
    "Near East", "Middle East", "United States", "The United States",
    "United Kingdom", "Europe", "Asia", "China",
}

# Keep short scientific / taxonomic aliases only
MAX_ALIAS_WORDS = 2

# Allowlist suffixes (very conservative)
ALLOWED_SUFFIXES = {
    "idae",   # Felidae
    "idae.",  # safety
}


# ------------------------------------------------------------
# Alias validation
# ------------------------------------------------------------

def is_taxonomic(alias: str) -> bool:
    low = alias.lower()
    return any(low.endswith(suf) for suf in ALLOWED_SUFFIXES)


def is_valid_alias(alias: str) -> bool:
    """
    Decide whether an alias is GRM-safe.

    Rules:
      - Exclude known geographic / political aggregates
      - Exclude long phrases
      - Keep capitalized scientific names
      - Keep taxonomic group names
    """
    if alias in GEO_STOPWORDS:
        return False

    words = alias.split()
    if len(words) > MAX_ALIAS_WORDS:
        return False

    # Capitalized scientific / proper names
    if alias and alias[0].isupper():
        return True

    if is_taxonomic(alias):
        return True

    return False


# ------------------------------------------------------------
# GRM normalization
# ------------------------------------------------------------

def normalize_grm(nodes: Dict[str, GRMNode]) -> None:
    """
    In-place normalization of GRM nodes.

    Filters aliases to a canonical, entity-relevant set.
    """
    for node in nodes.values():
        cleaned: List[str] = []
        seen = set()

        for a in node.aliases:
            if not is_valid_alias(a):
                continue

            key = a.lower()
            if key in seen or a == node.label:
                continue

            seen.add(key)
            cleaned.append(a)

        node.aliases = cleaned

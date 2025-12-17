# ============================================================
# DEPHAZE GRM — RELATION TYPE CEILING
# CLOSED SET — SAFE MODE FREEZE
# ============================================================
# Role:
#   Canonical relation type controller for the Global Reality Map (GRM).
#
# Purpose:
#   - Enforce a CLOSED relation vocabulary
#   - Prevent ontology drift and semantic explosion
#   - Keep GRM deterministic and audit-friendly
#
# This is NOT:
#   - NLP relation extraction
#   - open-world ontology inference
#   - a learning system
#
# This IS:
#   - a strict semantic ceiling
#   - deterministic normalization
#   - SAFE MODE compliant
#
# Invariants (SAFE MODE):
#   - Relation set is closed and finite
#   - No runtime extension
#   - Fallback is always defined
#
# Modifying ALLOWED_RELATIONS changes GRM semantics
# and breaks reproducibility guarantees.
# ============================================================

# ------------------------------------------------------------
# Allowed relation types (CLOSED SET)
# ------------------------------------------------------------

ALLOWED_RELATIONS = {
    "instance_of",
    "subclass_of",
    "part_of",
    "has_property",
    "causes",
    "affects",
    "located_in",
    "related_to",
}


# ------------------------------------------------------------
# Normalization
# ------------------------------------------------------------

def normalize_relation(raw: str) -> str:
    """
    Normalize a raw relation string into a canonical GRM relation.

    Notes:
      - Normalization is deterministic
      - Unknown relations NEVER create new types
      - All fall back to 'related_to'
    """
    r = (raw or "").lower().strip()

    # --- canonical mappings ---
    if r in {"is", "was", "are", "were"}:
        return "instance_of"
    if r in {"type of", "kind of"}:
        return "subclass_of"
    if r in {"part", "component of"}:
        return "part_of"
    if r in {"has", "with"}:
        return "has_property"
    if r in {"causes", "leads to", "results in"}:
        return "causes"
    if r in {"affects", "influences"}:
        return "affects"
    if r in {"in", "inside", "located"}:
        return "located_in"

    # --- fallback (SAFE MODE) ---
    return "related_to"


# ------------------------------------------------------------
# Ceiling check
# ------------------------------------------------------------

def allow_relation(rel: str) -> bool:
    """
    Check whether a relation type is allowed in GRM.

    This must be enforced at ingestion time.
    """
    return rel in ALLOWED_RELATIONS

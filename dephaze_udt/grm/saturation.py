# ============================================================
# DEPHAZE GRM — SATURATION DETECTOR
# CANONICAL STOP CONDITION — SAFE MODE FREEZE
# ============================================================
# Role:
#   Deterministic saturation detector for GRM nodes.
#
# Purpose:
#   - Decide when a node has reached structural completeness
#   - Prevent unbounded growth
#   - Provide a hard stop-condition for ingestion
#
# This is NOT:
#   - learning convergence
#   - statistical optimization
#   - gradient-based stopping
#
# This IS:
#   - a deterministic structural stop rule
#   - based on fixed, explicit thresholds
#   - SAFE MODE compliant
#
# Invariants (SAFE MODE):
#   - Thresholds are fixed constants
#   - No adaptive behavior
#   - Binary decision (saturated / not)
#
# Modifying thresholds changes GRM behavior
# and breaks reproducibility guarantees.
# ============================================================

# ------------------------------------------------------------
# Canonical thresholds (CLOSED)
# ------------------------------------------------------------

ALIAS_MIN = 2          # minimum number of aliases
REL_MIN = 1            # minimum number of relations
XI_MIN = 0.97          # minimum average coherence
NO_CHANGE_ROUNDS = 2   # rounds without structural change


# ------------------------------------------------------------
# Saturation decision
# ------------------------------------------------------------

def is_saturated(node, *, xi_avg: float, no_change_rounds: int) -> bool:
    """
    Determine whether a GRM node is saturated.

    Conditions:
      - sufficient alias density
      - sufficient relation count
      - high average coherence (Ξ)
      - stability over multiple rounds
    """
    if len(node.aliases) < ALIAS_MIN:
        return False

    if len(getattr(node, "relations", [])) < REL_MIN:
        return False

    if xi_avg < XI_MIN:
        return False

    if no_change_rounds < NO_CHANGE_ROUNDS:
        return False

    return True

# ============================================================
# DEPHAZE GRM — WIKI INGESTION GATE
# GOVERNANCE LAYER — SAFE MODE FREEZE
# ============================================================
# Role:
#   Hard admission gate for Wikipedia-derived entities.
#
# Purpose:
#   - Prevent uncontrolled world growth
#   - Enforce coherence and saturation constraints
#   - Protect canonical GRM identity
#
# This is NOT:
#   - ranking
#   - relevance filtering
#   - popularity scoring
#   - machine learning
#
# This IS:
#   - a deterministic governance policy
#   - a hard allow / deny gate
#   - SAFE MODE compliant
#
# Invariants (SAFE MODE):
#   - Fixed thresholds
#   - No adaptive behavior
#   - Deterministic evaluation order
#
# Modifying this gate changes world-growth semantics
# and breaks reproducibility guarantees.
# ============================================================

XI_MIN = 0.97  # minimum coherence threshold


class WikiGate:
    """
    Deterministic gate for Wikipedia ingestion.
    """

    def __init__(self, grm_nodes: dict, domain_locked: bool = False):
        self.grm_nodes = grm_nodes
        self.domain_locked = domain_locked

    # --------------------------------------------------------
    # Canonical checks
    # --------------------------------------------------------

    def canonical_labels(self):
        """
        Return lowercase canonical labels.
        """
        return [n.label.lower() for n in self.grm_nodes.values()]

    def has_canonical(self, label: str) -> bool:
        """
        Check if a canonical GRM node already exists.
        """
        key = f"wiki:{label}"
        return key in self.grm_nodes

    def alias_hits(self, label: str) -> bool:
        """
        Check whether label already exists as label or alias.
        """
        low = label.lower()
        for n in self.grm_nodes.values():
            if n.label.lower() == low:
                return True
            if any(a.lower() == low for a in n.aliases):
                return True
        return False

    def canonical_head_match(self, label: str) -> bool:
        """
        Block cases like:
          'domestic cat' when 'cat' already exists.
        """
        tokens = label.lower().split()
        if not tokens:
            return False
        head = tokens[-1]
        return head in self.canonical_labels()

    # --------------------------------------------------------
    # Gate decision
    # --------------------------------------------------------

    def allow(self, *, label: str, xi: float, saturated: bool = False) -> bool:
        """
        Decide whether a Wikipedia entity may enter GRM.
        """
        if self.domain_locked:
            return False

        if saturated:
            return False

        if xi < XI_MIN:
            return False

        if self.has_canonical(label):
            return False

        if self.alias_hits(label):
            return False

        if self.canonical_head_match(label):
            return False

        return True

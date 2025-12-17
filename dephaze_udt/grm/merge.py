# ============================================================
# DEPHAZE GRM — DETERMINISTIC ENTITY MERGE
# SAFE MODE FREEZE
# ============================================================
# Role:
#   Deterministic merge controller for GRM entities.
#
# Purpose:
#   - Ensure explicit, controlled entity creation
#   - Prevent accidental or fuzzy merges
#   - Keep GRM identity stable and auditable
#
# This is NOT:
#   - entity resolution
#   - fuzzy matching
#   - similarity-based merging
#   - a learning system
#
# This IS:
#   - canonical ID–based merge only
#   - explicit alias / source attachment
#   - deterministic and reproducible
#   - SAFE MODE compliant
#
# Invariants (SAFE MODE):
#   - Only canonical_id creates identity
#   - No implicit merges
#   - Append-only metadata
#
# Modifying merge rules breaks GRM identity guarantees.
# ============================================================

from dataclasses import dataclass, field
from typing import List, Dict, Optional


# ------------------------------------------------------------
# GRM Node
# ------------------------------------------------------------

@dataclass
class GRMNode:
    """
    Minimal GRM entity node.
    """
    id: str
    label: str
    aliases: List[str] = field(default_factory=list)
    relations: List[dict] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)


# ------------------------------------------------------------
# Merge Engine
# ------------------------------------------------------------

class GRMMerger:
    """
    Deterministic GRM merge engine.

    Identity is defined ONLY by canonical_id.
    """

    def __init__(self):
        self.nodes: Dict[str, GRMNode] = {}

    def get_or_create(
        self,
        *,
        canonical_id: str,
        label: str,
        alias: Optional[str] = None,
        source: Optional[str] = None,
    ) -> GRMNode:
        """
        Retrieve or create a GRM node by canonical ID.

        Notes:
          - canonical_id is the ONLY merge key
          - alias and source are optional metadata
          - no automatic deduplication is performed
        """
        if canonical_id not in self.nodes:
            self.nodes[canonical_id] = GRMNode(
                id=canonical_id,
                label=label,
            )

        node = self.nodes[canonical_id]

        if alias and alias != label and alias not in node.aliases:
            node.aliases.append(alias)

        if source and source not in node.sources:
            node.sources.append(source)

        return node

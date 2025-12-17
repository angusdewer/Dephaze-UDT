# ============================================================
# DEPHAZE GRM — PERSISTENCE LAYER (JSON)
# SAFE MODE FREEZE
# ============================================================
# Role:
#   Deterministic persistence layer for the Global Reality Map (GRM).
#
# Purpose:
#   - Save and load GRM state in a stable, auditable format
#   - Enable versioned snapshots for publication and deployment
#
# This is NOT:
#   - a database
#   - a storage engine
#   - a cache
#   - a learning memory
#
# This IS:
#   - a simple, explicit serialization layer
#   - deterministic and reproducible
#   - SAFE MODE compliant
#
# Invariants (SAFE MODE):
#   - Fixed schema per version
#   - No automatic migrations
#   - Full state save/load only
#
# Modifying the schema requires a version bump
# and breaks backward compatibility.
# ============================================================

import json
from typing import Dict
from grm_merge import GRMNode


# ------------------------------------------------------------
# Canonical GRM version
# ------------------------------------------------------------

GRM_VERSION = "grm-1.0"


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

def save_grm(nodes: Dict[str, GRMNode], path: str) -> None:
    """
    Save GRM state to a JSON file.

    The output is:
      - deterministic
      - human-readable
      - versioned
    """
    data = {
        "version": GRM_VERSION,
        "nodes": {},
    }

    for node_id, node in nodes.items():
        data["nodes"][node_id] = {
            "label": node.label,
            "aliases": node.aliases,
            "sources": node.sources,
            "relations": node.relations,
        }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ------------------------------------------------------------
# Load
# ------------------------------------------------------------

def load_grm(path: str) -> Dict[str, GRMNode]:
    """
    Load GRM state from a JSON file.

    Raises:
      ValueError if version mismatch is detected.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("version") != GRM_VERSION:
        raise ValueError("Unsupported GRM version")

    nodes: Dict[str, GRMNode] = {}

    for node_id, payload in data.get("nodes", {}).items():
        nodes[node_id] = GRMNode(
            id=node_id,
            label=payload.get("label"),
            aliases=payload.get("aliases", []),
            sources=payload.get("sources", []),
            relations=payload.get("relations", []),
        )

    return nodes

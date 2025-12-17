# ============================================================
# DEPHAZE GRM — WORLD LOCK
# READ-ONLY SNAPSHOT — SAFE MODE FREEZE
# ============================================================
# Role:
#   Deterministic, read-only snapshot of the Global Reality Map (GRM).
#
# Purpose:
#   - Freeze a world-state for audit, publication, or deployment
#   - Provide integrity guarantees (hash-based)
#   - Enable patch-friendly downstream processing
#
# This is NOT:
#   - a live knowledge graph
#   - a learned world model
#   - an embedding store
#   - an adaptive memory
#
# This IS:
#   - a deterministic structural snapshot
#   - order-independent and reproducible
#   - SAFE MODE compliant
#
# Invariants (SAFE MODE):
#   - No mutation after lock
#   - No learning, no training
#   - Stable serialization
#   - Hash defines identity
#
# Modifying this file or its output schema
# breaks world integrity guarantees.
# ============================================================

import json
import hashlib
from typing import Dict

from grm_merge import GRMNode


WORLDLOCK_VERSION = "worldlock-1.0"


# ============================================================
# Internal helpers
# ============================================================

def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# ============================================================
# Hash computation
# ============================================================

def compute_grm_hash(nodes: Dict[str, GRMNode]) -> str:
    """
    Compute a stable, order-independent hash of GRM content.

    Notes:
      - Node order is canonicalized
      - Aliases and sources are sorted
      - Relations are kept as-is (semantic layer responsibility)
    """
    stable = {}
    for node_id in sorted(nodes.keys()):
        n = nodes[node_id]
        stable[node_id] = {
            "label": n.label,
            "aliases": sorted(n.aliases),
            "sources": sorted(n.sources),
            "relations": n.relations,
        }

    payload = json.dumps(
        stable,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")

    return _sha256_bytes(payload)


# ============================================================
# World lock
# ============================================================

def lock_world(
    nodes: Dict[str, GRMNode],
    path: str,
    *,
    note: str = "",
) -> None:
    """
    Write a read-only world snapshot with integrity hash.

    After locking:
      - The file must not be modified
      - Any change invalidates the hash
    """
    grm_hash = compute_grm_hash(nodes)

    stable = {}
    for node_id in sorted(nodes.keys()):
        n = nodes[node_id]
        stable[node_id] = {
            "label": n.label,
            "aliases": sorted(n.aliases),
            "sources": sorted(n.sources),
            "relations": n.relations,
        }

    world = {
        "version": WORLDLOCK_VERSION,
        "locked": True,
        "note": note,
        "integrity": {
            "algo": "sha256",
            "hash": grm_hash,
        },
        "nodes": stable,
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(world, f, indent=2, ensure_ascii=False)


# ============================================================
# Verification
# ============================================================

def verify_world(path: str) -> bool:
    """
    Verify integrity of a locked GRM snapshot.

    Returns:
      True  → integrity OK
      False → hash mismatch
    """
    with open(path, "r", encoding="utf-8") as f:
        world = json.load(f)

    if world.get("version") != WORLDLOCK_VERSION:
        raise ValueError("Unsupported world-lock version")

    if world.get("locked") is not True:
        raise ValueError("Snapshot is not marked as locked")

    nodes = world.get("nodes", {})
    payload = json.dumps(
        nodes,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")

    actual = _sha256_bytes(payload)
    expected = world.get("integrity", {}).get("hash")

    return actual == expected

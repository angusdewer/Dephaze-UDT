# ============================================================
# DEPHAZE UDT — GLOBAL ATLAS (ROOT LEVEL)
# READ-ONLY PHASE REFERENCE — SAFE MODE FREEZE
# ============================================================
# Role:
#   Optional, read-only global reference atlas in Dephaze phase-space.
#
# Purpose:
#   - Provide sparse, human-curated reference points
#   - Support LambdaEngine anchoring (nearest factual context)
#
# This is NOT:
#   - a knowledge base
#   - a learned memory
#   - an embedding index
#   - a vector database
#
# This IS:
#   - a static phase reference table
#   - deterministic and reproducible
#   - SAFE MODE compliant
#
# Design notes:
#   - Linear O(N) scan is intentional (small N, deterministic)
#   - No spatial index to avoid platform-dependent behavior
#
# Modifying this file or atlas content
# changes global anchoring semantics.
# ============================================================

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Iterable
import json
from pathlib import Path

# NOTE:
# Root-level import is intentional to allow lightweight usage.
# In embedded contexts, this may be replaced by `core.phase`.
from phase import PhaseCoord


# ============================================================
# Atlas node (IMMUTABLE)
# ============================================================

@dataclass(frozen=True)
class AtlasNode:
    """
    Immutable atlas reference node.
    """
    key: str
    theta: float
    phi: float
    rho: float
    title: Optional[str] = None
    snippet: Optional[str] = None

    def phase(self) -> PhaseCoord:
        """
        Return phase-space coordinate of this node.
        """
        return PhaseCoord(self.theta, self.phi, self.rho)


# ============================================================
# Global Atlas (READ-ONLY)
# ============================================================

class GlobalAtlas:
    """
    Read-only phase-space atlas.

    - No training
    - No mutation
    - Optional component
    """

    def __init__(self, nodes: Iterable[AtlasNode]):
        self.nodes: List[AtlasNode] = list(nodes)

    # --------------------------------------------------------
    # Nearest lookup (deterministic)
    # --------------------------------------------------------

    def nearest(
        self,
        phase: PhaseCoord,
        max_dist: float = 1.0,
    ) -> Optional[AtlasNode]:
        """
        Return nearest atlas node within max_dist.
        """
        best = None
        best_d = float("inf")

        for n in self.nodes:
            d = n.phase().distance_to(phase)
            if d < best_d and d <= max_dist:
                best_d = d
                best = n

        return best

    # --------------------------------------------------------
    # Lambda adapter
    # --------------------------------------------------------

    def as_lambda_payload(self, phase: PhaseCoord) -> dict:
        """
        Return payload compatible with LambdaEngine.

        Empty dict if no anchor is found.
        """
        n = self.nearest(phase)
        if n is None:
            return {}

        return {
            "key": n.key,
            "theta": n.theta,
            "phi": n.phi,
            "rho": n.rho,
            "title": n.title,
            "extract": n.snippet,
        }


# ============================================================
# Loader
# ============================================================

def load_atlas_from_json(path: str | Path) -> GlobalAtlas:
    """
    Load atlas from a PhaseIndex-like JSON.

    Expected format:
      [
        { "key": "...", "theta": 0.1, "phi": -0.3, "rho": 0.7, "text": "..." },
        ...
      ]
    """
    p = Path(path)
    raw = json.loads(p.read_text(encoding="utf-8"))

    nodes: List[AtlasNode] = []
    for obj in raw:
        try:
            nodes.append(
                AtlasNode(
                    key=str(obj.get("key") or obj.get("id") or ""),
                    theta=float(obj["theta"]),
                    phi=float(obj["phi"]),
                    rho=float(obj["rho"]),
                    title=obj.get("text") or obj.get("title"),
                    snippet=obj.get("extract") or obj.get("summary"),
                )
            )
        except Exception:
            continue

    return GlobalAtlas(nodes)

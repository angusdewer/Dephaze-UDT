# ============================================================
# DEPHAZE UDT — ATLAS FEEDBACK FIELD
# SAFE MODE FREEZE
# ============================================================
# Role:
#   Deterministic stabilizing potential field constructed
#   from a validated star-map (atlas).
#
# Purpose:
#   - Attract Lambda decisions toward coherent regions
#   - Suppress noise and drift
#   - Allow novelty only when Sigma coherence is high
#
# This is NOT:
#   - an embedding space
#   - a learned memory
#   - a clustering model
#   - a feedback learning loop
#
# This IS:
#   - a read-only stabilizing field
#   - fully deterministic
#   - SAFE MODE compliant
#
# Invariants (SAFE MODE):
#   - No training, no learning
#   - No randomness
#   - Fixed atlas input
#   - Phase-space → XYZ mapping is invariant
#
# Modifying this field breaks global stability guarantees.
# ============================================================

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

from core.phase import PhaseCoord


# ============================================================
# Internal Star Representation (NUMERIC ONLY)
# ============================================================

@dataclass(frozen=True)
class AtlasStar:
    """
    Immutable numeric star used by the Atlas field.
    """
    x: float
    y: float
    z: float
    weight: float
    quality: float   # derived from sigma_xi × compactness


# ============================================================
# Atlas Field
# ============================================================

class AtlasField:
    """
    Continuous stabilizing potential field built from atlas stars.

    Deterministic. Read-only.
    """

    def __init__(
        self,
        stars: List[AtlasStar],
        *,
        alpha: float = 12.0,     # spatial falloff
        max_range: float = 2.0   # ignore stars beyond this radius
    ) -> None:
        self.stars = stars
        self.alpha = float(alpha)
        self.max_range2 = float(max_range * max_range)

    # --------------------------------------------------------
    # Loader (CANONICAL)
    # --------------------------------------------------------

    @classmethod
    def load(cls, path: str) -> "AtlasField":
        """
        Load atlas stars from a JSON snapshot.

        The JSON is assumed to be validated upstream.
        """
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        stars: List[AtlasStar] = []

        for obj in raw.get("stars", {}).values():
            try:
                x = float(obj["x"])
                y = float(obj["y"])
                z = float(obj["z"])
                w = float(obj.get("weight", 1.0))

                sigma_xi = float(obj.get("sigma_xi", 0.0))
                spread = float(obj.get("sigma_spread", 1.0))

                # Quality: coherence × compactness
                quality = max(0.0, sigma_xi * (1.0 - spread))

                stars.append(
                    AtlasStar(
                        x=x,
                        y=y,
                        z=z,
                        weight=w,
                        quality=quality,
                    )
                )
            except Exception:
                continue

        return cls(stars)

    # --------------------------------------------------------
    # Core Field Functions
    # --------------------------------------------------------

    def potential(self, phase: PhaseCoord) -> float:
        """
        Compute atlas stabilizing potential at a given phase.
        """
        x, y, z = self._phase_to_xyz(phase)

        total = 0.0
        for s in self.stars:
            dx = x - s.x
            dy = y - s.y
            dz = z - s.z
            d2 = dx * dx + dy * dy + dz * dz

            if d2 > self.max_range2:
                continue

            total += s.weight * s.quality * math.exp(-self.alpha * d2)

        return total

    def nearest_distance(self, phase: PhaseCoord) -> Optional[float]:
        """
        Euclidean distance to nearest atlas star (XYZ space).
        """
        if not self.stars:
            return None

        x, y, z = self._phase_to_xyz(phase)
        best = float("inf")

        for s in self.stars:
            dx = x - s.x
            dy = y - s.y
            dz = z - s.z
            d = math.sqrt(dx * dx + dy * dy + dz * dz)
            if d < best:
                best = d

        return best

    def audit(self, phase: PhaseCoord) -> Dict[str, float]:
        """
        Debug / validation snapshot.
        """
        return {
            "potential": self.potential(phase),
            "nearest_distance": self.nearest_distance(phase) or -1.0,
            "star_count": len(self.stars),
        }

    # --------------------------------------------------------
    # Internal Mapping
    # --------------------------------------------------------

    @staticmethod
    def _phase_to_xyz(p: PhaseCoord) -> Tuple[float, float, float]:
        """
        Canonical phase → XYZ mapping.

        NOTE:
        Must remain consistent with atlas_commit.py.
        """
        rr = max(0.0, min(1.0, p.rho))
        x = rr * math.sin(p.theta) * math.cos(p.phi)
        y = rr * math.sin(p.theta) * math.sin(p.phi)
        z = rr * math.cos(p.theta)
        return (x, y, z)

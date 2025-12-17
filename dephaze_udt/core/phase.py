# ============================================================
# DEPHAZE UDT — PHASE CORE
# CANONICAL DEFINITION — SAFE MODE FREEZE
# ============================================================
# Role:
#   Canonical definition of the Dephaze phase-space,
#   topology, and deterministic semantic → phase mapping.
#
# This file DEFINES what a "phase" is in Dephaze.
#
# This is NOT:
#   - an embedding
#   - a token-based representation
#   - a learned vector space
#   - a probability distribution
#
# This IS:
#   - a deterministic ontological coordinate system
#   - a topological phase-space
#   - invariant across runs, machines, and platforms
#
# Invariants (SAFE MODE):
#   - No training, no learning
#   - No randomness
#   - Hash-based deterministic projection
#   - Fixed coordinate ranges:
#       theta ∈ [-1, 1]
#       phi   ∈ [-1, 1]
#       rho   ∈ [ 0, 1]
#
# Modifying this file redefines Dephaze ontology
# and breaks reproducibility guarantees.
# ============================================================

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, List, Optional
import math
import hashlib
import re


# ============================================================
# Phase-space coordinate
# ============================================================

@dataclass(frozen=True)
class PhaseCoord:
    """
    Minimal 3D ontological phase-space coordinate.

    theta ∈ [-1, 1]
    phi   ∈ [-1, 1]
    rho   ∈ [ 0, 1]
    """
    theta: float
    phi: float
    rho: float

    def clamp(self) -> "PhaseCoord":
        return PhaseCoord(
            theta=max(-1.0, min(1.0, self.theta)),
            phi=max(-1.0, min(1.0, self.phi)),
            rho=max(0.0, min(1.0, self.rho)),
        )

    def distance_to(self, other: "PhaseCoord") -> float:
        """
        Euclidean distance in phase-space.
        """
        return math.sqrt(
            (self.theta - other.theta) ** 2
            + (self.phi - other.phi) ** 2
            + (self.rho - other.rho) ** 2
        )

    def to_rgb(self) -> Tuple[float, float, float]:
        """
        Compact visual marker (diagnostic only).
        NOT a rendering or perceptual mapping.
        """
        r = (self.theta + 1.0) * 0.5
        g = (self.phi + 1.0) * 0.5
        b = self.rho
        return (
            max(0.0, min(1.0, r)),
            max(0.0, min(1.0, g)),
            max(0.0, min(1.0, b)),
        )


# ============================================================
# Topology 2.0 (STRUCTURAL CONSTRAINTS)
# ============================================================

@dataclass
class TopologyRegion:
    """
    Axis-aligned region in phase-space.

    locked=True  → forbidden region (e.g. Rocksteeple)
    locked=False → neutral / shrine region
    """
    name: str
    theta_range: Tuple[float, float]
    phi_range: Tuple[float, float]
    rho_range: Tuple[float, float]
    locked: bool = False


class Topology:
    """
    Minimal deterministic topological constraint system.
    """

    def __init__(self, regions: List[TopologyRegion]):
        self.regions = regions

    def enforce(self, coord: PhaseCoord) -> PhaseCoord:
        """
        Enforce topological constraints.

        If coord falls into a locked region,
        it is deterministically pushed out.
        """
        c = coord.clamp()

        for r in self.regions:
            if not r.locked:
                continue
            if self._inside(c, r):
                c = PhaseCoord(
                    self._push_1d(c.theta, r.theta_range),
                    self._push_1d(c.phi, r.phi_range),
                    self._push_1d(c.rho, r.rho_range),
                ).clamp()
        return c

    @staticmethod
    def _inside(c: PhaseCoord, r: TopologyRegion) -> bool:
        return (
            r.theta_range[0] <= c.theta <= r.theta_range[1]
            and r.phi_range[0] <= c.phi <= r.phi_range[1]
            and r.rho_range[0] <= c.rho <= r.rho_range[1]
        )

    @staticmethod
    def _push_1d(v: float, rng: Tuple[float, float]) -> float:
        lo, hi = rng
        if v < lo or v > hi:
            return v
        # minimal deterministic displacement
        return lo - 0.02 if (v - lo) < (hi - v) else hi + 0.02


def default_topology() -> Topology:
    """
    Canonical Dephaze topology.
    """
    return Topology(
        regions=[
            TopologyRegion(
                name="origin_shrine",
                theta_range=(-0.05, 0.05),
                phi_range=(-0.05, 0.05),
                rho_range=(0.0, 0.15),
                locked=False,
            ),
            TopologyRegion(
                name="rocksteeple_forbidden",
                theta_range=(0.20, 0.30),
                phi_range=(0.50, 0.70),
                rho_range=(0.70, 1.00),
                locked=True,
            ),
        ]
    )


# ============================================================
# Deterministic semantic → phase mapper
# ============================================================

class PhaseMapper:
    """
    Deterministic semantic → phase mapper.

    Any input string maps to a stable PhaseCoord.

    NOT embedding.
    NOT token-based.
    NOT statistical.
    """

    def __init__(self, topology: Optional[Topology] = None):
        self.topology = topology or default_topology()

    @staticmethod
    def _normalize(text: str) -> str:
        t = text.strip().lower()
        t = re.sub(r"\s+", " ", t)
        return t

    @staticmethod
    def _hash_to_unit(seed: str) -> float:
        """
        Stable hash → [0,1]
        """
        h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
        v = int(h[:16], 16)
        return (v % 10**12) / 10**12

    def text_to_phase(self, text: str) -> PhaseCoord:
        """
        Core mapping: text → PhaseCoord.
        """
        t = self._normalize(text)
        if not t:
            return PhaseCoord(0.0, 0.0, 0.0)

        a = self._hash_to_unit("θ:" + t)
        b = self._hash_to_unit("φ:" + t)
        c = self._hash_to_unit("ρ:" + t)

        theta = a * 2.0 - 1.0
        phi = b * 2.0 - 1.0
        rho = c

        coord = PhaseCoord(theta, phi, rho)
        return self.topology.enforce(coord)


# ============================================================
# PromptStar (OPTIONAL DIAGNOSTIC CACHE)
# ============================================================

@dataclass
class PromptStar:
    key: str
    phase: PhaseCoord
    rgb: Tuple[float, float, float]
    hits: int = 1


class PromptStarMap:
    """
    Minimal prompt → phase cache.

    This is NOT learning.
    This is NOT memory in the ML sense.
    """

    def __init__(self):
        self._stars = {}

    def get_or_create(self, key: str, phase: PhaseCoord) -> PromptStar:
        k = key.strip().lower()
        star = self._stars.get(k)
        if star:
            star.hits += 1
            return star

        star = PromptStar(
            key=k,
            phase=phase,
            rgb=phase.to_rgb(),
            hits=1,
        )
        self._stars[k] = star
        return star

    def count(self) -> int:
        return len(self._stars)

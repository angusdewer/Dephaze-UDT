# ============================================================
# DEPHAZE UDT — GÖDEL RELATION FIELD
# SAFE MODE FREEZE
# ============================================================
# Role:
#   Deterministic structural relation field used by the Λ operator.
#
#   This is NOT a knowledge graph.
#   This is NOT an embedding space.
#   This is NOT a neural memory.
#
#   Each relation contributes:
#     - a bridge attractor (subject ↔ object midpoint)
#     - an edge-star attractor (relation-specific phase)
#
#   The field produces a smooth potential over phase-space
#   and an optional resultant vector for Lambda resolution.
#
# Invariants (SAFE MODE):
#   - Deterministic execution
#   - No learning, no training
#   - No probabilistic sampling
#   - Fixed-capacity structural memory
#   - Phase-space only (θ, φ, ρ)
#
# Modifying behavior breaks SAFE MODE guarantees.
# ============================================================

from __future__ import annotations

import math
import hashlib
from dataclasses import dataclass
from typing import List

from core.phase import PhaseCoord, PhaseMapper
from core.edge_phase import edge_phase as edge_phase_fn


# ============================================================
# Data structures
# ============================================================

@dataclass(frozen=True)
class RelationBridge:
    """
    Immutable structural relation element.

    Represents:
      subject ---relation---> object

    Stored as:
      - subject phase
      - object phase
      - edge-star phase (relation-specific attractor)
    """
    subject: str
    relation: str
    object_: str
    s_phase: PhaseCoord
    o_phase: PhaseCoord
    e_phase: PhaseCoord
    strength: float
    origin: str  # user / wiki / global


# ============================================================
# Gödel Field
# ============================================================

class GodelField:
    """
    Structural relation field composed of RelationBridge elements.

    The field defines a scalar potential over phase-space:

        Potential(phase) =
            Σ strength · (
                bridge_gain · exp(-α_bridge · d_mid²)
              + edge_gain   · exp(-α_edge   · d_edge²)
            )

    where:
      - d_mid  = distance to midpoint(subject, object)
      - d_edge = distance to relation edge-star

    Lambda uses this field as a deterministic influence source.
    """

    def __init__(
        self,
        *,
        alpha_bridge: float = 3.0,
        alpha_edge: float = 4.5,
        bridge_gain: float = 0.70,
        edge_gain: float = 1.00,
        max_bridges: int = 4096,
    ) -> None:
        self.alpha_bridge = float(alpha_bridge)
        self.alpha_edge = float(alpha_edge)
        self.bridge_gain = float(bridge_gain)
        self.edge_gain = float(edge_gain)
        self.max_bridges = int(max_bridges)

        # Fixed-capacity deterministic storage
        self.bridges: List[RelationBridge] = []

    # --------------------------------------------------------
    # Geometry helpers
    # --------------------------------------------------------

    @staticmethod
    def _dist(a: PhaseCoord, b: PhaseCoord) -> float:
        dt = a.theta - b.theta
        dp = a.phi - b.phi
        dr = a.rho - b.rho
        return math.sqrt(dt * dt + dp * dp + dr * dr)

    @staticmethod
    def _mid(a: PhaseCoord, b: PhaseCoord) -> PhaseCoord:
        return PhaseCoord(
            (a.theta + b.theta) * 0.5,
            (a.phi + b.phi) * 0.5,
            (a.rho + b.rho) * 0.5,
        ).clamp()

    @staticmethod
    def _stable_key(subject: str, relation: str, object_: str, origin: str) -> str:
        """
        Stable deterministic key for de-duplication.
        """
        k = f"{origin}|{subject}|{relation.lower()}|{object_}".encode(
            "utf-8", errors="ignore"
        )
        return hashlib.sha1(k).hexdigest()

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def add_relation(
        self,
        *,
        subject: str,
        relation: str,
        object_: str,
        mapper: PhaseMapper,
        strength: float,
        origin: str,
    ) -> None:
        """
        Insert or update a structural relation.

        If a duplicate relation exists (same key),
        the stronger one is kept.
        """
        s = (subject or "").strip()
        r = (relation or "").strip().lower()
        o = (object_ or "").strip()
        if not s or not r or not o:
            return

        # Deterministic phase projections
        sp = mapper.text_to_phase(s)
        op = mapper.text_to_phase(o)
        ep_raw = edge_phase_fn(s, r, o)
        ep = PhaseCoord(ep_raw.theta, ep_raw.phi, ep_raw.rho).clamp()

        key = self._stable_key(s, r, o, origin)

        idx = None
        for i, b in enumerate(self.bridges):
            if self._stable_key(b.subject, b.relation, b.object_, b.origin) == key:
                idx = i
                break

        rb = RelationBridge(
            subject=s,
            relation=r,
            object_=o,
            s_phase=sp,
            o_phase=op,
            e_phase=ep,
            strength=float(max(0.0, strength)),
            origin=origin,
        )

        if idx is None:
            self.bridges.append(rb)
        else:
            if rb.strength > self.bridges[idx].strength:
                self.bridges[idx] = rb

        # Capacity clamp (deterministic)
        if len(self.bridges) > self.max_bridges:
            self.bridges.sort(key=lambda x: x.strength, reverse=True)
            self.bridges = self.bridges[: self.max_bridges]

    def potential(self, phase: PhaseCoord) -> float:
        """
        Scalar potential of the field at a given phase.
        """
        if not self.bridges:
            return 0.0

        total = 0.0
        for b in self.bridges:
            mid = self._mid(b.s_phase, b.o_phase)

            d_mid = self._dist(phase, mid)
            bridge_term = math.exp(-self.alpha_bridge * d_mid * d_mid)

            d_edge = self._dist(phase, b.e_phase)
            edge_term = math.exp(-self.alpha_edge * d_edge * d_edge)

            total += b.strength * (
                self.bridge_gain * bridge_term
                + self.edge_gain * edge_term
            )

        return total

    def sample_attractors(self, seed_key: str, k: int = 8) -> List[PhaseCoord]:
        """
        Deterministically select up to k strong edge-star attractors.
        Used by Lambda as candidate phase hints.
        """
        if not self.bridges or k <= 0:
            return []

        strong = sorted(
            self.bridges, key=lambda x: x.strength, reverse=True
        )[: min(len(self.bridges), 64)]

        h = hashlib.sha256(
            (seed_key or "seed").encode("utf-8", errors="ignore")
        ).digest()

        picks: List[PhaseCoord] = []
        for i in range(k):
            j = h[i] % len(strong)
            picks.append(strong[j].e_phase)

        return picks

    def audit(self, phase: PhaseCoord) -> dict:
        """
        Minimal audit snapshot for debugging / visualization.
        """
        return {
            "bridge_count": len(self.bridges),
            "potential": self.potential(phase),
        }

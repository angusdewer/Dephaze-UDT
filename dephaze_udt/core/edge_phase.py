# ============================================================
# DEPHAZE UDT — EDGE PHASE
# SAFE MODE FREEZE
# ============================================================
# Role:
#   Deterministic mapping of a relation triple
#     (subject, relation, object)
#   to a PhaseCoord in the Dephaze phase-space.
#
# This is NOT:
#   - an embedding
#   - a learned representation
#   - a similarity space
#
# This IS:
#   - a stable topological identifier
#   - a deterministic phase attractor ("edge-star")
#   - invariant across runs, machines, and platforms
#
# Invariants (SAFE MODE):
#   - No training, no learning
#   - No randomness
#   - Hash-based deterministic projection
#   - Fixed output ranges:
#       theta ∈ [-1, 1]
#       phi   ∈ [-1, 1]
#       rho   ∈ [ 0, 1]
#
# Modifying this mapping breaks structural consistency
# across the entire Gödel field.
# ============================================================

from __future__ import annotations

import hashlib
from dataclasses import dataclass


# ============================================================
# Phase Coordinate (LOCAL, IMMUTABLE)
# ============================================================

@dataclass(frozen=True)
class PhaseCoord:
    """
    Minimal phase-space coordinate used by the Edge Phase.

    NOTE:
    This is intentionally duplicated here to keep the
    edge-phase module fully deterministic and dependency-light.
    """
    theta: float
    phi: float
    rho: float

    def clamp(self) -> "PhaseCoord":
        t = max(-1.0, min(1.0, float(self.theta)))
        p = max(-1.0, min(1.0, float(self.phi)))
        r = max(0.0, min(1.0, float(self.rho)))
        return PhaseCoord(t, p, r)


# ============================================================
# Internal helpers
# ============================================================

def _u16(b: bytes, off: int) -> int:
    return int.from_bytes(b[off : off + 2], "big", signed=False)


# ============================================================
# Edge Phase Mapping
# ============================================================

def edge_phase(
    subject: str,
    relation: str,
    object_: str,
    *,
    salt: str = "EDGE_PHASE_V1",
) -> PhaseCoord:
    """
    Deterministic mapping of a relation triple to phase-space.

    Inputs:
      subject  : entity A
      relation : structural relation (normalized lowercase)
      object_  : entity B

    Output:
      PhaseCoord(theta, phi, rho)

    Properties:
      - Deterministic
      - Collision-resistant (SHA-256)
      - Platform-independent
      - No semantic assumptions
    """
    s = (subject or "").strip()
    r = (relation or "").strip().lower()
    o = (object_ or "").strip()

    key = f"{salt}|{s}|{r}|{o}".encode("utf-8", errors="ignore")
    h = hashlib.sha256(key).digest()

    a = _u16(h, 0)   # 0 .. 65535
    b = _u16(h, 2)
    c = _u16(h, 4)

    # Map to canonical ranges
    theta = (a / 65535.0) * 2.0 - 1.0
    phi   = (b / 65535.0) * 2.0 - 1.0
    rho   = (c / 65535.0)

    return PhaseCoord(theta, phi, rho).clamp()

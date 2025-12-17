# ============================================================
# DEPHAZE UDT — PHASE FIELD
# SAFE MODE FREEZE
# ============================================================
# Role:
#   Structured, non-homogeneous stabilizing field
#   acting over the Dephaze phase-space.
#
# This is NOT:
#   - a semantic similarity function
#   - an embedding space
#   - a learned feature map
#
# This IS:
#   - a static topological bias field
#   - a deterministic stabilizer
#   - SAFE MODE compliant
#
# Invariants (SAFE MODE):
#   - No training, no learning
#   - No stochastic behavior
#   - Fixed channel definitions
#   - Phase-space only (θ, φ, ρ)
#
# Modifying this field changes system topology
# and breaks reproducibility guarantees.
# ============================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
import math

from core.phase import PhaseCoord


# ============================================================
# Phase Channel Definition
# ============================================================

@dataclass(frozen=True)
class PhaseChannel:
    """
    Immutable definition of a phase-space bias channel.
    """
    name: str
    theta_bias: float   # preferred theta direction
    rho_bias: float     # preferred depth (0..1)
    strength: float     # influence weight


# ============================================================
# Phase Field
# ============================================================

class PhaseField:
    """
    Static phase-space field composed of multiple bias channels.

    Each channel contributes a smooth Gaussian potential
    centered at (theta_bias, rho_bias).
    """

    def __init__(self, channels: Dict[str, PhaseChannel]):
        # Channels are treated as read-only after construction
        self.channels = channels

    # --------------------------------------------------------
    # Channel potential
    # --------------------------------------------------------

    def potential(self, phase: PhaseCoord, channel: str) -> float:
        """
        Compute scalar potential contribution of a channel
        at a given phase coordinate.
        """
        ch = self.channels.get(channel)
        if ch is None:
            return 0.0

        # Angular alignment
        d_theta = abs(phase.theta - ch.theta_bias)

        # Depth alignment
        d_rho = abs(phase.rho - ch.rho_bias)

        # Gaussian falloff (fixed shape)
        score = (
            math.exp(-4.0 * d_theta * d_theta)
            * math.exp(-4.0 * d_rho * d_rho)
        )

        return ch.strength * score

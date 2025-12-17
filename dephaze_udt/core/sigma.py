# ============================================================
# DEPHAZE UDT — SIGMA STATE (Σ)
# SAFE MODE FREEZE
# ============================================================
# Role:
#   Deterministic coherence memory operating purely
#   in Dephaze phase-space.
#
# This is NOT:
#   - learning
#   - training
#   - optimization
#   - a loss function
#   - a memory network
#
# This IS:
#   - fixed-size structural history
#   - coherence tracking via geometric dispersion
#   - deterministic and reproducible
#
# Invariants (SAFE MODE):
#   - No training, no learning
#   - No probabilistic updates
#   - Fixed update rules
#   - Phase-space only (θ, φ, ρ)
#
# Modifying this file changes the definition of Ξ
# and breaks reproducibility guarantees.
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Deque, Optional
from collections import deque

from core.phase import PhaseCoord


# ============================================================
# Sigma History (STRUCTURAL MEMORY)
# ============================================================

@dataclass
class SigmaHistory:
    """
    Fixed-size history of phase coordinates.

    Contains:
      - no text
      - no semantics
      - no learned state

    Only geometric structure in phase-space.
    """
    maxlen: int = 32
    recent: Deque[PhaseCoord] = field(default_factory=deque)

    def push(self, phase: PhaseCoord) -> None:
        if len(self.recent) >= self.maxlen:
            self.recent.popleft()
        self.recent.append(phase)

    def centroid(self) -> Optional[PhaseCoord]:
        if not self.recent:
            return None
        th = sum(p.theta for p in self.recent) / len(self.recent)
        ph = sum(p.phi for p in self.recent) / len(self.recent)
        rh = sum(p.rho for p in self.recent) / len(self.recent)
        return PhaseCoord(th, ph, rh).clamp()

    def spread(self) -> float:
        """
        Mean distance from centroid.

        Interpreted as structural dispersion,
        NOT statistical variance.
        """
        c = self.centroid()
        if c is None:
            return 0.0
        return sum(p.distance_to(c) for p in self.recent) / len(self.recent)


# ============================================================
# Sigma State (Σ)
# ============================================================

@dataclass
class SigmaState:
    """
    Σ-state: deterministic internal coherence state.

    Tracks:
      - recent phase history
      - coherence ratio Ξ

    Does NOT:
      - adapt rules
      - store knowledge
      - optimize behavior
    """
    history_size: int = 32
    history: SigmaHistory = field(init=False)
    xi: float = field(default=1.0)  # coherence ratio Ξ ∈ (0, 1]

    def __post_init__(self) -> None:
        self.history = SigmaHistory(maxlen=self.history_size)

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def current_phase(self) -> PhaseCoord:
        """
        Return the most recent phase.
        Origin is returned if history is empty.
        """
        if not self.history.recent:
            return PhaseCoord(0.0, 0.0, 0.0)
        return self.history.recent[-1]

    def update(self, new_phase: PhaseCoord) -> None:
        """
        Push new phase and update coherence Ξ.
        """
        prev_centroid = self.history.centroid()
        self.history.push(new_phase)
        self._update_xi(prev_centroid)

    # --------------------------------------------------------
    # Coherence (Ξ)
    # --------------------------------------------------------

    def _update_xi(self, prev_centroid: Optional[PhaseCoord]) -> None:
        """
        Update coherence ratio Ξ.

        Definition:
          Ξ = 1 / (1 + spread)

        Properties:
          - deterministic
          - monotonic
          - bounded in (0, 1]
        """
        spread = self.history.spread()
        self.xi = 1.0 / (1.0 + spread)

    # --------------------------------------------------------
    # Diagnostics
    # --------------------------------------------------------

    def audit(self) -> dict:
        """
        Structured, reproducible audit snapshot.
        """
        cp = self.current_phase()
        return {
            "history_len": len(self.history.recent),
            "xi": round(self.xi, 6),
            "spread": round(self.history.spread(), 6),
            "current_phase": (cp.theta, cp.phi, cp.rho),
        }

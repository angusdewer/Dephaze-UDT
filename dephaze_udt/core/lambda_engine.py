# ============================================================
# DEPHAZE UDT — LAMBDA ENGINE (Λ OPERATOR)
# SAFE MODE FREEZE
# ============================================================
# Role:
#   Deterministic decision operator resolving the current
#   world-state phase from competing structural influences.
#
#   This is NOT an inference engine.
#   This is NOT probabilistic reasoning.
#   This is a topological resolution operator (Λ).
#
# Invariants (SAFE MODE):
#   - Deterministic execution
#   - No training, no learning
#   - No stochastic sampling
#   - Phase-space operations only
#   - Backward-compatible field routing
#
# Modifying behavior here breaks SAFE MODE guarantees.
# ============================================================

import math
from typing import Any

from core.phase import PhaseCoord


# ============================================================
# Lambda Result (CANONICAL DECISION OUTPUT)
# ============================================================

class LambdaResult:
    """
    Structured output of a Lambda decision.
    """
    def __init__(self, mode: str, confidence: float, xi: float, chosen: PhaseCoord):
        self.mode = mode              # active influence tags
        self.confidence = confidence  # coherence-derived confidence (NOT probability)
        self.xi = xi                  # Sigma coherence snapshot
        self.chosen = chosen          # resolved phase coordinate


# ============================================================
# Lambda Engine
# ============================================================

class LambdaEngine:
    """
    Λ operator — deterministic phase resolution engine.

    Responsibilities:
    - Resolve phase movement toward Imago (PCM)
    - Apply optional stabilizing fields (Atlas, Gödel, Edge)
    - Produce a single coherent PhaseCoord decision

    Backward compatibility:
    - Accepts legacy init args (ignored safely)
    - Accepts legacy field names (global_atlas, godel, edge)
    - Supports Atlas v1 and v2 interfaces
    """

    def __init__(self, **_ignored: Any):
        # NOTE:
        # All legacy init args are intentionally ignored
        # to preserve backward compatibility and SAFE MODE.

        # PCM (Phase Coherence Memory) gain
        self.pcm_gain = 0.45

        # Noise damping factor (Sigma spread influence)
        self.noise_damp = 0.85

        # External field gains (structural only)
        self.atlas_gain = 0.35
        self.godel_gain = 0.60
        self.edge_gain = 0.35

    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------

    def _resolve_phase(self, obj, fallback: PhaseCoord) -> PhaseCoord:
        """
        Resolve a PhaseCoord from:
          - PhaseCoord
          - callable returning PhaseCoord
          - None → fallback
        """
        if obj is None:
            return fallback
        if callable(obj):
            try:
                obj = obj()
            except Exception:
                return fallback
        return obj if isinstance(obj, PhaseCoord) else fallback

    def _confidence(self, xi: float, spread: float) -> float:
        """
        Deterministic confidence estimator.

        NOTE:
        This is NOT probability.
        It is a coherence-weighted stability indicator.
        """
        base = 0.5 + 0.5 * math.tanh(2.5 * (xi - 0.5))
        damp = math.exp(-self.noise_damp * max(0.0, spread))
        return round(base * damp, 4)

    def _route_fields(self, atlas, godel_field, edge_field, extras: dict):
        """
        Resolve external fields from current or legacy names.
        """
        if atlas is None:
            atlas = extras.get("global_atlas") or extras.get("atlas")
        if godel_field is None:
            godel_field = (
                extras.get("global_godel_field")
                or extras.get("godel_field")
                or extras.get("godel")
            )
        if edge_field is None:
            edge_field = (
                extras.get("global_edge_field")
                or extras.get("edge_field")
                or extras.get("edge")
            )
        return atlas, godel_field, edge_field

    def _atlas_pull_vector(self, atlas, start: PhaseCoord):
        """
        Atlas compatibility layer.

        Supported interfaces:
          - pull_vector(start) -> (dx, dy, dz)
          - as_lambda_payload(start) -> {theta, phi, rho}
          - nearest(start) -> node with theta/phi/rho

        Returns:
          (dx, dy, dz) or None
        """
        # Atlas v2
        if hasattr(atlas, "pull_vector"):
            v = atlas.pull_vector(start)
            return (float(v[0]), float(v[1]), float(v[2]))

        # Atlas v1: as_lambda_payload
        if hasattr(atlas, "as_lambda_payload"):
            try:
                p = atlas.as_lambda_payload(start)
                if isinstance(p, dict) and all(k in p for k in ("theta", "phi", "rho")):
                    return (
                        float(p["theta"]) - start.theta,
                        float(p["phi"]) - start.phi,
                        float(p["rho"]) - start.rho,
                    )
            except Exception:
                pass

        # Atlas v1: nearest()
        if hasattr(atlas, "nearest"):
            try:
                n = atlas.nearest(start)
                if n is not None and all(hasattr(n, k) for k in ("theta", "phi", "rho")):
                    return (
                        float(n.theta) - start.theta,
                        float(n.phi) - start.phi,
                        float(n.rho) - start.rho,
                    )
            except Exception:
                pass

        return None

    # --------------------------------------------------------
    # Forward (CANONICAL Λ RESOLUTION)
    # --------------------------------------------------------

    def forward(
        self,
        *,
        sigma,
        imago_phase: PhaseCoord,
        atlas=None,
        godel_field=None,
        edge_field=None,
        **extras,
    ) -> LambdaResult:
        """
        Resolve the next phase coordinate deterministically.
        """

        atlas, godel_field, edge_field = self._route_fields(
            atlas, godel_field, edge_field, extras
        )

        # Starting phase (Sigma or Imago fallback)
        start_phase = self._resolve_phase(
            getattr(sigma, "current_phase", None), imago_phase
        )
        start = start_phase.clamp()

        xi = float(getattr(sigma, "xi", 1.0))
        spread = float(getattr(sigma, "spread", 0.0))

        mode_tags = ["POOR", "PCM"]

        # --- PCM: pull toward Imago ---
        theta = start.theta + self.pcm_gain * (imago_phase.theta - start.theta)
        phi = start.phi + self.pcm_gain * (imago_phase.phi - start.phi)
        rho = start.rho + self.pcm_gain * (imago_phase.rho - start.rho)

        # --- EDGE field (optional, inactive in SAFE MODE) ---
        if edge_field is not None and hasattr(edge_field, "resultant_vector"):
            try:
                v = edge_field.resultant_vector(start)
                theta += self.edge_gain * float(v[0])
                phi += self.edge_gain * float(v[1])
                rho += self.edge_gain * float(v[2])
                mode_tags.append("EDGE")
            except Exception:
                pass

        # --- GODEL field (structural memory) ---
        if godel_field is not None and hasattr(godel_field, "resultant_vector"):
            try:
                v = godel_field.resultant_vector(start)
                theta += self.godel_gain * float(v[0])
                phi += self.godel_gain * float(v[1])
                rho += self.godel_gain * float(v[2])
                mode_tags.append("GODEL_FIELD")
            except Exception:
                pass

        # --- ATLAS field (global stabilizer) ---
        if atlas is not None:
            v = self._atlas_pull_vector(atlas, start)
            if v is not None:
                theta += self.atlas_gain * float(v[0])
                phi += self.atlas_gain * float(v[1])
                rho += self.atlas_gain * float(v[2])
                mode_tags.append("ATLAS")

        chosen = PhaseCoord(theta, phi, rho).clamp()

        return LambdaResult(
            mode=" + ".join(mode_tags),
            confidence=self._confidence(xi, spread),
            xi=round(xi, 4),
            chosen=chosen,
        )

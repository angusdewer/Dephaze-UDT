# ============================================================
# DEPHAZE UDT — CORE ENGINE (SAFE MODE FREEZE)
# ============================================================
# Role:
#   Ontological core execution engine of Dephaze UDT.
#   This file defines the deterministic world-state pipeline:
#
#       Input (language)
#         → Phase mapping (Imago)
#         → Lambda decision (POOR + PCM [+ optional fields])
#         → Sigma coherence memory
#         → Gödel structural extraction
#
# Invariants (SAFE MODE):
#   - Deterministic execution only
#   - No training, no learning
#   - No probabilistic inference
#   - No external services required
#   - Phase-space is the primary representation
#   - Language is input only (never authoritative)
#
# WARNING:
#   Modifying behavior here breaks SAFE MODE and invalidates
#   reproducibility, auditability, and Zenodo freeze guarantees.
#
# ============================================================

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple, List

from core.phase import PhaseMapper, PhaseCoord, PromptStarMap, default_topology
from core.sigma import SigmaState
from core.lambda_engine import LambdaEngine, LambdaResult
from core.godel import GodelEngine, GodelOutput, Relation
from core.godel_field import GodelField
from core.prompt_classifier import classify_prompt, PromptKind
from core.godel_normalizer import normalize_relations


# ============================================================
# Wiki provider interface (OPTIONAL, SAFE MODE COMPATIBLE)
# ============================================================

class WikiProvider:
    """
    Optional external knowledge provider.
    Must be deterministic and read-only.
    """
    def search_and_fetch(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        raise NotImplementedError


# ============================================================
# Output bundle (CANONICAL API SURFACE)
# ============================================================

@dataclass
class UDTBundle:
    """
    Canonical structured output of a Dephaze UDT forward pass.
    """
    prompt: str
    imago_phase: PhaseCoord
    lambda_result: LambdaResult
    sigma_audit: Dict[str, Any]
    godel: GodelOutput
    wiki_title: Optional[str] = None
    wiki_extract: Optional[str] = None


# ============================================================
# Dephaze UDT Core Engine
# ============================================================

class DephazeUDT:
    """
    Deterministic world-state engine implementing the Dephaze core.
    """

    def __init__(
        self,
        *,
        history_size: int = 64,
        n_samples: int = 64,
        strict_anchor: bool = True,
        anchors: Optional[Dict[str, PhaseCoord]] = None,
        atlas: Optional[Any] = None,
        wiki: Optional[WikiProvider] = None,
        topology=None,
        # Gödel-field parameters (structural influence only)
        godel_user_weight: float = 0.60,
        godel_wiki_weight: float = 0.85,
        godel_global_weight: float = 0.50,
        godel_gate_min_xi: float = 0.62,
        godel_gate_max_spread: float = 0.80,
    ) -> None:

        # --- Phase topology ---
        self.topology = topology or default_topology()
        self.mapper = PhaseMapper(topology=self.topology)

        # --- Sigma coherence memory ---
        self.sigma = SigmaState(history_size=history_size)

        # --- Lambda decision engine ---
        # Backward compatible: ignores unknown kwargs safely
        self.lambda_engine = LambdaEngine(
            topology=self.topology,
            n_samples=n_samples,
        )

        # --- Structural extractors ---
        self.godel_engine = GodelEngine()
        self.stars = PromptStarMap()

        # --- Configuration ---
        self.strict_anchor = bool(strict_anchor)
        self.anchors = anchors or {}
        self.atlas = atlas
        self.wiki = wiki

        # --- Gödel relation field (ACTIVE but gated) ---
        self.godel_field = GodelField()
        try:
            self.lambda_engine.godel_field = self.godel_field
        except Exception:
            pass

        # --- Edge-field placeholder (NOT ACTIVE IN SAFE MODE) ---
        self.edge_field = None

        # --- Gödel gating parameters ---
        self.godel_user_weight = float(godel_user_weight)
        self.godel_wiki_weight = float(godel_wiki_weight)
        self.godel_global_weight = float(godel_global_weight)
        self.godel_gate_min_xi = float(godel_gate_min_xi)
        self.godel_gate_max_spread = float(godel_gate_max_spread)

        # --- Deterministic subject stoplist ---
        self._bad_subjects = {
            "he", "she", "it", "they", "this", "that", "there", "these", "those",
            "i", "you", "we", "me", "him", "her", "them",
            "a", "an", "the",
        }

    # ========================================================
    # MAIN FORWARD PASS (CANONICAL EXECUTION)
    # ========================================================

    def forward(self, prompt: str, *, use_wiki: bool = True) -> UDTBundle:
        p = (prompt or "").strip()

        # --- Ontological prompt classification ---
        kind = classify_prompt(p)
        ingest_godel = kind not in (PromptKind.NOISE, PromptKind.COMMAND_SHAPE)
        if kind in (PromptKind.NOISE, PromptKind.COMMAND_SHAPE):
            use_wiki = False

        # --- Phase mapping (Imago projection) ---
        imago = self.mapper.text_to_phase(p)
        self.stars.get_or_create(p or "<empty>", imago)

        # --- Lambda decision (world-state resolution) ---
        lam = self.lambda_engine.forward(
            sigma=self.sigma,
            imago_phase=imago,
            atlas=self.atlas,
            godel_field=self.godel_field,
            edge_field=self.edge_field,
        )

        # --- Sigma coherence update ---
        self.sigma.update(lam.chosen)
        sigma_a = self.sigma.audit()

        # --- Optional wiki fetch (read-only) ---
        wiki_title = None
        wiki_extract = None
        if use_wiki and self.wiki and p:
            try:
                wiki_title, wiki_extract = self.wiki.search_and_fetch(p)
            except Exception:
                pass

        # --- Gödel extraction (structural relations only) ---
        user_out = self.godel_engine.extract(p)
        wiki_out = self.godel_engine.extract(wiki_extract or "")
        global_snippet = getattr(lam, "global_fact_snippet", "") or ""
        glob_out = self.godel_engine.extract(global_snippet)

        # --- Normalize and clean relations ---
        clean_user_rel = self._clean_relations(
            normalize_relations(user_out.relations)
        )
        clean_wiki_rel = self._clean_relations(
            normalize_relations(wiki_out.relations)
        )
        clean_glob_rel = self._clean_relations(
            normalize_relations(glob_out.relations)
        )

        merged = GodelOutput(
            relations=clean_user_rel + clean_wiki_rel + clean_glob_rel,
            mentions=list(dict.fromkeys(
                user_out.mentions + wiki_out.mentions + glob_out.mentions
            )),
        )

        # --- Gödel-field ingest (GATED, SAFE MODE) ---
        if ingest_godel:
            self._ingest_godel_field(
                sigma_audit=sigma_a,
                user_rel=clean_user_rel,
                wiki_rel=clean_wiki_rel,
                global_rel=clean_glob_rel,
            )

        return UDTBundle(
            prompt=p,
            imago_phase=imago,
            lambda_result=lam,
            sigma_audit=sigma_a,
            godel=merged,
            wiki_title=wiki_title,
            wiki_extract=wiki_extract,
        )

    # ========================================================
    # Gating and strength functions
    # ========================================================

    def _gate_ok(self, sigma_audit: Dict[str, Any]) -> bool:
        xi = float(sigma_audit.get("xi", 0.0))
        spread = float(sigma_audit.get("spread", 999.0))
        return xi >= self.godel_gate_min_xi and spread <= self.godel_gate_max_spread

    def _rel_strength(self, base_weight: float, sigma_audit: Dict[str, Any]) -> float:
        xi = float(sigma_audit.get("xi", 0.0))
        spread = float(sigma_audit.get("spread", 999.0))
        damp = math.exp(-0.85 * max(0.0, spread))
        return max(0.0, float(base_weight) * xi * damp)

    # ========================================================
    # Relation cleaning (output + ingest safety)
    # ========================================================

    def _norm_node(self, s: str) -> str:
        s = (s or "").strip()
        while s.startswith("(") and s.endswith(")") and len(s) > 2:
            s = s[1:-1].strip()
        return s

    def _reject_relation(self, subj: str, rel: str, obj: str) -> bool:
        subj_l = subj.lower().strip()
        obj_l = obj.lower().strip()
        rel_l = (rel or "").lower().strip()

        if not subj or not obj or not rel_l:
            return True
        if subj_l in self._bad_subjects:
            return True
        if len(subj) < 2 or len(obj) < 2:
            return True
        if subj_l.startswith("born "):
            return True
        if obj_l in {"one", "a", "an", "the"}:
            return True
        return False

    def _clean_relations(self, rels: List[Relation]) -> List[Relation]:
        out: List[Relation] = []
        for r in rels:
            subj = self._norm_node(r.subject)
            obj = self._norm_node(r.object)
            rel = (r.relation or "").strip()
            if self._reject_relation(subj, rel, obj):
                continue
            out.append(Relation(subject=subj, relation=rel, object=obj))
        return out

    # ========================================================
    # Gödel-field ingest (STRUCTURAL MEMORY)
    # ========================================================

    def _ingest_godel_field(
        self,
        *,
        sigma_audit: Dict[str, Any],
        user_rel: List[Relation],
        wiki_rel: List[Relation],
        global_rel: List[Relation],
    ) -> None:
        if not self._gate_ok(sigma_audit):
            return

        def push(relations: List[Relation], strength: float, origin: str, limit: int) -> None:
            for r in relations[:limit]:
                self.godel_field.add_relation(
                    subject=r.subject,
                    relation=str(r.relation or "").strip().lower(),
                    object_=r.object,
                    mapper=self.mapper,
                    strength=float(strength),
                    origin=origin,
                )

        s_user = self._rel_strength(self.godel_user_weight, sigma_audit)
        s_wiki = self._rel_strength(self.godel_wiki_weight, sigma_audit)
        s_glob = self._rel_strength(self.godel_global_weight, sigma_audit)

        push(user_rel, s_user, "user", 8)
        push(wiki_rel, s_wiki, "wiki", 10)
        if global_rel:
            push(global_rel, s_glob, "global", 6)

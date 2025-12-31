# ============================================================
# DEPHAZE UDT — FINAL CLI (HEADLESS ENTRY POINT)
# SAFE MODE — DETERMINISTIC — FLUX ENABLED
# ============================================================
# Role:
#   Canonical command-line interface for Dephaze UDT.
#   Integrates UDT (Structure), Flux (Generation), Godel (Filter).
#
# Purpose:
#   - Deterministic structural analysis from shell / CI
#   - Scriptable, reproducible execution
#   - Noise-safe, governance-controlled Wiki usage
#   - Capable of generating hypothesis via Phi^3 Flux
#
# This is NOT:
#   - an AI model
#   - an LLM wrapper
#   - a crawler
#   - a server
#
# This IS:
#   - a headless structural analyzer
#   - ontology-first, phase-space driven
#   - SAFE MODE compliant
# ============================================================

from __future__ import annotations
import argparse
import json
import requests
import re
import math
from typing import Optional, Tuple
from dataclasses import dataclass

# Core imports
from core.dephaze import DephazeUDT, WikiProvider
from core.atlas_field import AtlasField
from core.phase_field import PhaseField, PhaseChannel


# ============================================================
# 1. THE PHYSICS (Constants)
# ============================================================
PHI = (1.0 + 5.0**0.5) / 2.0
PHI3 = PHI**3
CRITICAL_RESONANCE = 1.0 / math.sqrt(PHI3)


# ============================================================
# 2. FLUX MOTOR (The "Soul" / Generative Hallucination)
# ============================================================
class Phi3FluxMotor:
    """
    This module is responsible for 'creative madness'.
    It does not read data; it perturbs (vibrates) based on Phi^3 geometry.
    """
    def __init__(self, intensity: float = 0.15):
        self.intensity = intensity

    def ignite(self, seed_phase, entropy_key: int = 0):
        """
        Generates a deterministic 'hallucination' based on the seed.
        """
        # 1. Topological Twist - The Creative Leap
        d_theta = self.intensity * math.sin(seed_phase.phi * PHI3 + entropy_key)
        d_phi   = self.intensity * math.cos(seed_phase.theta * PHI3 + entropy_key)
        
        # 2. Energy Injection (Rho modulation)
        new_rho = seed_phase.rho * (1.0 + (self.intensity / PHI))
        
        # 3. Dephaze Limit (Prevent runaway infinity)
        if new_rho > 1.0:
            new_rho = 1.0 - (new_rho - 1.0)  # Rebound
            
        # Return modified coordinates (preserving type structure)
        return type(seed_phase)(
            theta = seed_phase.theta + d_theta,
            phi   = seed_phase.phi + d_phi,
            rho   = new_rho
        )


# ============================================================
# 3. GODEL FILTER (The "Mind" / Translator)
# ============================================================
@dataclass
class GodelVerdict:
    status: str      # "FACT", "HYPOTHESIS", "NOISE"
    confidence: float
    message: str
    target_star: Optional[str] = None

class GodelFilter:
    """
    Decides whether the hallucination is noise or genius.
    ROBUST VERSION: Handles list-based Atlas structures.
    """
    def __init__(self, atlas: AtlasField):
        self.atlas = atlas
        self.min_dist = 0.05  # Closer -> Fact
        self.max_dist = 0.55  # Further -> Noise

    def audit(self, candidate_phase) -> GodelVerdict:
        best_dist = 999.0
        best_star = None
        
        # Prepare Candidate XYZ
        cr, ct, cp = candidate_phase.rho, candidate_phase.theta, candidate_phase.phi
        cx = cr * math.sin(ct) * math.cos(cp)
        cy = cr * math.sin(ct) * math.sin(cp)
        cz = cr * math.cos(ct)

        # Iterate through Atlas (List safe)
        stars_container = self.atlas.stars
        iterator = stars_container.values() if isinstance(stars_container, dict) else stars_container

        for star in iterator:
            try:
                if isinstance(star, dict):
                    sx, sy, sz = star['x'], star['y'], star['z']
                    s_label = star.get('label', 'unknown')
                else:
                    sx, sy, sz = star.x, star.y, star.z
                    s_label = getattr(star, 'label', 'unknown')
            except AttributeError:
                continue

            d = math.sqrt((cx-sx)**2 + (cy-sy)**2 + (cz-sz)**2)
            if d < best_dist:
                best_dist = d
                best_star = s_label

        # Verdict Logic
        if best_dist < self.min_dist:
            return GodelVerdict("FACT", 1.0 - best_dist, "KNOWN FACT", best_star)
        
        if best_dist < self.max_dist:
            coherence = 1.0 - (best_dist / self.max_dist)
            return GodelVerdict("HYPOTHESIS", coherence, "VALID ASSOCIATION", best_star)
            
        return GodelVerdict("NOISE", 0.0, "INCOHERENT NOISE", None)


# ============================================================
# REAL WIKI PROVIDER (MINIMAL, GOVERNED)
# ============================================================

class RealWiki(WikiProvider):
    """
    Minimal, deterministic Wikipedia provider for CLI usage.
    """
    HEADERS = {
        "User-Agent": "DephazeUDT/1.0 (contact: dewerangus@gmail.com)"
    }

    def __init__(self, lang: str = "en", timeout: float = 5.0):
        self.lang = lang
        self.timeout = timeout

    def search_and_fetch(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            api = f"https://{self.lang}.wikipedia.org/w/api.php"
            
            # 1. Search
            r = requests.get(
                api,
                headers=self.HEADERS,
                params={"action": "query", "list": "search", "srsearch": query, "format": "json"},
                timeout=self.timeout,
            )
            r.raise_for_status()
            hits = r.json().get("query", {}).get("search", [])
            if not hits: return None, None
            title = hits[0]["title"]

            # 2. Extract
            r = requests.get(
                api,
                headers=self.HEADERS,
                params={"action": "query", "prop": "extracts", "titles": title, "exintro": True, "explaintext": True, "format": "json"},
                timeout=self.timeout,
            )
            r.raise_for_status()
            pages = r.json().get("query", {}).get("pages", {})
            page = next(iter(pages.values()), {})
            return title, page.get("extract")

        except Exception:
            return None, None


# ============================================================
# NOISE + STRUCTURAL HEURISTICS
# ============================================================

KNOWN_MORPHEMES = (
    "ion", "energy", "quantum", "theory", "field", "mass",
    "relativity", "particle", "wave", "space", "time"
)

def looks_like_real_term(s: str) -> bool:
    s = s.strip()
    if not s: return False
    sl = s.lower()
    if " " in sl: return True
    if s[0].isupper() and any(c.islower() for c in s[1:]): return True
    for m in KNOWN_MORPHEMES:
        if sl.endswith(m): return True
    if not any(v in sl for v in "aeiou"): return False
    return True

# ============================================================
# WIKI GOVERNANCE POLICY (FINAL)
# ============================================================

def wiki_allowed(label: str, xi: float, known: set[str], history_len: int) -> bool:
    s = (label or "").strip()
    if not s: return False
    sl = s.lower()
    if sl in known: return False
    if len(sl) < 3: return False
    if not any(c.isalpha() for c in sl): return False
    if not looks_like_real_term(s): return False
    if history_len <= 1: return True
    if xi > 0.70: return False
    if xi < 0.40: return False
    return True

def wiki_result_matches(prompt: str, title: str) -> bool:
    if not title: return False
    p = prompt.lower()
    t = title.lower()
    if t in p or p in t: return True
    for w in [w for w in t.split() if len(w) > 2]:
        if w in p: return True
    return False


# ============================================================
# CLI ENTRY POINT
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dephaze UDT – Deterministic Structural Analyzer (SAFE MODE + FLUX)"
    )
    parser.add_argument("prompt", type=str)
    parser.add_argument("--no-wiki", action="store_true")
    # Argument for paranoids/testing: force flux threshold higher
    parser.add_argument("--flux-threshold", type=float, default=0.45, help="Confidence threshold to trigger Flux Motor")
    args = parser.parse_args()

    known = set()

    # 1. LOAD ATLAS
    try:
        atlas = AtlasField.load("examples/atlas_stars.json")
    except Exception as e:
        print(f"[Warning] Could not load Atlas: {e}")
        atlas = None

    # 2. INIT COMPONENTS
    phase_field = PhaseField(
        channels={
            "entity": PhaseChannel("entity", 0.2, 0.2, 1.0),
            "role": PhaseChannel("role", 0.5, 0.45, 1.0),
            "group": PhaseChannel("group", 0.35, 0.6, 1.0),
            "definition": PhaseChannel("definition", 0.8, 0.8, 1.0),
        }
    )

    udt = DephazeUDT(
        history_size=32,
        n_samples=64,
        strict_anchor=True,
        anchors={},
        atlas=atlas,
        wiki=None,
    )
    
    # Init Flux & Godel
    flux_motor = Phi3FluxMotor(intensity=0.18)
    godel_filter = GodelFilter(atlas) if atlas else None

    # --------------------------------------------------------
    # PASS 1 — STRUCTURAL ANALYSIS (UDT)
    # --------------------------------------------------------
    udt.lambda_engine.phase_field = phase_field # Ensure field is linked
    bundle = udt.forward(args.prompt, use_wiki=False)
    
    flux_info = None

    # --------------------------------------------------------
    # PASS 1.5 — FLUX MOTOR INTERVENTION
    # --------------------------------------------------------
    confidence = bundle.lambda_result.confidence
    
    if confidence < args.flux_threshold and godel_filter:
        # Deterministic entropy from prompt
        entropy_key = sum(ord(c) for c in args.prompt)
        
        # Ignite Motor
        seed_phase = bundle.lambda_result.chosen
        hypo_phase = flux_motor.ignite(seed_phase, entropy_key)
        
        # Audit Hypothesis
        verdict = godel_filter.audit(hypo_phase)
        
        if verdict.status == "HYPOTHESIS":
            flux_info = f"GENERATED HYPOTHESIS -> Linked to '{verdict.target_star}' (conf={verdict.confidence:.2f})"
            bundle.lambda_result.mode = "FLUX_HYPOTHESIS"
            bundle.lambda_result.confidence = verdict.confidence
            bundle.lambda_result.chosen = hypo_phase
        elif verdict.status == "FACT":
            flux_info = f"FLUX CONVERGED TO FACT -> '{verdict.target_star}'"
        else:
            flux_info = "FLUX REJECTED (NOISE)"

    # --------------------------------------------------------
    # PASS 2 — CONDITIONAL WIKI
    # --------------------------------------------------------
    if (not args.no_wiki) and wiki_allowed(
        args.prompt,
        bundle.lambda_result.xi,
        known,
        bundle.sigma_audit["history_len"],
    ):
        wiki = RealWiki()
        title, extract = wiki.search_and_fetch(args.prompt)
        if wiki_result_matches(args.prompt, title):
            udt.wiki = wiki
            bundle = udt.forward(args.prompt, use_wiki=True)

    # --------------------------------------------------------
    # OUTPUT (MACHINE READABLE)
    # --------------------------------------------------------
    print("=== Dephaze UDT – Structural Output ===")
    print(f"Prompt: {bundle.prompt}")

    if flux_info:
        print(f"\nFlux Status: {flux_info}")

    print("\nLambda Decision:")
    print(f"  mode: {bundle.lambda_result.mode}")
    print(f"  conf: {bundle.lambda_result.confidence:.4f}")
    
    # Imago Phase
    im = bundle.imago_phase
    print(f"\nImago Phase: T={im.theta:.4f} P={im.phi:.4f} R={im.rho:.4f}")

    print("\nSigma Audit:")
    for k, v in bundle.sigma_audit.items():
        print(f"  {k}: {v}")

    # Relations
    if getattr(bundle, "godel", None) and bundle.godel.relations:
        print("\nRelations:")
        for r in bundle.godel.relations:
            print(f"  ({r.subject}) --[{r.relation}]--> ({r.object})")

    # Wiki attachment
    if bundle.wiki_title:
        print("\nWiki Attachment:")
        print(f"  title  : {bundle.wiki_title}")
        print(f"  extract: {bundle.wiki_extract[:300]}...")

    print("\n=== END ===")


if __name__ == "__main__":
    main()
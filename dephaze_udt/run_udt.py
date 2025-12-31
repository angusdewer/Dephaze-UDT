# ============================================================
# DEPHAZE UDT — STARSHIP CONSOLE (FLUX ENABLED)
# DETERMINISTIC STRUCTURE + GENERATIVE PHI^3 MOTOR
# ============================================================
# Role:
#   Canonical interactive entry point for Dephaze UDT.
#   Integrates UDT (Structure), Flux (Generation), Godel (Filter).
#
# Components:
#   1. UDT Engine: The rigid body (Structure)
#   2. Phi3 Flux Motor: The engine (Creative Hallucination)
#   3. Godel Filter: The navigation (Truth/Topology Check)
#
# ============================================================

import math
import numpy as np
from collections import deque
from dataclasses import dataclass
from typing import Tuple, Optional, Any

# Core imports
from core.dephaze import DephazeUDT
from core.atlas_field import AtlasField
from core.phase_field import PhaseField, PhaseChannel
from wiki.wiki_real import RealWiki
from cli import wiki_allowed

LOG_PATH = "udt_last.log"

# ============================================================
# 1. THE PHYSICS (Constants)
# ============================================================
PHI = (1.0 + 5.0**0.5) / 2.0
PHI3 = PHI**3  # ≈ 4.236
CRITICAL_RESONANCE = 1.0 / np.sqrt(PHI3)

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
        # We preserve the original object type but modify values.
        # Assuming seed_phase has theta, phi, rho attributes.
        
        # 1. Topological Twist - The Creative Leap
        d_theta = self.intensity * math.sin(seed_phase.phi * PHI3 + entropy_key)
        d_phi   = self.intensity * math.cos(seed_phase.theta * PHI3 + entropy_key)
        
        # 2. Energy Injection (Rho modulation)
        new_rho = seed_phase.rho * (1.0 + (self.intensity / PHI))
        
        # 3. Dephaze Limit (Prevent runaway infinity)
        if new_rho > 1.0:
            new_rho = 1.0 - (new_rho - 1.0)  # Rebound
            
        # Return modified coordinates (in the same structure)
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
    target_star: Optional[str] = None # Name of the nearest star

class GodelFilter:
    """
    Decides whether the hallucination is noise or genius.
    ROBUST VERSION: Handles list-based Atlas structures.
    """
    def __init__(self, atlas: AtlasField):
        self.atlas = atlas
        # The "Goldilocks Zone": Not too known, not too alien
        self.min_dist = 0.05  # Closer than this -> Fact (Boring)
        self.max_dist = 0.55  # Further than this -> Noise (Falsehood)

    def audit(self, candidate_phase) -> GodelVerdict:
        best_dist = 999.0
        best_star = None
        
        # 1. Prepare Candidate XYZ coordinates
        # (Faster to calculate here than inside the loop)
        cr, ct, cp = candidate_phase.rho, candidate_phase.theta, candidate_phase.phi
        cx = cr * math.sin(ct) * math.cos(cp)
        cy = cr * math.sin(ct) * math.sin(cp)
        cz = cr * math.cos(ct)

        # 2. Iterate through Atlas (which is a LIST)
        # Access stars regardless of whether they are objects or dicts
        stars_container = self.atlas.stars
        
        # Safety check: if it happens to be a dict
        if isinstance(stars_container, dict):
            iterator = stars_container.values()
        else:
            iterator = stars_container

        for star in iterator:
            # Data extraction (Safe Mode)
            try:
                if isinstance(star, dict):
                    sx, sy, sz = star['x'], star['y'], star['z']
                    s_label = star.get('label', 'unknown')
                else:
                    # Object attributes (Star class)
                    sx, sy, sz = star.x, star.y, star.z
                    s_label = getattr(star, 'label', 'unknown')
            except AttributeError:
                continue # Skip damaged stars

            # Distance calculation (Euclidean approximation in Cartesian)
            d = math.sqrt((cx-sx)**2 + (cy-sy)**2 + (cz-sz)**2)
                
            if d < best_dist:
                best_dist = d
                best_star = s_label

        # 3. Verdict (Godel Logic)
        
        # CASE 1: FACT (Too close)
        if best_dist < self.min_dist:
            return GodelVerdict("FACT", 1.0 - best_dist, "KNOWN FACT (Too close)", best_star)
            
        # CASE 2: HYPOTHESIS (The Goal)
        if best_dist < self.max_dist:
            # Coherence increases as we approach resonance
            coherence = 1.0 - (best_dist / self.max_dist)
            return GodelVerdict("HYPOTHESIS", coherence, "VALID ASSOCIATION (Resonance)", best_star)
            
        # CASE 3: NOISE
        return GodelVerdict("NOISE", 0.0, "INCOHERENT NOISE (No connection)", None)

# ============================================================
# Tee logger (console + file)
# ============================================================

class Tee:
    def __init__(self, path: str):
        self.f = open(path, "w", encoding="utf-8", errors="replace")

    def write(self, s: str):
        print(s, end="")
        self.f.write(s)
        self.f.flush()

    def close(self):
        try:
            self.f.close()
        except Exception:
            pass

# ============================================================
# Banner
# ============================================================

BANNER = """
=====================================================
 Dephaze STARSHIP – Structural Console (FLUX ENABLED)
 UDT (Body) | Flux Motor (Soul) | Godel (Mind)
-----------------------------------------------------
 Ctrl+C = STOP
=====================================================
"""

# ============================================================
# Wiki classification
# ============================================================

def classify_wiki_channel(title: str, extract: str) -> str:
    t = (title or "").lower()
    e = (extract or "").lower()
    if "rock band" in e or "band" in e or "discography" in t or "members" in t:
        return "group"
    if "electric current" in e or "alternating current" in e or "direct current" in e:
        return "definition"
    if "musician" in e or "guitarist" in e:
        return "role"
    return "entity"

# ============================================================
# Sigma snapshot
# ============================================================

def sigma_snapshot(udt: DephazeUDT):
    return {"xi": udt.sigma.xi, "recent": list(udt.sigma.history.recent)}

def sigma_restore(udt: DephazeUDT, snap):
    udt.sigma.xi = snap["xi"]
    udt.sigma.history.recent = deque(snap["recent"])

# ============================================================
# Output formatting (Extended)
# ============================================================

def format_bundle(bundle, header: str = None, flux_info: str = None) -> str:
    lines = []
    if header:
        lines.append(header)

    lines.append("\n=== Dephaze UDT – Structural Output ===")
    lines.append(f"Prompt: {bundle.prompt}")

    # FLUX STATUS DISPLAY
    if flux_info:
        lines.append(f"\n[FLUX MOTOR ACTIVE]: {flux_info}")
    
    im = bundle.imago_phase
    lines.append("\nImago phase:")
    lines.append(f"  θ={im.theta:.4f} φ={im.phi:.4f} ρ={im.rho:.4f}")

    lr = bundle.lambda_result
    lines.append("\nLambda decision:")
    lines.append(f"  mode       : {lr.mode}")
    lines.append(f"  confidence : {lr.confidence:.4f}")
    lines.append(f"  xi         : {lr.xi:.4f}")
    lines.append(
        f"  chosen     : θ={lr.chosen.theta:.4f} "
        f"φ={lr.chosen.phi:.4f} "
        f"ρ={lr.chosen.rho:.4f}"
    )

    s = bundle.sigma_audit
    lines.append("\nSigma audit:")
    lines.append(f"  history_len: {s['history_len']}")
    lines.append(f"  xi         : {s['xi']}")
    lines.append(f"  spread     : {s['spread']}")

    if getattr(bundle, "godel", None) and bundle.godel.relations:
        lines.append("\nRelations (Extracted):")
        for r in bundle.godel.relations:
            lines.append(f"  ({r.subject}) --[{r.relation}]--> ({r.object})")

    lines.append("\n=== END ===\n")
    return "\n".join(lines)

# ============================================================
# MAIN LOOP (INTEGRATED)
# ============================================================

def main():
    tee = Tee(LOG_PATH)

    try:
        tee.write(BANNER + "\n")

        # 1. LOAD SYSTEM
        atlas = AtlasField.load("examples/atlas_stars.json")
        tee.write(f"[System] Atlas Loaded: {len(atlas.stars)} stars\n")

        # 2. START COMPONENTS
        # UDT (The Body)
        phase_field = PhaseField(
            channels={
                "entity": PhaseChannel("entity", 0.2, 0.2, 1.0),
                "role": PhaseChannel("role", 0.5, 0.45, 1.0),
                "group": PhaseChannel("group", 0.35, 0.6, 1.0),
                "definition": PhaseChannel("definition", 0.8, 0.8, 1.0),
            }
        )
        udt = DephazeUDT(history_size=64, n_samples=64, strict_anchor=True)
        udt.lambda_engine.atlas_field = atlas
        udt.lambda_engine.phase_field = phase_field
        
        # Flux Motor (The Soul)
        flux_motor = Phi3FluxMotor(intensity=0.18)
        
        # Godel Filter (The Mind)
        godel_filter = GodelFilter(atlas)
        
        tee.write("[System] Flux Motor: ONLINE (Phi^3 Geometry)\n")
        tee.write("[System] Godel Filter: ONLINE (Topology Audit)\n")

        wiki = RealWiki(max_results=3)

        while True:
            try:
                prompt = input("UDT > ")
            except KeyboardInterrupt:
                tee.write("\nExit.\n")
                break

            prompt = prompt.strip()
            if not prompt or prompt.lower() in {"exit", "quit", "q"}:
                tee.write("Exit.\n")
                break

            # ----------------------------------------------------
            # STEP 1: STANDARD UDT (Structural Analysis)
            # ----------------------------------------------------
            udt.lambda_engine.phase_channel = "entity"
            bundle = udt.forward(prompt, use_wiki=False)
            
            flux_status_msg = None
            
            # ----------------------------------------------------
            # STEP 2: FLUX MOTOR INTERVENTION (If needed)
            # ----------------------------------------------------
            # If system is uncertain (low confidence), but not Wiki
            confidence = bundle.lambda_result.confidence
            
            # High threshold (0.95) set for demonstration purposes
            # In production, this might be lower (e.g., 0.45)
            if confidence < 0.95:
                # No certain match. Igniting the hallucination motor.
                tee.write(f"\n[...Low Signal ({confidence:.2f}). Igniting Flux Motor...]\n")
                
                # Entropy from prompt (to remain deterministic)
                entropy_key = sum(ord(c) for c in prompt)
                
                # GENERATION
                seed_phase = bundle.lambda_result.chosen
                hypo_phase = flux_motor.ignite(seed_phase, entropy_key)
                
                # FILTERING
                verdict = godel_filter.audit(hypo_phase)
                
                if verdict.status == "HYPOTHESIS":
                    flux_status_msg = f"GENERATED HYPOTHESIS -> Linked to '{verdict.target_star}' ({verdict.confidence:.2f})"
                    # Overwrite result with creative hypothesis
                    bundle.lambda_result.mode = "FLUX_HYPOTHESIS"
                    bundle.lambda_result.confidence = verdict.confidence
                    bundle.lambda_result.chosen = hypo_phase
                    
                elif verdict.status == "NOISE":
                    flux_status_msg = "FLUX REJECTED (Noise detected by Godel)"
                    # Keep original (weak) result, or flag error
                    
                elif verdict.status == "FACT":
                    flux_status_msg = f"FLUX CONVERGED TO FACT -> '{verdict.target_star}'"
                    # Confirmed known fact

            # Print Result
            tee.write(format_bundle(bundle, flux_info=flux_status_msg))

            # ----------------------------------------------------
            # STEP 3: WIKI BRANCHING (If allowed)
            # ----------------------------------------------------
            # Only go to Wiki if Flux didn't find anything, or explicit request
            if not wiki_allowed(
                prompt,
                bundle.lambda_result.xi,
                set(),
                bundle.sigma_audit["history_len"],
            ):
                continue

            for item in wiki.search_and_fetch_all(prompt):
                channel = classify_wiki_channel(item["title"], item["extract"])
                snap = sigma_snapshot(udt)
                try:
                    udt.lambda_engine.phase_channel = channel
                    text = f"{prompt} :: {item['title']}. {item['extract'][:800]}"
                    branch = udt.forward(text, use_wiki=False)
                    tee.write(
                        format_bundle(
                            branch,
                            header=f"[Branch {channel.upper()}] {item['title']}",
                        )
                    )
                finally:
                    sigma_restore(udt, snap)

    finally:
        tee.close()
        print(f"\n[LOG] Copy from: {LOG_PATH}\n")


if __name__ == "__main__":
    main()
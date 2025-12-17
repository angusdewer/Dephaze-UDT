# ============================================================
# DEPHAZE UDT — ATLAS COMMIT TOOL
# CANONICAL WRITE BARRIER — SAFE MODE ADJACENT
# ============================================================
# Role:
#   Explicit, manual commit tool for growing the numeric
#   Dephaze Atlas (star-map).
#
# Purpose:
#   - Convert validated UDT outputs into numeric atlas stars
#   - Enforce hard stability and coherence gates
#   - Provide an auditable, irreversible commit step
#
# This is NOT:
#   - training
#   - learning
#   - an ingestion daemon
#   - an automated growth loop
#
# This IS:
#   - a write-once structural commit
#   - governed by explicit thresholds
#   - SAFE MODE compliant by construction
#
# IMPORTANT:
#   Atlas growth happens ONLY through this tool.
#   Removing or bypassing this file breaks system guarantees.
# ============================================================

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import time
from dataclasses import dataclass, asdict
from typing import Dict, Any, Tuple

from core.dephaze import DephazeUDT
from cli import RealWiki, wiki_allowed, wiki_result_matches, looks_like_real_term


# ------------------------------------------------------------
# CONFIG — CANONICAL THRESHOLDS
# ------------------------------------------------------------

DEFAULT_ATLAS_PATH = "atlas_stars.json"

# UDT validation thresholds
MIN_SIGMA_XI = 0.90
MAX_SIGMA_SPREAD = 0.06

# noise rejection
MIN_LEN = 3


# ------------------------------------------------------------
# STAR MODEL (NUMERIC ONLY)
# ------------------------------------------------------------

@dataclass
class Star:
    """
    Numeric atlas star record.

    Contains:
      - no text memory
      - no learned parameters
      - only numeric coordinates and validation metadata
    """
    star_id: str
    label: str
    x: float
    y: float
    z: float
    r: int
    g: int
    b: int
    weight: int
    sigma_xi: float
    sigma_spread: float
    lambda_confidence: float
    created_utc: int
    updated_utc: int
    source: str  # "udt_validated"


# ------------------------------------------------------------
# UTILS
# ------------------------------------------------------------

def utc_now() -> int:
    return int(time.time())


def normalize_label(s: str) -> str:
    return " ".join((s or "").strip().lower().split())


def make_star_id(label: str) -> str:
    """
    Stable star ID derived from normalized label.
    """
    h = hashlib.sha256(normalize_label(label).encode("utf-8")).hexdigest()[:16]
    return f"star:{h}"


def phase_to_xyz(theta: float, phi: float, rho: float) -> Tuple[float, float, float]:
    """
    Canonical phase → Cartesian mapping.

    Must remain consistent with atlas_field / atlas.py.
    """
    rr = max(0.0, min(1.0, float(rho)))
    x = rr * math.sin(theta) * math.cos(phi)
    y = rr * math.sin(theta) * math.sin(phi)
    z = rr * math.cos(theta)
    return (x, y, z)


def clamp01(v: float) -> float:
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


def to_rgb(sigma_xi: float, spread: float) -> Tuple[int, int, int]:
    """
    Encode validation state into RGB (numeric only).

    G → stability
    B → coherence (Ξ)
    R → instability
    """
    g = int(round(255 * clamp01(1.0 - (spread / MAX_SIGMA_SPREAD))))
    xi_norm = clamp01((sigma_xi - MIN_SIGMA_XI) / max(1e-9, (1.0 - MIN_SIGMA_XI)))
    b = int(round(255 * xi_norm))
    r = int(round(255 * clamp01(1.0 - (0.6 * (g / 255.0) + 0.4 * (b / 255.0)))))
    return (r, g, b)


def load_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {"stars": {}}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json_atomic(path: str, data: Dict[str, Any]) -> None:
    """
    Atomic write to avoid partial corruption.
    """
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def is_noise_prompt(prompt: str) -> bool:
    s = (prompt or "").strip()
    if not s or len(s) < MIN_LEN:
        return True
    if not any(c.isalpha() for c in s):
        return True
    if not looks_like_real_term(s):
        return True
    return False


def validated(bundle) -> Tuple[bool, str]:
    """
    UDT validation gate for atlas commit.
    """
    if is_noise_prompt(bundle.prompt):
        return (False, "noise_prompt")

    s = bundle.sigma_audit or {}
    sigma_xi = float(s.get("xi", 0.0))
    spread = float(s.get("spread", 999.0))

    if sigma_xi < MIN_SIGMA_XI:
        return (False, f"sigma_xi_too_low:{sigma_xi:.6f}")
    if spread > MAX_SIGMA_SPREAD:
        return (False, f"spread_too_high:{spread:.6f}")

    return (True, "ok")


# ------------------------------------------------------------
# COMMIT
# ------------------------------------------------------------

def commit_star(atlas_path: str, star: Star) -> None:
    """
    Commit or update a star in the atlas (append-safe).
    """
    db = load_json(atlas_path)
    stars = db.setdefault("stars", {})

    if star.star_id in stars:
        prev = stars[star.star_id]
        prev["weight"] = int(prev.get("weight", 1)) + 1
        prev["updated_utc"] = star.updated_utc
        prev["sigma_xi"] = star.sigma_xi
        prev["sigma_spread"] = star.sigma_spread
        prev["lambda_confidence"] = star.lambda_confidence
        prev["x"], prev["y"], prev["z"] = star.x, star.y, star.z
        prev["r"], prev["g"], prev["b"] = star.r, star.g, star.b

        aliases = prev.setdefault("aliases", [])
        if star.label and star.label not in aliases and star.label != prev.get("label"):
            aliases.append(star.label)
    else:
        stars[star.star_id] = asdict(star)

    db["updated_utc"] = utc_now()
    db["version"] = db.get("version", 1)
    save_json_atomic(atlas_path, db)


# ------------------------------------------------------------
# MAIN (MANUAL ENTRY POINT)
# ------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Dephaze UDT — Atlas Commit Tool (validated star-map growth)"
    )
    ap.add_argument("prompt", type=str, help="Input to validate and (optionally) commit.")
    ap.add_argument("--atlas", type=str, default=DEFAULT_ATLAS_PATH)
    ap.add_argument("--no-wiki", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    # Isolated UDT instance per run
    udt = DephazeUDT(
        history_size=64,
        n_samples=64,
        strict_anchor=True,
        anchors={},
        atlas=None,
        wiki=None,
    )

    bundle = udt.forward(args.prompt, use_wiki=False)

    if not args.no_wiki:
        allow = wiki_allowed(
            args.prompt,
            bundle.lambda_result.xi,
            known=set(),
            history_len=bundle.sigma_audit["history_len"],
        )
        if allow:
            wiki = RealWiki()
            title, extract = wiki.search_and_fetch(args.prompt)
            if wiki_result_matches(args.prompt, title):
                udt.wiki = wiki
                bundle = udt.forward(args.prompt, use_wiki=True)

    ok, reason = validated(bundle)

    lr = bundle.lambda_result
    chosen = lr.chosen
    x, y, z = phase_to_xyz(chosen.theta, chosen.phi, chosen.rho)

    s = bundle.sigma_audit or {}
    sigma_xi = float(s.get("xi", 0.0))
    spread = float(s.get("spread", 999.0))
    r, g, b = to_rgb(sigma_xi, spread)

    star = Star(
        star_id=make_star_id(args.prompt),
        label=args.prompt.strip(),
        x=x,
        y=y,
        z=z,
        r=r,
        g=g,
        b=b,
        weight=1,
        sigma_xi=sigma_xi,
        sigma_spread=spread,
        lambda_confidence=float(getattr(lr, "confidence", 0.0)),
        created_utc=utc_now(),
        updated_utc=utc_now(),
        source="udt_validated",
    )

    if args.json:
        print(
            json.dumps(
                {
                    "prompt": args.prompt,
                    "validated": ok,
                    "reason": reason,
                    "star": asdict(star),
                    "wiki": {
                        "title": bundle.wiki_title,
                        "attached": bool(bundle.wiki_title),
                    },
                },
                ensure_ascii=False,
            )
        )
        if ok and not args.dry_run:
            commit_star(args.atlas, star)
        return

    print("=== ATLAS COMMIT ===")
    print(f"prompt      : {args.prompt!r}")
    print(f"validated   : {ok} ({reason})")
    print(f"star_id     : {star.star_id}")
    print(f"xyz         : ({star.x:.6f}, {star.y:.6f}, {star.z:.6f})")
    print(f"rgb         : ({star.r}, {star.g}, {star.b})")
    print(f"sigma_xi    : {star.sigma_xi:.6f}")
    print(f"sigma_spread: {star.sigma_spread:.6f}")
    print(f"wiki        : {bundle.wiki_title!r}")

    if ok and not args.dry_run:
        commit_star(args.atlas, star)
        print(f"COMMITTED → {args.atlas}")
    elif ok and args.dry_run:
        print("DRY-RUN (not written)")
    else:
        print("REJECTED (not written)")
    print("=== END ===")


if __name__ == "__main__":
    main()

# ============================================================
# DEPHAZE UDT — STRUCTURAL CONSOLE (ENTRY POINT)
# SAFE MODE — DETERMINISTIC — NO LLM
# ============================================================
# Role:
#   Canonical interactive entry point for Dephaze UDT.
#
# Purpose:
#   - Demonstrate structural reasoning in SAFE MODE
#   - Provide an auditable, reproducible console interface
#   - Serve as first-contact demo for developers and reviewers
#
# This is NOT:
#   - an AI model
#   - an LLM wrapper
#   - a server
#   - a training loop
#
# This IS:
#   - a deterministic structural engine
#   - phase-space driven
#   - ontology-first
#
# SAFE MODE INVARIANTS:
#   - No learning
#   - No weight updates
#   - No background processes
#   - Explicit external boundaries (Wiki)
#
# All console output is mirrored to udt_last.log
# to allow copy without terminal selection.
# ============================================================

from collections import deque
from core.dephaze import DephazeUDT
from core.atlas_field import AtlasField
from core.phase_field import PhaseField, PhaseChannel
from wiki.wiki_real import RealWiki
from cli import wiki_allowed

LOG_PATH = "udt_last.log"


# ------------------------------------------------------------
# Tee logger (console + file)
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# Banner
# ------------------------------------------------------------

BANNER = """
=================================================
 Dephaze UDT – Structural Console (SAFE MODE)
 Deterministic | No LLM | World-feedback ENABLED
-------------------------------------------------
 Ctrl+C = STOP (only at input prompt)
 COPY from udt_last.log (no console selection needed)
=================================================
"""


# ------------------------------------------------------------
# Wiki channel classification (STRUCTURAL)
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# Sigma snapshot / restore (STATE ISOLATION)
# ------------------------------------------------------------

def sigma_snapshot(udt: DephazeUDT):
    return {"xi": udt.sigma.xi, "recent": list(udt.sigma.history.recent)}


def sigma_restore(udt: DephazeUDT, snap):
    udt.sigma.xi = snap["xi"]
    udt.sigma.history.recent = deque(snap["recent"])


# ------------------------------------------------------------
# Output formatting
# ------------------------------------------------------------

def format_bundle(bundle, header: str = None) -> str:
    lines = []
    if header:
        lines.append(header)

    lines.append("\n=== Dephaze UDT – Structural Output ===")
    lines.append(f"Prompt: {bundle.prompt}")

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
    lines.append(f"  current    : {s['current_phase']}")

    if getattr(bundle, "godel", None) and bundle.godel.relations:
        lines.append("\nRelations:")
        for r in bundle.godel.relations:
            lines.append(f"  ({r.subject}) --[{r.relation}]--> ({r.object})")

    if getattr(bundle, "godel", None) and bundle.godel.mentions:
        lines.append("\nMentions:")
        lines.append("  " + ", ".join(bundle.godel.mentions))

    lines.append("\n=== END ===\n")
    return "\n".join(lines)


# ------------------------------------------------------------
# MAIN LOOP (MANUAL, DETERMINISTIC)
# ------------------------------------------------------------

def main():
    tee = Tee(LOG_PATH)

    try:
        tee.write(BANNER + "\n")

        atlas = AtlasField.load("examples/atlas_stars.json")
        tee.write(f"[Atlas] Loaded {len(atlas.stars)} stars\n")

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

            # --- base evaluation ---
            udt.lambda_engine.phase_channel = "entity"
            base = udt.forward(prompt, use_wiki=False)
            tee.write(format_bundle(base))

            # --- optional wiki branching ---
            if not wiki_allowed(
                prompt,
                base.lambda_result.xi,
                set(),
                base.sigma_audit["history_len"],
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

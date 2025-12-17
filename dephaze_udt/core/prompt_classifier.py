# ============================================================
# DEPHAZE UDT — PROMPT ONTOLOGICAL CLASSIFIER
# SAFE MODE FREEZE
# ============================================================
# Role:
#   Deterministic ontological gate for input prompts.
#
#   Classifies input by structural role, NOT by semantics.
#
# This is NOT:
#   - NLP intent classification
#   - a heuristic or ML-based router
#   - language understanding
#
# This IS:
#   - a structural safety gate
#   - a filter for phase-space eligibility
#
# Invariants (SAFE MODE):
#   - Deterministic execution
#   - No learning, no training
#   - Fixed rule set
#
# Modifying these rules alters system boundaries
# and breaks reproducibility guarantees.
# ============================================================

from enum import Enum, auto
import re


# ============================================================
# Prompt Kinds (ONTOLOGICAL ROLES)
# ============================================================

class PromptKind(Enum):
    ENTITY = auto()          # "angus young"
    STATEMENT = auto()       # "Angus Young is a guitarist"
    COMMAND_SHAPE = auto()   # "python run_udt.py"
    NOISE = auto()           # empty / junk


# ============================================================
# Command-shaped detection patterns
# ============================================================

_COMMAND_PREFIXES = (
    "python ",
    "pip ",
    "cd ",
    "ls ",
    "dir ",
    "rm ",
    "run ",
)

_COMMAND_PATTERN = re.compile(
    r"""
    (^|\s)python\s+.+\.py$ |
    (^|\s)(pip|cd|ls|dir|rm)\s+ |
    \.py$
    """,
    re.VERBOSE | re.IGNORECASE,
)


# ============================================================
# Classification
# ============================================================

def classify_prompt(prompt: str) -> PromptKind:
    """
    Classify input prompt by ontological role.

    Returns:
      PromptKind

    Notes:
      - Language meaning is NOT interpreted here.
      - This function only determines whether the input
        should enter the phase-space pipeline.
    """
    if not prompt:
        return PromptKind.NOISE

    p = prompt.strip()
    if not p:
        return PromptKind.NOISE

    low = p.lower()

    # --- COMMAND-SHAPED INPUT ---
    if low.startswith(_COMMAND_PREFIXES):
        return PromptKind.COMMAND_SHAPE

    if _COMMAND_PATTERN.search(low):
        return PromptKind.COMMAND_SHAPE

    # --- STATEMENT (simple structural copula) ---
    if " is " in low or " are " in low:
        return PromptKind.STATEMENT

    # --- DEFAULT: ENTITY ---
    return PromptKind.ENTITY

# ============================================================
# DEPHAZE UDT — GÖDEL RELATION NORMALIZER
# SAFE MODE FREEZE
# ============================================================
# Role:
#   Deterministic ontological normalization of implicit metadata
#   embedded in entity labels.
#
# Examples:
#   "Alan Turing (born 1912)"  →  (Alan Turing) --born_on--> (1912)
#   "Band X (formed 1998)"     →  (Band X) --formed_on--> (1998)
#
# This is NOT:
#   - NLP
#   - a dependency parser
#   - a learned extractor
#
# This IS:
#   - rule-based ontological decomposition
#   - deterministic and reproducible
#   - SAFE MODE compliant
#
# Invariants (SAFE MODE):
#   - No training, no learning
#   - Fixed rules, fixed outputs
#   - Regex used only as a structural trigger
#
# Modifying rules changes ontological semantics
# and breaks reproducibility guarantees.
# ============================================================

from __future__ import annotations

import re
from typing import List

from core.godel import Relation


# ============================================================
# Implicit metadata patterns (CANONICAL SET)
# ============================================================

_BORN_RE = re.compile(r"\(born\s+([^)]+)\)", re.IGNORECASE)
_DIED_RE = re.compile(r"\(died\s+([^)]+)\)", re.IGNORECASE)
_FORMED_RE = re.compile(r"\(formed\s+([^)]+)\)", re.IGNORECASE)


# ============================================================
# Normalization
# ============================================================

def normalize_relations(relations: List[Relation]) -> List[Relation]:
    """
    Normalize implicit metadata embedded in subject strings.

    Operation:
      - Extracts '(born …)', '(died …)', '(formed …)' annotations
      - Emits explicit ontological relations:
            born_on, died_on, formed_on
      - Preserves original semantic relations unchanged

    Input:
      Raw Gödel relations

    Output:
      Expanded, ontology-safe relations
    """
    out: List[Relation] = []

    for r in relations:
        subj = r.subject.strip()
        rel = r.relation.strip()
        obj = r.object.strip()

        # --- born ---
        m = _BORN_RE.search(subj)
        if m:
            born_val = m.group(1).strip()
            clean_subj = _BORN_RE.sub("", subj).strip()

            out.append(
                Relation(
                    subject=clean_subj,
                    relation="born_on",
                    object=born_val,
                )
            )
            subj = clean_subj

        # --- died ---
        m = _DIED_RE.search(subj)
        if m:
            died_val = m.group(1).strip()
            clean_subj = _DIED_RE.sub("", subj).strip()

            out.append(
                Relation(
                    subject=clean_subj,
                    relation="died_on",
                    object=died_val,
                )
            )
            subj = clean_subj

        # --- formed ---
        m = _FORMED_RE.search(subj)
        if m:
            formed_val = m.group(1).strip()
            clean_subj = _FORMED_RE.sub("", subj).strip()

            out.append(
                Relation(
                    subject=clean_subj,
                    relation="formed_on",
                    object=formed_val,
                )
            )
            subj = clean_subj

        # --- preserve original semantic relation ---
        out.append(
            Relation(
                subject=subj,
                relation=rel,
                object=obj,
            )
        )

    return out

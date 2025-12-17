# ============================================================
# DEPHAZE UDT — GÖDEL STRUCTURAL EXTRACTOR
# STRICT MODE v2.2 — SAFE MODE FREEZE
# ============================================================
# Role:
#   Deterministic extraction of explicit structural relations
#   from plain text using a minimal, closed rule set.
#
# This is NOT:
#   - NLP
#   - a dependency parser
#   - semantic role labeling
#   - a learned extractor
#
# This IS:
#   - a strict structural relation detector
#   - limited to explicit copula forms ("is", "are")
#   - deterministic and reproducible
#
# Design intent:
#   Precision > recall
#   Explicit structure > inferred meaning
#
# Invariants (SAFE MODE):
#   - No training, no learning
#   - Fixed regex patterns
#   - Deterministic output ordering
#
# Modifying patterns changes system semantics
# and breaks reproducibility guarantees.
# ============================================================

from dataclasses import dataclass, field
from typing import List
import re


# ============================================================
# Data structures
# ============================================================

@dataclass(frozen=True)
class Relation:
    """
    Minimal structural relation.
    """
    subject: str
    relation: str
    object: str
    confidence: float = 1.0


@dataclass
class GodelOutput:
    """
    Output container for Gödel extraction.
    """
    relations: List[Relation] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)


# ============================================================
# Gödel Engine
# ============================================================

class GodelEngine:
    """
    Strict structural relation extractor.

    Extracts only explicit copula relations:
      - X is Y
      - X are Y
    """

    STOP_OBJECT_HEADS = {"one", "a", "an", "the"}

    PATTERNS = [
        (
            "is",
            re.compile(
                r"^(?P<S>[^,]{2,80})\s+is\s+(?P<O>[^.,;:]{5,200})",
                re.I,
            ),
        ),
        (
            "are",
            re.compile(
                r"^(?P<S>[^,]{2,80})\s+are\s+(?P<O>[^.,;:]{5,200})",
                re.I,
            ),
        ),
    ]

    def extract(self, *texts: str) -> GodelOutput:
        """
        Extract structural relations and mentions from text.
        """
        out = GodelOutput()
        text = " ".join(t for t in texts if isinstance(t, str))
        if not text:
            return out

        sentences = re.split(r"[.!?]\s+", text)
        for s in sentences:
            for rel, pat in self.PATTERNS:
                m = pat.match(s)
                if not m:
                    continue

                subj = self._clean(m.group("S"))
                obj = self._clean_object(m.group("O"))

                if subj and obj:
                    out.relations.append(Relation(subj, rel, obj))

        out.mentions = self._mentions(text)
        return out

    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------

    def _clean(self, s: str) -> str:
        return re.sub(r"\s+", " ", s.strip())

    def _clean_object(self, o: str) -> str:
        """
        Trim object phrase to a bounded, ontology-safe length.
        """
        words = o.strip().split()
        if not words:
            return ""

        head = words[0].lower().split("-", 1)[0]
        if head in self.STOP_OBJECT_HEADS:
            return " ".join(words[:12])

        return " ".join(words[:8])

    def _mentions(self, text: str):
        """
        Extract capitalized entity-like mentions deterministically.
        """
        seen, out = set(), []
        for m in re.findall(
            r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}|[A-Z]{2,6})\b",
            text,
        ):
            if m.lower() not in seen:
                seen.add(m.lower())
                out.append(m)
        return out[:24]

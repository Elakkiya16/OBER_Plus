"""
OBER+ 5R helpers — pure functions, no data coupling.

  R2  persistence flag + average shortfall, banded H/M/L/VL using CAA's own
      OBEF University Guidebook v11.5 cutoff spacing (90/60/30/0, Appendix A /
      KPI 2.1) — reused, not invented
      + RBT/Bloom's-verb classification for the CLO wording drift check
  R5  immediate before/after gap-closure metric, same H/M/L/VL bands

Attainment itself is computed in compute.py, against OBER's own per-offering
numbers — nothing here re-derives or reweights it.
"""
from dataclasses import dataclass
import re

TARGET_ATTAINMENT = 60.0

# ---------------------------------------------------------------------------
# R2 — Reflect: flag + shortfall + H/M/L/VL band, + RBT drift
# ---------------------------------------------------------------------------

def band(ratio: float) -> str:
    """CAA's own cutoff spacing (90/60/30/0), reused not invented — see KPI 2.1
    in the OBEF University Guidebook v11.5, Appendix A."""
    if ratio is None:
        return "—"
    if ratio >= 90:
        return "H"
    if ratio >= 60:
        return "M"
    if ratio >= 30:
        return "L"
    return "VL"


BAND_LABEL = {"H": "High", "M": "Medium", "L": "Low", "VL": "Very Low", "OK": "On target"}


@dataclass
class ReflectResult:
    item_id: str
    label: str
    attainments: list
    target: float
    flagged: bool
    miss_count: int
    avg_shortfall: float | None
    avg_ratio: float | None
    band: str


def r2_reflect_series(item_id: str, label: str, attainments: list, target: float = TARGET_ATTAINMENT) -> ReflectResult:
    """attainments: list of 3 numbers (%), oldest first, for this CLO/PLO/course
    across its last 3 offerings — each already OBER's own computed number for
    that specific offering."""
    misses = [a for a in attainments if a is not None and a < target]
    flagged = len(misses) >= 2
    if misses:
        avg_shortfall = round(sum(target - m for m in misses) / len(misses), 2)
        avg_ratio = round(sum((m / target) * 100 for m in misses) / len(misses), 1)
    else:
        avg_shortfall = None
        avg_ratio = None
    return ReflectResult(
        item_id=item_id, label=label, attainments=attainments, target=target,
        flagged=flagged, miss_count=len(misses),
        avg_shortfall=avg_shortfall, avg_ratio=avg_ratio,
        # An item that never fell below target has no shortfall to band — it is
        # "On target", NOT band High. Handing it "H" made every healthy row look
        # like a graded result and hid the real spread across H/M/L/VL.
        band=band(avg_ratio) if avg_ratio is not None else "OK",
    )


# --- RBT / Bloom's-verb drift detection -------------------------------------

BLOOM_VERB_LEVELS = {
    # Remember
    "define": "Remember", "list": "Remember", "recall": "Remember", "state": "Remember",
    # Understand
    "explain": "Understand", "describe": "Understand", "summarize": "Understand", "discuss": "Understand",
    # Apply
    "apply": "Apply", "use": "Apply", "implement": "Apply", "solve": "Apply", "utilize": "Apply",
    # Analyze
    "analyze": "Analyze", "differentiate": "Analyze", "compare": "Analyze", "examine": "Analyze",
    # Evaluate
    "evaluate": "Evaluate", "assess": "Evaluate", "justify": "Evaluate", "critique": "Evaluate",
    # Create
    "design": "Create", "develop": "Create", "create": "Create", "formulate": "Create", "construct": "Create",
}
BLOOM_ORDER = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]


def classify_rbt(description: str) -> str:
    """Very simple leading-verb lookup (defensible given how clean real CLO
    sentences are — a full ML classifier per Kumar et al. 2025 is a build-time
    upgrade, not a design requirement)."""
    first_word = re.findall(r"[A-Za-z]+", description)[0].lower() if description else ""
    return BLOOM_VERB_LEVELS.get(first_word, "Unclassified")


# ---------------------------------------------------------------------------
# R5 — Reassess: immediate before/after gap closure, same H/M/L/VL bands
# ---------------------------------------------------------------------------

@dataclass
class ClosureResult:
    label: str
    before: float
    after: float
    target: float
    shortfall_before: float
    shortfall_after: float
    closure_pct: float | None
    band: str
    verdict: str


def r5_reassess(label: str, before: float, after: float, target: float = TARGET_ATTAINMENT) -> ClosureResult:
    shortfall_before = max(0.0, target - before)
    shortfall_after = max(0.0, target - after)
    if shortfall_before == 0:
        closure_pct = None  # was already meeting target before redesign — not applicable
        b = "H"
        verdict = "Already meeting target before redesign — not applicable"
    else:
        closure_pct = round(((shortfall_before - shortfall_after) / shortfall_before) * 100, 1)
        b = band(closure_pct)
        verdict = {
            "H": "Strong closure", "M": "Partial closure",
            "L": "Limited closure", "VL": "Regressed / very limited closure" if closure_pct < 0 else "Very limited closure",
        }[b]
    return ClosureResult(
        label=label, before=before, after=after, target=target,
        shortfall_before=shortfall_before, shortfall_after=shortfall_after,
        closure_pct=closure_pct, band=b, verdict=verdict,
    )

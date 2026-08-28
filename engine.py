"""
OBER+ computation engine.

Implements, in order:
  - OBER's real attainment formulas (verified against OBER_Presentation_6:7:26.pdf)
  - R1 Report: 3-offering gate
  - R2 Reflect: persistence flag + average shortfall, banded H/M/L/VL
              (cutoffs reused from CAA's own OBEF University Guidebook v11.5,
              Appendix A / KPI 2.1: 90/60/30/0 — not invented)
              + RBT/Bloom's-verb drift detection on CLO wording
  - R3 Recommend: evidence packaging (menu lives in data_model.py)
  - R4 Redesign: change-log passthrough (seeded in data_model.py)
  - R5 Reassess: immediate before/after gap-closure metric, same H/M/L/VL bands

No step here manually reweights CLOs into a course number using a weight we
invent — course/PLO-level numbers are always computed from OBER's own
per-offering formula, since each offering can use different component
weightages (confirmed: "not everytime same weightage we are following").
"""
from dataclasses import dataclass, field
import re

from data_model import simulate_marks, TARGET_ATTAINMENT, OFFERINGS

# ---------------------------------------------------------------------------
# OBER's real attainment formulas
# ---------------------------------------------------------------------------

def clo_attainment(course: dict, offering_idx: int) -> dict:
    """CLO attainment (%) = weighted average across components of
    (marks scored / marks possible for that CLO's questions), weight = that
    component's weight in THIS offering."""
    marks = simulate_marks(course, offering_idx)
    components = course["components_by_offering"][offering_idx]
    clo_ids = [c["id"] for c in course["clos"]]

    result = {}
    for clo_id in clo_ids:
        weighted_sum = 0.0
        weight_total = 0.0
        for comp_name, comp_weight in components.items():
            comp_data = marks.get(comp_name, {}).get(clo_id)
            if comp_data is None or comp_data["possible"] == 0:
                continue
            frac = comp_data["scored"] / comp_data["possible"]
            weighted_sum += frac * comp_weight
            weight_total += comp_weight
        result[clo_id] = round((weighted_sum / weight_total) * 100, 2) if weight_total else None
    return result


def clo_mark_share(course: dict, offering_idx: int) -> dict:
    """Each CLO's share of total course marks THIS offering (for reference/
    display only — never used to manually reweight a course number)."""
    marks_map = course["marks_by_offering"][offering_idx]
    totals = {}
    grand_total = 0.0
    for comp_name, clo_marks in marks_map.items():
        for clo_id, m in clo_marks.items():
            totals[clo_id] = totals.get(clo_id, 0.0) + m
            grand_total += m
    return {clo_id: round((m / grand_total) * 100, 1) for clo_id, m in totals.items()} if grand_total else {}


def plo_attainment(course: dict, offering_idx: int) -> dict:
    """PLO attainment = simple average of the CLO attainments mapped to it."""
    clo_att = clo_attainment(course, offering_idx)
    result = {}
    for plo in course.get("_plo_ids", []):
        mapped = [clo_att[c] for c, plos in course["clo_plo_map"].items() if plo in plos and clo_att.get(c) is not None]
        result[plo] = round(sum(mapped) / len(mapped), 2) if mapped else None
    return result


def course_attainment(course: dict, offering_idx: int) -> float:
    """Course attainment = CLO attainments weighted by each CLO's share of total marks."""
    clo_att = clo_attainment(course, offering_idx)
    shares = clo_mark_share(course, offering_idx)
    weighted_sum = sum(clo_att[c] * (shares.get(c, 0) / 100) for c in clo_att if clo_att[c] is not None)
    return round(weighted_sum, 2)


def prepare_course(course: dict, plo_ids: list):
    course = dict(course)
    course["_plo_ids"] = plo_ids
    return course


# ---------------------------------------------------------------------------
# R1 — Report: 3-offering gate
# ---------------------------------------------------------------------------

def r1_gate(course: dict) -> dict:
    n = len(course["components_by_offering"])
    return {"offerings_available": n, "gate_cleared": n >= 3}


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


BAND_LABEL = {"H": "High", "M": "Medium", "L": "Low", "VL": "Very Low"}


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
        band=band(avg_ratio) if avg_ratio is not None else "H",
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


def r2_drift(course: dict) -> list:
    """Compare each CLO's description + classified RBT level across the 3
    offerings; return a note for any CLO whose wording or level changed."""
    notes = []
    for clo in course["clos"]:
        descs = clo["description_by_offering"]
        levels = [classify_rbt(d) for d in descs]
        changes = []
        for i in range(1, len(descs)):
            if descs[i] != descs[i - 1]:
                changes.append({
                    "at_offering": OFFERINGS[i],
                    "from_text": descs[i - 1], "to_text": descs[i],
                    "from_level": levels[i - 1], "to_level": levels[i],
                    "level_changed": levels[i - 1] != levels[i],
                })
        if changes:
            notes.append({"clo_id": clo["id"], "changes": changes})
    return notes


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

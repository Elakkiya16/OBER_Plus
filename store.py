"""
OBER+ working data store.

Mirrors OBER's real entities exactly as they exist in the deployed tool
(verified against CAA_OBER_21:10:2025.pdf, the current OBER user guide):

    Semester -> Course -> CLOs
                       -> Evaluation Components (name, total marks)
                       -> Weightage Distribution  (CLO x Component, % , row = 100)
                       -> Mark Distribution       (CLO x Component, marks, col = component total)
                       -> CLO-PLO Mapping         (CLO x PLO, 1 = mapped)
                       -> Student marks           (per student, per component, per CLO)

OBER+ adds on top of that, and nothing else changes:
    - offerings          : the same course held across multiple semesters (R1)
    - clo_history        : CLO description as it stood in each offering (R2 drift)
    - recommendations    : R3 decisions, each with an ID
    - change_log         : R4 records, formal (linked to an R3 ID) or detected

Everything lives in st.session_state so entry screens actually save, exactly
like the real tool. Seed values below are taken from the CS F351 walkthrough
in the OBER user guide itself (same components, same 200-mark distribution,
same CLO-PLO mapping) so the tool opens on a course that is already set up.
"""
import streamlit as st
import random

PLO_IDS = [f"PLO{i}" for i in range(1, 9)]

SEMESTERS = [
    {"id": 2, "name": "First Semester 2025-26", "active": True},
    {"id": 1, "name": "Second Semester 2024-25", "active": False},
    {"id": 0, "name": "First Semester 2024-25", "active": False},
]

# Offering order, oldest first — the R1 longitudinal window.
OFFERING_ORDER = ["First Semester 2024-25", "Second Semester 2024-25", "First Semester 2025-26"]

# Default attainment target. Source: her own "Target Sheet" in
# CAA Materials/CS F531 ToC_CAA.xlsx, section "III. Target Setting", which sets
# "Target Level %" = 60 for every evaluation component of CS F351 (I Sem
# 2024-25). That sheet's own note — "Target Grades can be fixed based on subject
# difficulty" — is why this is a per-course default here rather than a constant.
DEFAULT_TARGET = 60.0
TARGET_ATTAINMENT = DEFAULT_TARGET  # kept for callers that want the default


# ---------------------------------------------------------------------------
# Seed data — CS F351, exactly as set up in the OBER user guide walkthrough
# ---------------------------------------------------------------------------

CSF351_CLOS = [
    ("CLO1", "Explain the fundamental concepts of alphabets, strings, languages, "
             "infinite sets, closure properties, and proof techniques."),
    ("CLO2", "Construct finite automata and regular expressions for languages."),
    ("CLO3", "Design context-free grammars and pushdown automata."),
    ("CLO4", "Develop Turing Machine models for language recognition."),
    ("CLO5", "Analyze computational problems in terms of decidability."),
]

CSF351_COMPONENTS = [
    ("Quiz", 30), ("Midsem", 60), ("Exit Quiz", 10),
    ("Problem Solving", 10), ("Assignment", 10), ("Compre", 80),
]

# Weightage Distribution (%) — each CLO row totals 100
CSF351_WEIGHTAGE = {
    "CLO1": {"Quiz": 60, "Midsem": 20, "Compre": 20},
    "CLO2": {"Midsem": 80, "Compre": 20},
    "CLO3": {"Exit Quiz": 25, "Compre": 75},
    "CLO4": {"Problem Solving": 30, "Compre": 70},
    "CLO5": {"Assignment": 40, "Compre": 60},
}

# Mark Distribution — each component column totals that component's total marks
CSF351_MARKDIST = {
    "CLO1": {"Quiz": 30, "Midsem": 12, "Compre": 6},
    "CLO2": {"Midsem": 48, "Compre": 4},
    "CLO3": {"Exit Quiz": 10, "Compre": 28},
    "CLO4": {"Problem Solving": 10, "Compre": 26},
    "CLO5": {"Assignment": 10, "Compre": 16},
}

CSF351_MAPPING = {
    "CLO1": ["PLO2"],
    "CLO2": ["PLO2", "PLO8"],
    "CLO3": ["PLO2", "PLO8"],
    "CLO4": ["PLO2", "PLO8"],
    "CLO5": ["PLO2"],
}

CSF459_CLOS = [
    ("CLO1", "Explain digital image formation, formats, colour models and "
             "fundamental image processing operations."),
    ("CLO2", "Apply feature detection and description techniques to images."),
    ("CLO3", "Analyze the performance of segmentation and recognition methods."),
    ("CLO4", "Design deep learning pipelines for vision tasks."),
]

CSF459_COMPONENTS = [
    ("Quiz", 20), ("Midsem", 60), ("Lab", 40), ("Project", 30), ("Compre", 50),
]

CSF459_WEIGHTAGE = {
    "CLO1": {"Quiz": 50, "Midsem": 30, "Compre": 20},
    "CLO2": {"Midsem": 40, "Lab": 40, "Compre": 20},
    "CLO3": {"Lab": 30, "Compre": 70},
    "CLO4": {"Project": 70, "Compre": 30},
}

CSF459_MARKDIST = {
    "CLO1": {"Quiz": 20, "Midsem": 20, "Compre": 10},
    "CLO2": {"Midsem": 40, "Lab": 25, "Compre": 10},
    "CLO3": {"Lab": 15, "Compre": 15},
    "CLO4": {"Project": 30, "Compre": 15},
}

CSF459_MAPPING = {
    "CLO1": ["PLO1", "PLO2"],
    "CLO2": ["PLO2", "PLO3"],
    "CLO3": ["PLO2", "PLO4"],
    "CLO4": ["PLO3", "PLO5"],
}


# CLO description as it stood in each offering (drives R2's drift check).
# CS F351 CLO3 was reworded between the 2nd and 3rd offering, with no
# recommendation behind it — the informal path R4 has to catch.
CLO_HISTORY = {
    "31314": {
        "CLO3": [
            "Apply context-free grammars and pushdown automata to language problems.",
            "Apply context-free grammars and pushdown automata to language problems.",
            "Design context-free grammars and pushdown automata.",
        ],
    },
}

# Per-offering mean performance driver per CLO (0-1). Third offering for
# CS F351 CLO4 reflects the redesign logged in the change log below.
OFFERING_PERFORMANCE = {
    "31314": {
        "CLO1": [0.72, 0.70, 0.71],
        "CLO2": [0.68, 0.66, 0.67],
        "CLO3": [0.63, 0.61, 0.64],
        "CLO4": [0.49, 0.50, 0.66],   # flagged in R2, redesigned in R4, recovers in R5
        "CLO5": [0.65, 0.62, 0.64],
    },
    # CS F459 deliberately spans the full H/M/L/VL range, so the banding is
    # legible as a scale rather than as one repeated label.
    "31316": {
        "CLO1": [0.74, 0.76, 0.75],   # never below target      -> On target
        "CLO2": [0.57, 0.55, 0.58],   # just under, persistently -> High
        "CLO3": [0.42, 0.40, 0.45],   # clearly under            -> Medium
        "CLO4": [0.20, 0.17, 0.22],   # severe                   -> Low
    },
}

SEED_RECOMMENDATIONS = [
    {
        "id": "R3-2025-006",
        "course": "31314",
        "clo": "CLO4",
        "category": "Worked examples / reduce cognitive load",
        "citation": "Paas & van Merriënboer, Current Directions in Psychological Science, 2020",
        "evidence": "Below target in 2 of 3 offerings; average shortfall 10.5 pts; band Medium.",
        "decided_by": "Dr. A. Rao",
        "decided_on": "2025-06-11",
        "status": "Implemented",
    },
    {
        "id": "R3-2025-011",
        "course": "31316",
        "clo": "CLO4",
        "category": "Industry-sourced problems as project/assessment content",
        "citation": "Naseer et al., Nature Scientific Reports, 2025",
        "evidence": "Below target in 3 of 3 offerings; average shortfall 41.4 pts; band Low.",
        "decided_by": "Dr. E. Rajasekar",
        "decided_on": "2025-06-20",
        "status": "Implemented",
    },
]

SEED_CHANGE_LOG = [
    {
        "id": "REC-2025-014",
        "course": "31314",
        "clo": "CLO4",
        "path": "formal",
        "recommendation_id": "R3-2025-006",
        "offering_boundary": "Second Semester 2024-25 → First Semester 2025-26",
        "what_changed": "Added 2 worked-example problem sets on Turing Machine construction; "
                        "raised Problem Solving weightage for CLO4 from 20% to 30% and its "
                        "mark allocation from 6 to 10.",
        "before": "Problem Solving: CLO4 = 6 marks; weightage 20%",
        "after": "Problem Solving: CLO4 = 10 marks; weightage 30%",
        "changed_by": "Dr. A. Rao",
        "changed_at": "2025-06-18",
    },
    {
        "id": "REC-2025-015",
        "course": "31314",
        "clo": "CLO3",
        "path": "detected",
        "recommendation_id": None,
        "offering_boundary": "Second Semester 2024-25 → First Semester 2025-26",
        "what_changed": "CLO3 description reworded during I/C handover (Dr. A. Rao → Dr. S. Menon). "
                        "Not routed through a recommendation; caught by the CLO drift check.",
        "before": "Apply context-free grammars and pushdown automata to language problems.",
        "after": "Design context-free grammars and pushdown automata.",
        "changed_by": "Dr. S. Menon",
        "changed_at": "2025-07-02",
    },
    {
        # The honest case: a recorded, well-grounded intervention that barely
        # moved the number. R5 has to be able to say so — a loop that only ever
        # reports success is not a loop.
        "id": "REC-2025-021",
        "course": "31316",
        "clo": "CLO4",
        "path": "formal",
        "recommendation_id": "R3-2025-011",
        "offering_boundary": "Second Semester 2024-25 → First Semester 2025-26",
        "what_changed": "Replaced the synthetic capstone dataset with an industry-supplied "
                        "defect-inspection set and re-scoped the project brief around it.",
        "before": "Project: synthetic benchmark dataset, fixed brief",
        "after": "Project: industry-supplied dataset, partner-reviewed brief",
        "changed_by": "Dr. E. Rajasekar",
        "changed_at": "2025-07-10",
    },
]

R3_STANDARD_MENU = [
    ("Active learning redesign", "Freeman et al., PNAS, 2014; Theobald et al., PNAS, 2020"),
    ("Peer instruction (Mazur-style)", "Vickrey et al., CBE Life Sciences Education, 2015"),
    ("Flipped classroom", "Lo & Hew, Journal of Engineering Education, 2019"),
    ("Supplemental instruction / peer-led sessions", "Dawson et al., Review of Educational Research, 2014"),
    ("Retrieval practice / low-stakes quizzing", "Roediger & Karpicke, 2006; Roediger et al., 2011"),
    ("Worked examples / reduce cognitive load", "Paas & van Merriënboer, Current Directions in Psych. Science, 2020"),
    ("Revise the assessment instrument / rubric", "Black & Wiliam, Phi Delta Kappan, 1998"),
]

R3_INNOVATIVE_MENU = [
    ("Industry-sourced problems as project/assessment content",
     "Naseer et al., Nature Scientific Reports, 2025"),
    ("Industry co-teach + CLO revision",
     "Naseer et al., 2025; gap vs. Dawson et al., Education Sciences, 2026"),
    ("AI-targeted remediation at the flagged CLO (instructor-reviewed)",
     "Al Foori & Oyelere, Frontiers in Computer Science, 2026 — hypothesis, not proven practice"),
]


# ---------------------------------------------------------------------------
# Student roster + marks
# ---------------------------------------------------------------------------

FIRST_NAMES = ["AABAN", "AAKARSH", "AAKIFAH", "AANVI", "ADITYA", "AHMED", "AISHA", "AMAL",
               "ANANYA", "ARJUN", "BHAVYA", "DEV", "FATIMA", "HARSH", "ISHAAN", "KAVYA",
               "LAYAN", "MEERA", "NOOR", "OMAR", "PRIYA", "RAHUL", "SARA", "TARIQ",
               "VIHAAN", "YASMIN", "ZAID", "ANIKA", "FARAZ", "RIYA"]
LAST_NAMES = ["HUSSAIN", "BATRA", "MINHAJ", "CHOUDHARY", "SHARMA", "KHAN", "RAHMAN", "NAIR",
              "IYER", "MEHTA", "SINGH", "PATEL", "ALI", "JOSHI", "REDDY", "GUPTA",
              "AHMED", "KUMAR", "SAEED", "VERMA", "MALIK", "RAO", "SHAIKH", "DESAI",
              "BANSAL", "QURESHI", "THOMAS", "PILLAI", "HASSAN", "AGARWAL"]


def _make_roster(course_id: str, n: int, seed: int):
    rng = random.Random(seed)
    roster = []
    for i in range(n):
        year = rng.choice(["2022", "2023", "2023", "2024"])
        num = rng.randint(10, 399)
        sid = f"{year}A7PS{num:04d}U"
        name = f"{FIRST_NAMES[i % len(FIRST_NAMES)]} {LAST_NAMES[(i * 7) % len(LAST_NAMES)]}"
        roster.append({"user_id": sid, "name": name})
    return roster


def _simulate_marks(course, offering_idx: int, seed: int):
    """Per student, per component, per CLO marks — the shape OBER stores after
    a marks-file upload. Mean performance per CLO comes from OFFERING_PERFORMANCE."""
    rng = random.Random(seed)
    perf = OFFERING_PERFORMANCE.get(course["id"], {})
    marks = {}
    for student in course["roster"]:
        sm = {}
        for comp_name, _total in course["components"]:
            comp_marks = {}
            for clo_id, alloc in course["mark_dist"].items():
                allocated = alloc.get(comp_name, 0)
                if not allocated:
                    continue
                mean = perf.get(clo_id, [0.65, 0.65, 0.65])[offering_idx]
                # Beta-ish spread around the target mean, clipped to the allocation
                a = max(0.5, mean * 8)
                b = max(0.5, (1 - mean) * 8)
                frac = min(1.0, max(0.0, rng.betavariate(a, b)))
                comp_marks[clo_id] = round(frac * allocated, 1)
            if comp_marks:
                sm[comp_name] = comp_marks
        marks[student["user_id"]] = sm
    return marks


# ---------------------------------------------------------------------------
# Store construction
# ---------------------------------------------------------------------------

def _build_course(cid, code, title, clos, components, weightage, mark_dist, mapping,
                  instructor_by_offering, n_students, seed):
    roster = _make_roster(cid, n_students, seed)
    course = {
        "id": cid,
        "code": code,
        "title": title,
        "label": f"{cid} - {code} - {title.upper()}",
        "clos": [{"name": n, "description": d} for n, d in clos],
        "components": [list(c) for c in components],
        "weightage": {k: dict(v) for k, v in weightage.items()},
        "mark_dist": {k: dict(v) for k, v in mark_dist.items()},
        "mapping": {k: list(v) for k, v in mapping.items()},
        "roster": roster,
        "handout": f"{cid}_handout_First_Semester_2025-26.pdf",
        "instructor_by_offering": instructor_by_offering,
        "target": DEFAULT_TARGET,
        "uploaded_components": [],
    }
    # Marks for each of the three offerings; the active semester is index 2.
    course["marks_by_offering"] = [
        _simulate_marks(course, i, seed + 100 * i) for i in range(3)
    ]
    course["marks"] = course["marks_by_offering"][2]
    return course


def init_store():
    if "store" in st.session_state:
        return st.session_state.store

    csf351 = _build_course(
        "31314", "CS F351", "Theory of Computation",
        CSF351_CLOS, CSF351_COMPONENTS, CSF351_WEIGHTAGE, CSF351_MARKDIST, CSF351_MAPPING,
        ["Dr. A. Rao", "Dr. A. Rao", "Dr. S. Menon"], 28, seed=41,
    )
    csf459 = _build_course(
        "31316", "CS F459", "Computer Vision",
        CSF459_CLOS, CSF459_COMPONENTS, CSF459_WEIGHTAGE, CSF459_MARKDIST, CSF459_MAPPING,
        ["Dr. E. Rajasekar"] * 3, 22, seed=77,
    )

    store = {
        "semesters": [dict(s) for s in SEMESTERS],
        "active_semester": "First Semester 2025-26",
        "courses": {c["id"]: c for c in (csf351, csf459)},
        "clo_history": {k: {kk: list(vv) for kk, vv in v.items()} for k, v in CLO_HISTORY.items()},
        "recommendations": [dict(r) for r in SEED_RECOMMENDATIONS],
        "change_log": [dict(r) for r in SEED_CHANGE_LOG],
        "user": "elakkiya@dubai.bits-pilani.ac.in",
    }
    st.session_state.store = store
    return store


def course_options(store):
    return {c["label"]: cid for cid, c in store["courses"].items()}


def clo_description_history(store, course_id, clo_name, current_desc):
    """Description as it stood in each of the 3 offerings; falls back to the
    current description where no separate history was recorded."""
    hist = store["clo_history"].get(course_id, {}).get(clo_name)
    if hist:
        return list(hist)
    return [current_desc, current_desc, current_desc]


def next_id(prefix, existing):
    nums = [int(x["id"].split("-")[-1]) for x in existing if x["id"].startswith(prefix)]
    n = max(nums) + 1 if nums else 1
    return f"{prefix}-{n:03d}"

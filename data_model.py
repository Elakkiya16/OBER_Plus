"""
OBER+ demo data model — SYNTHETIC DATA ONLY.

Two illustrative courses, modeled on the real OBER computation (verified against
OBER_Presentation_6:7:26.pdf: CLO attainment = weighted average across evaluation
components of marks-scored / marks-possible for that CLO's questions; PLO
attainment = simple average of mapped CLOs; Course attainment = CLO attainments
weighted by each CLO's share of total marks). Course codes, names, instructor
names, and all marks below are fabricated for demonstration only — not real
student records.

Deliberately embeds a demo narrative:
  - Course A / CLO3 ("Analyze"): below target in offerings 1 and 2, a redesign
    is logged after offering 2 (worked examples + rubric revision), offering 3
    recovers above target — drives R2's persistence flag and R5's gap closure.
  - Course A / CLO2: wording changes between offering 2 and 3 with no R3
    recommendation behind it — drives R2's RBT-drift note and R4's informal
    (detected, not formal) change-log path.
  - Course B: every CLO stays at/above target across all 3 offerings — a
    healthy contrast course, no flags.
"""
import numpy as np

RNG_SEED = 42
TARGET_ATTAINMENT = 60.0  # illustrative uniform target (%) — configurable per institution/course in a real deployment

OFFERINGS = ["Sem I 2024-25", "Sem II 2024-25", "Sem I 2025-26"]  # index 0,1,2 = offering 1,2,3

PLOS = [
    {"id": "PLO1", "name": "Engineering Knowledge"},
    {"id": "PLO2", "name": "Problem Analysis"},
    {"id": "PLO3", "name": "Design & Development of Solutions"},
    {"id": "PLO4", "name": "Modern Tool Usage"},
]

# ---------------------------------------------------------------------------
# Course A
# ---------------------------------------------------------------------------
COURSE_A = {
    "code": "CS D301 (Demo)",
    "name": "Data Structures & Algorithms",
    "instructor_by_offering": ["Dr. A. Rao", "Dr. A. Rao", "Dr. S. Menon"],  # I/C rotation between offering 2 and 3
    "clos": [
        {
            "id": "CLO1",
            # constant across all 3 offerings
            "description_by_offering": [
                "Explain fundamental data structures and their properties",
                "Explain fundamental data structures and their properties",
                "Explain fundamental data structures and their properties",
            ],
        },
        {
            "id": "CLO2",
            # wording drifts after offering 2 — nobody routed it through R3
            "description_by_offering": [
                "Apply appropriate data structures to solve computational problems",
                "Apply appropriate data structures to solve computational problems",
                "Design and apply data structures to solve computational problems",
            ],
        },
        {
            "id": "CLO3",
            # constant wording — this CLO's story is the ATTAINMENT gap + redesign, not a wording drift
            "description_by_offering": [
                "Analyze the time and space complexity of algorithms",
                "Analyze the time and space complexity of algorithms",
                "Analyze the time and space complexity of algorithms",
            ],
        },
        {
            "id": "CLO4",
            "description_by_offering": [
                "Design efficient algorithms for graph and tree-based problems",
                "Design efficient algorithms for graph and tree-based problems",
                "Design efficient algorithms for graph and tree-based problems",
            ],
        },
    ],
    "clo_plo_map": {"CLO1": ["PLO1"], "CLO2": ["PLO1", "PLO2"], "CLO3": ["PLO2"], "CLO4": ["PLO3", "PLO4"]},
    # per-offering evaluation components: name -> weight (%), must sum to 100 each offering
    "components_by_offering": [
        {"Quiz": 10, "Midterm": 30, "Assignment": 20, "Final Exam": 40},
        {"Quiz": 15, "Midterm": 25, "Assignment": 20, "Final Exam": 40},
        {"Quiz": 10, "Midterm": 25, "Assignment": 25, "Final Exam": 40},  # Assignment weight raised post-redesign
    ],
    # per-offering, per-component: which CLOs are examined and how many marks are allocated to each
    # (this is the "marks possible for that CLO's questions in that component" OBER uses)
    "marks_by_offering": [
        {  # offering 1
            "Quiz": {"CLO1": 10, "CLO2": 10},
            "Midterm": {"CLO1": 10, "CLO2": 15, "CLO3": 25},
            "Assignment": {"CLO2": 10, "CLO3": 10, "CLO4": 10},
            "Final Exam": {"CLO1": 10, "CLO2": 15, "CLO3": 20, "CLO4": 25},
        },
        {  # offering 2 — same shape
            "Quiz": {"CLO1": 8, "CLO2": 7},
            "Midterm": {"CLO1": 10, "CLO2": 15, "CLO3": 25},
            "Assignment": {"CLO2": 10, "CLO3": 10, "CLO4": 10},
            "Final Exam": {"CLO1": 10, "CLO2": 15, "CLO3": 20, "CLO4": 25},
        },
        {  # offering 3 — post-redesign: Assignment now carries more CLO3 practice weight
            "Quiz": {"CLO1": 8, "CLO2": 7},
            "Midterm": {"CLO1": 10, "CLO2": 15, "CLO3": 20},
            "Assignment": {"CLO2": 8, "CLO3": 17, "CLO4": 10},
            "Final Exam": {"CLO1": 10, "CLO2": 15, "CLO3": 20, "CLO4": 25},
        },
    ],
    # target mean attainment fraction (0-1) fed into the synthetic-mark generator per (offering, CLO)
    # this is what actually drives the demo narrative
    "target_mean_by_offering": [
        {"CLO1": 0.72, "CLO2": 0.68, "CLO3": 0.48, "CLO4": 0.63},  # offering 1: CLO3 already weak
        {"CLO1": 0.70, "CLO2": 0.66, "CLO3": 0.50, "CLO4": 0.61},  # offering 2: CLO3 still weak -> flagged (2/3)
        {"CLO1": 0.71, "CLO2": 0.69, "CLO3": 0.66, "CLO4": 0.64},  # offering 3: CLO3 recovers post-redesign
    ],
    "n_students_by_offering": [46, 51, 49],
}

# ---------------------------------------------------------------------------
# Course B — healthy contrast course, no flags
# ---------------------------------------------------------------------------
COURSE_B = {
    "code": "CS D452 (Demo)",
    "name": "Machine Learning Systems",
    "instructor_by_offering": ["Dr. N. Iyer", "Dr. N. Iyer", "Dr. N. Iyer"],
    "clos": [
        {"id": "CLO1", "description_by_offering": ["Explain core machine learning concepts and model families"] * 3},
        {"id": "CLO2", "description_by_offering": ["Apply supervised learning algorithms to real-world datasets"] * 3},
        {"id": "CLO3", "description_by_offering": ["Analyze model performance using appropriate evaluation metrics"] * 3},
        {"id": "CLO4", "description_by_offering": ["Evaluate trade-offs between different ML approaches for a given problem"] * 3},
        {"id": "CLO5", "description_by_offering": ["Design an end-to-end ML pipeline for a novel problem"] * 3},
    ],
    "clo_plo_map": {"CLO1": ["PLO1"], "CLO2": ["PLO1", "PLO2"], "CLO3": ["PLO2"], "CLO4": ["PLO2", "PLO3"], "CLO5": ["PLO3", "PLO4"]},
    "components_by_offering": [
        {"Quiz": 10, "Midterm": 25, "Project": 25, "Final Exam": 40},
        {"Quiz": 10, "Midterm": 25, "Project": 25, "Final Exam": 40},
        {"Quiz": 10, "Midterm": 25, "Project": 25, "Final Exam": 40},
    ],
    "marks_by_offering": [
        {
            "Quiz": {"CLO1": 10, "CLO2": 8},
            "Midterm": {"CLO1": 8, "CLO2": 10, "CLO3": 7},
            "Project": {"CLO2": 8, "CLO4": 9, "CLO5": 8},
            "Final Exam": {"CLO1": 8, "CLO3": 10, "CLO4": 12, "CLO5": 10},
        }
    ] * 3,
    "target_mean_by_offering": [
        {"CLO1": 0.74, "CLO2": 0.71, "CLO3": 0.69, "CLO4": 0.66, "CLO5": 0.63},
        {"CLO1": 0.75, "CLO2": 0.73, "CLO3": 0.68, "CLO4": 0.67, "CLO5": 0.65},
        {"CLO1": 0.76, "CLO2": 0.72, "CLO3": 0.70, "CLO4": 0.68, "CLO5": 0.66},
    ],
    "n_students_by_offering": [52, 55, 50],
}

COURSES = {COURSE_A["code"]: COURSE_A, COURSE_B["code"]: COURSE_B}


def simulate_marks(course: dict, offering_idx: int, seed_offset: int = 0):
    """
    Simulate a class of students' per-question scores for one offering, and
    aggregate into per-(component, CLO) (marks_scored, marks_possible) — the
    exact inputs OBER's real per-component attainment fraction needs.

    Returns: {component: {clo_id: {"scored": float, "possible": float}}}
    """
    rng = np.random.default_rng(RNG_SEED + offering_idx * 97 + seed_offset)
    n_students = course["n_students_by_offering"][offering_idx]
    components = course["components_by_offering"][offering_idx]
    marks_map = course["marks_by_offering"][offering_idx]
    target_means = course["target_mean_by_offering"][offering_idx]

    out = {}
    for comp_name in components:
        out[comp_name] = {}
        clo_marks = marks_map.get(comp_name, {})
        for clo_id, max_marks in clo_marks.items():
            mean_frac = target_means.get(clo_id, 0.65)
            # Beta distribution centered on mean_frac with realistic classroom spread
            concentration = 18.0
            a = max(0.5, mean_frac * concentration)
            b = max(0.5, (1 - mean_frac) * concentration)
            student_fracs = rng.beta(a, b, size=n_students)
            scored = float(np.sum(student_fracs * max_marks))
            possible = float(n_students * max_marks)
            out[comp_name][clo_id] = {"scored": scored, "possible": possible}
    return out


# ---------------------------------------------------------------------------
# R3 recommendation menu (from the confirmed project design — see project doc)
# ---------------------------------------------------------------------------
R3_STANDARD_MENU = [
    ("Active learning redesign", "Freeman et al., PNAS, 2014; Theobald et al., PNAS, 2020"),
    ("Peer instruction (Mazur-style)", "Vickrey et al., CBE Life Sciences Education, 2015"),
    ("Flipped classroom", "Lo & Hew, Journal of Engineering Education, 2019"),
    ("Supplemental instruction / peer-led sessions", "Dawson et al., Review of Educational Research, 2014"),
    ("Retrieval practice / low-stakes quizzing", "Roediger & Karpicke, 2006; Roediger et al., 2011"),
    ("Worked examples / reduce cognitive load", "Paas & van Merriënboer, Current Directions in Psychological Science, 2020"),
    ("Revise the assessment instrument/rubric", "Black & Wiliam, Phi Delta Kappan, 1998"),
]
R3_INNOVATIVE_MENU = [
    ("Industry-sourced problems as project/assessment content", "Naseer et al., Nature Scientific Reports, 2025"),
    ("Industry co-teach + CLO revision", "Naseer et al., 2025; gap vs. Dawson et al. (Illinois Tech), Education Sciences, 2026"),
    ("AI-targeted remediation at the flagged CLO/RBT cell (instructor-reviewed)", "Al Foori & Oyelere, Frontiers in Computer Science, 2026 — framed as a hypothesis, not a proven practice"),
]

# ---------------------------------------------------------------------------
# R4 change log — seeded records for the demo narrative (Course A only)
# ---------------------------------------------------------------------------
R4_LOG_COURSE_A = [
    {
        "id": "REC-2025-014",
        "path": "formal",
        "clo": "CLO3",
        "offering_boundary": "Sem II 2024-25 → Sem I 2025-26",
        "what_changed": "Assignment component redesigned: added 2 worked-example problem sets on complexity analysis; "
                          "Assignment's course weight raised 20%→25%; CLO3 marks share within Assignment raised 10→17.",
        "recommendation_id": "R3-2025-006",
        "recommendation_category": "Worked examples / reduce cognitive load",
        "before": "Assignment: CLO3 = 10 marks (of 60 total); course weight 20%",
        "after": "Assignment: CLO3 = 17 marks (of 60 total); course weight 25%",
        "changed_by": "Dr. A. Rao",
        "changed_at": "2025-06-18",
    },
    {
        "id": "REC-2025-015",
        "path": "informal",
        "clo": "CLO2",
        "offering_boundary": "Sem II 2024-25 → Sem I 2025-26",
        "what_changed": "CLO2 wording changed (I/C rotation: Dr. A. Rao → Dr. S. Menon) — not routed through R3.",
        "recommendation_id": None,
        "recommendation_category": None,
        "before": "Apply appropriate data structures to solve computational problems",
        "after": "Design and apply data structures to solve computational problems",
        "changed_by": "Dr. S. Menon",
        "changed_at": "2025-07-02",
    },
]

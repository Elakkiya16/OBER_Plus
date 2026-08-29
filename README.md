# OBER+

**Outcome-Based Education and Reporting Tool — extended with the 5R
continuous-improvement loop.**

OBER+ is BPDC OBER with a continuous-improvement layer added on top. The
CO/PO Mapping, Assessment and Report sections work exactly as they do in the
deployed tool at `ober.bits-dubai.ac.ae`. The OBER+ section adds five stages —
Report, Reflect, Recommend, Redesign, Reassess — that run on the same data
without changing how attainment is computed.

## Running it

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Sections

### CO / PO Mapping
| Screen | What it does |
|---|---|
| Handout Upload | Course handout per course code, with download-back |
| CLO Entry | CLO name + description, add / edit / delete |
| Evaluation Components | Components and total marks, plus the Weightage Distribution matrix (each CLO row must total 100%) and the Mark Distribution matrix (each component column must equal that component's total marks) |
| CLO-PLO Mapping | CLO × PLO grid, 1 per mapped cell |

### Assessment
**Marks Entry** — pick a course and component, download the marks template for
that component's CLOs, fill it in, upload it back. A blank cell is read as
ABSENT. Uploaded marks are listed with per-student component totals.

### Report
- **Overview** — the report catalogue: what can be generated, who reads it,
  which visualisation it carries and what it downloads as.
- **Marks Report** — every student's marks by component and CLO, exportable.
  Table only; raw per-student records are not chart material.
- **CLO Report** — a diverging bar of each CLO's distance from target (the
  reader's question is *above or below, and by how much*), then per-component
  attainment per CLO, the weighted-average row, and course attainment.
- **PLO Report** — columns for the PLOs this course actually feeds, read
  against the target rule, then the CLO→PLO grid with the programme-level
  average. An unmapped PLO is left out rather than drawn as a zero.

### OBER+ · 5R loop
- **R1 Report** — the same per-offering computation, accumulated across
  offerings and gated on *offering count* rather than calendar time, so an
  elective run twice a year clears the window in ~1.5 years instead of 3.
  Offerings are discrete sittings, so they are grouped columns on a
  light→dark ramp with time, not a joined line.
- **R2 Reflect** — flags anything below target in ≥2 of the last 3 offerings,
  scores severity as the average shortfall across only the offerings that
  missed, and bands it High / Medium / Low / Very Low using CAA's own KPI 2.1
  cutoff spacing (90 / 60 / 30 / 0, OBEF University Guidebook v11.5). Runs a
  CLO wording / RBT drift check alongside — never instead of — the flag.
- **R3 Recommend** — packages R2's evidence and presents a cited menu of
  standard and innovative practices, plus free-text instructor choice. Nothing
  is auto-picked; whatever is chosen is recorded with an ID.
- **R4 Redesign** — the change log. *Formal* records implement a recorded R3
  recommendation; *detected* records are changes R2's drift check caught with
  no recommendation behind them. Both keep full before/after content.
- **R5 Reassess** — the offering right after a logged redesign against the one
  right before it. Gap Closure = (shortfall before − shortfall after) ÷
  shortfall before, banded on the same cutoffs as R2. Every logged redesign is
  drawn as one dumbbell row — the standard before→after form — so all
  interventions are comparable on a single axis against the target rule.

## How attainment is computed

Unchanged from OBER:

```
component attainment (CLO c, component k)
    = marks scored by all students for c in k
    / (mark allocation for c in k × number of students)

CLO attainment  = Σ_k  component_attainment(c,k) × weightage(c,k) / 100
Course attainment = Σ_c CLO_attainment(c) × c's share of total marks
PLO attainment  = average of the CLO attainments mapped to that PLO
```

No stage re-derives or reweights these. Each offering can carry its own
component weightages, so R2 and R5 always read OBER's own already-computed
number for that specific offering rather than blending CLOs with a single
reused weight.

## Data

Ships loaded with CS F351 Theory of Computation, set up exactly as in the OBER
user guide walkthrough (same six components, same 200-mark distribution, same
CLO-PLO mapping), and CS F459 Computer Vision. Student rosters and marks are
generated so every screen and both reports have something to work on from the
first run; replace them by uploading real marks files through Marks Entry, or
point `store.py` at OBER's own database.

Edits made in the tool persist for the session.

## Files

| File | |
|---|---|
| `app.py` | shell — navigation, top bar, page routing |
| `store.py` | entities, seed course setup, roster and marks |
| `compute.py` | OBER's attainment computation |
| `engine.py` | 5R helpers — banding, persistence flag, RBT classification, gap closure |
| `pages_ober.py` | CO/PO Mapping, Assessment, Report screens |
| `pages_plus.py` | R1–R5 screens |
| `style.py` | interface styling and shared components |

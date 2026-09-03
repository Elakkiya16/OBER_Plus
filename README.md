<div align="center">

<img src="assets/banner.png" alt="OBER+ — Outcome-Based Education Report Plus" width="100%">

<br>

[![Python](https://img.shields.io/badge/Python-3.10%2B-FAB001?style=flat-square&labelColor=011E4B)](requirements.txt)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-87C6E9?style=flat-square&labelColor=011E4B)](https://streamlit.io)
[![Live app](https://img.shields.io/badge/Live%20app-oberplus.streamlit.app-E40613?style=flat-square&labelColor=011E4B)](https://oberplus.streamlit.app/)
[![Institution](https://img.shields.io/badge/BITS%20Pilani-Dubai%20Campus-87C6E9?style=flat-square&labelColor=011E4B)](https://www.bits-pilani.ac.in/dubai/)

**[Open the live app →](https://oberplus.streamlit.app/)**

</div>

---

OBER+ is BPDC OBER with a continuous-improvement layer added on top. The
CO/PO Mapping, Assessment and Report sections work exactly as they do in the
deployed tool at `ober.bits-dubai.ac.ae`. The OBER+ section adds five stages —
**Report, Reflect, Recommend, Redesign, Reassess** — that run on the same data
without changing how attainment is computed.

## Contents

- [Screenshots](#screenshots)
- [Running it](#running-it)
- [Sections](#sections)
- [Interface](#interface)
- [How attainment is computed](#how-attainment-is-computed)
- [Data](#data)
- [Files](#files)

## Screenshots

<table>
<tr>
<td width="50%"><img src="assets/screenshot_report.png" alt="R1 Report — attainment accumulated across offerings"></td>
<td width="50%"><img src="assets/screenshot_reassess.png" alt="R5 Reassess — gap closure for every logged redesign"></td>
</tr>
<tr>
<td align="center"><sub><b>R1 · Report</b> — attainment accumulated across offerings</sub></td>
<td align="center"><sub><b>R5 · Reassess</b> — did the redesign actually close the gap</sub></td>
</tr>
</table>

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

- **Marks Report** — every student's marks by component and CLO, exportable.
  Table only; raw per-student records are not chart material.
- **CLO Report** — a diverging bar of each CLO's distance from target (the
  reader's question is *above or below, and by how much*), then per-component
  attainment per CLO, the weighted-average row, and course attainment.
- **PLO Report** — columns for the PLOs this course actually feeds, read
  against the target rule, then the CLO→PLO grid with the programme-level
  average. An unmapped PLO is left out rather than drawn as a zero.

### OBER+ · 5R loop

| Stage | What it does |
|---|---|
| **R1 Report** | The same per-offering computation, accumulated across offerings and gated on *offering count* rather than calendar time, so an elective run twice a year clears the window in ~1.5 years instead of 3. Offerings are discrete sittings, so they are grouped columns on a light→dark ramp with time, not a joined line. |
| **R2 Reflect** | Flags anything below target in ≥2 of the last 3 offerings, scores severity as the average shortfall across only the offerings that missed, and bands it High / Medium / Low / Very Low using CAA's own KPI 2.1 cutoff spacing (90 / 60 / 30 / 0, OBEF University Guidebook v11.5). Runs a CLO wording / RBT drift check alongside — never instead of — the flag. |
| **R3 Recommend** | Packages R2's evidence and presents a cited menu of standard and innovative practices, plus free-text instructor choice. Nothing is auto-picked; whatever is chosen is recorded with an ID. |
| **R4 Redesign** | The change log. *Formal* records implement a recorded R3 recommendation; *detected* records are changes R2's drift check caught with no recommendation behind them. Both keep full before/after content. |
| **R5 Reassess** | The offering right after a logged redesign against the one right before it. Gap Closure = (shortfall before − shortfall after) ÷ shortfall before, banded on the same cutoffs as R2. Every logged redesign is drawn as one dumbbell row — the standard before→after form — so all interventions are comparable on a single axis against the target rule. |

## Interface

<img src="assets/banner.png" alt="" width="100%">

Navy is chrome only: the masthead and the primary nav bar sit on it and nothing
else does. Everything below that bar is carried by the campus tagline palette —
**innovate amber**, **achieve sky**, **lead red**. The rule across the top of the
masthead is that device; each section's page title takes one of the three so you
can tell where you are before reading the heading; KPI tiles take the next colour
in turn; table headers are sky; the one action a screen is for is amber, and row
actions stay quiet so a Delete never looks like the primary move. Band colours
are separate and reserved — they mean severity, never decoration.

| Token | Hex | Role |
|---|---|---|
| Navy | `#011E4B` | Structure — masthead, nav, headings |
| Amber | `#FAB001` | Innovate — primary action, one colour per section in turn |
| Sky | `#87C6E9` | Achieve — table headers, the next colour in turn |
| Red | `#E40613` | Lead — the third colour in turn, never decoration alone |

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

<details>
<summary>Show the file layout</summary>

| File | |
|---|---|
| `app.py` | shell — navigation, top bar, page routing |
| `store.py` | entities, seed course setup, roster and marks |
| `compute.py` | OBER's attainment computation |
| `engine.py` | 5R helpers — banding, persistence flag, RBT classification, gap closure |
| `pages_ober.py` | CO/PO Mapping, Assessment, Report screens |
| `pages_plus.py` | R1–R5 screens |
| `style.py` | interface styling and shared components |

</details>

<div align="center">
<sub>OBER+ · LEAD Academics Capstone · BITS Pilani, Dubai Campus</sub>
</div>

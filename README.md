# OBER+ — 5R Continuous-Improvement Demo

A Streamlit demo of OBER+, the 5R (Report → Reflect → Recommend → Redesign →
Reassess) continuous-improvement loop built on top of OBER's real CLO/PLO
attainment computation.

**All data in this demo is synthetic** — two illustrative courses ("CS D301
(Demo)" and "CS D452 (Demo)"), 3 offerings each, generated to walk through the
full 5R loop end to end. Course codes, names, instructors, and marks are
fabricated for demonstration; not real student records.

## What it shows

- **R1 Report** — OBER's real weighted-average attainment formulas (CLO =
  weighted average across components; PLO = simple average of mapped CLOs;
  Course = CLO attainments weighted by mark-share), gated on 3 offerings.
- **R2 Reflect** — persistence flag (below target in ≥2 of 3 offerings) +
  average-shortfall severity, banded High/Medium/Low/Very Low using CAA's own
  KPI 2.1 cutoff spacing (90/60/30/0, from the current caa.ae OBEF University
  Guidebook v11.5) — plus an RBT/Bloom's-verb wording-drift check on CLO text.
- **R3 Recommend** — evidence packet + literature-cited action menu (standard
  + innovative practices) + free-text instructor choice.
- **R4 Redesign** — change log with both a formal path (linked to an R3
  recommendation) and an informal/detected path (a drift R2 caught with no
  recommendation behind it).
- **R5 Reassess** — immediate before/after/target comparison and a Gap
  Closure metric, same H/M/L/VL bands.

Course A ("Data Structures & Algorithms") is built with a deliberate story:
CLO3 is chronically underperforming (flagged in R2), gets a formal redesign
logged in R4, and recovers above target in the very next offering (validated
in R5). CLO2's wording also drifts between offerings with no R3 recommendation
behind it, demonstrating R4's informal/detected path. Course B ("Machine
Learning Systems") is a healthy contrast course with no flags.

## Running it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`. Use the sidebar to switch between the two
demo courses and the tabs to walk through R1–R5.

## Files

- `data_model.py` — synthetic course/CLO/PLO/marks data + R3 menu + R4 log
- `engine.py` — OBER's real attainment formulas + R1–R5 computation
- `style.py` — shared palette + Plotly theme
- `app.py` — the Streamlit dashboard

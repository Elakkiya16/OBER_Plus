import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from data_model import COURSES, PLOS, OFFERINGS, TARGET_ATTAINMENT, R3_STANDARD_MENU, R3_INNOVATIVE_MENU, R4_LOG_COURSE_A
import engine as e
import style

st.set_page_config(page_title="OBER+ — Continuous Improvement Demo", page_icon="🎓", layout="wide")
st.markdown(style.CARD_CSS, unsafe_allow_html=True)
style.apply_plotly_template()

PLO_IDS = [p["id"] for p in PLOS]
PLO_NAME = {p["id"]: p["name"] for p in PLOS}


@st.cache_data
def load_course_data(course_code: str):
    course = e.prepare_course(COURSES[course_code], PLO_IDS)
    clo_by_offering = [e.clo_attainment(course, oi) for oi in range(3)]
    plo_by_offering = [e.plo_attainment(course, oi) for oi in range(3)]
    course_by_offering = [e.course_attainment(course, oi) for oi in range(3)]
    return course, clo_by_offering, plo_by_offering, course_by_offering


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------
st.sidebar.image("assets/bits_logo.png", width=140)
st.sidebar.title("OBER+")
st.sidebar.caption("5R continuous-improvement loop on top of OBER's real CLO/PLO attainment engine")
course_code = st.sidebar.radio("Course", list(COURSES.keys()), format_func=lambda c: f"{c} — {COURSES[c]['name']}")
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<span class='section-note'>All data on this page is <b>synthetic</b>, generated to demonstrate the 5R loop "
    "— not real student records. Attainment target shown as an illustrative uniform "
    f"{TARGET_ATTAINMENT:.0f}% (configurable per course/CLO in a real deployment).</span>",
    unsafe_allow_html=True,
)

course, clo_by_offering, plo_by_offering, course_by_offering = load_course_data(course_code)
clo_ids = [c["id"] for c in course["clos"]]
clo_desc_latest = {c["id"]: c["description_by_offering"][-1] for c in course["clos"]}

reflect_clo = {cid: e.r2_reflect_series(cid, cid, [clo_by_offering[oi][cid] for oi in range(3)]) for cid in clo_ids}
reflect_plo = {pid: e.r2_reflect_series(pid, PLO_NAME[pid], [plo_by_offering[oi][pid] for oi in range(3)])
               for pid in PLO_IDS if plo_by_offering[0].get(pid) is not None}
reflect_course = e.r2_reflect_series("COURSE", course["name"], course_by_offering)
drift_notes = e.r2_drift(course)
flagged_clos = [cid for cid, r in reflect_clo.items() if r.flagged]

st.markdown(f'<div class="oberplus-banner">📘 {course["code"]} — {course["name"]} · '
            f'{OFFERINGS[0]} → {OFFERINGS[2]} · Instructor: {" → ".join(dict.fromkeys(course["instructor_by_offering"]))}</div>',
            unsafe_allow_html=True)

tabs = st.tabs(["Overview", "R1 · Report", "R2 · Reflect", "R3 · Recommend", "R4 · Redesign", "R5 · Reassess"])

# --------------------------------------------------------------------------
# Overview
# --------------------------------------------------------------------------
with tabs[0]:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(style.kpi_card("Course Attainment (latest)", f'{course_by_offering[-1]:.1f}%',
                                    f"Target {TARGET_ATTAINMENT:.0f}%"), unsafe_allow_html=True)
    with c2:
        st.markdown(style.kpi_card("Offerings Tracked", f'{len(OFFERINGS)} / 3',
                                    "R1 gate: cleared ✓"), unsafe_allow_html=True)
    with c3:
        st.markdown(style.kpi_card("CLOs Flagged (R2)", f'{len(flagged_clos)} / {len(clo_ids)}',
                                    ", ".join(flagged_clos) if flagged_clos else "none — healthy"), unsafe_allow_html=True)
    with c4:
        st.markdown(style.kpi_card("Redesigns Logged (R4)", f'{len(R4_LOG_COURSE_A) if course_code=="CS D301 (Demo)" else 0}',
                                    "formal + informal"), unsafe_allow_html=True)

    left, right = st.columns([3, 2])
    with left:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=OFFERINGS, y=course_by_offering, mode="lines+markers",
                                  name="Course attainment", line=dict(width=3, color=style.CATEGORICAL[0]),
                                  marker=dict(size=9)))
        fig.add_hline(y=TARGET_ATTAINMENT, line_dash="dash", line_color=style.INK_MUTED,
                      annotation_text="Target", annotation_position="bottom right")
        fig.update_layout(title="Course Attainment Trend (R1 data)", yaxis_title="Attainment (%)",
                           yaxis_range=[0, 100], height=360)
        st.plotly_chart(fig, width='stretch')
    with right:
        latest_plo = {pid: plo_by_offering[-1][pid] for pid in PLO_IDS if plo_by_offering[-1].get(pid) is not None}
        fig2 = go.Figure(go.Bar(x=list(latest_plo.values()), y=[PLO_NAME[p] for p in latest_plo],
                                 orientation="h", marker_color=style.CATEGORICAL[2]))
        fig2.add_vline(x=TARGET_ATTAINMENT, line_dash="dash", line_color=style.INK_MUTED)
        fig2.update_layout(title="PLO Attainment (latest offering)", xaxis_title="Attainment (%)",
                            xaxis_range=[0, 100], height=360)
        st.plotly_chart(fig2, width='stretch')

# --------------------------------------------------------------------------
# R1 — Report
# --------------------------------------------------------------------------
with tabs[1]:
    gate = e.r1_gate(course)
    st.subheader("R1 · Report")
    st.markdown(f"<span class='section-note'>Computation is OBER's existing per-offering chain, unchanged. "
                f"What R1 adds: results accumulate across offerings, gated on **offering count** "
                f"(not calendar time) before any trend judgment downstream. Gate: "
                f"**{gate['offerings_available']} of 3 offerings available — "
                f"{'cleared ✓' if gate['gate_cleared'] else 'not yet cleared'}**.</span>", unsafe_allow_html=True)

    fig = go.Figure()
    for i, cid in enumerate(clo_ids):
        y = [clo_by_offering[oi][cid] for oi in range(3)]
        fig.add_trace(go.Scatter(x=OFFERINGS, y=y, mode="lines+markers", name=cid,
                                  line=dict(width=2.5, color=style.CATEGORICAL[i % len(style.CATEGORICAL)]),
                                  marker=dict(size=8)))
    fig.add_hline(y=TARGET_ATTAINMENT, line_dash="dash", line_color=style.INK_MUTED, annotation_text="Target")
    fig.update_layout(title="CLO Attainment by Offering (raw, OBER's weighted-average formula)",
                       yaxis_title="Attainment (%)", yaxis_range=[0, 100], height=420)
    st.plotly_chart(fig, width='stretch')

    df = pd.DataFrame({cid: [clo_by_offering[oi][cid] for oi in range(3)] for cid in clo_ids}, index=OFFERINGS).T
    df.insert(0, "CLO description (latest wording)", [clo_desc_latest[c] for c in df.index])
    st.dataframe(df, width='stretch')

# --------------------------------------------------------------------------
# R2 — Reflect
# --------------------------------------------------------------------------
with tabs[2]:
    st.subheader("R2 · Reflect")
    st.markdown("<span class='section-note'>Flag: below target in ≥2 of the last 3 offerings. "
                 "Shortfall: average (target − attainment) across just the offerings that missed. "
                 "Band: H/M/L/VL on (attainment ÷ target) × 100, using CAA's own KPI 2.1 cutoff spacing "
                 "(90 / 60 / 30 / 0) — reused, not invented.</span>", unsafe_allow_html=True)

    def reflect_table(results: dict, level: str):
        rows = []
        for key, r in results.items():
            rows.append({
                level: key, "Offering 1": r.attainments[0], "Offering 2": r.attainments[1], "Offering 3": r.attainments[2],
                "Target": r.target, "Flagged": "🚩 Yes" if r.flagged else "No",
                "Misses (of 3)": r.miss_count,
                "Avg shortfall (pts)": f"{r.avg_shortfall:.2f}" if r.avg_shortfall is not None else "—",
                "Band": r.band,
            })
        return pd.DataFrame(rows)

    st.markdown("**CLO level**")
    clo_df = reflect_table(reflect_clo, "CLO")
    for _, row in clo_df.iterrows():
        cols = st.columns([0.7, 0.7, 0.7, 0.7, 0.7, 0.9, 1.1, 1.1])
        cols[0].write(f"**{row['CLO']}**")
        cols[1].write(f"{row['Offering 1']:.1f}%")
        cols[2].write(f"{row['Offering 2']:.1f}%")
        cols[3].write(f"{row['Offering 3']:.1f}%")
        cols[4].write(f"{row['Target']:.0f}%")
        cols[5].write(row["Flagged"])
        cols[6].write(f"{row['Misses (of 3)']} miss(es), avg −{row['Avg shortfall (pts)']} pts"
                      if row["Avg shortfall (pts)"] != "—" else "no misses")
        cols[7].markdown(style.band_chip_html(row["Band"]), unsafe_allow_html=True)

    st.markdown("**PLO level**")
    plo_df = reflect_table(reflect_plo, "PLO")
    for _, row in plo_df.iterrows():
        cols = st.columns([1.0, 0.7, 0.7, 0.7, 0.7, 0.9, 1.1, 1.1])
        cols[0].write(f"**{row['PLO']}**")
        cols[1].write(f"{row['Offering 1']:.1f}%")
        cols[2].write(f"{row['Offering 2']:.1f}%")
        cols[3].write(f"{row['Offering 3']:.1f}%")
        cols[4].write(f"{row['Target']:.0f}%")
        cols[5].write(row["Flagged"])
        cols[6].write(f"{row['Misses (of 3)']} miss(es), avg −{row['Avg shortfall (pts)']} pts"
                      if row["Avg shortfall (pts)"] != "—" else "no misses")
        cols[7].markdown(style.band_chip_html(row["Band"]), unsafe_allow_html=True)

    st.markdown("**Course level**")
    st.markdown(style.band_chip_html(reflect_course.band,
                extra=f" · {'flagged' if reflect_course.flagged else 'not flagged'} · "
                      f"{reflect_course.miss_count} miss(es)"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**RBT / wording drift check** (from CLO description text — OBER has no structured RBT field)")
    if drift_notes:
        for note in drift_notes:
            for ch in note["changes"]:
                st.warning(
                    f"**{note['clo_id']}** changed at *{ch['at_offering']}* — "
                    f"RBT level {'changed' if ch['level_changed'] else 'unchanged'} "
                    f"({ch['from_level']} → {ch['to_level']})\n\n"
                    f"Before: \"{ch['from_text']}\"\n\nAfter: \"{ch['to_text']}\"\n\n"
                    f"_Attached as a note only — never suspends or replaces the flag above._"
                )
    else:
        st.info("No wording drift detected across the 3-offering window.")

# --------------------------------------------------------------------------
# R3 — Recommend
# --------------------------------------------------------------------------
with tabs[3]:
    st.subheader("R3 · Recommend")
    st.markdown("<span class='section-note'>R3 never auto-picks a fix. It packages R2's evidence and hands a person "
                 "a menu — whatever gets picked becomes a recorded, identified decision that R4/R5 can trace.</span>",
                 unsafe_allow_html=True)
    if not flagged_clos:
        st.info("No flagged CLOs for this course — nothing to recommend against.")
    else:
        target_clo = flagged_clos[0]
        r = reflect_clo[target_clo]
        st.markdown(f"#### Evidence packet — {target_clo}")
        st.markdown(f"*\"{clo_desc_latest[target_clo]}\"*")
        c1, c2, c3 = st.columns(3)
        c1.metric("Flagged", f"{r.miss_count} of 3 offerings")
        c2.metric("Avg shortfall", f"{r.avg_shortfall} pts")
        c3.markdown(style.band_chip_html(r.band), unsafe_allow_html=True)

        st.markdown("##### Standard practices")
        for name, cite in R3_STANDARD_MENU:
            st.markdown(f"- **{name}** — _{cite}_")
        st.markdown("##### Innovative practices")
        for name, cite in R3_INNOVATIVE_MENU:
            st.markdown(f"- **{name}** — _{cite}_")
        st.markdown("##### Instructor choice")
        st.text_input("Free text (always available, recorded the same way as a menu pick, without a citation)",
                       placeholder="e.g. custom in-class intervention...", disabled=True)

        if course_code == "CS D301 (Demo)":
            picked = next((r for r in R4_LOG_COURSE_A if r["clo"] == target_clo and r["path"] == "formal"), None)
            if picked:
                st.success(f"**Recorded decision {picked['recommendation_id']}**: "
                           f"\"{picked['recommendation_category']}\" — selected by {picked['changed_by']}, "
                           f"logged {picked['changed_at']}. This ID is what R4/R5 trace forward.")

# --------------------------------------------------------------------------
# R4 — Redesign
# --------------------------------------------------------------------------
with tabs[4]:
    st.subheader("R4 · Redesign")
    st.markdown("<span class='section-note'>Every change gets a record — formal (linked to an R3 recommendation) "
                 "or informal/detected (caught by R2's drift check, no recommendation behind it). Nothing left "
                 "unattended.</span>", unsafe_allow_html=True)
    log = R4_LOG_COURSE_A if course_code == "CS D301 (Demo)" else []
    if not log:
        st.info("No changes logged for this course in the demo window.")
    else:
        for rec in log:
            badge = "🟢 Formal (linked to R3)" if rec["path"] == "formal" else "🟠 Informal (detected, no R3 link)"
            with st.container():
                st.markdown(f"**{rec['id']}** · {badge} · {rec['clo']} · {rec['offering_boundary']}")
                st.markdown(f"{rec['what_changed']}")
                cb1, cb2 = st.columns(2)
                cb1.markdown(f"**Before:**\n\n{rec['before']}")
                cb2.markdown(f"**After:**\n\n{rec['after']}")
                st.caption(f"Changed by {rec['changed_by']} on {rec['changed_at']}"
                           + (f" · implements {rec['recommendation_id']} ({rec['recommendation_category']})"
                              if rec["recommendation_id"] else " · no linked R3 recommendation"))
                st.markdown("---")

# --------------------------------------------------------------------------
# R5 — Reassess
# --------------------------------------------------------------------------
with tabs[5]:
    st.subheader("R5 · Reassess")
    st.markdown("<span class='section-note'>Validated immediately: the one offering right after a redesign vs. the "
                 "one right before it — not a fresh 3-offering wait.</span>", unsafe_allow_html=True)
    formal_recs = [r for r in log] if course_code == "CS D301 (Demo)" else []
    formal_recs = [r for r in formal_recs if r["path"] == "formal"] if formal_recs else []
    if not formal_recs:
        st.info("No formal redesign logged for this course to reassess.")
    else:
        rec = formal_recs[0]
        target_clo = rec["clo"]
        before_val = clo_by_offering[1][target_clo]
        after_val = clo_by_offering[2][target_clo]
        result = e.r5_reassess(target_clo, before_val, after_val)

        c1, c2, c3 = st.columns(3)
        c1.markdown(style.kpi_card("Attainment before", f"{result.before:.1f}%", OFFERINGS[1]), unsafe_allow_html=True)
        c2.markdown(style.kpi_card("Attainment after", f"{result.after:.1f}%", OFFERINGS[2]), unsafe_allow_html=True)
        c3.markdown(style.kpi_card("Target", f"{result.target:.0f}%", "unchanged"), unsafe_allow_html=True)

        fig = go.Figure(go.Bar(
            x=["Before", "After"], y=[result.before, result.after],
            marker_color=[style.STATUS["VL"] if result.before < result.target else style.STATUS["H"],
                          style.STATUS["H"] if result.after >= result.target else style.STATUS["L"]],
            text=[f"{result.before:.1f}%", f"{result.after:.1f}%"], textposition="outside",
        ))
        fig.add_hline(y=result.target, line_dash="dash", line_color=style.INK_MUTED, annotation_text="Target")
        fig.update_layout(title=f"{target_clo} — before vs. after redesign", yaxis_range=[0, 100], height=380)
        st.plotly_chart(fig, width='stretch')

        st.markdown(f"#### Gap Closure metric: **{result.closure_pct}%** " +
                    style.band_chip_html(result.band), unsafe_allow_html=True)
        st.caption(f"Closure = (shortfall before − shortfall after) ÷ shortfall before = "
                   f"({result.shortfall_before:.1f} − {result.shortfall_after:.1f}) ÷ {result.shortfall_before:.1f} "
                   f"→ {result.verdict}. Redesign: {rec['what_changed']}")

"""
OBER+ stages: R1 Report, R2 Reflect, R3 Recommend, R4 Redesign, R5 Reassess.

Same screen grammar as the OBER pages — Select Course Code, then a report or
an action form. Nothing here re-derives attainment: every number comes from
OBER's own computation for that specific offering, since each offering can
carry its own component weightages.
"""
import plotly.graph_objects as go
import streamlit as st

import compute as cp
import style as S
from engine import r2_reflect_series, r5_reassess, classify_rbt, band
from store import (OFFERING_ORDER, PLO_IDS, TARGET_ATTAINMENT, R3_STANDARD_MENU,
                   R3_INNOVATIVE_MENU, clo_description_history, next_id)
from pages_ober import course_picker


def _plot_theme(fig, height=340, title=""):
    fig.update_layout(
        height=height, title=dict(text=title, font=dict(size=14, color=S.INK)),
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="Inter, system-ui, sans-serif", size=12, color=S.INK_SOFT),
        margin=dict(t=44, l=8, r=8, b=8),
        xaxis=dict(gridcolor="#eef1f5", linecolor="#dfe4ec", tickfont=dict(color=S.INK_MUTED)),
        yaxis=dict(gridcolor="#eef1f5", linecolor="#dfe4ec", tickfont=dict(color=S.INK_MUTED)),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    return fig


def _series(course):
    """Attainment % across the 3 offerings, at each level."""
    clo = {c["name"]: [cp.clo_attainment(course, i).get(c["name"], 0) * 100 for i in range(3)]
           for c in course["clos"]}
    plo = {p: [cp.plo_attainment(course, i).get(p, 0) * 100 for i in range(3)] for p in PLO_IDS}
    crs = [cp.course_attainment(course, i) * 100 for i in range(3)]
    return clo, plo, crs


def _reflect(course):
    clo_s, plo_s, crs_s = _series(course)
    rc = {k: r2_reflect_series(k, k, v) for k, v in clo_s.items()}
    rp = {k: r2_reflect_series(k, k, v) for k, v in plo_s.items()
          if any(k in course["mapping"].get(c["name"], []) for c in course["clos"])}
    rcr = r2_reflect_series("COURSE", course["code"], crs_s)
    return rc, rp, rcr, clo_s, crs_s


def _drift(store, course):
    notes = []
    for clo in course["clos"]:
        hist = clo_description_history(store, course["id"], clo["name"], clo["description"])
        for i in range(1, len(hist)):
            if hist[i] != hist[i - 1]:
                lv_from, lv_to = classify_rbt(hist[i - 1]), classify_rbt(hist[i])
                notes.append({
                    "clo": clo["name"], "at": OFFERING_ORDER[i],
                    "from_text": hist[i - 1], "to_text": hist[i],
                    "from_level": lv_from, "to_level": lv_to,
                    "level_changed": lv_from != lv_to,
                })
    return notes


# ---------------------------------------------------------------------------
# R1 — Report
# ---------------------------------------------------------------------------

def page_r1(store):
    st.markdown(S.crumb("R1 · Report"), unsafe_allow_html=True)
    note = ("Computation is OBER's existing per-offering chain, unchanged. R1 accumulates "
            "those results across offerings and gates on <b>offering count</b>, not calendar "
            "time, before anything downstream may be read as a trend.")
    with S.card("Longitudinal Attainment Report", note=note):
        course = course_picker(store, "r1_course")
        n = len(OFFERING_ORDER)
        clo_s, _plo_s, crs_s = _series(course)
        st.markdown(
            '<div class="stats">'
            + S.stat("Offerings on record", f"{n} / 3",
                     "gate cleared" if n >= 3 else "gate not yet cleared")
            + S.stat("Course attainment (latest)", f"{crs_s[-1]:.1f}%",
                     f"target {TARGET_ATTAINMENT:.0f}%")
            + S.stat("Instructor", course["instructor_by_offering"][-1], OFFERING_ORDER[-1])
            + S.stat("CLOs tracked", str(len(course["clos"])), course["code"])
            + "</div>", unsafe_allow_html=True)

    with S.card():
        fig = go.Figure()
        for i, (name, vals) in enumerate(clo_s.items()):
            fig.add_trace(go.Scatter(x=OFFERING_ORDER, y=vals, mode="lines+markers", name=name,
                                     line=dict(width=2.4, color=S.CHART[i % len(S.CHART)]),
                                     marker=dict(size=7)))
        fig.add_trace(go.Scatter(x=OFFERING_ORDER, y=crs_s, mode="lines+markers", name="Course",
                                 line=dict(width=3, color=S.INK, dash="dot"), marker=dict(size=8)))
        fig.add_hline(y=TARGET_ATTAINMENT, line_dash="dash", line_color=S.INK_MUTED,
                      annotation_text="Target")
        fig.update_yaxes(range=[0, 100], title="Attainment (%)")
        st.plotly_chart(_plot_theme(fig, 400, "CLO attainment by offering"), width="stretch")

        headers = ["CLO", "Description"] + OFFERING_ORDER
        rows = [[c["name"], c["description"]] + [f"{v:.2f}%" for v in clo_s[c["name"]]]
                for c in course["clos"]]
        rows.append(["", "Course attainment"] + [f"{v:.2f}%" for v in crs_s])
        st.markdown(S.report_table("", "", headers, rows,
                                   row_classes=[""] * len(course["clos"]) + ["total"]),
                    unsafe_allow_html=True)




# ---------------------------------------------------------------------------
# R2 — Reflect
# ---------------------------------------------------------------------------

def page_r2(store):
    st.markdown(S.crumb("R2 · Reflect"), unsafe_allow_html=True)
    note = ("<b>Flag</b> — below target in at least 2 of the last 3 offerings. "
            "<b>Shortfall</b> — average (target − attainment) across only the offerings that "
            "missed. <b>Band</b> — H/M/L/VL on (attainment ÷ target) × 100, using CAA's own "
            "KPI 2.1 cutoff spacing (90 / 60 / 30 / 0) from the OBEF University Guidebook v11.5.")
    with S.card("Persistence & Severity Review", note=note):
        course = course_picker(store, "r2_course")
        rc, rp, rcr, _clo_s, _crs = _reflect(course)
        flagged = [k for k, r in rc.items() if r.flagged]
        st.markdown(
            '<div class="stats">'
            + S.stat("CLOs flagged", f"{len(flagged)} / {len(rc)}",
                     ", ".join(flagged) if flagged else "none")
            + S.stat("Course level", S.BAND_LABEL[rcr.band],
                     "flagged" if rcr.flagged else "not flagged")
            + S.stat("Target", f"{TARGET_ATTAINMENT:.0f}%", "uniform across CLOs")
            + "</div>", unsafe_allow_html=True)

    with S.card("CLO level"):
        st.markdown(_reflect_table(rc), unsafe_allow_html=True)

    with S.card("PLO level"):
        st.markdown(_reflect_table(rp), unsafe_allow_html=True)

    drift_note = ("CLO Entry stores free text with no RBT field, and wording can change between "
                  "offerings at the I/C's discretion. This check reads the stored description for "
                  "each offering and classifies its leading action verb. A drift note never "
                  "suspends or replaces the flag above — it is attached alongside it, and feeds "
                  "R4 as a detected change.")
    with S.card("CLO wording / RBT drift check", note=drift_note):
        notes = _drift(store, course)
        if not notes:
            st.markdown('<div class="card-note">No wording change detected across the '
                        '3-offering window.</div>', unsafe_allow_html=True)
        for nte in notes:
            st.markdown(S.record_card(
                nte["clo"],
                f'RBT {"changed" if nte["level_changed"] else "unchanged"}: '
                f'{nte["from_level"]} → {nte["to_level"]}',
                "pill-detected", f'changed at {nte["at"]}',
                "Description was edited between offerings with no recommendation behind it.",
                before=nte["from_text"], after=nte["to_text"], accent=S.ORANGE,
            ), unsafe_allow_html=True)


def _reflect_table(results):
    headers = ["Item"] + OFFERING_ORDER + ["Target", "Flagged", "Misses", "Avg shortfall", "Band"]
    rows, cell_cls = [], []
    for k, r in results.items():
        flag = ('<span class="chip chip-flag">Yes</span>' if r.flagged
                else '<span class="chip chip-ok">No</span>')
        rows.append([k] + [f"{v:.2f}%" for v in r.attainments] +
                    [f"{r.target:.0f}%", flag, f"{r.miss_count} of 3",
                     f"−{r.avg_shortfall:.2f} pts" if r.avg_shortfall is not None else "—",
                     S.band_chip(r.band)])
        cell_cls.append([""] + ["bad" if v < r.target else "ok" for v in r.attainments]
                        + ["", "", "", "", ""])
    return S.report_table("", "", headers, rows, cell_classes=cell_cls)


# ---------------------------------------------------------------------------
# R3 — Recommend
# ---------------------------------------------------------------------------

def page_r3(store):
    st.markdown(S.crumb("R3 · Recommend"), unsafe_allow_html=True)
    note = ("R3 never auto-picks a fix. It packages R2's evidence and hands a person a menu; "
            "whatever is selected becomes a recorded decision with an ID that R4 and R5 trace "
            "forward.")
    with S.card("Evidence Packet & Recommendation", note=note):
        course = course_picker(store, "r3_course")
        rc, _rp, _rcr, _clo_s, _crs = _reflect(course)
        flagged = [k for k, r in rc.items() if r.flagged]
        if not flagged:
            st.markdown('<div class="card-note">No flagged CLOs for this course — nothing to '
                        'recommend against.</div>', unsafe_allow_html=True)
        else:
            target_clo = st.selectbox("Flagged CLO:", flagged, key="r3_clo")
            r = rc[target_clo]
            desc = next(c["description"] for c in course["clos"] if c["name"] == target_clo)
            st.markdown(f'<div class="card-note" style="font-style:italic;">"{desc}"</div>',
                        unsafe_allow_html=True)
            st.markdown(
                '<div class="stats">'
                + S.stat("Flagged", f"{r.miss_count} of 3", "offerings below target")
                + S.stat("Avg shortfall", f"{r.avg_shortfall:.2f} pts", "across missed offerings")
                + S.stat("Severity band", S.BAND_LABEL[r.band], "CAA cutoff spacing")
                + "</div>", unsafe_allow_html=True)

    if flagged:
        with S.card("Standard practices"):
            st.markdown(S.menu_grid(R3_STANDARD_MENU, S.BLUE), unsafe_allow_html=True)
        with S.card("Innovative practices"):
            st.markdown(S.menu_grid(R3_INNOVATIVE_MENU, S.BRAND_GOLD), unsafe_allow_html=True)

        with S.card("Record a decision"):
            names = ([n for n, _c in R3_STANDARD_MENU] + [n for n, _c in R3_INNOVATIVE_MENU]
                     + ["Instructor choice (free text)"])
            pick = st.selectbox("Action category:", names, key="r3_pick")
            free = ""
            if pick.startswith("Instructor choice"):
                free = st.text_input("Describe the action:", key="r3_free")
            who = st.text_input("Decided by:", value=course["instructor_by_offering"][-1],
                                key="r3_who")
            if st.button("Record Recommendation", key="r3_save"):
                cite = dict(R3_STANDARD_MENU + R3_INNOVATIVE_MENU).get(
                    pick, "instructor choice — no citation")
                rid = next_id("R3-2026", store["recommendations"])
                store["recommendations"].append({
                    "id": rid, "course": course["id"], "clo": target_clo,
                    "category": free.strip() if free.strip() else pick,
                    "citation": cite, "decided_by": who,
                    "evidence": f"Below target in {r.miss_count} of 3 offerings; average "
                                f"shortfall {r.avg_shortfall:.2f} pts; band {S.BAND_LABEL[r.band]}.",
                    "decided_on": "2026-08-28", "status": "Recorded",
                })
                st.success(f"Recorded as {rid}. R4 can now log a redesign against this ID.")

    recs = [r for r in store["recommendations"] if r["course"] == course["id"]]
    if recs:
        with S.card("Recorded decisions"):
            for r in recs:
                st.markdown(S.record_card(
                    r["id"], r["status"], "pill-formal", f'{r["clo"]} · {r["decided_on"]}',
                    f'<b>{r["category"]}</b><br/>'
                    f'<span style="font-size:0.8rem;font-style:italic;">{r["citation"]}</span>'
                    f'<br/>{r["evidence"]}',
                    footer=f'Decided by {r["decided_by"]}', accent=S.GREEN,
                ), unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# R4 — Redesign
# ---------------------------------------------------------------------------

def page_r4(store):
    st.markdown(S.crumb("R4 · Redesign"), unsafe_allow_html=True)
    note = ("Every change is recorded — <b>formal</b> when it implements a recorded R3 "
            "recommendation, <b>detected</b> when R2's drift check caught it with no "
            "recommendation behind it. Both carry full before/after content, the offering "
            "boundary, and who changed it.")
    with S.card("Change Log", note=note):
        course = course_picker(store, "r4_course")
        log = [r for r in store["change_log"] if r["course"] == course["id"]]
        formal = len([r for r in log if r["path"] == "formal"])
        st.markdown('<div class="stats">'
                    + S.stat("Records", str(len(log)), "this course")
                    + S.stat("Formal", str(formal), "linked to an R3 ID")
                    + S.stat("Detected", str(len(log) - formal), "no recommendation behind them")
                    + "</div>", unsafe_allow_html=True)

    with S.card():
        if not log:
            st.markdown('<div class="card-note">No changes logged for this course.</div>',
                        unsafe_allow_html=True)
        for rec in log:
            is_formal = rec["path"] == "formal"
            st.markdown(S.record_card(
                rec["id"],
                "Formal · linked to R3" if is_formal else "Detected · no R3 link",
                "pill-formal" if is_formal else "pill-detected",
                f'{rec["clo"]} · {rec["offering_boundary"]}',
                rec["what_changed"], before=rec["before"], after=rec["after"],
                footer=(f'Changed by {rec["changed_by"]} on {rec["changed_at"]}'
                        + (f' · implements {rec["recommendation_id"]}'
                           if rec["recommendation_id"] else ' · no linked R3 recommendation')),
                accent=S.GREEN if is_formal else S.ORANGE,
            ), unsafe_allow_html=True)

    with S.card("Log a change"):
        clos = [c["name"] for c in course["clos"]]
        a = st.columns(2)
        clo = a[0].selectbox("CLO:", clos, key="r4_clo")
        recs = ["— none (detected / informal) —"] + [
            r["id"] for r in store["recommendations"] if r["course"] == course["id"]]
        link = a[1].selectbox("Implements recommendation:", recs, key="r4_link")
        what = st.text_input("What changed:", key="r4_what")
        b = st.columns(2)
        before = b[0].text_input("Before:", key="r4_before")
        after = b[1].text_input("After:", key="r4_after")
        who = st.text_input("Changed by:", value=course["instructor_by_offering"][-1], key="r4_who")
        if st.button("Add to Change Log", key="r4_save"):
            if not what.strip():
                st.warning("Describe what changed.")
            else:
                store["change_log"].append({
                    "id": next_id("REC-2026", store["change_log"]),
                    "course": course["id"], "clo": clo,
                    "path": "detected" if link.startswith("—") else "formal",
                    "recommendation_id": None if link.startswith("—") else link,
                    "offering_boundary": f"{OFFERING_ORDER[-2]} → {OFFERING_ORDER[-1]}",
                    "what_changed": what.strip(), "before": before.strip(),
                    "after": after.strip(), "changed_by": who, "changed_at": "2026-08-28",
                })
                st.rerun()


# ---------------------------------------------------------------------------
# R5 — Reassess
# ---------------------------------------------------------------------------

def page_r5(store):
    st.markdown(S.crumb("R5 · Reassess"), unsafe_allow_html=True)
    note = ("Validated immediately: the offering right after a logged redesign against the one "
            "right before it, not a fresh 3-offering wait. <b>Gap Closure</b> = (shortfall before "
            "− shortfall after) ÷ shortfall before, banded on the same CAA cutoff spacing as R2.")
    with S.card("Gap Closure Report", note=note):
        course = course_picker(store, "r5_course")
        log = [r for r in store["change_log"] if r["course"] == course["id"]]
        if not log:
            st.markdown('<div class="card-note">Nothing logged in R4 for this course to '
                        'reassess.</div>', unsafe_allow_html=True)
            return
        labels = [f'{r["id"]} — {r["clo"]}' for r in log]
        rec = log[labels.index(st.selectbox("Redesign record:", labels, key="r5_pick"))]

    clo = rec["clo"]
    before = cp.clo_attainment(course, 1).get(clo, 0) * 100
    after = cp.clo_attainment(course, 2).get(clo, 0) * 100
    res = r5_reassess(clo, before, after)

    with S.card():
        st.markdown('<div class="stats">'
                    + S.stat("Attainment before", f"{res.before:.2f}%", OFFERING_ORDER[1])
                    + S.stat("Attainment after", f"{res.after:.2f}%", OFFERING_ORDER[2])
                    + S.stat("Target", f"{res.target:.0f}%", "unchanged")
                    + S.stat("Gap closure",
                             f"{res.closure_pct:.1f}%" if res.closure_pct is not None else "n/a",
                             res.verdict)
                    + "</div>", unsafe_allow_html=True)

        fig = go.Figure(go.Bar(
            x=["Before", "After"], y=[res.before, res.after],
            marker_color=[S.BAND_COLOR["VL"] if res.before < res.target else S.BAND_COLOR["H"],
                          S.BAND_COLOR["H"] if res.after >= res.target else S.BAND_COLOR["L"]],
            text=[f"{res.before:.1f}%", f"{res.after:.1f}%"], textposition="outside", width=0.45,
        ))
        fig.add_hline(y=res.target, line_dash="dash", line_color=S.INK_MUTED,
                      annotation_text="Target")
        fig.update_yaxes(range=[0, 100], title="Attainment (%)")
        st.plotly_chart(_plot_theme(fig, 340, f"{clo} — before vs. after redesign"),
                        width="stretch")

        rows = [
            ["Shortfall before", f"{res.shortfall_before:.2f} pts"],
            ["Shortfall after", f"{res.shortfall_after:.2f} pts"],
            ["Gap Closure",
             f"{res.closure_pct:.1f}%" if res.closure_pct is not None else "not applicable"],
            ["Band", S.band_chip(res.band)],
            ["Redesign applied", rec["what_changed"]],
            ["Linked recommendation", rec["recommendation_id"] or "none — detected change"],
        ]
        st.markdown(S.report_table("", "", ["Metric", "Value"], rows,
                                   row_classes=["", "", "total", "", "", ""]),
                    unsafe_allow_html=True)

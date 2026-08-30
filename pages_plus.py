"""
OBER+ stages: R1 Report, R2 Reflect, R3 Recommend, R4 Redesign, R5 Reassess.

Chart forms follow the reader's question, not habit:
  R1  grouped columns  — three offerings are discrete sittings, not a continuous
                         series; shaded light→dark with time (an ordered
                         sequence, so a sequential ramp of one hue)
  R5  dumbbell         — the form for before → after per item, across every
                         logged redesign on one axis

Nothing here re-derives attainment: every number is OBER's own computation for
that specific offering.
"""
import streamlit as st

import compute as cp
import style as S
from engine import r2_reflect_series, r5_reassess, classify_rbt
from store import (OFFERING_ORDER, PLO_IDS, R3_STANDARD_MENU,
                   R3_INNOVATIVE_MENU, clo_description_history, next_id)
from pages_ober import course_picker, head

SHORT = ["Sem I 2024-25", "Sem II 2024-25", "Sem I 2025-26"]


def target_of(course):
    return float(course.get("target", 60.0))


def _series(course):
    clo = {c["name"]: [cp.clo_attainment(course, i).get(c["name"], 0) * 100 for i in range(3)]
           for c in course["clos"]}
    plo = {p: [cp.plo_attainment(course, i).get(p, 0) * 100 for i in range(3)] for p in PLO_IDS}
    crs = [cp.course_attainment(course, i) * 100 for i in range(3)]
    return clo, plo, crs


def _reflect(course):
    t = target_of(course)
    clo_s, plo_s, crs_s = _series(course)
    rc = {k: r2_reflect_series(k, k, v, t) for k, v in clo_s.items()}
    rp = {k: r2_reflect_series(k, k, v, t) for k, v in plo_s.items()
          if any(k in course["mapping"].get(c["name"], []) for c in course["clos"])}
    rcr = r2_reflect_series("COURSE", course["code"], crs_s, t)
    return rc, rp, rcr, clo_s, crs_s


def _drift(store, course):
    notes = []
    for clo in course["clos"]:
        hist = clo_description_history(store, course["id"], clo["name"], clo["description"])
        for i in range(1, len(hist)):
            if hist[i] != hist[i - 1]:
                a, b = classify_rbt(hist[i - 1]), classify_rbt(hist[i])
                notes.append({"clo": clo["name"], "at": OFFERING_ORDER[i],
                              "from_text": hist[i - 1], "to_text": hist[i],
                              "from_level": a, "to_level": b, "level_changed": a != b})
    return notes


def target_control(course, key):
    """Editable per course — her own Target Sheet notes targets can be fixed by
    subject difficulty, so this is not a constant."""
    c = st.columns([1.1, 4])
    v = c[0].number_input("Attainment target (%)", min_value=0, max_value=100, step=5,
                          value=int(target_of(course)), key=key)
    course["target"] = float(v)
    return float(v)


# ---------------------------------------------------------------------------
# R1 — grouped columns
# ---------------------------------------------------------------------------

def _grouped_columns(clo_series, target):
    W, Hgt = 1140, 340
    PADL, PADR, PADT, PADB = 54, 96, 20, 48
    plotw, ploth = W - PADL - PADR, Hgt - PADT - PADB
    ytop = lambda v: PADT + (100 - v) / 100 * ploth
    out = [f'<svg viewBox="0 0 {W} {Hgt}" style="width:100%;height:{Hgt}px;display:block;">']
    for g in (0, 20, 40, 60, 80, 100):
        gy = ytop(g)
        out.append(f'<line x1="{PADL}" y1="{gy:.1f}" x2="{W - PADR}" y2="{gy:.1f}" '
                   f'stroke="#EDF1F6" stroke-width="1"/>'
                   f'<text x="{PADL - 12}" y="{gy + 4:.1f}" text-anchor="end" font-size="12" '
                   f'fill="{S.MUTED}" font-family="Manrope,sans-serif">{g}</text>')
    n = max(1, len(clo_series))
    gw = plotw / n
    barw = min(46, (gw - 22) / 3)
    for gi, (clo, vals) in enumerate(clo_series.items()):
        gx = PADL + gi * gw
        group_w = len(vals) * barw + (len(vals) - 1) * 2
        x0 = gx + (gw - group_w) / 2
        for bi, v in enumerate(vals):
            bx = x0 + bi * (barw + 2)
            by, bh = ytop(v), ytop(0) - ytop(v)
            out.append(f'<path d="M{bx:.1f},{by + 4:.1f} a4,4 0 0 1 4,-4 h{barw - 8:.1f} '
                       f'a4,4 0 0 1 4,4 v{bh - 4:.1f} h-{barw:.1f} Z" fill="{S.SEQ[bi]}"/>')
            out.append(f'<text x="{bx + barw / 2:.1f}" y="{by - 7:.1f}" text-anchor="middle" '
                       f'font-size="11.5" font-weight="700" fill="{S.SOFT}" '
                       f'font-family="Manrope,sans-serif">{v:.0f}</text>')
        out.append(f'<text x="{gx + gw / 2:.1f}" y="{Hgt - 18}" text-anchor="middle" '
                   f'font-size="14" font-weight="700" fill="{S.INK}" '
                   f'font-family="Manrope,sans-serif">{clo}</text>')
    ty = ytop(target)
    out.append(f'<line x1="{PADL}" y1="{ty:.1f}" x2="{W - PADR}" y2="{ty:.1f}" stroke="{S.RED}" '
               f'stroke-width="2" stroke-dasharray="7 5"/>'
               f'<text x="{W - PADR + 10}" y="{ty + 4:.1f}" text-anchor="start" font-size="12.5" '
               f'font-weight="800" fill="{S.RED}" font-family="Manrope,sans-serif">'
               f'Target {target:.0f}%</text></svg>')
    return "".join(out)


def page_r1(store):
    head("Report", "Attainment accumulated across offerings.")
    with S.card():
        c = st.columns([3, 2])
        with c[0]:
            course = course_picker(store, "r1_course")
        t = target_of(course)
        clo_s, _p, crs_s = _series(course)
        below = sum(1 for v in clo_s.values() if v[-1] < t)
        st.markdown(S.stats_row([
            S.stat("Offerings on record", f"3<span class='faint'>/3</span>", "Trend gate cleared"),
            S.stat("Course attainment", f"{crs_s[-1]:.1f}%", f"target {t:.0f}%"),
            S.stat("CLOs below target", f"{below}<span class='faint'>/{len(clo_s)}</span>",
                   "latest offering"),
            S.stat("Instructor", course["instructor_by_offering"][-1],
                   OFFERING_ORDER[-1], small=True),
        ]), unsafe_allow_html=True)

    with S.card("CLO attainment by offering",
                right="target 60%"):
        st.markdown(S.legend(list(zip(SHORT, S.SEQ))), unsafe_allow_html=True)
        st.markdown(_grouped_columns(clo_s, t), unsafe_allow_html=True)

    with S.card("The record"):
        headers = ["CLO", "Description"] + SHORT
        rows, cls = [], []
        for c in course["clos"]:
            v = clo_s[c["name"]]
            rows.append([c["name"], c["description"]] + [f"{x:.1f}%" for x in v])
            cls.append(["", ""] + ["bad" if x < t else "ok" for x in v])
        rows.append(["Course", "Weighted by each CLO's mark share"] +
                    [f"{x:.1f}%" for x in crs_s])
        cls.append(["", ""] + ["bad" if x < t else "ok" for x in crs_s])
        st.markdown(S.table(headers, rows, row_classes=[""] * len(course["clos"]) + ["total"],
                            cell_classes=cls), unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# R2 — Reflect
# ---------------------------------------------------------------------------

def page_r2(store):
    head("Reflect", "What is persistently below target, and by how much.")
    with S.card():
        c = st.columns([3, 2])
        with c[0]:
            course = course_picker(store, "r2_course")
        t = target_control(course, "r2_target")
        rc, rp, rcr, _c, _s = _reflect(course)
        flagged = [k for k, r in rc.items() if r.flagged]
        worst = max([r.avg_shortfall for r in rc.values() if r.avg_shortfall] or [0])
        worst_clo = next((k for k, r in rc.items()
                          if r.avg_shortfall and abs(r.avg_shortfall - worst) < 1e-9), "—")
        wb = rc[worst_clo].band if worst_clo in rc else "OK"
        st.markdown(S.stats_row([
            S.stat("CLOs flagged", f"{len(flagged)}<span class='faint'>/{len(rc)}</span>",
                   ", ".join(flagged) if flagged else "none below target twice"),
            S.stat("Course level", S.BAND_LABEL[rcr.band],
                   "flagged" if rcr.flagged else "not flagged", small=True),
            S.stat("Lowest performing", worst_clo, f"−{worst:.2f} pts · band {S.BAND_LABEL[wb]}",
                   accent=S.BAND_COLOR.get(wb, S.GOLD)),
            S.stat("Offerings", "3<span class='faint'>/3</span>", "gate cleared"),
        ]), unsafe_allow_html=True)

    with S.card("Attainment bands"):
        st.markdown(S.band_scale(t), unsafe_allow_html=True)

    with S.card("Course learning outcomes"):
        desc = {c["name"]: c["description"] for c in course["clos"]}
        for k, r in rc.items():
            short = desc.get(k, "")
            short = short if len(short) < 46 else short[:44].rsplit(" ", 1)[0] + "…"
            sf = (f'<div style="font-size:16.5px;font-weight:700;color:{S.INK};">'
                  f'−{r.avg_shortfall:.2f} pts</div>'
                  f'<div style="height:8px;border-radius:999px;background:'
                  f'{S.BAND_COLOR[r.band]}22;margin-top:9px;overflow:hidden;">'
                  f'<div style="width:{max(0, min(100, r.avg_ratio or 0)):.0f}%;height:100%;'
                  f'background:{S.BAND_COLOR[r.band]};"></div></div>'
                  if r.avg_shortfall is not None else
                  f'<div style="font-size:14.5px;color:{S.MUTED};">No shortfall</div>')
            chip = (S.band_chip(r.band, f" · {r.avg_ratio:.0f}%")
                    if r.avg_ratio is not None else S.band_chip("OK"))
            st.markdown(S.clo_card(k, short, list(zip(r.attainments, SHORT)), t, sf, chip,
                                   alert=(r.band in ("L", "VL"))), unsafe_allow_html=True)

    with S.card("Programme outcomes"):
        rows, cls = [], []
        for k, r in rp.items():
            flag = ('<span class="chip" style="background:#FCECEA;color:#C0392F;">Flagged</span>'
                    if r.flagged else
                    '<span class="chip" style="background:#EEF1F5;color:#7E8CA1;">No</span>')
            rows.append([k] + [f"{v:.1f}%" for v in r.attainments] + [
                flag,
                f"−{r.avg_shortfall:.2f} pts" if r.avg_shortfall is not None else "—",
                S.band_meter(r.avg_ratio, r.band)])
            cls.append([""] + ["bad" if v < t else "ok" for v in r.attainments] + ["", "", ""])
        st.markdown(S.table(["PLO"] + SHORT + ["Flagged", "Avg shortfall", "vs target"],
                            rows, cell_classes=cls), unsafe_allow_html=True)

    notes = _drift(store, course)
    with S.card("CLO wording drift",
                right=f"{len(notes)} detected" if notes else "none detected"):
        if not notes:
            st.markdown(f'<div class="card-note">No CLO description changed across the '
                        f'three-offering window.</div>', unsafe_allow_html=True)
        for n in notes:
            st.markdown(S.record_card(
                n["clo"], f'{n["from_level"]} → {n["to_level"]}', "#FDF3E3", "#8A5A12",
                f'changed at {n["at"]}',
                "Edited between offerings with no recommendation behind it.",
                before=n["from_text"], after=n["to_text"], accent=S.BAND_COLOR["L"]),
                unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# R3 — Recommend
# ---------------------------------------------------------------------------

def page_r3(store):
    head("Recommend", "Evidence packaged for a person to decide on.")
    with S.card():
        c = st.columns([3, 2])
        with c[0]:
            course = course_picker(store, "r3_course")
        rc, _rp, _rcr, _c, _s = _reflect(course)
        flagged = [k for k, r in rc.items() if r.flagged]
        if not flagged:
            st.markdown('<div class="card-note">No flagged CLOs for this course — nothing to '
                        'recommend against.</div>', unsafe_allow_html=True)
        else:
            with c[1]:
                target_clo = st.selectbox("Flagged CLO", flagged, key="r3_clo")
            r = rc[target_clo]
            st.markdown(S.stats_row([
                S.stat("Missed", f"{r.miss_count} of 3", "offerings below target"),
                S.stat("Avg shortfall", f"−{r.avg_shortfall:.2f}", "points"),
                S.stat("Band", S.BAND_LABEL[r.band], f"{r.avg_ratio:.0f}% of target", small=True,
                       accent=S.BAND_COLOR[r.band]),
            ]), unsafe_allow_html=True)
            desc = next(c["description"] for c in course["clos"] if c["name"] == target_clo)
            st.markdown(f'<div style="font-size:14.5px;color:{S.SOFT};margin-top:16px;">'
                        f'<b style="color:{S.INK};">{target_clo}</b> — {desc}</div>',
                        unsafe_allow_html=True)

    if flagged:
        with S.card("Standard practices", right="established evidence"):
            st.markdown(S.menu_grid(R3_STANDARD_MENU, S.CHART[0]), unsafe_allow_html=True)
        with S.card("Innovative practices", right="for specialised electives"):
            st.markdown(S.menu_grid(R3_INNOVATIVE_MENU, S.GOLD), unsafe_allow_html=True)

        with S.card("Record a decision"):
            names = ([n for n, _c in R3_STANDARD_MENU] + [n for n, _c in R3_INNOVATIVE_MENU]
                     + ["Instructor choice (free text)"])
            a = st.columns([3.4, 1.8, 1.2])
            pick = a[0].selectbox("Action", names, key="r3_pick")
            who = a[1].text_input("Decided by", value=course["instructor_by_offering"][-1],
                                  key="r3_who")
            a[2].markdown('<div style="height:29px;"></div>', unsafe_allow_html=True)
            free = ""
            if pick.startswith("Instructor choice"):
                free = st.text_input("Describe the action", key="r3_free")
            if a[2].button("Record", key="r3_save", width="stretch", type="primary"):
                cite = dict(R3_STANDARD_MENU + R3_INNOVATIVE_MENU).get(
                    pick, "instructor choice — no citation")
                rid = next_id("R3-2026", store["recommendations"])
                store["recommendations"].append({
                    "id": rid, "course": course["id"], "clo": target_clo,
                    "category": free.strip() or pick, "citation": cite, "decided_by": who,
                    "evidence": f"Below target in {r.miss_count} of 3 offerings; average "
                                f"shortfall {r.avg_shortfall:.2f} pts; band {S.BAND_LABEL[r.band]}.",
                    "decided_on": "2026-08-29", "status": "Recorded"})
                st.success(f"Recorded as {rid} — R4 can now log a redesign against it.")

    recs = [r for r in store["recommendations"] if r["course"] == course["id"]]
    if recs:
        with S.card("Recorded decisions"):
            for r in recs:
                st.markdown(S.record_card(
                    r["id"], r["status"], "#E7F6EE", "#10693D",
                    f'{r["clo"]} · {r["decided_on"]}',
                    f'<b>{r["category"]}</b><br/>{r["evidence"]}',
                    footer=f'{r["citation"]} · decided by {r["decided_by"]}',
                    accent=S.BAND_COLOR["H"]), unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# R4 — Redesign
# ---------------------------------------------------------------------------

def page_r4(store):
    head("Redesign", "Every change on record, deliberate or not.")
    with S.card():
        course = course_picker(store, "r4_course")
        log = [r for r in store["change_log"] if r["course"] == course["id"]]
        formal = len([r for r in log if r["path"] == "formal"])
        st.markdown(S.stats_row([
            S.stat("Records", str(len(log)), "this course"),
            S.stat("Formal", str(formal), "linked to a recommendation"),
            S.stat("Detected", str(len(log) - formal), "caught by the drift check"),
        ]), unsafe_allow_html=True)

    with S.card("Change log"):
        if not log:
            st.markdown('<div class="card-note">Nothing logged for this course.</div>',
                        unsafe_allow_html=True)
        for rec in log:
            f = rec["path"] == "formal"
            st.markdown(S.record_card(
                rec["id"], "Formal" if f else "Detected",
                "#E7F6EE" if f else "#FDF3E3", "#10693D" if f else "#8A5A12",
                f'{rec["clo"]} · {rec["offering_boundary"]}',
                rec["what_changed"], before=rec["before"], after=rec["after"],
                footer=(f'{rec["changed_by"]} · {rec["changed_at"]}'
                        + (f' · implements {rec["recommendation_id"]}'
                           if rec["recommendation_id"] else ' · no linked recommendation')),
                accent=S.BAND_COLOR["H"] if f else S.BAND_COLOR["L"]), unsafe_allow_html=True)

    with S.card("Log a change"):
        a = st.columns(2)
        clo = a[0].selectbox("CLO", [c["name"] for c in course["clos"]], key="r4_clo")
        recs = ["— none (detected) —"] + [r["id"] for r in store["recommendations"]
                                          if r["course"] == course["id"]]
        link = a[1].selectbox("Implements", recs, key="r4_link")
        what = st.text_input("What changed", key="r4_what")
        b = st.columns([1, 1, 0.7])
        before = b[0].text_input("Before", key="r4_before")
        after = b[1].text_input("After", key="r4_after")
        b[2].markdown('<div style="height:29px;"></div>', unsafe_allow_html=True)
        if b[2].button("Add to log", key="r4_save", width="stretch", type="primary"):
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
                    "after": after.strip(),
                    "changed_by": course["instructor_by_offering"][-1],
                    "changed_at": "2026-08-29"})
                st.rerun()


# ---------------------------------------------------------------------------
# R5 — dumbbell across every logged redesign
# ---------------------------------------------------------------------------

def _dumbbell(rows, target):
    """rows: list of (clo, rec_id, before, after, closure, band, verdict)"""
    W = 1120
    PADL, PADR, PADT = 210, 160, 30
    rowh = 62
    Hgt = PADT + len(rows) * rowh + 30
    plot = W - PADL - PADR
    dx = lambda v: PADL + max(0.0, min(100.0, v)) / 100 * plot
    out = [f'<svg viewBox="0 0 {W} {Hgt}" style="width:100%;height:{Hgt}px;display:block;">']
    for g in (0, 20, 40, 60, 80, 100):
        gx = dx(g)
        out.append(f'<line x1="{gx:.1f}" y1="{PADT - 8}" x2="{gx:.1f}" '
                   f'y2="{PADT + len(rows) * rowh - 18}" stroke="#EDF1F6" stroke-width="1"/>'
                   f'<text x="{gx:.1f}" y="{PADT + len(rows) * rowh + 4}" text-anchor="middle" '
                   f'font-size="12" fill="{S.MUTED}" font-family="Manrope,sans-serif">{g}</text>')
    tx = dx(target)
    out.append(f'<line x1="{tx:.1f}" y1="{PADT - 16}" x2="{tx:.1f}" '
               f'y2="{PADT + len(rows) * rowh - 18}" stroke="{S.RED}" stroke-width="2" '
               f'stroke-dasharray="7 5"/>'
               f'<text x="{tx:.1f}" y="{PADT - 22}" text-anchor="middle" font-size="12.5" '
               f'font-weight="800" fill="{S.RED}" font-family="Manrope,sans-serif">'
               f'Target {target:.0f}%</text>')
    for i, (clo, rec, before, after, closure, band, verdict) in enumerate(rows):
        cy = PADT + i * rowh + 14
        out.append(f'<text x="0" y="{cy + 5:.1f}" font-size="15" font-weight="800" '
                   f'fill="{S.INK}" font-family="Manrope,sans-serif">{clo}</text>'
                   f'<text x="58" y="{cy + 5:.1f}" font-size="12.5" fill="{S.MUTED}" '
                   f'font-family="Manrope,sans-serif">{rec}</text>')
        out.append(f'<line x1="{dx(before):.1f}" y1="{cy:.1f}" x2="{dx(after):.1f}" '
                   f'y2="{cy:.1f}" stroke="{S.SKY}" stroke-width="4" stroke-linecap="round"/>')
        out.append(f'<circle cx="{dx(before):.1f}" cy="{cy:.1f}" r="7" fill="{S.AMBER}" '
                   f'stroke="#FFFFFF" stroke-width="2.5"/>'
                   f'<circle cx="{dx(after):.1f}" cy="{cy:.1f}" r="7" fill="{S.RED_T}" '
                   f'stroke="#FFFFFF" stroke-width="2.5"/>')
        ctxt = f"{closure:.0f}%" if closure is not None else "n/a"
        out.append(f'<text x="{W - PADR + 16}" y="{cy + 5:.1f}" font-size="15" font-weight="800" '
                   f'fill="{S.BAND_COLOR[band]}" font-family="Manrope,sans-serif">{ctxt}</text>'
                   f'<text x="{W - PADR + 74}" y="{cy + 5:.1f}" font-size="12.5" '
                   f'fill="{S.MUTED}" font-family="Manrope,sans-serif">{verdict}</text>')
    out.append("</svg>")
    return "".join(out)


def page_r5(store):
    head("Reassess", "Did the change actually close the gap?")
    with S.card():
        c = st.columns([3, 2])
        with c[0]:
            course = course_picker(store, "r5_course")
        log = [r for r in store["change_log"] if r["course"] == course["id"]]
        if not log:
            st.markdown('<div class="card-note">Nothing logged in R4 to reassess.</div>',
                        unsafe_allow_html=True)
            return
        labels = [f'{r["id"]} — {r["clo"]}' for r in log]
        with c[1]:
            rec = log[labels.index(st.selectbox("Redesign record", labels, key="r5_pick"))]

    t = target_of(course)
    rows = []
    for r in log:
        clo = r["clo"]
        before = cp.clo_attainment(course, 1).get(clo, 0) * 100
        after = cp.clo_attainment(course, 2).get(clo, 0) * 100
        res = r5_reassess(clo, before, after, t)
        rows.append((clo, r["id"], before, after, res.closure_pct, res.band,
                     res.verdict.split(" —")[0]))

    with S.card("Every logged redesign, before → after",
                right="before → after"):
        st.markdown(S.legend([("Offering before the redesign", S.AMBER),
                              ("Offering after", S.RED_T)]), unsafe_allow_html=True)
        st.markdown(_dumbbell(rows, t), unsafe_allow_html=True)

    sel = next(x for x in rows if x[1] == rec["id"])
    _clo, _rid, before, after, closure, band, verdict = sel
    res = r5_reassess(_clo, before, after, t)

    c = st.columns([1, 1.6])
    with c[0]:
        with S.card():
            ctxt = f"{closure:.0f}%" if closure is not None else "n/a"
            st.markdown(
                f'<div class="k" style="font-size:12px;font-weight:800;letter-spacing:0.1em;'
                f'color:{S.MUTED};text-transform:uppercase;">Selected · {rec["id"]}</div>'
                f'<div class="hero" style="color:{S.BAND_COLOR[band]};margin-top:12px;">{ctxt}</div>'
                f'<div style="font-size:15px;font-weight:700;color:{S.INK};margin-top:12px;">'
                f'{res.verdict}</div>'
                f'<div style="height:10px;border-radius:999px;background:{S.BAND_COLOR[band]}22;'
                f'margin-top:16px;overflow:hidden;"><div style="width:'
                f'{max(0, min(100, closure or 0)):.0f}%;height:100%;'
                f'background:{S.BAND_COLOR[band]};"></div></div>', unsafe_allow_html=True)
    with c[1]:
        with S.card("Detail"):
            st.markdown(S.table(["", ""], [
                ["Attainment before → after", f"{before:.2f}% → {after:.2f}%"],
                ["Shortfall before → after",
                 f"{res.shortfall_before:.2f} pts → {res.shortfall_after:.2f} pts"],
                ["Redesign applied", rec["what_changed"]],
                ["Linked recommendation", rec["recommendation_id"] or "none — detected change"],
                ["Logged by", f'{rec["changed_by"]} · {rec["changed_at"]}'],
            ], cell_classes=[["", "kv"]] * 5), unsafe_allow_html=True)

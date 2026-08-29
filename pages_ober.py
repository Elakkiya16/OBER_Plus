"""
OBER's own screens: Handout Upload, CLO Entry, Evaluation Components (with the
Weightage and Mark Distribution matrices), CLO-PLO Mapping, Marks Entry, a
Reports overview, and the three reports. Same flow, controls and validation
rules as the deployed tool.
"""
import streamlit as st

import compute as cp
import style as S
from store import DEFAULT_TARGET, PLO_IDS, course_options


# ---------------------------------------------------------------------------
# Shared
# ---------------------------------------------------------------------------

def head(title, sub, course=None):
    st.markdown(S.page_head(title, sub), unsafe_allow_html=True)


def course_picker(store, key: str, label="Select course code"):
    opts = course_options(store)
    labels = list(opts.keys())
    prev = st.session_state.get("sel_course_label")
    idx = labels.index(prev) if prev in labels else 0
    chosen = st.selectbox(label, labels, index=idx, key=key)
    st.session_state.sel_course_label = chosen
    return store["courses"][opts[chosen]]


# ---------------------------------------------------------------------------
# Handout Upload
# ---------------------------------------------------------------------------

def page_handout(store):
    head("Handout Upload", "The approved course handout on file.")
    with S.card():
        course = course_picker(store, "ho_course")
        if course["handout"]:
            st.markdown(
                f'<div style="display:flex;align-items:center;justify-content:space-between;'
                f'gap:24px;background:#F7F9FC;border-radius:12px;padding:18px 22px;'
                f'margin-top:6px;"><div style="display:flex;align-items:center;gap:16px;">'
                f'<div style="width:44px;height:44px;border-radius:10px;background:{S.NAVY};'
                f'color:#fff;font-size:12px;font-weight:800;display:flex;align-items:center;'
                f'justify-content:center;">PDF</div><div>'
                f'<div style="font-size:15.5px;font-weight:700;color:{S.INK};">'
                f'{course["handout"]}</div>'
                f'<div style="font-size:13.5px;color:{S.MUTED};margin-top:4px;">'
                f'On file for {store["active_semester"]}</div></div></div></div>',
                unsafe_allow_html=True)
            st.download_button("Download handout",
                               data=f"Course handout for {course['label']}".encode(),
                               file_name=course["handout"], key="ho_dl")

    with S.card("Replace handout"):
        up = st.file_uploader("Choose a PDF or Word file", type=["pdf", "doc", "docx"],
                              key="ho_up")
        if st.button("Upload", key="ho_btn"):
            if up is None:
                st.warning("Choose a handout file first.")
            else:
                course["handout"] = up.name
                st.success("Handout uploaded and saved.")


# ---------------------------------------------------------------------------
# CLO Entry
# ---------------------------------------------------------------------------

def page_clo_entry(store):
    head("CLO Entry", "Course learning outcomes for the selected course.")
    with S.card():
        course = course_picker(store, "clo_course")

    with S.card("Defined outcomes", right=f'{len(course["clos"])} CLOs'):
        if not course["clos"]:
            st.info("No CLOs entered yet for this course.")
        else:
            h = st.columns([1.1, 6.2, 1.6])
            h[0].markdown('<div class="field-label">Name</div>', unsafe_allow_html=True)
            h[1].markdown('<div class="field-label">Description</div>', unsafe_allow_html=True)
            h[2].markdown('<div class="field-label">Actions</div>', unsafe_allow_html=True)
            for i, clo in enumerate(course["clos"]):
                c = st.columns([1.1, 6.2, 0.8, 0.8])
                if st.session_state.get("clo_editing") == (course["id"], i):
                    nn = c[0].text_input("n", value=clo["name"], key=f"cn{i}",
                                         label_visibility="collapsed")
                    nd = c[1].text_input("d", value=clo["description"], key=f"cd{i}",
                                         label_visibility="collapsed")
                    if c[2].button("Save", key=f"cs{i}"):
                        old = clo["name"]
                        clo["name"], clo["description"] = nn, nd
                        if old != nn:
                            for m in ("weightage", "mark_dist", "mapping"):
                                if old in course[m]:
                                    course[m][nn] = course[m].pop(old)
                        st.session_state.clo_editing = None
                        st.rerun()
                    if c[3].button("Cancel", key=f"cc{i}"):
                        st.session_state.clo_editing = None
                        st.rerun()
                else:
                    c[0].text_input("n", value=clo["name"], key=f"vn{i}", disabled=True,
                                    label_visibility="collapsed")
                    c[1].text_input("d", value=clo["description"], key=f"vd{i}", disabled=True,
                                    label_visibility="collapsed")
                    if c[2].button("Edit", key=f"ce{i}"):
                        st.session_state.clo_editing = (course["id"], i)
                        st.rerun()
                    if c[3].button("Delete", key=f"cx{i}"):
                        name = clo["name"]
                        course["clos"].pop(i)
                        for m in ("weightage", "mark_dist", "mapping"):
                            course[m].pop(name, None)
                        st.rerun()

    with S.card("Add new CLO",
                note="The leading verb sets the RBT level OBER+ tracks for wording drift in R2."):
        a = st.columns([1.4, 5.4, 1.4])
        n = a[0].text_input("CLO name", key="new_clo_name", placeholder="CLO5")
        d = a[1].text_input("Description", key="new_clo_desc",
                            placeholder="Start with a Bloom's action verb")
        a[2].markdown('<div style="height:29px;"></div>', unsafe_allow_html=True)
        if a[2].button("Add CLO", key="add_clo", width="stretch"):
            if not n.strip():
                st.warning("Enter a CLO name.")
            elif any(c["name"] == n.strip() for c in course["clos"]):
                st.warning(f"{n.strip()} already exists for this course.")
            else:
                course["clos"].append({"name": n.strip(), "description": d.strip()})
                course["weightage"].setdefault(n.strip(), {})
                course["mark_dist"].setdefault(n.strip(), {})
                course["mapping"].setdefault(n.strip(), [])
                st.rerun()


# ---------------------------------------------------------------------------
# Evaluation Components
# ---------------------------------------------------------------------------

def page_components(store):
    head("Evaluation Components", "Components, their weightage per CLO, and the mark split.")
    with S.card():
        course = course_picker(store, "ec_course")

    grand = sum(int(t) for _n, t in course["components"])
    with S.card("Components", right=f'{len(course["components"])} defined · {grand} marks total'):
        if not course["components"]:
            st.info("No components yet.")
        else:
            h = st.columns([4.4, 1.6, 1.6])
            h[0].markdown('<div class="field-label">Evaluation component</div>',
                          unsafe_allow_html=True)
            h[1].markdown('<div class="field-label">Total marks</div>', unsafe_allow_html=True)
            h[2].markdown('<div class="field-label">Actions</div>', unsafe_allow_html=True)
            for i, (name, total) in enumerate(course["components"]):
                c = st.columns([4.4, 1.6, 0.8, 0.8])
                if st.session_state.get("ec_editing") == (course["id"], i):
                    nn = c[0].text_input("n", value=name, key=f"ecn{i}",
                                         label_visibility="collapsed")
                    nt = c[1].number_input("t", value=int(total), min_value=0, step=1,
                                           key=f"ect{i}", label_visibility="collapsed")
                    if c[2].button("Save", key=f"ecs{i}"):
                        if nn != name:
                            for clo in course["weightage"]:
                                if name in course["weightage"][clo]:
                                    course["weightage"][clo][nn] = course["weightage"][clo].pop(name)
                            for clo in course["mark_dist"]:
                                if name in course["mark_dist"][clo]:
                                    course["mark_dist"][clo][nn] = course["mark_dist"][clo].pop(name)
                        course["components"][i] = [nn, int(nt)]
                        st.session_state.ec_editing = None
                        st.rerun()
                    if c[3].button("Cancel", key=f"ecc{i}"):
                        st.session_state.ec_editing = None
                        st.rerun()
                else:
                    c[0].text_input("n", value=name, key=f"ecvn{i}", disabled=True,
                                    label_visibility="collapsed")
                    c[1].text_input("t", value=str(total), key=f"ecvt{i}", disabled=True,
                                    label_visibility="collapsed")
                    if c[2].button("Edit", key=f"ece{i}"):
                        st.session_state.ec_editing = (course["id"], i)
                        st.rerun()
                    if c[3].button("Delete", key=f"ecx{i}"):
                        course["components"].pop(i)
                        for clo in course["weightage"]:
                            course["weightage"][clo].pop(name, None)
                        for clo in course["mark_dist"]:
                            course["mark_dist"][clo].pop(name, None)
                        st.rerun()

        a = st.columns([4.4, 1.6, 1.6])
        nm = a[0].text_input("Name", key="ec_new_name", placeholder="e.g. Exit Quiz")
        tm = a[1].number_input("Total marks", min_value=0, step=1, value=0, key="ec_new_total")
        a[2].markdown('<div style="height:29px;"></div>', unsafe_allow_html=True)
        if a[2].button("Add component", key="ec_add", width="stretch"):
            if not nm.strip():
                st.warning("Enter a component name.")
            elif any(c[0] == nm.strip() for c in course["components"]):
                st.warning("That component already exists.")
            else:
                course["components"].append([nm.strip(), int(tm)])
                st.rerun()

    _weightage_matrix(course)
    _mark_matrix(course, grand)


def _matrix_header(comps, widths, with_totals=True):
    head_cols = st.columns(widths)
    head_cols[0].markdown('<div class="mx-h lead">CLO / component</div>', unsafe_allow_html=True)
    for i, label in enumerate(comps):
        head_cols[i + 1].markdown(f'<div class="mx-h">{label}</div>', unsafe_allow_html=True)
    if with_totals:
        head_cols[-1].markdown('<div class="mx-h">Total</div>', unsafe_allow_html=True)


def _weightage_matrix(course):
    comps = [c[0] for c in course["components"]]
    clos = [c["name"] for c in course["clos"]]
    if not comps or not clos:
        return
    with S.card("I. Weightage Distribution (%)", right="Each CLO row must total 100%"):
        widths = [1.7] + [1.0] * len(comps) + [1.0]
        _matrix_header(comps, widths)
        all_ok = True
        for clo in clos:
            row = st.columns(widths)
            row[0].markdown(f'<div class="mx-l">{clo}</div>', unsafe_allow_html=True)
            total = 0
            for i, comp in enumerate(comps):
                cur = course["weightage"].get(clo, {}).get(comp, 0)
                v = row[i + 1].number_input(
                    f"w_{clo}_{comp}", min_value=0, max_value=100, step=5, value=int(cur),
                    key=f"w_{course['id']}_{clo}_{comp}", label_visibility="collapsed")
                if v:
                    course["weightage"].setdefault(clo, {})[comp] = int(v)
                else:
                    course["weightage"].get(clo, {}).pop(comp, None)
                total += int(v)
            ok = total == 100
            all_ok &= ok
            row[-1].markdown(f'<div class="mx-t {"ok" if ok else "bad"}">{total}</div>',
                             unsafe_allow_html=True)
        b = st.columns([1.7, 6])
        if b[0].button("Save weightages", key="save_w", width="stretch"):
            if all_ok:
                st.success("Weightages saved.")
            else:
                st.error("Fix CLO rows so each totals exactly 100%.")
        if not all_ok:
            b[1].markdown(f'<div style="color:{S.RED};font-size:14px;padding-top:12px;">'
                          f'Fix CLO rows so each totals exactly 100%.</div>',
                          unsafe_allow_html=True)


def _mark_matrix(course, grand):
    comps = course["components"]
    clos = [c["name"] for c in course["clos"]]
    if not comps or not clos:
        return
    with S.card(f"II. Mark Distribution ({grand})",
                right="Each column must equal that component's total marks"):
        widths = [1.7] + [1.0] * len(comps) + [1.0]
        _matrix_header([f"{n}<br/>({t})" for n, t in comps], widths)
        col_totals = {n: 0 for n, _t in comps}
        for clo in clos:
            row = st.columns(widths)
            row[0].markdown(f'<div class="mx-l">{clo}</div>', unsafe_allow_html=True)
            rtot = 0
            for i, (comp, ctot) in enumerate(comps):
                cur = course["mark_dist"].get(clo, {}).get(comp, 0)
                v = row[i + 1].number_input(
                    f"m_{clo}_{comp}", min_value=0, max_value=int(ctot), step=1, value=int(cur),
                    key=f"m_{course['id']}_{clo}_{comp}", label_visibility="collapsed")
                if v:
                    course["mark_dist"].setdefault(clo, {})[comp] = int(v)
                else:
                    course["mark_dist"].get(clo, {}).pop(comp, None)
                col_totals[comp] += int(v)
                rtot += int(v)
            row[-1].markdown(f'<div class="mx-t ok">{rtot}</div>', unsafe_allow_html=True)

        foot = st.columns(widths)
        foot[0].markdown('<div class="mx-l">Total</div>', unsafe_allow_html=True)
        all_ok = True
        for i, (comp, ctot) in enumerate(comps):
            ok = col_totals[comp] == int(ctot)
            all_ok &= ok
            foot[i + 1].markdown(
                f'<div class="mx-t {"ok" if ok else "bad"}">{col_totals[comp]}</div>',
                unsafe_allow_html=True)
        gt = sum(col_totals.values())
        foot[-1].markdown(f'<div class="mx-t navy">{gt}</div>', unsafe_allow_html=True)

        if st.button("Save mark distribution", key="save_m"):
            if all_ok:
                st.success("Mark distribution saved.")
            else:
                st.error("Each column total must equal that component's total marks.")


# ---------------------------------------------------------------------------
# CLO-PLO Mapping
# ---------------------------------------------------------------------------

def page_mapping(store):
    head("CLO-PLO Mapping", "Which programme outcomes each CLO feeds.")
    with S.card():
        course = course_picker(store, "map_course")

    with S.card("Mapping grid",
                note="Enter 1 in each cell the CLO maps to. PLO attainment is the average of the "
                     "CLOs mapped to it."):
        widths = [1.5] + [1.0] * len(PLO_IDS)
        h = st.columns(widths)
        h[0].markdown('<div class="mx-h lead">CO / PO</div>', unsafe_allow_html=True)
        for i, p in enumerate(PLO_IDS):
            h[i + 1].markdown(f'<div class="mx-h">{p}</div>', unsafe_allow_html=True)
        for clo in course["clos"]:
            name = clo["name"]
            row = st.columns(widths)
            row[0].markdown(f'<div class="mx-l">{name}</div>', unsafe_allow_html=True)
            mapped = course["mapping"].setdefault(name, [])
            for i, p in enumerate(PLO_IDS):
                v = row[i + 1].number_input(
                    f"p_{name}_{p}", min_value=0, max_value=1, step=1,
                    value=1 if p in mapped else 0,
                    key=f"p_{course['id']}_{name}_{p}", label_visibility="collapsed")
                if v and p not in mapped:
                    mapped.append(p)
                elif not v and p in mapped:
                    mapped.remove(p)
        if st.button("Save mapping", key="save_map"):
            st.success("CLO-PLO mapping saved.")


# ---------------------------------------------------------------------------
# Marks Entry
# ---------------------------------------------------------------------------

def page_marks_entry(store):
    head("Marks Entry", "Download the template, fill it, upload it back.")
    with S.card():
        c = st.columns(2)
        with c[0]:
            course = course_picker(store, "me_course")
        comps = [x[0] for x in course["components"]]
        if not comps:
            st.info("Add evaluation components for this course first.")
            return
        with c[1]:
            comp = st.selectbox("Select evaluation component", comps, key="me_comp")

    clos_in = [x["name"] for x in course["clos"]
               if course["mark_dist"].get(x["name"], {}).get(comp)]
    total_marks = dict(course["components"])[comp]

    with S.card(f"Upload marks for {comp}",
                right=f'{total_marks} marks · {", ".join(clos_in) if clos_in else "no CLOs mapped"}'):
        c = st.columns(2)
        with c[0]:
            st.markdown(
                f'<div style="background:#F7F9FC;border-radius:12px;padding:20px;">'
                f'<div style="font-size:15.5px;font-weight:700;color:{S.INK};">'
                f'1 · Download the template</div>'
                f'<div style="font-size:13.5px;color:{S.MUTED};margin-top:6px;line-height:1.5;">'
                f'One column per CLO assessed in this component, one row per enrolled student.'
                f'</div></div>', unsafe_allow_html=True)
            header = "User ID,Name," + ",".join(clos_in)
            template = header + "\n" + "\n".join(
                f'{s["user_id"]},{s["name"]},' + ",".join([""] * len(clos_in))
                for s in course["roster"])
            st.download_button("Download template", data=template.encode(),
                               file_name=f"{course['id']}_{comp.replace(' ', '_')}_template.csv",
                               key="me_tpl")
        with c[1]:
            st.markdown(
                f'<div style="background:#F7F9FC;border-radius:12px;padding:20px;">'
                f'<div style="font-size:15.5px;font-weight:700;color:{S.INK};">'
                f'2 · Upload it back</div>'
                f'<div style="font-size:13.5px;color:{S.MUTED};margin-top:6px;line-height:1.5;">'
                f'Leave a cell blank to record the student as absent for that CLO.</div></div>',
                unsafe_allow_html=True)
            up = st.file_uploader("Marks file", type=["csv"], key="me_up",
                                  label_visibility="collapsed")
            if up is not None and st.button("Upload marks", key="me_btn"):
                try:
                    n = _ingest_marks(course, comp, up, clos_in)
                    st.success(f"Marks uploaded for {comp} — {n} students updated.")
                except Exception as exc:
                    st.error(f"Could not read that file: {exc}")

    with S.card("Uploaded marks", right=f'{len(course["roster"])} students'):
        rows, cls = [], []
        for s in course["roster"]:
            sm = course["marks"].get(s["user_id"], {}).get(comp, {})
            vals = [f'{sm[c]:.1f}' if sm.get(c) is not None else
                    f'<span style="color:{S.MUTED};font-style:italic;">Absent</span>'
                    for c in clos_in]
            tot = cp.student_component_total(course, s["user_id"], comp)
            rows.append([s["user_id"], s["name"]] + vals + [f"{tot:.1f}" if sm else "—"])
            cls.append(["", ""] + [""] * len(clos_in) + [""])
        st.markdown(S.table(["User ID", "Name"] + clos_in + ["Total"], rows,
                            cell_classes=cls), unsafe_allow_html=True)


def _ingest_marks(course, comp, upload, clos_in):
    text = upload.read().decode("utf-8-sig", errors="replace")
    lines = [l for l in text.splitlines() if l.strip()]
    hdr = [h.strip() for h in lines[0].split(",")]
    clo_cols = {h: i for i, h in enumerate(hdr) if h in clos_in}
    if not clo_cols:
        raise ValueError("no CLO columns in that file match this component")
    n = 0
    for line in lines[1:]:
        parts = [p.strip() for p in line.split(",")]
        uid = parts[0]
        if uid not in course["marks"]:
            continue
        entry = {}
        for c, i in clo_cols.items():
            if i < len(parts) and parts[i].upper() not in ("", "ABSENT"):
                try:
                    entry[c] = float(parts[i])
                except ValueError:
                    pass
        if entry:
            course["marks"][uid][comp] = entry
            n += 1
    if n == 0:
        raise ValueError("no matching student rows found")
    return n


# ---------------------------------------------------------------------------
# Reports — overview
# ---------------------------------------------------------------------------

CATALOG = [
    ("Marks Report", "Every student, by component and CLO.", "Instructor · moderation",
     "Table only — raw marks; no chart earns its place", ["Excel", "CSV"], True),
    ("CLO Report", "Per-CLO attainment across components, plus course attainment.",
     "Instructor", "Diverging bar — distance from target per CLO", ["Excel", "PDF"], True),
    ("PLO Report", "CLO attainment carried into each mapped programme outcome.",
     "Programme · accreditation", "Bars against target, plus the CLO→PLO grid",
     ["Excel", "PDF"], True),
    ("Attainment Trend", "The same course across every offering on record.",
     "Instructor · HoD", "Grouped columns per CLO; heatmap past ~6 CLOs",
     ["Excel", "PDF"], False),
    ("Continuous Improvement Report",
     "The full 5R chain: flagged → recommended → redesigned → reassessed, with IDs and dates.",
     "CAA · accreditation", "Evidence chain, not a chart — one row per flagged CLO",
     ["PDF"], False),
    ("Programme PLO Summary", "Every course feeding each PLO, one grid.",
     "HoD · programme review", "Heatmap, course × PLO, sequential", ["Excel", "PDF"], False),
]


def page_reports_hub(store):
    head("Reports", "What can be generated, for whom, and in what form.")
    with S.card():
        course_picker(store, "rh_course")

    with S.card("Report catalogue", right="3 in OBER today · 3 proposed for OBER+"):
        rows, cls = [], []
        for name, what, who, viz, fmts, exists in CATALOG:
            badge = (S.band_chip("OK", "") if False else
                     f'<span class="chip" style="background:'
                     f'{"#F2F4F7" if exists else "#FDF3E3"};color:'
                     f'{S.MUTED if exists else "#8A5A12"};">'
                     f'{"In OBER" if exists else "Proposed"}</span>')
            tags = " ".join(f'<span class="chip" style="background:#EEF3FB;color:{S.NAVY};">{f}</span>'
                            for f in fmts)
            rows.append([f'<b>{name}</b> {badge}<br/>'
                         f'<span style="font-size:13px;color:{S.MUTED};">{what}</span>',
                         viz, who, tags])
            cls.append(["", "", "", ""])
        st.markdown(S.table(["Report", "Visualisation", "Audience", "Download"], rows,
                            cell_classes=cls), unsafe_allow_html=True)

    c = st.columns(2)
    with c[0]:
        with S.card("Why a chart, or not"):
            st.markdown(
                f'<div style="font-size:14.5px;color:{S.SOFT};line-height:1.7;">'
                f'The reader\'s question picks the form. <b style="color:{S.INK};">Above or below '
                f'target</b> → diverging bar. <b style="color:{S.INK};">Compare discrete '
                f'sittings</b> → grouped columns. <b style="color:{S.INK};">Before → after</b> → '
                f'dumbbell. <b style="color:{S.INK};">A grid of many CLOs or courses</b> → '
                f'heatmap. Raw marks stay a table.</div>', unsafe_allow_html=True)
    with c[1]:
        with S.card("Formats"):
            st.markdown(
                f'<div style="font-size:14.5px;color:{S.SOFT};line-height:1.7;">'
                f'<b style="color:{S.INK};">Excel</b> for anything someone will re-cut.<br/>'
                f'<b style="color:{S.INK};">PDF</b> for anything submitted as-is, with charts '
                f'rendered in.<br/><b style="color:{S.INK};">CSV</b> only where a system, not a '
                f'person, is the reader.</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Reports — Marks
# ---------------------------------------------------------------------------

def page_report_marks(store):
    head("Marks Report", "Every student, by component and CLO.")
    with S.card():
        c = st.columns([3, 1.2, 1.2])
        with c[0]:
            course = course_picker(store, "rm_course")
        c[1].markdown('<div style="height:29px;"></div>', unsafe_allow_html=True)
        if c[1].button("Generate report", key="rm_gen", width="stretch"):
            st.session_state.rm_shown = True

    if not st.session_state.get("rm_shown"):
        return

    comps = [x[0] for x in course["components"]]
    clos = [x["name"] for x in course["clos"]]
    headers = ["#", "User ID", "Name"]
    for comp in comps:
        in_comp = [cl for cl in clos if course["mark_dist"].get(cl, {}).get(comp)]
        headers += [f"{comp} · {cl}" for cl in in_comp] + [f"{comp} total"]
    headers += ["Grand total"]

    tints = {comp: f"t{(i % 5) + 1}" for i, comp in enumerate(comps)}
    rows, cls, csv_rows = [], [], [headers]
    for n, s in enumerate(course["roster"], 1):
        row, cl = [str(n), s["user_id"], s["name"]], ["", "", ""]
        grand = 0.0
        for comp in comps:
            in_comp = [c for c in clos if course["mark_dist"].get(c, {}).get(comp)]
            sm = course["marks"].get(s["user_id"], {}).get(comp, {})
            for c in in_comp:
                v = sm.get(c)
                row.append(f"{v:.1f}" if v is not None else "—")
                cl.append(tints[comp])
            t = cp.student_component_total(course, s["user_id"], comp)
            grand += t
            row.append(f"{t:.1f}" if sm else "0")
            cl.append(tints[comp])
        row.append(f"{grand:.1f}")
        cl.append("")
        rows.append(row)
        cls.append(cl)
        csv_rows.append(row)

    with S.card(right=f'{len(course["roster"])} students'):
        st.markdown(S.table(headers, rows, cell_classes=cls), unsafe_allow_html=True)
        st.download_button("Download marks report",
                           data="\n".join(",".join(r) for r in csv_rows).encode(),
                           file_name=f"{course['id']}_marks_report.csv", key="rm_dl")


# ---------------------------------------------------------------------------
# Reports — CLO (with the diverging bar)
# ---------------------------------------------------------------------------

def page_report_clo(store):
    head("CLO Report", "Attainment per CLO across evaluation components.")
    with S.card():
        c = st.columns([3, 1.2, 1.2])
        with c[0]:
            course = course_picker(store, "rc_course")
        c[1].markdown('<div style="height:29px;"></div>', unsafe_allow_html=True)
        if c[1].button("Generate report", key="rc_gen", width="stretch"):
            st.session_state.rc_shown = True

    if not st.session_state.get("rc_shown"):
        return

    from pages_plus import target_of
    t = target_of(course)
    clos = [c["name"] for c in course["clos"]]
    comp_att = cp.component_attainment(course)
    clo_att = cp.clo_attainment(course)
    crs = cp.course_attainment(course)

    with S.card("Distance from target",
                right="diverging — the question is above or below, and by how much"):
        st.markdown(_diverging_svg(clos, clo_att, t), unsafe_allow_html=True)

    with S.card():
        headers = ["Evaluation component"] + clos
        rows, rcls = [], []
        for comp, _tm in course["components"]:
            rows.append([comp] + [f"{comp_att[c].get(comp):.2f}"
                                  if comp_att[c].get(comp) is not None else "0.00" for c in clos])
            rcls.append("")
        rows.append(["Attainment (weighted average)"] + [f"{clo_att[c]:.2f}" for c in clos])
        rcls.append("total")
        rows.append(["Course attainment", f"{crs * 100:.0f}%"] + [""] * (len(clos) - 1))
        rcls.append("grand")
        cell_cls = [[""] * (len(clos) + 1) for _ in rows]
        cell_cls[-1][1] = "gold"
        st.markdown(S.table(headers, rows, row_classes=rcls, cell_classes=cell_cls,
                            caption="CLO Attainment", caption_color="red"),
                    unsafe_allow_html=True)
        st.download_button("Download CLO report",
                           data="\n".join(",".join(r) for r in [headers] + rows).encode(),
                           file_name=f"{course['id']}_clo_report.csv", key="rc_dl")


def _diverging_svg(clos, clo_att, target):
    W, rowh = 1120, 52
    Hgt = 34 + len(clos) * rowh
    zero, scale = W * 0.52, 11.0
    out = [f'<svg viewBox="0 0 {W} {Hgt}" style="width:100%;height:{Hgt}px;display:block;">']
    for i, clo in enumerate(clos):
        att = clo_att.get(clo, 0.0) * 100
        delta = att - target
        cy = 26 + i * rowh
        w = min(abs(delta) * scale, zero - 340)
        if delta >= 0:
            x, col, lx, anch = zero, S.BAND_COLOR["H"], zero + w + 12, "start"
        else:
            ratio = (att / target * 100) if target else 0
            col = (S.BAND_COLOR["VL"] if ratio < 30 else
                   S.BAND_COLOR["L"] if ratio < 60 else
                   S.BAND_COLOR["M"] if ratio < 90 else S.BAND_COLOR["H"])
            x, lx, anch = zero - w, zero - w - 12, "end"
        out.append(f'<text x="{zero - 330}" y="{cy + 5:.0f}" font-size="15" font-weight="800" '
                   f'fill="{S.INK}" font-family="Manrope,sans-serif">{clo}</text>')
        out.append(f'<text x="{zero - 272}" y="{cy + 5:.0f}" font-size="14" fill="{S.MUTED}" '
                   f'font-family="Manrope,sans-serif">attainment {att / 100:.2f}</text>')
        out.append(f'<rect x="{x:.1f}" y="{cy - 13}" width="{w:.1f}" height="26" rx="4" '
                   f'fill="{col}"/>')
        out.append(f'<text x="{lx:.1f}" y="{cy + 5:.0f}" text-anchor="{anch}" font-size="14" '
                   f'font-weight="800" fill="{col}" font-family="Manrope,sans-serif">'
                   f'{delta:+.1f} pts</text>')
    out.append(f'<line x1="{zero}" y1="6" x2="{zero}" y2="{Hgt - 22}" stroke="{S.RED}" '
               f'stroke-width="2"/>')
    out.append(f'<text x="{zero}" y="{Hgt - 6}" text-anchor="middle" font-size="12.5" '
               f'font-weight="800" fill="{S.RED}" font-family="Manrope,sans-serif">'
               f'Target {target:.0f}%</text></svg>')
    return "".join(out)


# ---------------------------------------------------------------------------
# Reports — PLO
# ---------------------------------------------------------------------------

def _plo_bars(plo_att, target):
    """One column per PLO the course actually feeds, read against the target rule.

    Unmapped PLOs are left out rather than drawn at zero — a zero there would
    read as a failed outcome instead of an outcome this course does not carry.
    """
    items = [(p, v * 100) for p, v in plo_att.items() if v]
    if not items:
        return ""
    W, Hgt = 1140, 300
    PADL, PADR, PADT, PADB = 54, 96, 20, 46
    plotw, ploth = W - PADL - PADR, Hgt - PADT - PADB
    ytop = lambda v: PADT + (100 - v) / 100 * ploth
    out = [f'<svg viewBox="0 0 {W} {Hgt}" style="width:100%;height:{Hgt}px;display:block;">']
    for g in (0, 20, 40, 60, 80, 100):
        gy = ytop(g)
        out.append(f'<line x1="{PADL}" y1="{gy:.1f}" x2="{W - PADR}" y2="{gy:.1f}" '
                   f'stroke="#EDF1F6" stroke-width="1"/>'
                   f'<text x="{PADL - 12}" y="{gy + 4:.1f}" text-anchor="end" font-size="12" '
                   f'fill="{S.MUTED}" font-family="Manrope,sans-serif">{g}</text>')
    gw = plotw / max(1, len(items))
    barw = min(74, gw - 26)
    for i, (plo, v) in enumerate(items):
        bx = PADL + i * gw + (gw - barw) / 2
        by, bh = ytop(v), ytop(0) - ytop(v)
        col = S.NAVY if v >= target else S.BAND_COLOR["L"]
        out.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{barw:.1f}" height="{bh:.1f}" '
                   f'rx="4" fill="{col}"/>')
        out.append(f'<text x="{bx + barw / 2:.1f}" y="{by - 8:.1f}" text-anchor="middle" '
                   f'font-size="12.5" font-weight="700" fill="{S.SOFT}" '
                   f'font-family="Manrope,sans-serif">{v:.0f}</text>')
        out.append(f'<text x="{bx + barw / 2:.1f}" y="{Hgt - 16}" text-anchor="middle" '
                   f'font-size="14" font-weight="700" fill="{S.INK}" '
                   f'font-family="Manrope,sans-serif">{plo}</text>')
    ty = ytop(target)
    out.append(f'<line x1="{PADL}" y1="{ty:.1f}" x2="{W - PADR}" y2="{ty:.1f}" '
               f'stroke="{S.RED}" stroke-width="2" stroke-dasharray="7 5"/>'
               f'<text x="{W - PADR + 10}" y="{ty + 4:.1f}" text-anchor="start" font-size="12.5" '
               f'font-weight="800" fill="{S.RED}" font-family="Manrope,sans-serif">'
               f'Target {target:.0f}%</text></svg>')
    return "".join(out)


def page_report_plo(store):
    head("PLO Report", "CLO attainment carried into each mapped programme outcome.")
    with S.card():
        c = st.columns([3, 1.2, 1.2])
        with c[0]:
            course = course_picker(store, "rp_course")
        c[1].markdown('<div style="height:29px;"></div>', unsafe_allow_html=True)
        if c[1].button("Generate report", key="rp_gen", width="stretch"):
            st.session_state.rp_shown = True

    if not st.session_state.get("rp_shown"):
        return

    clo_att = cp.clo_attainment(course)
    plo_att = cp.plo_attainment(course)
    bars = _plo_bars(plo_att, DEFAULT_TARGET)
    if bars:
        with S.card("Programme outcomes this course feeds",
                    right="only the mapped PLOs — an unmapped one is not a zero"):
            st.markdown(bars, unsafe_allow_html=True)
    with S.card():
        headers = ["CLO", "Attainment"] + PLO_IDS
        rows, rcls = [], []
        for c in course["clos"]:
            n = c["name"]
            a = clo_att.get(n, 0.0)
            rows.append([n, f"{a:.2f}"] +
                        [f"{a:.2f}" if p in course["mapping"].get(n, []) else "—"
                         for p in PLO_IDS])
            rcls.append("")
        rows.append(["Attainment (average)", ""] +
                    [f"{plo_att[p]:.2f}" if plo_att[p] else "—" for p in PLO_IDS])
        rcls.append("total")
        st.markdown(S.table(headers, rows, row_classes=rcls,
                            caption="CLO – PLO Attainment", caption_color="orange"),
                    unsafe_allow_html=True)
        st.download_button("Download PLO report",
                           data="\n".join(",".join(r) for r in [headers] + rows).encode(),
                           file_name=f"{course['id']}_plo_report.csv", key="rp_dl")

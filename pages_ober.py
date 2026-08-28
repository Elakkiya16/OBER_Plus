"""
OBER's own screens, rebuilt: Handout Upload, CLO Entry, Evaluation Components
(with Weightage + Mark Distribution), CLO-PLO Mapping, Marks Entry, and the
three Reports. Same flow, same controls, same validation rules as the
deployed tool.
"""
import streamlit as st

import compute as cp
import style as S
from store import PLO_IDS, course_options


# ---------------------------------------------------------------------------
# Shared: the "Select Course Code" control every OBER screen opens with
# ---------------------------------------------------------------------------

def course_picker(store, key: str):
    opts = course_options(store)
    labels = list(opts.keys())
    prev = st.session_state.get("sel_course_label")
    idx = labels.index(prev) if prev in labels else 0
    chosen = st.selectbox("Select Course Code:", labels, index=idx, key=key)
    st.session_state.sel_course_label = chosen
    return store["courses"][opts[chosen]]


# ---------------------------------------------------------------------------
# 3.1 Handout Upload
# ---------------------------------------------------------------------------

def page_handout(store):
    st.markdown(S.crumb("HandoutUpload"), unsafe_allow_html=True)
    with S.card("Upload Handout (PDF or Word)"):
        course = course_picker(store, "ho_course")

        if course["handout"]:
            st.markdown(f'<div class="card-note">📎 Existing File: '
                        f'<b>{course["handout"]}</b></div>', unsafe_allow_html=True)
            st.download_button(
                "Download Handout",
                data=f"Course handout for {course['label']}".encode(),
                file_name=course["handout"], key="ho_dl")

        up = st.file_uploader("Choose file", type=["pdf", "doc", "docx"], key="ho_up")
        if st.button("Upload", key="ho_btn"):
            if up is None:
                st.warning("Choose a handout file first.")
            else:
                course["handout"] = up.name
                st.success("Handout uploaded and saved")


# ---------------------------------------------------------------------------
# 3.2 CLO Entry
# ---------------------------------------------------------------------------

def page_clo_entry(store):
    st.markdown(S.crumb("CloEntry"), unsafe_allow_html=True)
    with S.card("CLO Entry"):
        course = course_picker(store, "clo_course")

        if course["clos"]:
            hdr = st.columns([1.1, 6.4, 1.5])
            hdr[0].markdown('<div class="field-label">Name</div>', unsafe_allow_html=True)
            hdr[1].markdown('<div class="field-label">Description</div>', unsafe_allow_html=True)
            hdr[2].markdown('<div class="field-label">Actions</div>', unsafe_allow_html=True)

            for i, clo in enumerate(course["clos"]):
                c = st.columns([1.1, 6.4, 0.75, 0.75])
                editing = st.session_state.get("clo_editing") == (course["id"], i)
                if editing:
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
        else:
            st.info("No CLOs entered yet for this course.")

    with S.card("Add New CLO"):
        n = st.text_input("CLO Name", key="new_clo_name")
        d = st.text_input("CLO Description", key="new_clo_desc")
        if st.button("Add CLO", key="add_clo"):
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
# 3.3 Evaluation Components + Weightage + Mark Distribution
# ---------------------------------------------------------------------------

def page_components(store):
    st.markdown(S.crumb("EvaluationComponents"), unsafe_allow_html=True)
    with S.card("Evaluation Components"):
        course = course_picker(store, "ec_course")

        if course["components"]:
            hdr = st.columns([4.5, 1.6, 1.5])
            hdr[0].markdown('<div class="field-label">Evaluation Component</div>',
                            unsafe_allow_html=True)
            hdr[1].markdown('<div class="field-label">Total Marks</div>', unsafe_allow_html=True)
            hdr[2].markdown('<div class="field-label">Actions</div>', unsafe_allow_html=True)

            for i, (name, total) in enumerate(course["components"]):
                c = st.columns([4.5, 1.6, 0.75, 0.75])
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
        else:
            st.markdown('<div class="card-note">No components yet.</div>', unsafe_allow_html=True)

    with S.card("Add New Evaluation Component"):
        a = st.columns([4.5, 1.6, 1.5])
        nm = a[0].text_input("Name", key="ec_new_name")
        tm = a[1].number_input("Total Marks", min_value=0, step=1, value=0, key="ec_new_total")
        a[2].markdown('<div style="height:27px;"></div>', unsafe_allow_html=True)
        if a[2].button("Add Component", key="ec_add"):
            if not nm.strip():
                st.warning("Enter a component name.")
            elif any(c[0] == nm.strip() for c in course["components"]):
                st.warning("That component already exists.")
            else:
                course["components"].append([nm.strip(), int(tm)])
                st.rerun()

    _weightage_matrix(course)
    _mark_matrix(course)


def _weightage_matrix(course):
    comps = [c[0] for c in course["components"]]
    clos = [c["name"] for c in course["clos"]]
    if not comps or not clos:
        return

    with S.card("I. Weightage Distribution (%)",
                title_right="Each CLO row must total 100%"):
        widths = [1.7] + [1.0] * len(comps) + [1.0]
        head = st.columns(widths)
        head[0].markdown('<div class="mx-head"><div class="lead">CLOS / Evaluation Component'
                         '</div></div>', unsafe_allow_html=True)
        for i, c in enumerate(comps):
            head[i + 1].markdown(f'<div class="mx-head"><div>{c}</div></div>',
                                 unsafe_allow_html=True)
        head[-1].markdown('<div class="mx-head"><div>Total</div></div>', unsafe_allow_html=True)

        all_ok = True
        for clo in clos:
            row = st.columns(widths)
            row[0].markdown(f'<div class="mx-lead">{clo}</div>', unsafe_allow_html=True)
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
            row[-1].markdown(f'<div class="mx-total {"ok" if ok else "bad"}">{total}</div>',
                             unsafe_allow_html=True)

        b = st.columns([1.6, 6])
        if b[0].button("Save Weightages", key="save_w"):
            if all_ok:
                st.success("Weightages saved.")
            else:
                st.error("Fix CLO rows so each totals exactly 100%.")
        if not all_ok:
            b[1].markdown('<div style="color:#e0463c;font-size:0.82rem;padding-top:9px;">'
                          'Fix CLO rows so each totals exactly 100%.</div>',
                          unsafe_allow_html=True)


def _mark_matrix(course):
    comps = course["components"]
    clos = [c["name"] for c in course["clos"]]
    if not comps or not clos:
        return
    grand = sum(int(t) for _n, t in comps)

    with S.card(f"II. Mark Distribution ({grand})",
                title_right="Column totals must equal each component's total marks"):
        widths = [1.7] + [1.0] * len(comps) + [1.0]
        head = st.columns(widths)
        head[0].markdown('<div class="mx-head"><div class="lead">CLOS / Evaluation Component'
                         '</div></div>', unsafe_allow_html=True)
        for i, (n, t) in enumerate(comps):
            head[i + 1].markdown(f'<div class="mx-head"><div>{n}<br/>({t})</div></div>',
                                 unsafe_allow_html=True)
        head[-1].markdown('<div class="mx-head"><div>Total</div></div>', unsafe_allow_html=True)

        col_totals = {n: 0 for n, _t in comps}
        for clo in clos:
            row = st.columns(widths)
            row[0].markdown(f'<div class="mx-lead">{clo}</div>', unsafe_allow_html=True)
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
            row[-1].markdown(f'<div class="mx-total ok">{rtot}</div>', unsafe_allow_html=True)

        foot = st.columns(widths)
        foot[0].markdown('<div class="mx-lead">Total</div>', unsafe_allow_html=True)
        all_ok = True
        for i, (comp, ctot) in enumerate(comps):
            ok = col_totals[comp] == int(ctot)
            all_ok &= ok
            foot[i + 1].markdown(
                f'<div class="mx-total {"ok" if ok else "bad"}">{col_totals[comp]}</div>',
                unsafe_allow_html=True)
        gt = sum(col_totals.values())
        foot[-1].markdown(f'<div class="mx-total {"ok" if gt == grand else "bad"}">{gt}</div>',
                          unsafe_allow_html=True)

        if st.button("Save Mark Distribution", key="save_m"):
            if all_ok:
                st.success("Mark distribution saved.")
            else:
                st.error("Each column total must equal that component's total marks.")


# ---------------------------------------------------------------------------
# 3.4 CLO-PLO Mapping
# ---------------------------------------------------------------------------

def page_mapping(store):
    st.markdown(S.crumb("PloMapping"), unsafe_allow_html=True)
    with S.card("PLO Mapping", note="Enter 1 in each PLO cell the CLO maps to."):
        course = course_picker(store, "map_course")

        widths = [1.4] + [1.0] * len(PLO_IDS)
        head = st.columns(widths)
        head[0].markdown('<div class="mx-head"><div class="lead">CO / PO</div></div>',
                         unsafe_allow_html=True)
        for i, p in enumerate(PLO_IDS):
            head[i + 1].markdown(f'<div class="mx-head"><div>{p}</div></div>',
                                 unsafe_allow_html=True)

        for clo in course["clos"]:
            name = clo["name"]
            row = st.columns(widths)
            row[0].markdown(f'<div class="mx-lead">{name}</div>', unsafe_allow_html=True)
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

        if st.button("Save Mapping", key="save_map"):
            st.success("CLO-PLO mapping saved.")


# ---------------------------------------------------------------------------
# 4. Marks Entry
# ---------------------------------------------------------------------------

def page_marks_entry(store):
    st.markdown(S.crumb("MarksEntry"), unsafe_allow_html=True)
    with S.card("Marks Entry"):
        course = course_picker(store, "me_course")
        comps = [c[0] for c in course["components"]]
        if not comps:
            st.info("Add evaluation components for this course first.")
            return
        comp = st.selectbox("Select Evaluation Component:", comps, key="me_comp")
        st.markdown(f'<div class="card-note">Selected Component: <b>{comp}</b></div>',
                    unsafe_allow_html=True)

        clos_in_comp = [c["name"] for c in course["clos"]
                        if course["mark_dist"].get(c["name"], {}).get(comp)]
        header = "User ID,Name," + ",".join(clos_in_comp)
        template = header + "\n" + "\n".join(
            f'{s["user_id"]},{s["name"]},' + ",".join([""] * len(clos_in_comp))
            for s in course["roster"])
        st.download_button("Download Template", data=template.encode(),
                           file_name=f"{course['id']}_{comp.replace(' ', '_')}_template.csv",
                           key="me_tpl")

        up = st.file_uploader("Upload Marks File:", type=["csv"], key="me_up")
        if up is not None and st.button("Upload Marks", key="me_btn"):
            try:
                n = _ingest_marks(course, comp, up, clos_in_comp)
                st.success(f"Marks uploaded for {comp} — {n} students updated.")
            except Exception as exc:
                st.error(f"Could not read that file: {exc}")

    with S.card("Previously Uploaded Marks",
                note="A blank cell means the student was marked ABSENT for that CLO."):
        rows = []
        for s in course["roster"]:
            sm = course["marks"].get(s["user_id"], {}).get(comp, {})
            vals = [f'{sm[c]:.1f}' if sm.get(c) is not None else "" for c in clos_in_comp]
            total = cp.student_component_total(course, s["user_id"], comp)
            rows.append([s["user_id"], s["name"]] + vals + [f"{total:.1f}" if sm else ""])
        st.markdown(S.table(["User ID", "Name"] + clos_in_comp + ["Total Marks"], rows,
                            classes=["strong", ""] + ["num"] * (len(clos_in_comp) + 1)),
                    unsafe_allow_html=True)


def _ingest_marks(course, comp, upload, clos_in_comp):
    text = upload.read().decode("utf-8-sig", errors="replace")
    lines = [l for l in text.splitlines() if l.strip()]
    hdr = [h.strip() for h in lines[0].split(",")]
    clo_cols = {h: i for i, h in enumerate(hdr) if h in clos_in_comp}
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
# 5. Reports
# ---------------------------------------------------------------------------

def page_report_marks(store):
    st.markdown(S.crumb("ReportMarks"), unsafe_allow_html=True)
    with S.card("Marks Report"):
        course = course_picker(store, "rm_course")
        if st.button("Generate Report", key="rm_gen"):
            st.session_state.rm_shown = True

    if not st.session_state.get("rm_shown"):
        return

    with S.card():
        comps = [x[0] for x in course["components"]]
        clos = [x["name"] for x in course["clos"]]
        headers = ["Sl No", "User ID", "Name"]
        for comp in comps:
            in_comp = [cl for cl in clos if course["mark_dist"].get(cl, {}).get(comp)]
            headers += [f"{comp} · {cl}" for cl in in_comp] + [f"{comp} Total"]

        tints = {comp: f"tint{(i % 3) + 1}" for i, comp in enumerate(comps)}
        rows, cell_cls, csv_rows = [], [], [headers]
        for n, s in enumerate(course["roster"], 1):
            row, cls = [str(n), s["user_id"], s["name"]], ["", "", ""]
            for comp in comps:
                in_comp = [cl for cl in clos if course["mark_dist"].get(cl, {}).get(comp)]
                sm = course["marks"].get(s["user_id"], {}).get(comp, {})
                for cl in in_comp:
                    v = sm.get(cl)
                    row.append(f"{v:.1f}" if v is not None else "-")
                    cls.append(tints[comp])
                row.append(f"{cp.student_component_total(course, s['user_id'], comp):.1f}"
                           if sm else "0")
                cls.append(tints[comp])
            rows.append(row)
            cell_cls.append(cls)
            csv_rows.append(row)

        st.markdown(S.report_table("", "", headers, rows, cell_classes=cell_cls),
                    unsafe_allow_html=True)
        st.download_button("Download Marks Report",
                           data="\n".join(",".join(r) for r in csv_rows).encode(),
                           file_name=f"{course['id']}_marks_report.csv", key="rm_dl")


def page_report_clo(store):
    st.markdown(S.crumb("ReportClo"), unsafe_allow_html=True)
    with S.card("CLO Report"):
        course = course_picker(store, "rc_course")
        if st.button("Generate Report", key="rc_gen"):
            st.session_state.rc_shown = True

    if not st.session_state.get("rc_shown"):
        return

    with S.card():
        clos = [c["name"] for c in course["clos"]]
        comp_att = cp.component_attainment(course)
        clo_att = cp.clo_attainment(course)
        crs = cp.course_attainment(course)

        headers = ["Evaluation Component"] + clos
        rows, row_cls = [], []
        for comp, _t in course["components"]:
            rows.append([comp] + [f"{comp_att[c].get(comp):.2f}"
                                  if comp_att[c].get(comp) is not None else "0.00" for c in clos])
            row_cls.append("")
        rows.append(["Attainment (Weighted Average)"] + [f"{clo_att[c]:.2f}" for c in clos])
        row_cls.append("total")
        rows.append(["Course Attainment"] + [f"{crs * 100:.0f}%"] + [""] * (len(clos) - 1))
        row_cls.append("grand")

        st.markdown(S.report_table("CLO Attainment", "red", headers, rows, row_classes=row_cls),
                    unsafe_allow_html=True)
        st.download_button("Download CLO Report",
                           data="\n".join(",".join(r) for r in [headers] + rows).encode(),
                           file_name=f"{course['id']}_clo_report.csv", key="rc_dl")


def page_report_plo(store):
    st.markdown(S.crumb("ReportPlo"), unsafe_allow_html=True)
    with S.card("PLO Report"):
        course = course_picker(store, "rp_course")
        if st.button("Generate Report", key="rp_gen"):
            st.session_state.rp_shown = True

    if not st.session_state.get("rp_shown"):
        return

    with S.card():
        clo_att = cp.clo_attainment(course)
        plo_att = cp.plo_attainment(course)
        headers = ["CLO", "CLO Attainment"] + PLO_IDS
        rows, row_cls = [], []
        for c in course["clos"]:
            n = c["name"]
            a = clo_att.get(n, 0.0)
            rows.append([n, f"{a:.2f}"] +
                        [f"{a:.2f}" if p in course["mapping"].get(n, []) else "0.00"
                         for p in PLO_IDS])
            row_cls.append("")
        rows.append(["Attainment (Average)", ""] + [f"{plo_att[p]:.2f}" for p in PLO_IDS])
        row_cls.append("total")
        st.markdown(S.report_table("CLO_PLO Attainment", "orange", headers, rows,
                                   row_classes=row_cls), unsafe_allow_html=True)
        st.download_button("Download Report",
                           data="\n".join(",".join(r) for r in [headers] + rows).encode(),
                           file_name=f"{course['id']}_plo_report.csv", key="rp_dl")

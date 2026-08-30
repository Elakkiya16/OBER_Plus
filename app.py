"""
OBER+ — Outcome-Based Education and Reporting Tool, extended with the 5R
continuous-improvement loop.

CO/PO Mapping, Assessment and Report reproduce OBER as deployed. The OBER+
section adds R1 Report, R2 Reflect, R3 Recommend, R4 Redesign and R5 Reassess
on top of the same data, without changing how attainment is computed.
"""
import streamlit as st

import style as S
import pages_ober as P
import pages_plus as PP
from store import OFFERING_ORDER, init_store

st.set_page_config(page_title="BPDC OBER+", page_icon="🎓", layout="wide",
                   initial_sidebar_state="collapsed")
st.markdown(S.CSS, unsafe_allow_html=True)

store = init_store()

# section -> [(screen label, render fn)]
SECTIONS = {
    "CO / PO Mapping": [("Handout Upload", P.page_handout),
                        ("CLO Entry", P.page_clo_entry),
                        ("Evaluation Components", P.page_components),
                        ("CLO-PLO Mapping", P.page_mapping)],
    "Assessment": [("Marks Entry", P.page_marks_entry)],
    "Report": [("Marks Report", P.page_report_marks),
               ("CLO Report", P.page_report_clo),
               ("PLO Report", P.page_report_plo)],
    "OBER+ 5R Loop": [("Report", PP.page_r1), ("Reflect", PP.page_r2),
                      ("Recommend", PP.page_r3), ("Redesign", PP.page_r4),
                      ("Reassess", PP.page_r5)],
}

st.session_state.setdefault("section", "CO / PO Mapping")
st.session_state.setdefault("screen", "CLO Entry")

# --- masthead ---------------------------------------------------------------
st.markdown(S.masthead_html(store["user"]), unsafe_allow_html=True)

# --- primary nav, drawn over the masthead's navy band ----------------------
with st.container():
    st.markdown('<div class="nav-marker"></div>', unsafe_allow_html=True)
    nav = st.columns([1.4, 1.0, 0.85, 1.35, 5.4])
    for i, sec in enumerate(S.PRIMARY_NAV):
        with nav[i]:
            if st.button(sec, key=f"sec_{sec}", width="stretch",
                         type="primary" if st.session_state.section == sec else "secondary"):
                st.session_state.section = sec
                st.session_state.screen = SECTIONS[sec][0][0]
                st.rerun()

# --- second row: section pills, or the numbered stage strip ----------------
section = st.session_state.section
screens = SECTIONS[section]
is_5r = section == "OBER+ 5R Loop"

with st.container():
    st.markdown('<div class="sub-marker"></div>', unsafe_allow_html=True)
    # Screen pills on the left, the semester picker on the right. The semester
    # is a choice, not a fixed line in the masthead: picking one repoints every
    # course at that offering's marks, so the OBER screens and reports read the
    # semester you are actually looking at.
    n = len(screens)
    widths = [1.55] * n + [max(0.4, 9.0 - 1.55 * n), 2.0]
    sub = st.columns(widths, vertical_alignment="center")
    for i, (name, _fn) in enumerate(screens):
        with sub[i]:
            label = f"{i + 1} · {name}" if is_5r else name
            if st.button(label, key=f"scr_{section}_{name}", width="stretch",
                         type="primary" if st.session_state.screen == name else "secondary"):
                st.session_state.screen = name
                st.rerun()

    sems = [s["name"] for s in store["semesters"]]
    current = store["active_semester"]
    with sub[-1]:
        picked = st.selectbox("Semester", sems, index=sems.index(current),
                              key="sem_pick", label_visibility="collapsed")
    if picked != current:
        store["active_semester"] = picked
        idx = OFFERING_ORDER.index(picked)
        for c in store["courses"].values():
            c["marks"] = c["marks_by_offering"][idx]
        st.rerun()

# --- page -------------------------------------------------------------------
current = st.session_state.screen
fn = dict(screens).get(current)
if fn is None:
    current = screens[0][0]
    st.session_state.screen = current
    fn = screens[0][1]
fn(store)

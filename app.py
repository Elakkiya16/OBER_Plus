"""
OBER+ — Outcome-Based Education and Reporting Tool, extended with the 5R
continuous-improvement loop.

The CO/PO Mapping, Assessment and Report sections reproduce OBER as deployed.
The OBER+ section adds R1 Report, R2 Reflect, R3 Recommend, R4 Redesign and
R5 Reassess on top of the same data, without changing how attainment is
computed.
"""
import streamlit as st

import style as S
import pages_ober as P
import pages_plus as PP
from store import init_store

st.set_page_config(page_title="BPDC OBER+", page_icon="🎓", layout="wide",
                   initial_sidebar_state="expanded")
st.markdown(S.CSS, unsafe_allow_html=True)

store = init_store()

NAV = [
    ("CO / PO MAPPING", [
        ("Handout Upload", P.page_handout),
        ("CLO Entry", P.page_clo_entry),
        ("Evaluation Components", P.page_components),
        ("CLO-PLO Mapping", P.page_mapping),
    ]),
    ("ASSESSMENT", [
        ("Marks Entry", P.page_marks_entry),
    ]),
    ("REPORT", [
        ("Marks Report", P.page_report_marks),
        ("CLO Report", P.page_report_clo),
        ("PLO Report", P.page_report_plo),
    ]),
    ("OBER+  ·  5R LOOP", [
        ("R1 · Report", PP.page_r1),
        ("R2 · Reflect", PP.page_r2),
        ("R3 · Recommend", PP.page_r3),
        ("R4 · Redesign", PP.page_r4),
        ("R5 · Reassess", PP.page_r5),
    ]),
]

PAGES = {name: fn for _group, items in NAV for name, fn in items}

# --- left navigation --------------------------------------------------------
with st.sidebar:
    st.image("assets/bits_logo.png", width=118)
    st.markdown('<div class="nav-brand">BPDC OBER<span class="nav-plus">+</span>'
                '<span class="nav-sub">Outcome-Based Education &amp; Reporting</span></div>',
                unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = "CLO Entry"

    for group, items in NAV:
        st.markdown(f'<div class="nav-group">{group}</div>', unsafe_allow_html=True)
        for name, _fn in items:
            active = st.session_state.page == name
            if st.button(name, key=f"nav_{name}", width="stretch",
                         type="primary" if active else "secondary"):
                st.session_state.page = name
                st.rerun()

# --- top bar + page ---------------------------------------------------------
st.markdown(S.topbar(store["user"], store["active_semester"]), unsafe_allow_html=True)
PAGES[st.session_state.page](store)

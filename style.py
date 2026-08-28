"""
OBER's own interface, reproduced.

Layout, colours and control styling follow the deployed BPDC OBER tool as
documented in CAA_OBER_21:10:2025.pdf: dark navy left nav with collapsible
groups, white top bar carrying the BITS Pilani mark / signed-in user /
red Logout, an orange breadcrumb under it, and white content cards holding
"Select Course Code" forms, black-header data tables and coloured report
tables. OBER+ screens use the same components so the added stages read as
part of the same tool rather than a separate dashboard.
"""

NAV_BG = "#212f3f"
NAV_BG_HOVER = "#2b3a4d"
NAV_ACTIVE = "#33445c"
NAV_TEXT = "#c9d3e0"
NAV_TEXT_ACTIVE = "#ffffff"
NAV_GROUP = "#e8edf4"

INK = "#1f2937"
INK_SOFT = "#4b5563"
INK_MUTED = "#8a94a6"
PAGE_BG = "#eef1f5"
CARD_BG = "#ffffff"
BORDER = "#dfe4ec"

BLUE = "#4a89dc"
BLUE_DARK = "#3a6fb0"
GREEN = "#26a65b"
RED = "#e0463c"
ORANGE = "#e8871e"
CYAN = "#1a9fb5"

BRAND_NAVY = "#0b2e6b"
BRAND_GOLD = "#e0a62e"

# Report table header fills, as OBER uses them
HDR_BLACK = "#111827"
HDR_RED = "#e8443a"
HDR_ORANGE = "#ef8c2a"

BAND_COLOR = {"H": "#1a9e4b", "M": "#e0a62e", "L": "#e8871e", "VL": "#d6392e"}
BAND_LABEL = {"H": "High", "M": "Medium", "L": "Low", "VL": "Very Low"}

CHART = ["#2E5AC4", "#C2860E", "#0E8DA3", "#8A4FD1", "#2F9E7A"]


CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {{
    font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif;
}}
.stApp {{ background: {PAGE_BG}; }}
#MainMenu, footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ background: transparent; height: 0; }}
.block-container {{ padding-top: 1.1rem; padding-bottom: 3rem; max-width: 100%; }}

/* ---------------- Left navigation ---------------- */
section[data-testid="stSidebar"] {{ background: {NAV_BG}; width: 268px !important; }}
section[data-testid="stSidebar"] > div {{ background: {NAV_BG}; }}
section[data-testid="stSidebar"] * {{ color: {NAV_TEXT}; }}
section[data-testid="stSidebar"] .block-container {{ padding: 0 0 2rem 0; }}

.nav-brand {{
    padding: 20px 18px 16px 18px;
    font-size: 1.02rem; font-weight: 700; color: #ffffff !important;
    letter-spacing: 0.02em; border-bottom: 1px solid rgba(255,255,255,0.07);
}}
.nav-brand .nav-plus {{ color: {BRAND_GOLD} !important; }}
.nav-brand .nav-sub {{
    display: block; font-size: 0.72rem; font-weight: 500; color: #8c9ab0 !important;
    margin-top: 3px; letter-spacing: 0.01em;
}}
.nav-group {{
    padding: 15px 18px 7px 18px; font-size: 0.73rem; font-weight: 700;
    letter-spacing: 0.09em; text-transform: uppercase; color: #7f8ea6 !important;
}}

/* Sidebar buttons rendered as OBER's nav rows */
section[data-testid="stSidebar"] div[data-testid="stButton"] {{ margin: 0 !important; }}
section[data-testid="stSidebar"] .stButton > button {{
    background: transparent !important; color: {NAV_TEXT} !important;
    border: none !important; border-left: 3px solid transparent !important;
    border-radius: 0 !important; text-align: left !important;
    justify-content: flex-start !important;
    padding: 8px 18px !important; min-height: 0 !important;
    font-size: 0.855rem !important; font-weight: 500 !important;
    transition: background .12s ease;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{
    background: {NAV_BG_HOVER} !important; color: #ffffff !important;
}}
section[data-testid="stSidebar"] .stButton > button:focus {{ box-shadow: none !important; }}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
    background: {NAV_ACTIVE} !important; color: #ffffff !important;
    border-left-color: {BRAND_GOLD} !important; font-weight: 600 !important;
}}
section[data-testid="stSidebar"] div[data-testid="stImage"] {{ padding: 16px 0 0 18px; }}

/* ---------------- Top bar ---------------- */
.topbar {{
    background: {CARD_BG}; border: 1px solid {BORDER}; border-radius: 6px;
    padding: 10px 18px; margin-bottom: 14px;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 1px 2px rgba(16,24,40,.04);
}}
.topbar-left {{ display: flex; align-items: center; gap: 12px; }}
.topbar-mark {{ font-size: 1.0rem; font-weight: 700; color: {BRAND_NAVY}; letter-spacing: -0.01em; }}
.topbar-mark span {{ display:block; font-size:0.66rem; font-weight:500; color:{INK_MUTED}; letter-spacing:0.02em; }}
.topbar-right {{ display: flex; align-items: center; gap: 14px; }}
.topbar-user {{ font-size: 0.86rem; font-weight: 700; color: {CYAN}; }}
.topbar-logout {{
    background: {RED}; color: #fff !important; font-size: 0.76rem; font-weight: 600;
    padding: 4px 13px; border-radius: 4px;
}}
.topbar-sem {{ font-size: 0.78rem; color: {INK_MUTED}; }}

/* ---------------- Breadcrumb ---------------- */
.crumb {{ margin: 2px 0 14px 2px; font-size: 1.06rem; font-weight: 700; color: {INK}; }}
.crumb .crumb-page {{ color: {ORANGE}; margin-left: 8px; }}

/* ---------------- Content card ---------------- */
/* st.container(border=True) styled as OBER's white content panel */
div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > div > div.oberplus-card-marker) {{
    background: {CARD_BG}; border: 1px solid {BORDER} !important; border-radius: 6px;
    padding: 16px 20px 18px 20px; margin-bottom: 14px;
    box-shadow: 0 1px 2px rgba(16,24,40,.04);
}}
.oberplus-card-marker {{ display: none; }}
.card {{
    background: {CARD_BG}; border: 1px solid {BORDER}; border-radius: 6px;
    padding: 18px 20px 20px 20px; margin-bottom: 16px;
    box-shadow: 0 1px 2px rgba(16,24,40,.04);
}}
.card-title {{ font-size: 0.95rem; font-weight: 700; color: {INK}; margin-bottom: 14px; }}
.card-note {{ font-size: 0.83rem; color: {INK_SOFT}; line-height: 1.55; margin-bottom: 12px; }}
.field-label {{ font-size: 0.79rem; color: {INK_SOFT}; font-weight: 600; margin-bottom: 3px; }}

/* ---------------- Streamlit control restyling ---------------- */
div[data-testid="stSelectbox"] label, div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label, div[data-testid="stFileUploader"] label {{
    font-size: 0.79rem !important; color: {INK_SOFT} !important; font-weight: 600 !important;
}}
div[data-baseweb="select"] > div {{
    border-radius: 4px !important; border-color: {BORDER} !important; min-height: 36px;
}}
.stTextInput input, .stNumberInput input {{
    border-radius: 4px !important; border-color: {BORDER} !important; font-size: 0.86rem;
}}
/* read-only rows in CLO Entry / Evaluation Components stay legible */
.stTextInput input:disabled, .stNumberInput input:disabled {{
    -webkit-text-fill-color: {INK} !important; color: {INK} !important;
    background: #f7f9fc !important; opacity: 1 !important;
}}
.stButton > button {{
    background: {BLUE}; color: #fff; border: none; border-radius: 4px;
    font-size: 0.82rem; font-weight: 600; padding: 6px 16px; min-height: 34px;
    transition: background .12s ease;
}}
.stButton > button:hover {{ background: {BLUE_DARK}; color: #fff; }}
.stButton > button:focus {{ box-shadow: none; color: #fff; }}
.stDownloadButton > button {{
    background: {GREEN}; color: #fff; border: none; border-radius: 4px;
    font-size: 0.82rem; font-weight: 600; padding: 6px 16px; min-height: 34px;
}}
.stDownloadButton > button:hover {{ background: #1e8c4c; color: #fff; }}
div[data-testid="stFileUploaderDropzone"] {{
    background: #f8fafc; border: 1px dashed {BORDER}; border-radius: 4px; padding: 10px 14px;
}}
div[data-testid="stAlert"] {{ border-radius: 5px; font-size: 0.85rem; }}

/* ---------------- Data tables ---------------- */
.tbl-wrap {{ overflow-x: auto; border: 1px solid {BORDER}; border-radius: 5px; margin-bottom: 14px; }}
table.ober {{ width: 100%; border-collapse: collapse; font-size: 0.845rem; background: {CARD_BG}; }}
table.ober th {{
    background: {HDR_BLACK}; color: #fff; text-align: left; font-weight: 600;
    padding: 9px 13px; white-space: nowrap; font-size: 0.80rem;
}}
table.ober td {{
    padding: 9px 13px; border-bottom: 1px solid #eef1f5; color: {INK_SOFT}; white-space: nowrap;
}}
table.ober tr:last-child td {{ border-bottom: none; }}
table.ober tr:hover td {{ background: #f9fbfd; }}
table.ober td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
table.ober td.strong {{ color: {INK}; font-weight: 600; }}

/* Report tables with OBER's coloured caption bars */
.rpt-cap {{
    color: #fff; font-weight: 700; font-size: 0.86rem; text-align: center;
    padding: 8px 12px; border-radius: 5px 5px 0 0;
}}
.rpt-cap.red {{ background: {HDR_RED}; }}
.rpt-cap.orange {{ background: {HDR_ORANGE}; }}
table.rpt {{ width: 100%; border-collapse: collapse; font-size: 0.845rem; background: {CARD_BG}; }}
table.rpt th {{
    background: #f1f4f8; color: {INK}; font-weight: 700; font-size: 0.80rem;
    padding: 8px 12px; border: 1px solid #e3e8f0; text-align: center; white-space: nowrap;
}}
table.rpt th.lead {{ text-align: left; }}
table.rpt td {{
    padding: 8px 12px; border: 1px solid #e9edf4; text-align: center;
    color: {INK_SOFT}; font-variant-numeric: tabular-nums; white-space: nowrap;
}}
table.rpt td.lead {{ text-align: left; color: {INK}; }}
table.rpt tr.total td {{ background: #fdf6e3; font-weight: 700; color: {INK}; }}
table.rpt tr.grand td {{ background: {HDR_BLACK}; color: #fff; font-weight: 700; }}
table.rpt td.tint1 {{ background: #fdf1f2; }}
table.rpt td.tint2 {{ background: #eefaf1; }}
table.rpt td.tint3 {{ background: #eef4fd; }}
table.rpt td.ok {{ background: #eefaf1; }}
table.rpt td.bad {{ background: #fdeeed; }}

/* Matrix entry grid (weightage / mark distribution / mapping) */
.mx-head, .mx-row {{ display: grid; gap: 6px; align-items: center; margin-bottom: 5px; }}
.mx-head div {{
    font-size: 0.74rem; font-weight: 700; color: {INK}; text-align: center;
    background: #f1f4f8; padding: 7px 4px; border-radius: 3px; line-height: 1.25;
}}
.mx-head div.lead, .mx-row div.lead {{ text-align: left; }}
.mx-total {{
    font-size: 0.86rem; font-weight: 700; text-align: center; padding: 7px 4px;
    border-radius: 3px; font-variant-numeric: tabular-nums;
}}
.mx-total.ok {{ background: #d9f2e2; color: #14663a; }}
.mx-total.bad {{ background: #fbdedc; color: #9c2b23; }}
.mx-lead {{ font-size: 0.85rem; font-weight: 600; color: {INK}; padding: 7px 2px; }}
div[data-testid="stNumberInput"] input {{ text-align: center; padding: 4px 6px !important; }}
div[data-testid="stNumberInput"] button {{ display: none; }}

/* ---------------- Chips / status ---------------- */
.chip {{
    display: inline-flex; align-items: center; gap: 5px; padding: 2px 10px;
    border-radius: 999px; font-size: 0.76rem; font-weight: 700;
}}
.chip-flag {{ background: #fdeeed; color: {RED}; }}
.chip-ok {{ background: #eef2f7; color: {INK_MUTED}; }}
.pill-formal {{ background: #e6f6ec; color: #14663a; }}
.pill-detected {{ background: #fdf1de; color: #8a5a12; }}

/* ---------------- Stat row ---------------- */
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 16px; }}
.stat {{
    background: {CARD_BG}; border: 1px solid {BORDER}; border-top: 3px solid {BRAND_GOLD};
    border-radius: 6px; padding: 14px 16px;
}}
.stat .k {{ font-size: 0.72rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: {INK_MUTED}; }}
.stat .v {{ font-size: 1.65rem; font-weight: 700; color: {INK}; line-height: 1.15; margin-top: 3px; }}
.stat .s {{ font-size: 0.79rem; color: {INK_MUTED}; margin-top: 2px; }}

/* ---------------- Record card (R3 decisions / R4 log) ---------------- */
.rec {{
    background: {CARD_BG}; border: 1px solid {BORDER}; border-left: 4px solid var(--a, {BLUE});
    border-radius: 6px; padding: 14px 18px; margin-bottom: 12px;
}}
.rec-head {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 7px; }}
.rec-id {{ font-weight: 700; color: {INK}; font-size: 0.9rem; }}
.rec-meta {{ font-size: 0.8rem; color: {INK_MUTED}; }}
.rec-body {{ font-size: 0.87rem; color: {INK_SOFT}; line-height: 1.55; margin-bottom: 10px; }}
.ba {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 9px; }}
.ba-box {{ background: #f7f9fc; border-radius: 4px; padding: 9px 12px; font-size: 0.83rem; color: {INK_SOFT}; }}
.ba-box b {{ display: block; font-size: 0.69rem; text-transform: uppercase; letter-spacing: 0.06em; color: {INK_MUTED}; margin-bottom: 3px; }}

.menu-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 10px; margin-bottom: 6px; }}
.menu-card {{
    background: {CARD_BG}; border: 1px solid {BORDER}; border-left: 3px solid var(--a, {BLUE});
    border-radius: 5px; padding: 11px 14px;
}}
.menu-card .t {{ font-weight: 600; color: {INK}; font-size: 0.87rem; margin-bottom: 3px; }}
.menu-card .c {{ font-size: 0.77rem; color: {INK_MUTED}; font-style: italic; line-height: 1.4; }}
</style>
"""


from contextlib import contextmanager
import streamlit as st


@contextmanager
def card(title: str = "", note: str = "", title_right: str = ""):
    """OBER's white content panel. Uses a real Streamlit container so anything
    rendered inside it (widgets included) sits within the panel."""
    with st.container(border=True):
        st.markdown('<div class="oberplus-card-marker"></div>', unsafe_allow_html=True)
        if title:
            right = (f'<span style="float:right;font-weight:500;font-size:0.78rem;'
                     f'color:{INK_MUTED};">{title_right}</span>') if title_right else ""
            st.markdown(f'<div class="card-title">{title}{right}</div>', unsafe_allow_html=True)
        if note:
            st.markdown(f'<div class="card-note">{note}</div>', unsafe_allow_html=True)
        yield


def topbar(user: str, semester: str) -> str:
    return (
        f'<div class="topbar"><div class="topbar-left">'
        f'<div class="topbar-mark">BITS Pilani<span>Dubai Campus</span></div>'
        f'</div><div class="topbar-right">'
        f'<span class="topbar-sem">{semester}</span>'
        f'<span class="topbar-user">{user}</span>'
        f'<span class="topbar-logout">Logout</span>'
        f'</div></div>'
    )


def crumb(page: str) -> str:
    return f'<div class="crumb">BPDC OBER+<span class="crumb-page">{page}</span></div>'


def band_chip(code: str) -> str:
    c = BAND_COLOR.get(code, INK_MUTED)
    return (f'<span class="chip" style="background:{c}1f;color:{c};">'
            f'{BAND_LABEL.get(code, code)}</span>')


def stat(k: str, v: str, s: str = "") -> str:
    sub = f'<div class="s">{s}</div>' if s else ""
    return f'<div class="stat"><div class="k">{k}</div><div class="v">{v}</div>{sub}</div>'


def table(headers, rows, classes=None) -> str:
    """Black-header data table. rows: list of lists of pre-formatted strings.
    classes: optional list of per-column css classes."""
    classes = classes or [""] * len(headers)
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = ""
    for r in rows:
        tds = "".join(f'<td class="{classes[i] if i < len(classes) else ""}">{c}</td>'
                      for i, c in enumerate(r))
        body += f"<tr>{tds}</tr>"
    return f'<div class="tbl-wrap"><table class="ober"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def report_table(caption, caption_color, headers, rows, row_classes=None, cell_classes=None) -> str:
    """OBER report table with a coloured caption bar.
    rows: list of lists. row_classes: per-row tr class. cell_classes: per-row list of td classes."""
    cap = f'<div class="rpt-cap {caption_color}">{caption}</div>' if caption else ""
    head = "".join(
        f'<th class="{"lead" if i == 0 else ""}">{h}</th>' for i, h in enumerate(headers))
    body = ""
    for ri, r in enumerate(rows):
        rc = (row_classes[ri] if row_classes and ri < len(row_classes) else "") or ""
        cc = cell_classes[ri] if cell_classes and ri < len(cell_classes) else None
        tds = ""
        for i, c in enumerate(r):
            base = "lead" if i == 0 else ""
            extra = (cc[i] if cc and i < len(cc) else "") or ""
            cls = " ".join(x for x in (base, extra) if x)
            tds += f'<td class="{cls}">{c}</td>'
        body += f'<tr class="{rc}">{tds}</tr>'
    return (f'{cap}<div class="tbl-wrap" style="border-radius:0 0 5px 5px;">'
            f'<table class="rpt"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')


def menu_grid(items, accent) -> str:
    cards = "".join(
        f'<div class="menu-card" style="--a:{accent};"><div class="t">{n}</div>'
        f'<div class="c">{c}</div></div>' for n, c in items)
    return f'<div class="menu-grid">{cards}</div>'


def record_card(rid, badge, badge_class, meta, body, before=None, after=None, footer="", accent=BLUE) -> str:
    ba = ""
    if before is not None:
        ba = (f'<div class="ba"><div class="ba-box"><b>Before</b>{before}</div>'
              f'<div class="ba-box"><b>After</b>{after}</div></div>')
    foot = f'<div class="rec-meta">{footer}</div>' if footer else ""
    return (
        f'<div class="rec" style="--a:{accent};"><div class="rec-head">'
        f'<span class="rec-id">{rid}</span>'
        f'<span class="chip {badge_class}">{badge}</span>'
        f'<span class="rec-meta">{meta}</span></div>'
        f'<div class="rec-body">{body}</div>{ba}{foot}</div>'
    )

"""
OBER+ interface — the approved design.

Navy masthead carrying the BITS Pilani mark and primary nav; a second row that
is either section pills (OBER's screens) or the numbered 1-2-3-4-5 stage strip
(the 5R loop), so the loop reads as a sequence rather than five more menu items.
White content panels below.

Colour: navy is chrome ONLY — the masthead and the primary nav bar sit on it and
nothing else does. Everything below that bar is carried by the campus tagline
palette sampled from tagline.jpg: innovate amber #FAB001, achieve sky #87C6E9,
lead red #E40613, with darkened in-hue variants where type needs contrast on
white. The masthead logo is the supplied "with white text" lockup, used
untouched — knocking white out of it erases the wordmark.

Band colours are a separate reserved 4-step severity ramp, validated all-PASS by
the dataviz validator (lightness band, chroma floor, CVD adjacent separation,
normal-vision floor, contrast). They are never reused as a chart series colour,
and every band always ships with its text label — which is what discharges the
amber step's contrast warning.

Type: Sora for headings, Manrope for everything else.
"""
from contextlib import contextmanager
from functools import lru_cache
import base64
import pathlib
import streamlit as st


@lru_cache(maxsize=1)
def _logo_b64() -> str:
    p = pathlib.Path(__file__).with_name("assets") / "bits_logo.png"
    try:
        return base64.b64encode(p.read_bytes()).decode()
    except OSError:
        return ""

# --- Brand ------------------------------------------------------------------
# Navy is chrome ONLY: the masthead and the primary nav bar sit on it and
# nothing else does. Everything below that bar is carried by the campus tagline
# palette, sampled from tagline.jpg — innovate amber, achieve sky, lead red.
NAVY = "#011E4B"
NAVY2 = "#0B2E6B"

AMBER = "#FAB001"     # innovate
SKY = "#87C6E9"       # achieve
RED_T = "#E40613"     # lead

# Darkened in-hue variants, for type and marks that need contrast on white.
AMBER_D = "#A66E00"
SKY_D = "#1B6FA8"
RED_D = "#C1050F"

# Names the rest of the app already uses, pointed at the tagline palette.
GOLD = AMBER
CYAN = SKY
BRAND_RED = RED_T

# --- Ink & surface ----------------------------------------------------------
INK = "#0E1A2B"
SOFT = "#55647C"
MUTED = "#8493A9"
FAINT = "#C4CDDA"
PAGE = "#FFFFFF"        # white, not grey
CARD = "#FFFFFF"
BORDER = "#D2E4F2"      # sky-tinted, not grey
LINE = "#E8F3FB"
RED = RED_D          # target rules and error text

# --- Bands: reserved severity ramp, validated all-PASS ----------------------
BAND_COLOR = {"H": "#178A52", "M": "#CAA11A", "L": "#E05A24", "VL": "#A02436",
              "OK": "#7E8CA1"}
BAND_LABEL = {"H": "High", "M": "Medium", "L": "Low", "VL": "Very Low",
              "OK": "On target"}
BAND_ORDER = ["VL", "L", "M", "H"]
BAND_CUTS = {"VL": (0, 30), "L": (30, 60), "M": (60, 90), "H": (90, 100)}

# --- Offerings are an ordered sequence -> sequential ramp of ONE hue ---------
# Three offerings, three campus colours: innovate -> achieve -> lead.
SEQ = ["#FAB001", "#87C6E9", "#E40613"]

# --- Chart series (categorical), validated all-PASS -------------------------
CHART = ["#2E5AC4", "#C2860E", "#0E8DA3", "#8A4FD1", "#2F9E7A"]

PRIMARY_NAV = ["CO / PO Mapping", "Assessment", "Report", "OBER+ 5R Loop"]
STAGES = ["Report", "Reflect", "Recommend", "Redesign", "Reassess"]


CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp, input, select, textarea, button {{
    font-family: 'Manrope', system-ui, -apple-system, sans-serif;
    -webkit-font-smoothing: antialiased;
}}
.stApp {{ background: {PAGE}; }}
#MainMenu, footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ background: transparent; height: 0; }}
section[data-testid="stSidebar"] {{ display: none; }}
/* Content is inset 44px; the chrome bleeds back out with negative margins. */
.block-container {{ padding: 0 44px 4rem 44px !important; max-width: 100% !important; }}

/* ======================= Masthead =======================
   The rule across the top is the innovate/achieve/lead device. Navy lives here
   and in the nav bar below it, and nowhere else. All masthead type is white,
   and the supplied logo already carries the white BITS Pilani Dubai Campus
   wordmark, so it is used untouched — knocking white out of it erases the
   wordmark. */
.mast {{ background: {NAVY}; padding: 0 44px; margin: 0 -44px; }}
.brandrule {{ display: flex; height: 6px; margin: 0 -44px; }}
.brandrule i {{ flex: 1; }}
.mast-logo {{ height: 104px; width: auto; display: block; }}
.mast-top {{ height: 140px; display: flex; align-items: center; justify-content: space-between; }}
.mast-brand {{ display: flex; align-items: center; gap: 20px; }}
.mast-rule {{ width: 1px; height: 66px; background: rgba(255,255,255,0.22); }}
.mast-name {{ font-family: 'Sora', system-ui, sans-serif; font-size: 23px; font-weight: 800;
              color: #FFFFFF; letter-spacing: -0.02em; line-height: 1.1; }}
.mast-name .plus {{ color: {GOLD}; }}
.mast-sub {{ font-size: 11.5px; font-weight: 700; color: #FFFFFF; margin-top: 5px;
             letter-spacing: 0.09em; }}
.mast-right {{ display: flex; align-items: center; gap: 22px; }}
.mast-sem {{ font-size: 14px; font-weight: 500; color: #FFFFFF; }}
.mast-user {{ font-size: 14.5px; font-weight: 700; color: #FFFFFF; }}
.mast-logout {{ border: 1.5px solid rgba(255,255,255,0.28); color: #FFFFFF; font-size: 13px;
                font-weight: 700; padding: 8px 18px; border-radius: 999px; }}
.mast-nav {{ display: flex; gap: 34px; align-items: center; }}
.mast-nav .t {{ font-size: 15px; font-weight: 600; color: #9DB0CE; padding: 15px 0; }}
.mast-nav .t.on {{ font-size: 15px; font-weight: 800; color: #FFFFFF;
                   border-bottom: 3px solid {GOLD}; }}

/* ======================= Nav rows =======================
   A marker div inside a Streamlit container is the only reliable way to scope
   styling to the widgets in that container — an HTML wrapper written with
   st.markdown does not contain the widgets that follow it. */
div[data-testid="stLayoutWrapper"]:has(> div > div > div > div > div > div.nav-marker) {{
    background: {SKY}; margin: 0 -44px; padding: 2px 44px 0 44px;
    width: calc(100% + 88px) !important; max-width: none !important;
    flex: 0 0 auto !important;
}}
div[data-testid="stVerticalBlock"]:has(> div > div > div > div > div.nav-marker) {{
    gap: 0 !important;
}}
div[data-testid="stVerticalBlock"]:has(> div > div > div > div > div.nav-marker) div[data-testid="stButton"] {{
    margin: 0 !important;
}}
div[data-testid="stVerticalBlock"]:has(> div > div > div > div > div.nav-marker) .stButton > button {{
    background: transparent !important; border: none !important; box-shadow: none !important;
    color: #17457F !important; font-size: 16px !important; font-weight: 700 !important;
    padding: 15px 0 13px 0 !important; min-height: 0 !important; letter-spacing: 0.005em;
    border-bottom: 4px solid transparent !important; border-radius: 0 !important;
}}
div[data-testid="stVerticalBlock"]:has(> div > div > div > div > div.nav-marker) .stButton > button:hover {{
    color: {NAVY} !important;
}}
div[data-testid="stVerticalBlock"]:has(> div > div > div > div > div.nav-marker) .stButton > button[kind="primary"] {{
    color: {NAVY} !important; font-weight: 800 !important;
    border-bottom-color: {RED_T} !important;
}}

div[data-testid="stLayoutWrapper"]:has(> div > div > div > div > div > div.sub-marker) {{
    background: {CARD}; margin: 0 -44px 26px -44px; padding: 13px 44px;
    width: calc(100% + 88px) !important; max-width: none !important;
    flex: 0 0 auto !important; border-bottom: 1px solid {BORDER};
}}
div[data-testid="stVerticalBlock"]:has(> div > div > div > div > div.sub-marker) {{
    gap: 0 !important;
}}
div[data-testid="stVerticalBlock"]:has(> div > div > div > div > div.sub-marker) div[data-testid="stButton"] {{
    margin: 0 !important;
}}
div[data-testid="stVerticalBlock"]:has(> div > div > div > div > div.sub-marker) .stButton > button {{
    background: #EAF4FB !important; border: none !important; color: {NAVY2} !important;
    font-size: 15px !important; font-weight: 700 !important; border-radius: 999px !important;
    padding: 10px 16px !important; min-height: 0 !important; box-shadow: none !important;
}}
div[data-testid="stVerticalBlock"]:has(> div > div > div > div > div.sub-marker) .stButton > button:hover {{
    background: #D8EBF8 !important; color: {INK} !important;
}}
div[data-testid="stVerticalBlock"]:has(> div > div > div > div > div.sub-marker) .stButton > button[kind="primary"] {{
    background: {AMBER} !important; color: {INK} !important; font-weight: 800 !important;
}}
.nav-marker, .sub-marker {{ display: none; }}

/* ======================= Body ======================= */
.page-head {{ display: flex; align-items: center; gap: 16px; }}
.page-head .tick {{ width: 7px; height: 38px; border-radius: 4px; flex: none; }}
.page-title {{ font-family: 'Sora', system-ui, sans-serif; font-size: 36px; font-weight: 800;
               letter-spacing: -0.035em; color: {INK}; line-height: 1.1; }}
.page-sub {{ font-size: 16px; color: {SOFT}; margin: 9px 0 22px 0; }}

/* ======================= Cards ======================= */
div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > div > div.ob-card) {{
    box-shadow: 0 1px 2px rgba(14,26,43,0.04);
    background: {CARD}; border: 1px solid {BORDER} !important; border-radius: 14px;
    padding: 20px 24px 22px 24px; margin-bottom: 16px;
}}
.ob-card {{ display: none; }}
.card-title {{ font-size: 17px; font-weight: 700; color: {INK}; letter-spacing: -0.015em;
               margin-bottom: 16px; }}
.card-note {{ font-size: 14.5px; color: {SOFT}; line-height: 1.6; margin-bottom: 14px; }}
.field-label {{ font-size: 12px; font-weight: 800; letter-spacing: 0.09em; color: {MUTED};
                margin-bottom: 7px; text-transform: uppercase; }}

/* ======================= Controls ======================= */
div[data-testid="stSelectbox"] label, div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label, div[data-testid="stFileUploader"] label {{
    font-size: 12px !important; color: {MUTED} !important; font-weight: 800 !important;
    letter-spacing: 0.09em; text-transform: uppercase;
}}
div[data-baseweb="select"] > div {{
    border-radius: 10px !important; border-color: #B5D2E6 !important; min-height: 44px;
    font-weight: 600; font-size: 15px;
}}
/* The border lives on the wrapper Streamlit renders inside the field, not on
   the <input> itself — on a white page it defaults to white, so the field
   disappears unless that wrapper is styled. */
div[data-testid="stNumberInput"] > div > div,
div[data-testid="stTextInput"] > div > div,
div[data-baseweb="input"], div[data-baseweb="base-input"] {{
    border-radius: 10px !important; border: 1.5px solid #B5D2E6 !important;
    background: {CARD} !important;
}}
.stTextInput input, .stNumberInput input {{
    border-radius: 10px !important; border-color: #B5D2E6 !important; font-size: 15px;
    font-weight: 500; padding: 10px 14px !important; background: transparent !important;
}}
.stTextInput input:disabled, .stNumberInput input:disabled {{
    -webkit-text-fill-color: {SOFT} !important; color: {SOFT} !important;
    background: #F4FAFE !important; opacity: 1 !important;
}}
.stButton > button {{
    background: {CARD}; color: {INK}; border: 1.5px solid #CBDDEB; border-radius: 10px;
    font-size: 14.5px; font-weight: 700; padding: 11px 22px; min-height: 44px;
}}
.stButton > button:hover {{ background: #F4FAFE; border-color: {MUTED}; color: {INK}; }}
.stButton > button:focus {{ box-shadow: none; color: {INK}; }}
/* One amber action per screen — the thing the screen is for. Row actions stay
   quiet so a Delete never looks like the primary move. */
.stButton > button[kind="primary"] {{
    background: {AMBER}; color: {INK}; border: none;
}}
.stButton > button[kind="primary"]:hover {{ background: #E8A200; color: {INK}; }}
.stDownloadButton > button {{
    background: {CARD}; color: {INK} !important; border: 1.5px solid {BORDER};
    border-radius: 10px; font-size: 14.5px; font-weight: 700; padding: 10px 20px; min-height: 44px;
}}
.stDownloadButton > button:hover {{ background: #F4FAFE; border-color: {MUTED}; }}
div[data-testid="stFileUploaderDropzone"] {{
    background: #F7FBFE; border: 1.5px dashed #B9D6EA; border-radius: 12px; padding: 16px 20px;
}}
div[data-testid="stAlert"] {{ border-radius: 11px; font-size: 14.5px; }}
div[data-testid="stExpander"] {{ border: 1px solid {BORDER}; border-radius: 12px; background: {CARD}; }}
div[data-testid="stExpander"] summary {{ font-size: 14.5px; font-weight: 700; color: {SOFT}; }}
div[data-testid="stExpander"] p, div[data-testid="stExpander"] li {{
    font-size: 14.5px; color: {SOFT}; line-height: 1.65;
}}

/* ======================= Tables ======================= */
.tbl {{ overflow-x: auto; border: 1px solid {BORDER}; border-radius: 14px; background: {CARD}; }}
table.t {{ width: 100%; border-collapse: collapse; font-size: 14.5px; }}
table.t th {{
    background: {SKY}; color: {INK}; font-size: 12px; font-weight: 800;
    letter-spacing: 0.08em; text-transform: uppercase; padding: 14px 16px;
    text-align: center; white-space: nowrap;
}}
table.t th.lead {{ text-align: left; }}
table.t td {{
    padding: 14px 16px; border-bottom: 1px solid {LINE}; text-align: center;
    color: {SOFT}; font-weight: 500; font-variant-numeric: tabular-nums; white-space: nowrap;
}}
table.t td.lead {{ text-align: left; color: {INK}; font-weight: 600; white-space: normal; }}
table.t tr:last-child td {{ border-bottom: none; }}
table.t tr.total td {{ background: #FBF9F2; font-weight: 800; color: {INK}; }}
table.t tr.grand td {{ background: {SKY_D}; color: #FFFFFF; font-weight: 800; }}
table.t tr.grand td.gold {{ color: {GOLD}; }}
table.t td.kv {{ text-align: left; white-space: normal; }}
table.t td.ok {{ color: {BAND_COLOR["H"]}; font-weight: 600; }}
table.t td.bad {{ color: {RED}; font-weight: 600; }}
table.t td.t1 {{ background: #FDF5F4; }} table.t td.t2 {{ background: #F2FAF5; }}
table.t td.t3 {{ background: #F3F6FD; }} table.t td.t4 {{ background: #FCF8EE; }}
table.t td.t5 {{ background: #F5F3FA; }}
.cap {{ color: #FFFFFF; font-weight: 700; font-size: 15px; text-align: center; padding: 12px;
        border-radius: 14px 14px 0 0; }}
.cap.red {{ background: {RED_T}; }} .cap.orange {{ background: {AMBER_D}; }}

/* ======================= Matrix entry ======================= */
.mx-h {{ font-size: 11.5px; font-weight: 800; letter-spacing: 0.07em; color: {MUTED};
         text-align: center; background: #F4FAFE; border-radius: 7px; padding: 9px 4px;
         line-height: 1.35; text-transform: uppercase; }}
.mx-h.lead {{ text-align: left; padding-left: 12px; }}
.mx-l {{ font-size: 15px; font-weight: 700; color: {INK}; padding: 10px 0 10px 4px; }}
.mx-t {{ font-size: 15px; font-weight: 800; text-align: center; padding: 10px 4px;
         border-radius: 7px; font-variant-numeric: tabular-nums; }}
.mx-t.ok {{ background: #E7F6EE; color: #10693D; }}
.mx-t.bad {{ background: #FDECEA; color: #99251C; }}
.mx-t.navy {{ background: {SKY_D}; color: #FFFFFF; }}
div[data-testid="stNumberInput"] input {{ text-align: center; padding: 8px 6px !important; }}
div[data-testid="stNumberInput"] button {{ display: none; }}

/* ======================= Chips, stats, meters ======================= */
.chip {{ display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px;
         border-radius: 999px; font-size: 13px; font-weight: 700; white-space: nowrap; }}
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
          gap: 16px; margin-bottom: 4px; }}
.stat {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 14px; padding: 18px 20px; }}
.stat.accent {{ border-left: 5px solid var(--a, {AMBER}); }}
.stat .k {{ font-size: 12px; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase;
            color: {MUTED}; }}
.stat .v {{ font-family: 'Sora', system-ui, sans-serif; font-size: 34px; font-weight: 800;
            color: {INK}; margin-top: 9px; line-height: 1.1; letter-spacing: -0.035em; }}
.stat .v.sm {{ font-size: 20px; letter-spacing: -0.02em; }}
.stat .v .faint {{ color: {FAINT}; }}
.stat .s {{ font-size: 13.5px; color: {MUTED}; margin-top: 8px; font-weight: 600; }}
.hero {{ font-family: 'Sora', system-ui, sans-serif; font-size: 64px; font-weight: 800;
         line-height: 1; letter-spacing: -0.045em; }}

.meter {{ display: flex; align-items: center; gap: 11px; }}
.meter-tr {{ position: relative; flex: 1; height: 10px; border-radius: 999px; overflow: hidden;
             min-width: 90px; }}
.meter-fl {{ height: 100%; }}
.meter-v {{ font-size: 14px; font-weight: 800; color: {INK}; min-width: 44px; text-align: right;
            font-variant-numeric: tabular-nums; }}

.bandscale {{ display: flex; height: 32px; border-radius: 8px; overflow: hidden; }}
.bandscale div {{ display: flex; align-items: center; justify-content: center; color: #FFFFFF;
                  font-size: 12.5px; font-weight: 700; }}
.bandticks {{ display: flex; margin-top: 6px; font-size: 12px; font-weight: 600; color: {MUTED};
              font-variant-numeric: tabular-nums; }}

/* ======================= CLO cards ======================= */
.clocard {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 14px;
            padding: 18px 24px; margin-bottom: 12px;
            display: grid; grid-template-columns: 190px 1fr 178px 150px;
            align-items: center; gap: 26px; }}
.clocard.alert {{ background: #FFFBF9; border: 1.5px solid {BAND_COLOR["L"]}; }}
.clocard .cid {{ font-size: 17px; font-weight: 800; color: {INK}; }}
.clocard .cdesc {{ font-size: 13.5px; color: {MUTED}; margin-top: 4px; line-height: 1.4; }}
.offs {{ display: flex; gap: 10px; }}
.off {{ flex-grow: 1; border-radius: 9px; padding: 10px 0; text-align: center; }}
.off .ov {{ font-size: 17px; font-weight: 700; }}
.off .ol {{ font-size: 11.5px; color: {MUTED}; margin-top: 3px; }}
.off.good {{ background: #F1F8F4; }} .off.good .ov {{ color: {BAND_COLOR["H"]}; }}
.off.miss {{ background: #FDF1F0; }} .off.miss .ov {{ color: {RED}; }}
.off.bad {{ background: #FBE7E5; }} .off.bad .ov {{ color: {BAND_COLOR["VL"]}; }}

/* ======================= Record cards ======================= */
.rec {{ background: {CARD}; border: 1px solid {BORDER}; border-left: 4px solid var(--a, {SKY_D});
        border-radius: 14px; padding: 18px 22px; margin-bottom: 12px; }}
.rec-h {{ display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 10px; }}
.rec-id {{ font-size: 15.5px; font-weight: 800; color: {INK}; }}
.rec-m {{ font-size: 13.5px; color: {MUTED}; }}
.rec-b {{ font-size: 14.5px; color: {SOFT}; line-height: 1.6; margin-bottom: 14px; }}
.ba {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 12px; }}
.ba-x {{ background: #F4FAFE; border-radius: 10px; padding: 13px 15px; font-size: 14px;
         color: {SOFT}; line-height: 1.5; }}
.ba-x b {{ display: block; font-size: 11.5px; font-weight: 800; letter-spacing: 0.08em;
           color: {MUTED}; margin-bottom: 5px; text-transform: uppercase; }}

.menu {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 12px; }}
.menu-c {{ background: {CARD}; border: 1px solid {BORDER}; border-left: 3px solid var(--a, {SKY_D});
           border-radius: 11px; padding: 14px 16px; }}
.menu-c .t {{ font-size: 14.5px; font-weight: 700; color: {INK}; line-height: 1.35; }}
.menu-c .c {{ font-size: 12.5px; color: {MUTED}; margin-top: 6px; line-height: 1.45; }}

.legend {{ display: flex; gap: 18px; align-items: center; flex-wrap: wrap; }}
.legend span.i {{ display: flex; align-items: center; gap: 7px; font-size: 13px;
                  font-weight: 600; color: {SOFT}; }}
.legend span.sw {{ width: 12px; height: 12px; border-radius: 3px; }}
</style>
"""


# ---------------------------------------------------------------------------
# Chrome
# ---------------------------------------------------------------------------

def masthead_html(user: str) -> str:
    b64 = _logo_b64()
    logo = (f'<img class="mast-logo" src="data:image/png;base64,{b64}" alt="BITS Pilani Dubai">'
            f'<div class="mast-rule"></div>') if b64 else ""
    rule = (f'<div class="brandrule"><i style="background:{AMBER};"></i>'
            f'<i style="background:{SKY};"></i><i style="background:{RED_T};"></i></div>')
    return (f'<div class="mast">{rule}<div class="mast-top"><div class="mast-brand">{logo}'
            f'<div><div class="mast-name">OBER<span class="plus">+</span></div>'
            f'<div class="mast-sub">OUTCOME-BASED EDUCATION &amp; REPORTING</div></div></div>'
            f'<div class="mast-right"><span class="mast-user">{user}</span>'
            f'<span class="mast-logout">Logout</span></div></div></div>')


SECTION_COLOR = {
    "CO / PO Mapping": AMBER,
    "Assessment": SKY,
    "Report": RED_T,
    # the loop touches all three stages of the tagline, so its tick carries all three
    "OBER+ 5R Loop": f"linear-gradient(180deg,{AMBER} 0 33%,{SKY} 33% 66%,{RED_T} 66% 100%)",
}


def page_head(title: str, sub: str = "") -> str:
    """The rule beside the title carries the section's campus colour, so each
    part of the tool is recognisable before you read the heading."""
    col = SECTION_COLOR.get(st.session_state.get("section", ""), AMBER)
    s = f'<div class="page-sub">{sub}</div>' if sub else ""
    return (f'<div class="page-head"><span class="tick" style="background:{col};"></span>'
            f'<div class="page-title">{title}</div></div>{s}')


@contextmanager
def card(title: str = "", note: str = "", right: str = ""):
    with st.container(border=True):
        st.markdown('<div class="ob-card"></div>', unsafe_allow_html=True)
        if title:
            r = (f'<span style="float:right;font-size:13px;font-weight:600;color:{MUTED};">'
                 f'{right}</span>') if right else ""
            st.markdown(f'<div class="card-title">{title}{r}</div>', unsafe_allow_html=True)
        if note:
            st.markdown(f'<div class="card-note">{note}</div>', unsafe_allow_html=True)
        yield


# ---------------------------------------------------------------------------
# Bands
# ---------------------------------------------------------------------------

def band_chip(code: str, suffix: str = "") -> str:
    c = BAND_COLOR.get(code, MUTED)
    bg = "#EEF1F5" if code == "OK" else f"{c}1f"
    return (f'<span class="chip" style="background:{bg};color:{c};">'
            f'{BAND_LABEL.get(code, code)}{suffix}</span>')


def band_meter(ratio, code: str) -> str:
    if ratio is None:
        return '<span class="chip" style="background:#EEF1F5;color:#7E8CA1;">On target</span>'
    c = BAND_COLOR[code]
    pos = max(0.0, min(100.0, float(ratio)))
    cuts = "".join(f'<div style="position:absolute;left:{x}%;top:0;width:1px;height:100%;'
                   f'background:rgba(255,255,255,.85);"></div>' for x in (30, 60, 90))
    return (f'<div class="meter"><div class="meter-tr" style="background:{c}24;">'
            f'<div class="meter-fl" style="width:{pos}%;background:{c};"></div>{cuts}</div>'
            f'<span class="meter-v">{pos:.0f}%</span></div>')


def band_scale(target: float) -> str:
    zones = "".join(f'<div style="width:{BAND_CUTS[b][1] - BAND_CUTS[b][0]}%;'
                    f'background:{BAND_COLOR[b]};">{BAND_LABEL[b]}</div>' for b in BAND_ORDER)
    ticks = ('<div style="width:30%;">0</div><div style="width:30%;">30</div>'
             '<div style="width:30%;">60</div>'
             '<div style="width:10%;display:flex;justify-content:space-between;">'
             '<span>90</span><span>100</span></div>')
    return f'<div class="bandscale">{zones}</div><div class="bandticks">{ticks}</div>'


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

def stat(k: str, v: str, s: str = "", small: bool = False, accent: str = "") -> str:
    cls = "stat accent" if accent else "stat"
    style = f' style="--a:{accent};"' if accent else ""
    sub = f'<div class="s">{s}</div>' if s else ""
    vc = "v sm" if small else "v"
    return f'<div class="{cls}"{style}><div class="k">{k}</div><div class="{vc}">{v}</div>{sub}</div>'


BRAND_CYCLE = [AMBER, SKY, RED_T, SKY_D]


def stats_row(items) -> str:
    """Each tile takes the next campus colour, so a KPI row carries the identity
    instead of four navy boxes. A tile that already has a band accent keeps it —
    meaning always outranks decoration."""
    out = []
    for i, it in enumerate(items):
        out.append(it.replace('<div class="stat">',
                              f'<div class="stat accent" style="--a:{BRAND_CYCLE[i % 4]};">', 1)
                   if '<div class="stat">' in it else it)
    return f'<div class="stats">{"".join(out)}</div>'


def legend(items) -> str:
    out = '<div class="legend">'
    for lab, col in items:
        out += f'<span class="i"><span class="sw" style="background:{col};"></span>{lab}</span>'
    return out + "</div>"


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------

def table(headers, rows, row_classes=None, cell_classes=None,
          caption="", caption_color="") -> str:
    cap = f'<div class="cap {caption_color}">{caption}</div>' if caption else ""
    radius = "0 0 14px 14px" if caption else "14px"
    if any(str(h).strip() for h in headers):
        cells = "".join(f'<th class="{"lead" if i == 0 else ""}">{h}</th>'
                        for i, h in enumerate(headers))
        head = f'<thead><tr>{cells}</tr></thead>'
    else:
        head = ""  # a two-column key/value table needs no header strip
    body = ""
    for ri, r in enumerate(rows):
        rc = (row_classes[ri] if row_classes and ri < len(row_classes) else "") or ""
        cc = cell_classes[ri] if cell_classes and ri < len(cell_classes) else None
        tds = ""
        for i, c in enumerate(r):
            cls = " ".join(x for x in (("lead" if i == 0 else ""),
                                       (cc[i] if cc and i < len(cc) else "") or "") if x)
            tds += f'<td class="{cls}">{c}</td>'
        body += f'<tr class="{rc}">{tds}</tr>'
    return (f'{cap}<div class="tbl" style="border-radius:{radius};">'
            f'<table class="t">{head}<tbody>{body}</tbody></table></div>')


# ---------------------------------------------------------------------------
# Cards
# ---------------------------------------------------------------------------

def clo_card(cid, desc, offerings, target, shortfall_html, band_html, alert=False) -> str:
    offs = ""
    for val, lab in offerings:
        k = "good" if val >= target else ("bad" if val < target * 0.5 else "miss")
        offs += f'<div class="off {k}"><div class="ov">{val:.1f}%</div><div class="ol">{lab}</div></div>'
    return (f'<div class="clocard{" alert" if alert else ""}">'
            f'<div><div class="cid">{cid}</div><div class="cdesc">{desc}</div></div>'
            f'<div class="offs">{offs}</div>'
            f'<div>{shortfall_html}</div>'
            f'<div style="text-align:right;">{band_html}</div></div>')


def menu_grid(items, accent) -> str:
    cards = "".join(f'<div class="menu-c" style="--a:{accent};"><div class="t">{n}</div>'
                    f'<div class="c">{c}</div></div>' for n, c in items)
    return f'<div class="menu">{cards}</div>'


def record_card(rid, badge, badge_bg, badge_fg, meta, body,
                before=None, after=None, footer="", accent=SKY_D) -> str:
    ba = ""
    if before is not None:
        ba = (f'<div class="ba"><div class="ba-x"><b>Before</b>{before}</div>'
              f'<div class="ba-x"><b>After</b>{after}</div></div>')
    foot = f'<div class="rec-m">{footer}</div>' if footer else ""
    return (f'<div class="rec" style="--a:{accent};"><div class="rec-h">'
            f'<span class="rec-id">{rid}</span>'
            f'<span class="chip" style="background:{badge_bg};color:{badge_fg};">{badge}</span>'
            f'<span class="rec-m">{meta}</span></div>'
            f'<div class="rec-b">{body}</div>{ba}{foot}</div>')

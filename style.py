"""
Shared palette + Plotly template.

Brand colours pulled directly from BITS Pilani Dubai's own materials — sampled
from the official seal (assets/bits_logo.png, from her AIRE+ mid-year deck)
and cross-checked against the srgbClr values actually used across that deck's
slides: navy ~#002060/#011893, gold/amber ~#FFC000/#F8A819, sky blue/cyan
~#0FC0DF/#33BCE1, red ~#FF0000/#ED1C24.

The categorical series below are brand-derived but were then run through the
dataviz skill's validator (scripts/validate_palette.js) and adjusted until
every check passed (lightness band, chroma floor, CVD adjacent-pair separation,
normal-vision floor, contrast) — see conversation for the exact command run.
Status colours (H/M/L/VL) stay on the skill's own reserved status palette,
deliberately distinct from the categorical set, so a band colour never doubles
as a series colour on the same screen.
"""
import plotly.graph_objects as go
import plotly.io as pio

# --- Brand ---------------------------------------------------------------
BRAND_NAVY = "#0B2E6B"     # primary ink / header text — from the wordmark navy
BRAND_NAVY_DEEP = "#04184A"
BRAND_GOLD = "#E0A62E"     # seal border/wedge gold
BRAND_CYAN = "#19A6BD"     # seal wedge sky-blue, deepened for contrast
BRAND_RED = "#D6362B"      # seal wedge red (reserved for critical status only — see STATUS)

INK_PRIMARY = BRAND_NAVY_DEEP
INK_SECONDARY = "#4A5568"
INK_MUTED = "#8A93A6"
SURFACE = "#fcfcfd"
PAGE = "#f5f7fb"
GRID = "#e3e7f0"
BASELINE = "#c7cede"

# Validated categorical order (validate_palette.js --mode light: all PASS)
CATEGORICAL = ["#2E5AC4", "#C2860E", "#0E8DA3", "#8A4FD1", "#2F9E7A"]

STATUS = {"H": "#0ca30c", "M": "#fab219", "L": "#ec835a", "VL": "#d03b3b"}
STATUS_ICON = {"H": "●", "M": "▲", "L": "▲", "VL": "■"}
BAND_TEXT = {"H": "High", "M": "Medium", "L": "Low", "VL": "Very Low"}

CARD_CSS = f"""
<style>
.stApp {{ background-color: {PAGE}; }}
section[data-testid="stSidebar"] {{ background-color: {BRAND_NAVY_DEEP}; }}
section[data-testid="stSidebar"] * {{ color: #F2F5FC !important; }}
section[data-testid="stSidebar"] .stRadio > label {{ color: #F2F5FC !important; }}
.oberplus-card {{
    background: {SURFACE};
    border: 1px solid rgba(11,32,96,0.10);
    border-top: 3px solid {BRAND_GOLD};
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 10px;
    box-shadow: 0 1px 3px rgba(11,32,96,0.06);
}}
.oberplus-kpi-value {{ font-size: 2.0rem; font-weight: 700; color: {INK_PRIMARY}; line-height: 1.1; }}
.oberplus-kpi-label {{ font-size: 0.80rem; color: {INK_SECONDARY}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; font-weight: 600; }}
.oberplus-kpi-sub {{ font-size: 0.85rem; color: {INK_MUTED}; margin-top: 4px; }}
.band-chip {{
    display:inline-flex; align-items:center; gap:6px;
    padding: 3px 10px; border-radius: 999px; font-size: 0.80rem; font-weight: 600;
    border: 1px solid rgba(11,11,11,0.10);
}}
.oberplus-banner {{
    background: linear-gradient(90deg, {BRAND_NAVY_DEEP} 0%, {BRAND_NAVY} 55%, {BRAND_CYAN} 100%);
    color: white; padding: 12px 20px; border-radius: 10px; font-size: 0.88rem; margin-bottom: 14px;
    border-left: 4px solid {BRAND_GOLD};
}}
.section-note {{ color: {INK_SECONDARY}; font-size: 0.88rem; }}
h1, h2, h3 {{ color: {INK_PRIMARY}; }}
.stTabs [data-baseweb="tab"] {{ font-weight: 600; }}
.stTabs [aria-selected="true"] {{ color: {BRAND_NAVY} !important; }}
div[data-baseweb="tab-highlight"] {{ background-color: {BRAND_GOLD} !important; }}
</style>
"""


def band_chip_html(band_code: str, extra: str = "") -> str:
    color = STATUS[band_code]
    label = BAND_TEXT[band_code]
    return (f'<span class="band-chip" style="background:{color}22;color:{color};'
            f'border-color:{color}55;">{STATUS_ICON[band_code]} {label}{extra}</span>')


def kpi_card(label: str, value: str, sub: str = "") -> str:
    sub_html = f'<div class="oberplus-kpi-sub">{sub}</div>' if sub else ""
    return (f'<div class="oberplus-card"><div class="oberplus-kpi-label">{label}</div>'
            f'<div class="oberplus-kpi-value">{value}</div>{sub_html}</div>')


def apply_plotly_template():
    template = go.layout.Template()
    template.layout = go.Layout(
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font=dict(family="system-ui, -apple-system, Segoe UI, sans-serif", color=INK_SECONDARY, size=13),
        title=dict(font=dict(color=INK_PRIMARY, size=15)),
        xaxis=dict(gridcolor=GRID, linecolor=BASELINE, zerolinecolor=BASELINE, tickfont=dict(color=INK_MUTED)),
        yaxis=dict(gridcolor=GRID, linecolor=BASELINE, zerolinecolor=BASELINE, tickfont=dict(color=INK_MUTED)),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=40, l=10, r=10, b=10),
        colorway=CATEGORICAL,
    )
    pio.templates["oberplus"] = template
    pio.templates.default = "oberplus"

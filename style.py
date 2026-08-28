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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{ font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif; }}

.stApp {{ background-color: {PAGE}; }}

/* Hide Streamlit's default chrome for a product-like top bar */
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ background: transparent; }}

/* ---------------- Sidebar ---------------- */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {BRAND_NAVY_DEEP} 0%, #071f5c 100%);
}}
section[data-testid="stSidebar"] * {{ color: #F2F5FC !important; }}
section[data-testid="stSidebar"] .block-container {{ padding-top: 1.6rem; }}
.sidebar-eyebrow {{
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase;
    color: {BRAND_CYAN} !important; margin: 18px 0 8px 0;
}}
.sidebar-divider {{ height: 1px; background: rgba(255,255,255,0.14); border: none; margin: 18px 0; }}
.sidebar-footnote {{
    font-size: 0.78rem; line-height: 1.55; color: rgba(242,245,252,0.72) !important;
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.09);
    border-radius: 10px; padding: 12px 14px; margin-top: 4px;
}}
.sidebar-footnote b {{ color: #F2F5FC !important; }}

/* Course radio rendered as nav-style cards */
section[data-testid="stSidebar"] div[role="radiogroup"] {{ gap: 6px; }}
section[data-testid="stSidebar"] div[role="radiogroup"] label {{
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 10px 12px !important;
    margin: 0 !important;
    transition: background 0.15s ease, border-color 0.15s ease;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
    background: rgba(255,255,255,0.10); border-color: rgba(25,166,189,0.5);
}}
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {{
    background: rgba(25,166,189,0.18); border-color: {BRAND_CYAN};
}}

/* ---------------- KPI / content cards ---------------- */
.oberplus-card {{
    background: {SURFACE};
    border: 1px solid rgba(11,32,96,0.08);
    border-top: 3px solid {BRAND_GOLD};
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 10px;
    box-shadow: 0 1px 2px rgba(11,32,96,0.05), 0 8px 20px -14px rgba(11,32,96,0.25);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}
.oberplus-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(11,32,96,0.08), 0 14px 28px -16px rgba(11,32,96,0.30);
}}
.oberplus-kpi-icon {{
    display: inline-flex; align-items: center; justify-content: center;
    width: 34px; height: 34px; border-radius: 9px; font-size: 1.05rem;
    background: rgba(11,46,107,0.08); margin-bottom: 10px;
}}
.oberplus-kpi-value {{ font-size: 2.0rem; font-weight: 800; color: {INK_PRIMARY}; line-height: 1.1; letter-spacing: -0.02em; }}
.oberplus-kpi-label {{ font-size: 0.76rem; color: {INK_SECONDARY}; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 6px; font-weight: 700; }}
.oberplus-kpi-sub {{ font-size: 0.85rem; color: {INK_MUTED}; margin-top: 6px; }}

.band-chip {{
    display:inline-flex; align-items:center; gap:6px;
    padding: 3px 10px; border-radius: 999px; font-size: 0.80rem; font-weight: 700;
    border: 1px solid rgba(11,11,11,0.10);
}}

.oberplus-banner {{
    background: linear-gradient(90deg, {BRAND_NAVY_DEEP} 0%, {BRAND_NAVY} 55%, {BRAND_CYAN} 100%);
    color: white; padding: 14px 22px; border-radius: 12px; font-size: 0.92rem; margin-bottom: 18px;
    border-left: 4px solid {BRAND_GOLD};
    box-shadow: 0 10px 24px -14px rgba(4,24,74,0.55);
}}
.oberplus-banner b {{ font-weight: 700; }}

.section-note {{ color: {INK_SECONDARY}; font-size: 0.88rem; line-height: 1.55; }}
.section-eyebrow {{
    display:inline-block; font-size: 0.72rem; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase;
    color: {BRAND_NAVY}; background: rgba(11,32,96,0.07); padding: 4px 10px; border-radius: 999px; margin-bottom: 10px;
}}
h1, h2, h3 {{ color: {INK_PRIMARY}; letter-spacing: -0.01em; }}

/* ---------------- Tabs ---------------- */
.stTabs [data-baseweb="tab-list"] {{ gap: 4px; border-bottom: 1px solid {GRID}; }}
.stTabs [data-baseweb="tab"] {{ font-weight: 600; color: {INK_SECONDARY}; padding: 10px 16px; }}
.stTabs [aria-selected="true"] {{ color: {BRAND_NAVY} !important; }}
div[data-baseweb="tab-highlight"] {{ background-color: {BRAND_GOLD} !important; height: 3px !important; }}

/* ---------------- Alerts restyled to match brand ---------------- */
div[data-testid="stAlert"] {{ border-radius: 12px; border: 1px solid rgba(11,32,96,0.08); box-shadow: 0 1px 2px rgba(11,32,96,0.05); }}

/* ---------------- st.metric ---------------- */
div[data-testid="stMetric"] {{
    background: {SURFACE}; border: 1px solid rgba(11,32,96,0.08); border-radius: 12px;
    padding: 12px 16px; box-shadow: 0 1px 2px rgba(11,32,96,0.05);
}}
div[data-testid="stMetricLabel"] {{ color: {INK_SECONDARY} !important; font-weight: 600; }}
div[data-testid="stMetricValue"] {{ color: {INK_PRIMARY} !important; }}

/* ---------------- Practice / log cards ---------------- */
.practice-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; margin: 6px 0 20px 0; }}
.practice-card {{
    background: {SURFACE}; border: 1px solid rgba(11,32,96,0.08); border-radius: 12px;
    padding: 14px 16px; box-shadow: 0 1px 2px rgba(11,32,96,0.05);
    border-left: 4px solid var(--accent, {BRAND_NAVY});
}}
.practice-card .practice-title {{ font-weight: 700; color: {INK_PRIMARY}; font-size: 0.92rem; margin-bottom: 4px; }}
.practice-card .practice-cite {{ font-size: 0.80rem; color: {INK_MUTED}; font-style: italic; }}

.log-card {{
    background: {SURFACE}; border: 1px solid rgba(11,32,96,0.08); border-radius: 14px;
    padding: 16px 20px; margin-bottom: 14px; box-shadow: 0 1px 2px rgba(11,32,96,0.05);
    border-left: 5px solid var(--accent, {BRAND_NAVY});
}}
.log-card .log-head {{ display:flex; align-items:center; gap:10px; margin-bottom: 8px; flex-wrap: wrap; }}
.log-card .log-id {{ font-weight: 800; color: {INK_PRIMARY}; }}
.log-card .log-badge {{
    font-size: 0.74rem; font-weight: 700; padding: 2px 9px; border-radius: 999px;
    background: var(--accent-bg, rgba(11,32,96,0.08)); color: var(--accent, {BRAND_NAVY});
}}
.log-card .log-meta {{ font-size: 0.82rem; color: {INK_MUTED}; }}
.log-card .log-body {{ font-size: 0.90rem; color: {INK_SECONDARY}; margin-bottom: 10px; }}
.log-ba-grid {{ display:grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 8px; }}
.log-ba-box {{ background: {PAGE}; border-radius: 8px; padding: 10px 12px; font-size: 0.85rem; color: {INK_SECONDARY}; }}
.log-ba-box b {{ display:block; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; color: {INK_MUTED}; margin-bottom: 3px; }}

/* ---------------- Reflect data table ---------------- */
.rt-wrap {{
    background: {SURFACE}; border: 1px solid rgba(11,32,96,0.08); border-radius: 14px;
    overflow: hidden; box-shadow: 0 1px 2px rgba(11,32,96,0.05); margin-bottom: 18px;
}}
.rt-table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
.rt-table th {{
    text-align: left; font-size: 0.70rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em;
    color: {INK_MUTED}; background: {PAGE}; padding: 10px 16px; border-bottom: 1px solid rgba(11,32,96,0.08);
}}
.rt-table td {{ padding: 12px 16px; border-bottom: 1px solid rgba(11,32,96,0.06); color: {INK_SECONDARY}; vertical-align: middle; }}
.rt-table tr:last-child td {{ border-bottom: none; }}
.rt-table tr:hover td {{ background: rgba(11,32,96,0.02); }}
.rt-table td.rt-id {{ font-weight: 700; color: {INK_PRIMARY}; }}
.flag-chip {{
    display:inline-flex; align-items:center; gap:5px; font-size: 0.78rem; font-weight: 600; padding: 2px 9px; border-radius: 999px;
}}
.flag-chip.flag-yes {{ background: {BRAND_RED}18; color: {BRAND_RED}; }}
.flag-chip.flag-no {{ background: {INK_MUTED}18; color: {INK_MUTED}; }}

/* ---------------- CLO snapshot strip ---------------- */
.clo-strip {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 4px 0 6px 0; }}
.clo-pill {{
    display:flex; align-items:center; gap:8px; background: {SURFACE};
    border: 1px solid rgba(11,32,96,0.08); border-radius: 11px; padding: 9px 14px;
    box-shadow: 0 1px 2px rgba(11,32,96,0.05); min-width: 150px;
}}
.clo-pill .clo-pill-id {{ font-weight: 700; color: {INK_PRIMARY}; font-size: 0.86rem; }}
.clo-pill .clo-pill-val {{ font-size: 0.86rem; color: {INK_SECONDARY}; margin-left: auto; }}
</style>
"""


def band_chip_html(band_code: str, extra: str = "") -> str:
    color = STATUS[band_code]
    label = BAND_TEXT[band_code]
    return (f'<span class="band-chip" style="background:{color}22;color:{color};'
            f'border-color:{color}55;">{STATUS_ICON[band_code]} {label}{extra}</span>')


def kpi_card(label: str, value: str, sub: str = "", icon: str = "") -> str:
    sub_html = f'<div class="oberplus-kpi-sub">{sub}</div>' if sub else ""
    icon_html = f'<div class="oberplus-kpi-icon">{icon}</div>' if icon else ""
    return (f'<div class="oberplus-card">{icon_html}<div class="oberplus-kpi-label">{label}</div>'
            f'<div class="oberplus-kpi-value">{value}</div>{sub_html}</div>')


def practice_grid_html(items: list, accent: str) -> str:
    cards = "".join(
        f'<div class="practice-card" style="--accent:{accent};">'
        f'<div class="practice-title">{name}</div><div class="practice-cite">{cite}</div></div>'
        for name, cite in items
    )
    return f'<div class="practice-grid">{cards}</div>'


def log_card_html(rec: dict) -> str:
    is_formal = rec["path"] == "formal"
    accent = STATUS["H"] if is_formal else BRAND_GOLD
    accent_bg = f"{accent}22"
    badge_text = "Formal · linked to R3" if is_formal else "Informal · detected, no R3 link"
    footer = (f"Changed by {rec['changed_by']} on {rec['changed_at']}"
              + (f" · implements {rec['recommendation_id']} ({rec['recommendation_category']})"
                 if rec["recommendation_id"] else " · no linked R3 recommendation"))
    return (
        f'<div class="log-card" style="--accent:{accent};--accent-bg:{accent_bg};">'
        f'<div class="log-head"><span class="log-id">{rec["id"]}</span>'
        f'<span class="log-badge">{badge_text}</span>'
        f'<span class="log-meta">{rec["clo"]} · {rec["offering_boundary"]}</span></div>'
        f'<div class="log-body">{rec["what_changed"]}</div>'
        f'<div class="log-ba-grid">'
        f'<div class="log-ba-box"><b>Before</b>{rec["before"]}</div>'
        f'<div class="log-ba-box"><b>After</b>{rec["after"]}</div>'
        f'</div>'
        f'<div class="log-meta">{footer}</div>'
        f'</div>'
    )


def data_table_html(headers: list, rows: list, id_col: int = 0) -> str:
    """rows: list of lists of already-formatted cell strings, aligned to headers."""
    head = "<tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr>"
    body = "".join(
        "<tr>" + "".join(f'<td class="rt-id">{c}</td>' if i == id_col else f"<td>{c}</td>"
                          for i, c in enumerate(row)) + "</tr>"
        for row in rows
    )
    return f'<div class="rt-wrap"><table class="rt-table">{head}{body}</table></div>'


def drift_card_html(clo_id: str, at_offering: str, level_changed: bool, from_level: str, to_level: str,
                     from_text: str, to_text: str) -> str:
    accent = BRAND_GOLD
    return (
        f'<div class="log-card" style="--accent:{accent};--accent-bg:{accent}22;">'
        f'<div class="log-head"><span class="log-id">{clo_id}</span>'
        f'<span class="log-badge">changed at {at_offering}</span>'
        f'<span class="log-meta">RBT level {"changed" if level_changed else "unchanged"} '
        f'({from_level} → {to_level})</span></div>'
        f'<div class="log-ba-grid">'
        f'<div class="log-ba-box"><b>Before</b>{from_text}</div>'
        f'<div class="log-ba-box"><b>After</b>{to_text}</div>'
        f'</div>'
        f'<div class="log-meta">Attached as a note only — never suspends or replaces the R2 flag.</div>'
        f'</div>'
    )


def reflect_table_html(results: dict, level_label: str, offerings: list) -> str:
    head = (f'<tr><th>{level_label}</th><th>{offerings[0]}</th><th>{offerings[1]}</th><th>{offerings[2]}</th>'
            f'<th>Target</th><th>Flagged</th><th>Misses / avg shortfall</th><th>Band</th></tr>')
    rows_html = []
    for key, r in results.items():
        flag_html = (f'<span class="flag-chip flag-yes">🚩 Yes</span>' if r.flagged
                     else '<span class="flag-chip flag-no">No</span>')
        miss_txt = (f"{r.miss_count} miss(es), avg −{r.avg_shortfall:.2f} pts"
                    if r.avg_shortfall is not None else "no misses")
        rows_html.append(
            f'<tr><td class="rt-id">{key}</td>'
            f'<td>{r.attainments[0]:.1f}%</td><td>{r.attainments[1]:.1f}%</td><td>{r.attainments[2]:.1f}%</td>'
            f'<td>{r.target:.0f}%</td><td>{flag_html}</td><td>{miss_txt}</td>'
            f'<td>{band_chip_html(r.band)}</td></tr>'
        )
    return f'<div class="rt-wrap"><table class="rt-table">{head}{"".join(rows_html)}</table></div>'


def clo_strip_html(rows: list) -> str:
    """rows: list of (clo_id, latest_value, band_code)"""
    pills = "".join(
        f'<div class="clo-pill"><span class="clo-pill-id">{cid}</span>'
        f'{band_chip_html(band)}<span class="clo-pill-val">{val:.1f}%</span></div>'
        for cid, val, band in rows
    )
    return f'<div class="clo-strip">{pills}</div>'


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

"""
theme.py
--------
Shared theme constants, CSS, and Plotly helpers for every page.
"""

import plotly.graph_objects as go
import streamlit as st


# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
CYAN = "#00d4ff"
CYAN_BRIGHT = "#22e0ff"
CYAN_DEEP = "#0891b2"
PURPLE = "#7b2ff7"
PINK = "#ec4899"
BLUE = "#2563eb"
SKY = "#29B6F6"
GREEN = "#22c55e"
AMBER = "#f59e0b"
RED = "#ef4444"
TEXT = "#F0F2F6"
TEXT_DIM = "#A0AAB8"
DARK = "#0a0e1a"


DEPT_COLORS = {
    "Cardiology":       "#22d3ee",
    "Orthopedics":      "#2dd4bf",
    "Oncology":         "#a78bfa",
    "Neurology":        "#f0abfc",
    "ICU":              "#fb7185",
    "General Medicine": "#fb923c",
    "Pulmonology":      "#fbbf24",
    "Emergency":        "#facc15",
    "Urology":          "#a3e635",
    "Gynecology":       "#4ade80",
    "Psychiatry":       "#f87171",
    "ENT":              "#c084fc",
    "Pediatrics":       "#67e8f9",
    "Dermatology":      "#5eead4",
    "Radiology":        "#34d399",
}


_COMMON_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        -webkit-font-smoothing: antialiased;
    }

    .stApp {
        background:
            radial-gradient(ellipse at top left, rgba(0, 212, 255, 0.06), transparent 55%),
            radial-gradient(ellipse at bottom right, rgba(123, 47, 247, 0.05), transparent 55%),
            linear-gradient(180deg, #0a0e1a 0%, #0c1220 50%, #0a0e1a 100%);
        color: #F0F2F6;
    }

    /* ---------- Sidebar ---------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(12, 18, 32, 0.98), rgba(10, 14, 26, 0.98));
        border-right: 1px solid rgba(0, 212, 255, 0.12);
    }
    [data-testid="stSidebar"] * { color: #c9d7ee; }
    [data-testid="stSidebarNav"] > ul > li:first-child { display: none; }

    /* ---------- Metric cards ---------- */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(20, 30, 50, 0.7), rgba(15, 22, 38, 0.65));
        border: 1px solid rgba(0, 212, 255, 0.14);
        border-left: 3px solid #00d4ff;
        border-radius: 14px;
        padding: 16px 20px;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.25);
        animation: fadeInUp 0.6s ease both;
        min-width: 150px;
        overflow: hidden;
    }
    [data-testid="stMetric"]:hover {
        border-left-color: #7b2ff7;
        border-color: rgba(0, 212, 255, 0.35);
        box-shadow: 0 12px 32px rgba(0, 212, 255, 0.12);
        transform: translateY(-3px);
    }
    [data-testid="stMetricValue"] {
        color: #00d4ff;
        font-family: 'JetBrains Mono', 'Inter', monospace;
        font-weight: 700;
        font-variant-numeric: tabular-nums;
        font-size: clamp(1.3rem, 1.7vw, 2rem);
        letter-spacing: -0.02em;
        line-height: 1.15;
    }
    [data-testid="stMetricLabel"] {
        color: #A0AAB8;
        font-size: clamp(0.68rem, 0.82vw, 0.78rem);
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        white-space: normal;
        line-height: 1.35;
        min-height: 2.3em;
    }

    [data-testid="column"] {
        min-width: 150px !important;
        padding: 0 6px;
    }

    /* ---------- Page header ---------- */
    .page-title {
        font-size: clamp(1.8rem, 3vw, 2.4rem);
        font-weight: 800;
        background: linear-gradient(90deg, #00d4ff 0%, #7b2ff7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.4rem;
        letter-spacing: -0.03em;
        line-height: 1.2;
        padding-top: 0.3rem;
        animation: fadeInUp 0.8s ease both;
    }
    .page-sub {
        color: #A0AAB8;
        font-size: clamp(0.92rem, 1.05vw, 1.05rem);
        line-height: 1.6;
        margin-bottom: 1.6rem;
        animation: fadeInUp 0.9s ease both;
    }
    .section-label {
        display: flex;
        align-items: center;
        gap: 10px;
        color: #F0F2F6;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin: 1.6rem 0 0.8rem 0;
    }
    .section-label::before {
        content: "";
        display: inline-block;
        width: 4px;
        height: 16px;
        background: linear-gradient(180deg, #00d4ff, #7b2ff7);
        border-radius: 2px;
    }
    .metric-sub {
        color: #A0AAB8;
        font-size: 0.78rem;
        margin-top: 6px;
        letter-spacing: 0.02em;
        line-height: 1.4;
    }
    hr {
        border: none;
        border-top: 1px solid rgba(0, 212, 255, 0.1);
        margin: 1.6rem 0;
    }

    /* ---------- Multiselect / select widgets ---------- */
    /* The field itself */
    [data-baseweb="select"] > div {
        background-color: rgba(20, 30, 50, 0.65) !important;
        border-color: rgba(0, 212, 255, 0.25) !important;
        border-radius: 10px !important;
    }
    [data-baseweb="select"] > div:hover {
        border-color: rgba(0, 212, 255, 0.5) !important;
    }

    /* Selected value pills (tags) — softer blue, white text */
    [data-baseweb="tag"] {
        background-color: rgba(0, 212, 255, 0.18) !important;
        border: 1px solid rgba(0, 212, 255, 0.45) !important;
        border-radius: 8px !important;
        color: #F0F2F6 !important;
    }
    [data-baseweb="tag"]:hover {
        background-color: rgba(0, 212, 255, 0.28) !important;
    }
    [data-baseweb="tag"] span {
        color: #F0F2F6 !important;
        font-weight: 500 !important;
    }
    /* The small ✕ inside each tag — make it clearly visible */
    [data-baseweb="tag"] svg {
        color: #F0F2F6 !important;
        fill: #F0F2F6 !important;
        opacity: 0.95 !important;
        transition: color 0.15s ease, fill 0.15s ease;
    }
    [data-baseweb="tag"] svg:hover {
        color: #FF4B4B !important;
        fill: #FF4B4B !important;
        opacity: 1 !important;
    }

    /* Dropdown option menu */
    [data-baseweb="popover"] ul {
        background-color: rgba(12, 18, 32, 0.98) !important;
        border: 1px solid rgba(0, 212, 255, 0.15) !important;
        border-radius: 10px !important;
    }
    [data-baseweb="popover"] li {
        background-color: transparent !important;
        color: #F0F2F6 !important;
    }
    [data-baseweb="popover"] li:hover {
        background-color: rgba(0, 212, 255, 0.10) !important;
    }
    /* Muted highlight for currently-selected option (was bright blue) */
    [data-baseweb="popover"] li[aria-selected="true"] {
        background-color: rgba(0, 212, 255, 0.15) !important;
        color: #00d4ff !important;
    }
    [data-baseweb="popover"] li[aria-selected="true"]:hover {
        background-color: rgba(0, 212, 255, 0.20) !important;
    }

    /* Date input field */
    [data-baseweb="input"] {
        background-color: rgba(20, 30, 50, 0.65) !important;
        border-color: rgba(0, 212, 255, 0.25) !important;
        border-radius: 10px !important;
    }

    /* Buttons — softer */
    .stButton > button {
        background-color: rgba(20, 30, 50, 0.75) !important;
        color: #F0F2F6 !important;
        border: 1px solid rgba(0, 212, 255, 0.25) !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background-color: rgba(0, 212, 255, 0.12) !important;
        border-color: rgba(0, 212, 255, 0.55) !important;
        color: #00d4ff !important;
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0);    }
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
</style>
"""


def apply_page_style() -> None:
    """Inject the shared CSS. Call once per page, after set_page_config."""
    st.markdown(_COMMON_CSS, unsafe_allow_html=True)


def style_dark(fig: go.Figure, height: int = 400) -> go.Figure:
    """Apply dark theme to any Plotly figure."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT, family="Inter, -apple-system, sans-serif", size=12.5),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.035)",
            zerolinecolor="rgba(255,255,255,0.08)",
            tickfont=dict(color=TEXT_DIM, size=11.5),
            showline=False,
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.035)",
            zerolinecolor="rgba(255,255,255,0.08)",
            tickfont=dict(color=TEXT_DIM, size=11.5),
            showline=False,
        ),
        margin=dict(l=30, r=30, t=60, b=40),
        height=height,
        hoverlabel=dict(
            bgcolor="#0c1220",
            bordercolor="rgba(0, 212, 255, 0.4)",
            font=dict(size=13, color=TEXT, family="Inter, sans-serif"),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=TEXT, size=12),
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="left", x=0,
        ),
    )
    return fig


def section_label(text: str) -> None:
    st.markdown(f'<div class="section-label">{text}</div>', unsafe_allow_html=True)


def page_header(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">{subtitle}</div>', unsafe_allow_html=True)
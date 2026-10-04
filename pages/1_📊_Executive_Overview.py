"""
pages/1_📊_Executive_Overview.py
--------------------------------
Executive Overview — hospital-wide KPIs and headline charts.

Integrates cross-page filters via utils.filters.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.loader import load_all
from utils.filters import render_filters, apply_filters, apply_filters_by_admission_id


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Executive Overview · Smart Hospital",
    page_icon="📊",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------
CYAN = "#00d4ff"
PURPLE = "#7b2ff7"
BLUE = "#2563eb"
GREEN = "#22c55e"
AMBER = "#f59e0b"
RED = "#ef4444"
TEXT = "#F0F2F6"
TEXT_DIM = "#A0AAB8"

PALETTE = [
    "#00d4ff", "#7b2ff7", "#22c55e", "#f59e0b",
    "#ef4444", "#06b6d4", "#a855f7", "#ec4899",
    "#10b981", "#f97316", "#3b82f6", "#84cc16",
    "#eab308", "#14b8a6", "#8b5cf6",
]


# ---------------------------------------------------------------------------
# Chart helpers
# ---------------------------------------------------------------------------
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
        margin=dict(l=30, r=30, t=70, b=40),
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


def pct_change(new_value: float, old_value: float) -> float:
    if old_value == 0:
        return 0.0
    return (new_value - old_value) / old_value * 100.0


def fmt_delta(pct: float) -> str:
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.1f}%"


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
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

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(12, 18, 32, 0.98), rgba(10, 14, 26, 0.98));
            border-right: 1px solid rgba(0, 212, 255, 0.12);
        }
        [data-testid="stSidebar"] * { color: #c9d7ee; }
        [data-testid="stSidebarNav"] > ul > li:first-child { display: none; }

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
            margin-bottom: 0.4rem;
            animation: fadeInUp 0.9s ease both;
        }
        .page-note {
            color: #6b7f9e;
            font-size: 0.82rem;
            font-style: italic;
            margin-bottom: 1.6rem;
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
        hr {
            border: none;
            border-top: 1px solid rgba(0, 212, 255, 0.1);
            margin: 1.6rem 0;
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(10px); }
            to   { opacity: 1; transform: translateY(0);    }
        }

        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
@st.cache_data(ttl=600, show_spinner="Loading data...")
def get_data() -> dict:
    return load_all()


data = get_data()
patients = data["patients"]
doctors = data["doctors"]
departments = data["departments"]
icu = data["icu"]
emergency = data["emergency"]
billing = data["billing"]

# Raw admissions (unfiltered) — needed for the sidebar widget options.
admissions_raw = data["admissions"]

# --- Filters ---
filters = render_filters(data)

# Filtered versions used everywhere below.
admissions = apply_filters(admissions_raw, filters)
icu_f = apply_filters_by_admission_id(icu, admissions)
emergency_f = apply_filters_by_admission_id(emergency, admissions)
billing_f = apply_filters_by_admission_id(billing, admissions)


# ---------------------------------------------------------------------------
# Time windows — computed on the FILTERED admissions.
# ---------------------------------------------------------------------------
if admissions.empty:
    st.markdown('<div class="page-title">Executive Overview</div>', unsafe_allow_html=True)
    st.warning("No data matches the current filters. Adjust or reset the filters in the sidebar.")
    st.stop()

anchor = admissions["admission_date"].max()
last_start = anchor - pd.DateOffset(months=12)
prev_start = anchor - pd.DateOffset(months=24)
current_month_start = anchor.replace(day=1)
complete_through = current_month_start - pd.Timedelta(days=1)

adm_recent = admissions[admissions["admission_date"] > last_start]
adm_prev = admissions[
    (admissions["admission_date"] > prev_start)
    & (admissions["admission_date"] <= last_start)
]

billing_with_dates = billing_f.merge(
    admissions[["admission_id", "admission_date", "admission_ym", "department"]],
    on="admission_id",
    how="left",
)
bill_recent = billing_with_dates[billing_with_dates["admission_date"] > last_start]
bill_prev = billing_with_dates[
    (billing_with_dates["admission_date"] > prev_start)
    & (billing_with_dates["admission_date"] <= last_start)
]


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.markdown('<div class="page-title">Executive Overview</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="page-sub">'
    f"Twelve months of hospital performance, comparing "
    f"{last_start.strftime('%b %Y')} through {complete_through.strftime('%b %Y')} "
    f"against the same period one year earlier."
    f'</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="page-note">'
    f"Note: {anchor.strftime('%b %Y')} is still in progress and has been "
    f"left out of all trend lines to keep comparisons fair."
    f'</div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# KPI row 1
# ---------------------------------------------------------------------------
admissions_delta = pct_change(len(adm_recent), len(adm_prev))
revenue_recent = bill_recent["amount"].sum() if not bill_recent.empty else 0
revenue_prev = bill_prev["amount"].sum() if not bill_prev.empty else 0
revenue_delta = pct_change(revenue_recent, revenue_prev)
los_recent = adm_recent["length_of_stay"].mean() if not adm_recent.empty else 0
los_prev = adm_prev["length_of_stay"].mean() if not adm_prev.empty else 0
los_delta = pct_change(los_recent, los_prev)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Patients", f"{patients['patient_id'].nunique():,}")
c2.metric("Admissions, 12 months", f"{len(adm_recent):,}",
          delta=fmt_delta(admissions_delta))
c3.metric("Revenue, 12 months", f"₹{revenue_recent / 1e7:.1f} Cr",
          delta=fmt_delta(revenue_delta))
c4.metric("Avg Length of Stay", f"{los_recent:.1f} days",
          delta=fmt_delta(los_delta), delta_color="inverse")


# ---------------------------------------------------------------------------
# KPI row 2
# ---------------------------------------------------------------------------
icu_with_dates = icu_f.merge(
    admissions[["admission_id", "admission_date"]],
    on="admission_id", how="left",
)
icu_recent = icu_with_dates[icu_with_dates["admission_date"] > last_start]
icu_prev = icu_with_dates[
    (icu_with_dates["admission_date"] > prev_start)
    & (icu_with_dates["admission_date"] <= last_start)
]

er_with_dates = emergency_f.merge(
    admissions[["admission_id", "admission_date"]],
    on="admission_id", how="left",
)
er_recent = er_with_dates[er_with_dates["admission_date"] > last_start]
er_prev = er_with_dates[
    (er_with_dates["admission_date"] > prev_start)
    & (er_with_dates["admission_date"] <= last_start)
]

readmit_recent = adm_recent["is_readmission"].mean() * 100 if not adm_recent.empty else 0
readmit_prev = adm_prev["is_readmission"].mean() * 100 if not adm_prev.empty else 0
readmit_delta = pct_change(readmit_recent, readmit_prev)

c1, c2, c3, c4 = st.columns(4)
c1.metric("ICU Stays, 12 months", f"{len(icu_recent):,}",
          delta=fmt_delta(pct_change(len(icu_recent), len(icu_prev))))
c2.metric("Emergency Visits", f"{len(er_recent):,}",
          delta=fmt_delta(pct_change(len(er_recent), len(er_prev))))
c3.metric("Readmission Rate", f"{readmit_recent:.2f}%",
          delta=fmt_delta(readmit_delta), delta_color="inverse")
c4.metric("Departments", f"{admissions['department'].nunique()}")


# ---------------------------------------------------------------------------
# Chart 1 — Monthly trend
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="section-label">Monthly Trend · Last 24 Complete Months</div>',
    unsafe_allow_html=True,
)

trend_start = anchor - pd.DateOffset(months=24)
adm_trend = admissions[
    (admissions["admission_date"] > trend_start)
    & (admissions["admission_date"] < current_month_start)
]
bill_trend = billing_with_dates[
    (billing_with_dates["admission_date"] > trend_start)
    & (billing_with_dates["admission_date"] < current_month_start)
]

monthly_adm = (
    adm_trend.groupby("admission_ym").size().reset_index(name="admissions")
)
monthly_rev = (
    bill_trend.groupby("admission_ym")["amount"].sum().reset_index(name="revenue")
)
monthly = monthly_adm.merge(monthly_rev, on="admission_ym").sort_values("admission_ym")

fig1 = go.Figure()
fig1.add_trace(go.Bar(
    x=monthly["admission_ym"],
    y=monthly["admissions"],
    name="Admissions",
    marker=dict(
        color="rgba(0, 212, 255, 0.55)",
        line=dict(color="rgba(0, 212, 255, 0.9)", width=1),
        cornerradius=4,
    ),
    yaxis="y",
    hovertemplate="<b>%{x}</b><br>Admissions: %{y:,}<extra></extra>",
))
fig1.add_trace(go.Scatter(
    x=monthly["admission_ym"],
    y=monthly["revenue"],
    name="Revenue (₹)",
    mode="lines+markers",
    line=dict(color=PURPLE, width=3, shape="spline", smoothing=0.6),
    marker=dict(size=8, color=PURPLE, line=dict(color="#0a0e1a", width=2)),
    fill="tozeroy",
    fillcolor="rgba(123, 47, 247, 0.08)",
    yaxis="y2",
    hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>",
))
fig1.update_layout(
    yaxis=dict(title="Admissions", side="left",
               title_font=dict(color=TEXT_DIM, size=12)),
    yaxis2=dict(title="Revenue (₹)", overlaying="y", side="right",
                showgrid=False,
                title_font=dict(color=TEXT_DIM, size=12)),
    hovermode="x unified",
)
style_dark(fig1, height=460)
st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Chart 2 + 3
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.markdown(
        '<div class="section-label">Admissions by Department</div>',
        unsafe_allow_html=True,
    )
    dept_counts = (
        adm_recent.groupby("department").size()
        .reset_index(name="count")
        .sort_values("count", ascending=True)
    )
    fig2 = px.bar(
        dept_counts,
        x="count", y="department",
        orientation="h",
        color="count",
        color_continuous_scale=[
            [0.0, "#0e2a4a"],
            [0.5, "#0891b2"],
            [1.0, CYAN],
        ],
        text="count",
    )
    fig2.update_traces(
        textposition="outside",
        textfont=dict(color=TEXT, size=11, family="JetBrains Mono"),
        marker=dict(cornerradius=5, line=dict(width=0)),
        hovertemplate="<b>%{y}</b><br>%{x:,} admissions<extra></extra>",
    )
    style_dark(fig2, height=480)
    fig2.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_title=None, yaxis_title=None,
        margin=dict(l=30, r=70, t=50, b=30),
    )
    st.plotly_chart(fig2, use_container_width=True,
                    config={"displayModeBar": False})

with c2:
    st.markdown(
        '<div class="section-label">Outcomes · Last 12 Months</div>',
        unsafe_allow_html=True,
    )
    outcome_order = ["Recovered", "Discharged", "Transferred", "Deceased"]
    outcome_counts = (
        adm_recent.groupby("outcome").size()
        .reindex(outcome_order)
        .reset_index(name="count")
        .sort_values("count", ascending=True)
    )
    fig3 = px.bar(
        outcome_counts,
        x="count", y="outcome",
        orientation="h",
        color="outcome",
        color_discrete_map={
            "Recovered": CYAN,
            "Discharged": GREEN,
            "Transferred": AMBER,
            "Deceased": RED,
        },
        text="count",
    )
    fig3.update_traces(
        textposition="inside",
        insidetextanchor="end",
        textfont=dict(color="#0a0e1a", size=12.5, family="JetBrains Mono"),
        marker=dict(cornerradius=5, line=dict(width=0)),
        hovertemplate="<b>%{y}</b><br>%{x:,} admissions<extra></extra>",
    )
    style_dark(fig3, height=480)
    fig3.update_layout(
        showlegend=False,
        xaxis_title=None, yaxis_title=None,
        margin=dict(l=30, r=30, t=50, b=30),
    )
    st.plotly_chart(fig3, use_container_width=True,
                    config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Chart 4 + 5
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.markdown(
        '<div class="section-label">Admissions by Day of Week</div>',
        unsafe_allow_html=True,
    )
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday",
                 "Friday", "Saturday", "Sunday"]
    dow_counts = (
        adm_recent.groupby("admission_dow").size()
        .reindex(dow_order)
        .reset_index(name="count")
    )
    fig4 = px.bar(
        dow_counts,
        x="admission_dow", y="count",
        color="count",
        color_continuous_scale=[
            [0.0, "#0e2a4a"],
            [0.5, "#0891b2"],
            [1.0, CYAN],
        ],
        text="count",
    )
    fig4.update_traces(
        textposition="outside",
        textfont=dict(color=TEXT, size=11, family="JetBrains Mono"),
        marker=dict(cornerradius=5, line=dict(width=0)),
        hovertemplate="<b>%{x}</b><br>%{y:,} admissions<extra></extra>",
    )
    style_dark(fig4, height=380)
    fig4.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_title=None, yaxis_title=None,
        margin=dict(l=30, r=30, t=50, b=50),
    )
    st.plotly_chart(fig4, use_container_width=True,
                    config={"displayModeBar": False})

with c2:
    st.markdown(
        '<div class="section-label">Seasonal Distribution</div>',
        unsafe_allow_html=True,
    )
    season_order = ["Winter", "Summer", "Monsoon", "Post-Monsoon"]
    season_counts = (
        adm_recent.groupby("season").size()
        .reindex(season_order)
        .reset_index(name="count")
    )
    fig5 = px.bar(
        season_counts,
        x="season", y="count",
        color="season",
        color_discrete_map={
            "Winter": CYAN,
            "Summer": AMBER,
            "Monsoon": BLUE,
            "Post-Monsoon": PURPLE,
        },
        text="count",
    )
    fig5.update_traces(
        textposition="outside",
        textfont=dict(color=TEXT, size=11, family="JetBrains Mono"),
        marker=dict(cornerradius=5, line=dict(width=0)),
        hovertemplate="<b>%{x}</b><br>%{y:,} admissions<extra></extra>",
    )
    style_dark(fig5, height=380)
    fig5.update_layout(
        showlegend=False,
        xaxis_title=None, yaxis_title=None,
        margin=dict(l=30, r=30, t=50, b=50),
    )
    st.plotly_chart(fig5, use_container_width=True,
                    config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "Executive Overview · Built by Shahan Malik · "
    "Streamlit · SQLite · Plotly · Pandas · 2026"
)
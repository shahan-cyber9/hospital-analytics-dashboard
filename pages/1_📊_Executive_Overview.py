"""
pages/1_📊_Executive_Overview.py
--------------------------------
Executive Overview — hospital-wide KPIs and headline charts.

Compares last 12 months vs previous 12 months for trend indicators.
Excludes the partial current month from trend charts to avoid fake cliffs.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.loader import load_all


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Executive Overview · Smart Hospital",
    page_icon="📊",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Theme constants
# ---------------------------------------------------------------------------
CYAN = "#00d4ff"
PURPLE = "#7b2ff7"
BLUE = "#2563eb"
GREEN = "#22c55e"
AMBER = "#f59e0b"
RED = "#ef4444"
TEXT = "#c9d7ee"
MUTED = "#8ba3c7"

PALETTE = [
    "#00d4ff", "#7b2ff7", "#22c55e", "#f59e0b",
    "#ef4444", "#06b6d4", "#a855f7", "#ec4899",
    "#10b981", "#f97316", "#3b82f6", "#84cc16",
    "#eab308", "#14b8a6", "#8b5cf6",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def style_dark(fig: go.Figure, height: int = 380) -> go.Figure:
    """Apply dark-theme styling to any Plotly figure."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT, family="Inter, -apple-system, sans-serif", size=12),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)",
                   zerolinecolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)",
                   zerolinecolor="rgba(255,255,255,0.1)"),
        margin=dict(l=20, r=20, t=60, b=30),
        height=height,
        hoverlabel=dict(bgcolor="#0f1525", font_size=13, font_color=TEXT),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=TEXT),
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="left", x=0,
        ),
    )
    return fig


def pct_change(new_value: float, old_value: float) -> float:
    """Percentage change. Returns 0 if old_value is 0."""
    if old_value == 0:
        return 0.0
    return (new_value - old_value) / old_value * 100.0


def fmt_delta(pct: float) -> str:
    """Format a percentage as '+X.X%' or '-X.X%'."""
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.1f}%"


# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(180deg, #0a0e1a 0%, #0f1525 100%);
            color: #e6edf7;
        }
        [data-testid="stSidebar"] {
            background: rgba(15, 21, 37, 0.95);
            border-right: 1px solid rgba(0, 200, 255, 0.15);
        }
        [data-testid="stSidebar"] * { color: #c9d7ee; }
        [data-testid="stSidebarNav"] > ul > li:first-child { display: none; }

        [data-testid="stMetric"] {
            background: rgba(20, 30, 50, 0.55);
            border: 1px solid rgba(0, 200, 255, 0.18);
            border-radius: 14px;
            padding: 16px 20px;
            backdrop-filter: blur(8px);
            transition: all 0.25s ease;
            animation: fadeInUp 0.6s ease both;
        }
        [data-testid="stMetric"]:hover {
            border-color: rgba(0, 212, 255, 0.45);
            box-shadow: 0 8px 24px rgba(0, 212, 255, 0.15);
            transform: translateY(-2px);
        }
        [data-testid="stMetricValue"] { color: #00d4ff; font-weight: 700; }
        [data-testid="stMetricLabel"] {
            color: #8ba3c7; font-size: 0.82rem;
            letter-spacing: 0.05em; text-transform: uppercase;
        }

        .page-title {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(90deg, #00d4ff 0%, #7b2ff7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.1rem;
            line-height: 1.3;
            padding-top: 0.3rem;
            animation: fadeInUp 0.8s ease both;
        }
        .page-sub {
            color: #8ba3c7;
            font-size: 1rem;
            margin-bottom: 0.3rem;
            animation: fadeInUp 0.9s ease both;
        }
        .page-note {
            color: #6b7f9e;
            font-size: 0.82rem;
            margin-bottom: 1.5rem;
            font-style: italic;
        }
        .section-label {
            color: #8ba3c7;
            font-size: 0.82rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin: 1.4rem 0 0.4rem 0;
        }
        hr { border-color: rgba(0, 200, 255, 0.12); }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(8px); }
            to   { opacity: 1; transform: translateY(0);   }
        }
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
admissions = data["admissions"]
icu = data["icu"]
emergency = data["emergency"]
billing = data["billing"]


# ---------------------------------------------------------------------------
# Time windows
# ---------------------------------------------------------------------------
anchor = admissions["admission_date"].max()             # latest date overall
last_start = anchor - pd.DateOffset(months=12)
prev_start = anchor - pd.DateOffset(months=24)

# The latest calendar month may be incomplete (e.g., data ends Oct 4).
# Exclude it from monthly trend charts so they don't show a fake cliff.
current_month_start = anchor.replace(day=1)
complete_through = current_month_start - pd.Timedelta(days=1)

adm_recent = admissions[admissions["admission_date"] > last_start]
adm_prev = admissions[
    (admissions["admission_date"] > prev_start)
    & (admissions["admission_date"] <= last_start)
]

billing_with_dates = billing.merge(
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
    f"Hospital-wide performance · "
    f"<b>{last_start.date()}</b> to <b>{complete_through.date()}</b> "
    f"vs. previous 12 months"
    f'</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="page-note">'
    f"Month {anchor.strftime('%b %Y')} is in progress and excluded from trends."
    f'</div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# KPI row 1
# ---------------------------------------------------------------------------
admissions_delta = pct_change(len(adm_recent), len(adm_prev))
revenue_recent = bill_recent["amount"].sum()
revenue_prev = bill_prev["amount"].sum()
revenue_delta = pct_change(revenue_recent, revenue_prev)
los_recent = adm_recent["length_of_stay"].mean()
los_prev = adm_prev["length_of_stay"].mean()
los_delta = pct_change(los_recent, los_prev)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Patients", f"{len(patients):,}")
c2.metric("Admissions (12mo)", f"{len(adm_recent):,}",
          delta=fmt_delta(admissions_delta))
c3.metric("Revenue (12mo)", f"₹{revenue_recent / 1e7:.1f} Cr",
          delta=fmt_delta(revenue_delta))
c4.metric("Avg Length of Stay", f"{los_recent:.1f} days",
          delta=fmt_delta(los_delta), delta_color="inverse")


# ---------------------------------------------------------------------------
# KPI row 2
# ---------------------------------------------------------------------------
icu_with_dates = icu.merge(
    admissions[["admission_id", "admission_date"]],
    on="admission_id", how="left",
)
icu_recent = icu_with_dates[icu_with_dates["admission_date"] > last_start]
icu_prev = icu_with_dates[
    (icu_with_dates["admission_date"] > prev_start)
    & (icu_with_dates["admission_date"] <= last_start)
]

er_with_dates = emergency.merge(
    admissions[["admission_id", "admission_date"]],
    on="admission_id", how="left",
)
er_recent = er_with_dates[er_with_dates["admission_date"] > last_start]
er_prev = er_with_dates[
    (er_with_dates["admission_date"] > prev_start)
    & (er_with_dates["admission_date"] <= last_start)
]

readmit_recent = adm_recent["is_readmission"].mean() * 100
readmit_prev = adm_prev["is_readmission"].mean() * 100
readmit_delta = pct_change(readmit_recent, readmit_prev)

c1, c2, c3, c4 = st.columns(4)
c1.metric("ICU Stays (12mo)", f"{len(icu_recent):,}",
          delta=fmt_delta(pct_change(len(icu_recent), len(icu_prev))))
c2.metric("ER Visits (12mo)", f"{len(er_recent):,}",
          delta=fmt_delta(pct_change(len(er_recent), len(er_prev))))
c3.metric("Readmission Rate", f"{readmit_recent:.2f}%",
          delta=fmt_delta(readmit_delta), delta_color="inverse")
c4.metric("Departments", f"{len(departments)}")


# ---------------------------------------------------------------------------
# Chart 1 — Monthly trend (excludes partial current month)
# ---------------------------------------------------------------------------
st.markdown('<div class="section-label">Monthly Trend · Last 24 Complete Months</div>',
            unsafe_allow_html=True)

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
monthly = (
    monthly_adm.merge(monthly_rev, on="admission_ym")
    .sort_values("admission_ym")
)

fig1 = go.Figure()
fig1.add_trace(go.Bar(
    x=monthly["admission_ym"],
    y=monthly["admissions"],
    name="Admissions",
    marker=dict(color="rgba(0, 212, 255, 0.55)"),
    yaxis="y",
    hovertemplate="<b>%{x}</b><br>Admissions: %{y:,}<extra></extra>",
))
fig1.add_trace(go.Scatter(
    x=monthly["admission_ym"],
    y=monthly["revenue"],
    name="Revenue (₹)",
    mode="lines+markers",
    line=dict(color=PURPLE, width=3),
    marker=dict(size=7, color=PURPLE),
    yaxis="y2",
    hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>",
))
fig1.update_layout(
    yaxis=dict(title="Admissions", side="left"),
    yaxis2=dict(title="Revenue (₹)", overlaying="y", side="right", showgrid=False),
    hovermode="x unified",
)
style_dark(fig1, height=440)
st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Chart 2 + 3 — Department bars + Outcome bars
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="section-label">Admissions by Department</div>',
                unsafe_allow_html=True)
    dept_counts = (
        adm_recent.groupby("department").size()
        .reset_index(name="count")
        .sort_values("count", ascending=True)   # ascending for horizontal bar
    )
    fig2 = px.bar(
        dept_counts,
        x="count", y="department",
        orientation="h",
        color="count",
        color_continuous_scale=[[0, "#122a45"], [1, CYAN]],
        text="count",
    )
    fig2.update_traces(
        textposition="outside",
        textfont=dict(color=TEXT, size=11),
        hovertemplate="<b>%{y}</b><br>%{x:,} admissions<extra></extra>",
    )
    style_dark(fig2, height=460)
    fig2.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_title=None, yaxis_title=None,
        margin=dict(l=20, r=60, t=60, b=30),
    )
    st.plotly_chart(fig2, use_container_width=True,
                    config={"displayModeBar": False})

with c2:
    st.markdown('<div class="section-label">Outcomes · Last 12 Months</div>',
                unsafe_allow_html=True)
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
        textfont=dict(color="#0a0e1a", size=12, family="Inter"),
        hovertemplate="<b>%{y}</b><br>%{x:,} admissions<extra></extra>",
    )
    style_dark(fig3, height=460)
    fig3.update_layout(
        showlegend=False,
        xaxis_title=None, yaxis_title=None,
        margin=dict(l=20, r=20, t=60, b=30),
    )
    st.plotly_chart(fig3, use_container_width=True,
                    config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Chart 4 + 5 — Day of week + Season
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="section-label">Admissions by Day of Week</div>',
                unsafe_allow_html=True)
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
        color_continuous_scale=[[0, "#122a45"], [1, CYAN]],
        text="count",
    )
    fig4.update_traces(
        textposition="outside",
        textfont=dict(color=TEXT, size=11),
        hovertemplate="<b>%{x}</b><br>%{y:,} admissions<extra></extra>",
    )
    style_dark(fig4, height=360)
    fig4.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_title=None, yaxis_title=None,
    )
    st.plotly_chart(fig4, use_container_width=True,
                    config={"displayModeBar": False})

with c2:
    st.markdown('<div class="section-label">Seasonal Distribution</div>',
                unsafe_allow_html=True)
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
        textfont=dict(color=TEXT, size=11),
        hovertemplate="<b>%{x}</b><br>%{y:,} admissions<extra></extra>",
    )
    style_dark(fig5, height=360)
    fig5.update_layout(
        showlegend=False,
        xaxis_title=None, yaxis_title=None,
    )
    st.plotly_chart(fig5, use_container_width=True,
                    config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "Executive Overview · Built by **Shahan Malik** · "
    "Streamlit · SQLite · Plotly · Pandas · 2026"
)
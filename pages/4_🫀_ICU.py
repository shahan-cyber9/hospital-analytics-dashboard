"""
pages/4_🫀_ICU.py
-----------------
ICU Dashboard: occupancy gauges, ventilator utilisation, oxygen demand,
length-of-stay distribution, and department-level ICU load.

Uses Plotly's go.Indicator for gauge charts.
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
    page_title="ICU · Smart Hospital",
    page_icon="🫀",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Theme
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

# Assumed ICU capacity for occupancy calculations.
TOTAL_ICU_BEDS = 30


# ---------------------------------------------------------------------------
# Chart helpers
# ---------------------------------------------------------------------------
def style_dark(fig: go.Figure, height: int = 400) -> go.Figure:
    """Apply dark theme to any Plotly figure (axes, legends, hover)."""
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


def make_gauge(
    value: float,
    title: str,
    suffix: str = "%",
    max_val: int = 100,
    thresholds: tuple = (60, 80, 90),
    primary_color: str = CYAN,
) -> go.Figure:
    """
    Build a semicircular gauge with colour-coded safety bands.

    thresholds = (green_max, cyan_max, amber_max) — anything above amber_max
    is rendered in the danger band.
    """
    green_max, cyan_max, amber_max = thresholds

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={
                "suffix": suffix,
                "font": {
                    "color": primary_color,
                    "size": 44,
                    "family": "JetBrains Mono, monospace",
                },
            },
            title={
                "text": f"<span style='font-size:13px; color:{TEXT_DIM}; "
                        f"letter-spacing:0.08em;'>{title.upper()}</span>",
                "font": {"family": "Inter, sans-serif"},
            },
            gauge={
                "axis": {
                    "range": [0, max_val],
                    "tickcolor": TEXT_DIM,
                    "tickfont": {"color": TEXT_DIM, "size": 10},
                    "tickwidth": 1,
                    "nticks": 6,
                },
                "bar": {"color": primary_color, "thickness": 0.28},
                "bgcolor": "rgba(255,255,255,0.03)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, green_max], "color": "rgba(34, 197, 94, 0.18)"},
                    {"range": [green_max, cyan_max], "color": "rgba(0, 212, 255, 0.18)"},
                    {"range": [cyan_max, amber_max], "color": "rgba(245, 158, 11, 0.20)"},
                    {"range": [amber_max, max_val], "color": "rgba(239, 68, 68, 0.20)"},
                ],
                "threshold": {
                    "line": {"color": RED, "width": 3},
                    "thickness": 0.8,
                    "value": amber_max,
                },
            },
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": TEXT, "family": "Inter, sans-serif"},
        height=290,
        margin=dict(l=30, r=30, t=60, b=10),
    )
    return fig


# ---------------------------------------------------------------------------
# Global CSS
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
            padding: 18px 20px;
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
@st.cache_data(ttl=600, show_spinner="Loading ICU data...")
def get_data() -> dict:
    return load_all()


@st.cache_data(ttl=600, show_spinner="Computing ICU census...")
def compute_icu_census(icu_df: pd.DataFrame) -> pd.Series:
    """Compute daily ICU census by expanding each stay into one row per day."""
    all_days: list = []
    for start, days in zip(icu_df["icu_admit_date"], icu_df["icu_days"]):
        all_days.extend(
            pd.date_range(start=start, periods=int(days), freq="D")
        )
    census = pd.Series(all_days).value_counts().sort_index()
    return census


data = get_data()
patients = data["patients"]
doctors = data["doctors"]
departments = data["departments"]
admissions = data["admissions"]
icu = data["icu"]


icu_full = icu.merge(
    admissions[["admission_id", "department", "outcome", "diagnosis"]],
    on="admission_id",
    how="left",
)


# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.markdown('<div class="page-title">ICU Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-sub">'
    "Intensive care load and resource utilisation. Occupancy is derived from "
    "individual ICU stays and compared against an assumed capacity of "
    f"{TOTAL_ICU_BEDS} beds."
    "</div>",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Derived metrics
# ---------------------------------------------------------------------------
census = compute_icu_census(icu)

total_icu_stays = len(icu)
avg_icu_days = icu["icu_days"].mean()
avg_census = census.mean()
peak_census = int(census.max())
avg_occupancy = (avg_census / TOTAL_ICU_BEDS) * 100
peak_occupancy = (peak_census / TOTAL_ICU_BEDS) * 100
vent_share = icu["ventilator_used"].mean() * 100
oxy_share = icu["oxygen_required"].mean() * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total ICU Stays", f"{total_icu_stays:,}")
c2.metric("Avg Length of Stay", f"{avg_icu_days:.1f} days")
c3.metric("Avg Occupancy", f"{avg_occupancy:.0f}%")
c4.metric("Peak Occupancy", f"{peak_occupancy:.0f}%")


# ---------------------------------------------------------------------------
# Gauges
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="section-label">Critical Care Utilisation</div>',
    unsafe_allow_html=True,
)

g1, g2, g3 = st.columns(3)

with g1:
    fig_occ = make_gauge(
        value=min(avg_occupancy, 100),
        title="ICU Occupancy",
        suffix="%",
        max_val=100,
        thresholds=(60, 80, 90),
        primary_color=CYAN,
    )
    st.plotly_chart(fig_occ, use_container_width=True,
                    config={"displayModeBar": False})

with g2:
    fig_vent = make_gauge(
        value=vent_share,
        title="Ventilator Use",
        suffix="%",
        max_val=100,
        thresholds=(30, 50, 70),
        primary_color=PURPLE,
    )
    st.plotly_chart(fig_vent, use_container_width=True,
                    config={"displayModeBar": False})

with g3:
    fig_oxy = make_gauge(
        value=oxy_share,
        title="Oxygen Support",
        suffix="%",
        max_val=100,
        thresholds=(50, 75, 90),
        primary_color=SKY,
    )
    st.plotly_chart(fig_oxy, use_container_width=True,
                    config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# LOS distribution + Monthly trend
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.markdown(
        '<div class="section-label">ICU Length of Stay Distribution</div>',
        unsafe_allow_html=True,
    )
    median_los = icu["icu_days"].median()
    fig_los = px.histogram(
        icu,
        x="icu_days",
        nbins=20,
        color_discrete_sequence=[CYAN],
    )
    fig_los.update_traces(
        marker=dict(line=dict(color=CYAN_BRIGHT, width=0.5)),
        opacity=0.85,
        hovertemplate="<b>%{x} days</b><br>%{y} stays<extra></extra>",
    )
    fig_los.add_vline(
        x=median_los,
        line=dict(color=AMBER, width=2, dash="dash"),
        annotation_text=f"Median {median_los:.0f}d",
        annotation_position="top right",
        annotation_font=dict(color=AMBER, size=11),
    )
    style_dark(fig_los, height=400)
    fig_los.update_layout(
        xaxis_title="ICU days",
        yaxis_title="Number of stays",
        bargap=0.05,
    )
    st.plotly_chart(fig_los, use_container_width=True,
                    config={"displayModeBar": False})

with c2:
    st.markdown(
        '<div class="section-label">Monthly ICU Admissions · Complete Months</div>',
        unsafe_allow_html=True,
    )
    anchor = icu["icu_admit_date"].max()
    current_month_start = anchor.replace(day=1)

    icu_trend = icu[icu["icu_admit_date"] < current_month_start].copy()
    icu_trend["ym"] = icu_trend["icu_admit_date"].dt.strftime("%Y-%m")
    monthly = icu_trend.groupby("ym").size().reset_index(name="stays")
    monthly = monthly.sort_values("ym")

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=monthly["ym"],
        y=monthly["stays"],
        mode="lines+markers",
        line=dict(color=CYAN, width=3, shape="spline", smoothing=0.5),
        marker=dict(size=7, color=CYAN, line=dict(color="#0a0e1a", width=2)),
        fill="tozeroy",
        fillcolor="rgba(0, 212, 255, 0.10)",
        hovertemplate="<b>%{x}</b><br>%{y} ICU stays<extra></extra>",
    ))
    style_dark(fig_trend, height=400)
    fig_trend.update_layout(
        showlegend=False,
        xaxis_title=None,
        yaxis_title="ICU stays",
    )
    st.plotly_chart(fig_trend, use_container_width=True,
                    config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Department + Outcomes
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.markdown(
        '<div class="section-label">ICU Load by Department</div>',
        unsafe_allow_html=True,
    )
    dept_icu = (
        icu_full.groupby("department", observed=True)
        .agg(
            stays=("icu_id", "count"),
            avg_days=("icu_days", "mean"),
            vent=("ventilator_used", "sum"),
        )
        .reset_index()
        .sort_values("stays", ascending=True)
    )
    fig_dept = px.bar(
        dept_icu,
        x="stays", y="department",
        orientation="h",
        color="stays",
        color_continuous_scale=[
            [0.0, "#0e2a4a"],
            [0.5, CYAN_DEEP],
            [1.0, CYAN],
        ],
        text="stays",
    )
    fig_dept.update_traces(
        textposition="outside",
        textfont=dict(color=TEXT, size=11, family="JetBrains Mono"),
        marker=dict(cornerradius=5, line=dict(width=0)),
        hovertemplate="<b>%{y}</b><br>%{x} ICU stays<extra></extra>",
    )
    style_dark(fig_dept, height=460)
    fig_dept.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_title=None, yaxis_title=None,
        margin=dict(l=30, r=70, t=50, b=30),
    )
    st.plotly_chart(fig_dept, use_container_width=True,
                    config={"displayModeBar": False})

with c2:
    st.markdown(
        '<div class="section-label">Outcome Mix · ICU vs Non-ICU (100% Stack)</div>',
        unsafe_allow_html=True,
    )
    icu_ids = set(icu["admission_id"])
    adm_tagged = admissions.copy()
    adm_tagged["had_icu"] = adm_tagged["admission_id"].isin(icu_ids)
    adm_tagged["cohort"] = adm_tagged["had_icu"].map(
        {True: "ICU", False: "Non-ICU"}
    )

    outcome_mix = (
        adm_tagged.groupby(["cohort", "outcome"], observed=True)
        .size()
        .reset_index(name="count")
    )

    # Manual percentage normalization (Plotly 7 removed `barnorm`).
    totals = outcome_mix.groupby("cohort")["count"].transform("sum")
    outcome_mix["share"] = outcome_mix["count"] / totals

    outcome_order = ["Recovered", "Discharged", "Transferred", "Deceased"]
    outcome_mix["outcome"] = pd.Categorical(
        outcome_mix["outcome"], categories=outcome_order, ordered=True
    )
    outcome_mix = outcome_mix.sort_values(["cohort", "outcome"])

    fig_out = px.bar(
        outcome_mix,
        x="cohort", y="share",
        color="outcome",
        barmode="stack",
        category_orders={
            "cohort": ["ICU", "Non-ICU"],
            "outcome": outcome_order,
        },
        color_discrete_map={
            "Recovered": CYAN,
            "Discharged": GREEN,
            "Transferred": AMBER,
            "Deceased": RED,
        },
        custom_data=["count"],
    )
    fig_out.update_traces(
        marker=dict(line=dict(width=0)),
        hovertemplate=(
            "<b>%{x}</b><br>%{fullData.name}: "
            "%{y:.1%} (%{customdata[0]:,} admissions)<extra></extra>"
        ),
    )
    style_dark(fig_out, height=460)
    fig_out.update_layout(
        xaxis_title=None,
        yaxis=dict(
            title=dict(text="Share of admissions",
                       font=dict(color=TEXT_DIM, size=12)),
            tickformat=".0%",
            range=[0, 1],
        ),
        margin=dict(l=30, r=30, t=60, b=40),
    )
    st.plotly_chart(fig_out, use_container_width=True,
                    config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Operational summary
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="section-label">Operational Summary</div>',
    unsafe_allow_html=True,
)

avg_stay_vent = icu[icu["ventilator_used"]]["icu_days"].mean()
avg_stay_no_vent = icu[~icu["ventilator_used"]]["icu_days"].mean()

c1, c2, c3, c4 = st.columns(4)
c1.metric(
    label="On Ventilator",
    value=f"{int(icu['ventilator_used'].sum()):,} stays",
    delta=f"avg {avg_stay_vent:.1f} days",
    delta_color="off",
)
c2.metric(
    label="No Ventilator",
    value=f"{int((~icu['ventilator_used']).sum()):,} stays",
    delta=f"avg {avg_stay_no_vent:.1f} days",
    delta_color="off",
)
c3.metric(
    label="On Oxygen",
    value=f"{int(icu['oxygen_required'].sum()):,} stays",
    delta=f"{oxy_share:.0f}% of ICU",
    delta_color="off",
)
c4.metric(
    label="Peak Census",
    value=f"{peak_census} patients",
    delta=f"capacity {TOTAL_ICU_BEDS} beds",
    delta_color="off",
)


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "ICU Dashboard · Built by Shahan Malik · "
    "Streamlit · SQLite · Plotly · Pandas · 2026"
)
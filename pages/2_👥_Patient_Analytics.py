"""
pages/2_👥_Patient_Analytics.py
-------------------------------
Patient Analytics: age, gender, diagnosis, department, and readmission.

Focuses on the "who" behind hospital operations: patient demographics,
disease patterns, and where patients come from.
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
    page_title="Patient Analytics · Smart Hospital",
    page_icon="👥",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------
CYAN = "#00d4ff"
CYAN_DEEP = "#0891b2"
PURPLE = "#7b2ff7"
PINK = "#ec4899"
BLUE = "#2563eb"
GREEN = "#22c55e"
AMBER = "#f59e0b"
RED = "#ef4444"
TEXT = "#c9d7ee"
TEXT_DIM = "#A0AAB8"
TEXT_FAINT = "#6b7f9e"

GENDER_COLORS = {"Female": CYAN, "Male": PINK}


# ---------------------------------------------------------------------------
# Chart helpers
# ---------------------------------------------------------------------------
def style_dark(fig: go.Figure, height: int = 400) -> go.Figure:
    """Apply dark theme with refined spacing and typography."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color=TEXT,
            family="Inter, -apple-system, sans-serif",
            size=12.5,
        ),
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
            color: #c9d7ee;
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
@st.cache_data(ttl=600, show_spinner="Loading patient data...")
def get_data() -> dict:
    return load_all()


data = get_data()
patients = data["patients"]
doctors = data["doctors"]
departments = data["departments"]
admissions = data["admissions"]


# ---------------------------------------------------------------------------
# Merge patient demographics into admissions
# ---------------------------------------------------------------------------
admissions_enriched = admissions.merge(
    patients[["patient_id", "age_group", "gender", "city"]].rename(
        columns={
            "age_group": "patient_age_group",
            "gender": "patient_gender",
            "city": "patient_city",
        }
    ),
    on="patient_id",
    how="left",
)


# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.markdown('<div class="page-title">Patient Analytics</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-sub">'
    "A demographic and clinical profile of the patient population, from "
    "age and gender distribution to disease frequency, department mix, "
    "and readmission behaviour."
    "</div>",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
female_share = (patients["gender"] == "Female").mean() * 100
avg_age = patients["age"].mean()
readmit_rate = admissions["is_readmission"].mean() * 100
unique_diagnoses = admissions["diagnosis"].nunique()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Patients", f"{len(patients):,}")
c2.metric("Average Age", f"{avg_age:.1f} years")
c3.metric("Female Share", f"{female_share:.1f}%")
c4.metric("Unique Diagnoses", f"{unique_diagnoses}")


# ---------------------------------------------------------------------------
# Age distribution + Gender split
# ---------------------------------------------------------------------------
c1, c2 = st.columns([2, 1])

with c1:
    st.markdown(
        '<div class="section-label">Age Distribution by Gender</div>',
        unsafe_allow_html=True,
    )
    fig_age = px.histogram(
        patients,
        x="age",
        color="gender",
        nbins=25,
        barmode="overlay",
        color_discrete_map=GENDER_COLORS,
        opacity=0.45,
    )
    # Add a soft outline to each layer so the shape stays visible
    # even where distributions overlap heavily.
    fig_age.update_traces(
        marker=dict(line=dict(width=1.2)),
        hovertemplate="<b>Age %{x}</b><br>%{fullData.name}: %{y}<extra></extra>",
    )
    style_dark(fig_age, height=400)
    fig_age.update_layout(
        xaxis_title="Age (years)",
        yaxis_title="Number of Patients",
        bargap=0.05,
    )
    st.plotly_chart(fig_age, use_container_width=True,
                    config={"displayModeBar": False})

with c2:
    st.markdown(
        '<div class="section-label">Gender Split</div>',
        unsafe_allow_html=True,
    )
    gender_counts = (
        patients.groupby("gender", observed=True).size()
        .reset_index(name="count")
    )
    fig_gender = px.pie(
        gender_counts,
        names="gender",
        values="count",
        hole=0.55,
        color="gender",
        color_discrete_map=GENDER_COLORS,
    )
    fig_gender.update_traces(
        textposition="outside",
        textinfo="label+percent",
        textfont=dict(color=TEXT, size=13),
        hovertemplate="<b>%{label}</b><br>%{value:,} patients<br>%{percent}<extra></extra>",
    )
    style_dark(fig_gender, height=400)
    fig_gender.update_layout(
        showlegend=False,
        margin=dict(l=80, r=80, t=40, b=40),
    )
    st.plotly_chart(fig_gender, use_container_width=True,
                    config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Top diagnoses
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="section-label">Top 15 Diagnoses by Admission Volume</div>',
    unsafe_allow_html=True,
)

top_diag = (
    admissions.groupby("diagnosis").size()
    .reset_index(name="count")
    .nlargest(15, "count")
    .sort_values("count", ascending=True)
)

fig_diag = px.bar(
    top_diag,
    x="count", y="diagnosis",
    orientation="h",
    color="count",
    color_continuous_scale=[
        [0.0, "#0e2a4a"],
        [0.3, "#0e5a7f"],
        [0.6, CYAN_DEEP],
        [1.0, CYAN],
    ],
    text="count",
)
fig_diag.update_traces(
    textposition="outside",
    textfont=dict(color=TEXT, size=11, family="JetBrains Mono"),
    marker=dict(cornerradius=5, line=dict(width=0)),
    hovertemplate="<b>%{y}</b><br>%{x:,} admissions<extra></extra>",
)
style_dark(fig_diag, height=520)
fig_diag.update_layout(
    showlegend=False,
    coloraxis_showscale=False,
    xaxis_title=None, yaxis_title=None,
    margin=dict(l=30, r=90, t=50, b=30),
)
st.plotly_chart(fig_diag, use_container_width=True,
                config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Department x Age heatmap
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="section-label">Department Mix Across Age Groups</div>',
    unsafe_allow_html=True,
)

heat_data = (
    admissions_enriched
    .groupby(["department", "patient_age_group"], observed=True)
    .size()
    .unstack(fill_value=0)
)

# Sort rows by total admissions (busiest first).
heat_data = heat_data.loc[
    heat_data.sum(axis=1).sort_values(ascending=False).index
]

# Natural age order for columns.
age_order = ["0-17", "18-29", "30-44", "45-59", "60-74", "75+"]
heat_data = heat_data.reindex(
    columns=[c for c in age_order if c in heat_data.columns]
)

# Blank text in cells with zero admissions to reduce visual noise.
text_vals = [
    [f"{int(v)}" if v > 0 else "" for v in row]
    for row in heat_data.values
]

fig_heat = px.imshow(
    heat_data,
    aspect="auto",
    color_continuous_scale=[
        [0.0, "#0a0e1a"],
        [0.4, "#0e3a5f"],
        [0.7, CYAN_DEEP],
        [1.0, CYAN],
    ],
)
fig_heat.update_traces(
    text=text_vals,
    texttemplate="%{text}",
    hovertemplate="<b>%{y}</b><br>Age %{x}<br>%{z:,} admissions<extra></extra>",
    textfont=dict(size=11, family="JetBrains Mono", color=TEXT),
)
style_dark(fig_heat, height=520)
fig_heat.update_layout(
    xaxis_title=None, yaxis_title=None,
    coloraxis_colorbar=dict(
        title=dict(text="Admissions", font=dict(color=TEXT_DIM)),
        tickfont=dict(color=TEXT_DIM),
        outlinewidth=0,
    ),
    margin=dict(l=30, r=30, t=40, b=30),
)
st.plotly_chart(fig_heat, use_container_width=True,
                config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Readmission by department + Geographic
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.markdown(
        '<div class="section-label">Readmission Rate by Department</div>',
        unsafe_allow_html=True,
    )
    readmit = (
        admissions.groupby("department", observed=True)
        .agg(
            admissions=("admission_id", "count"),
            readmits=("is_readmission", "sum"),
        )
        .reset_index()
    )
    readmit["rate"] = readmit["readmits"] / readmit["admissions"] * 100
    readmit = readmit.sort_values("rate", ascending=True)

    fig_readmit = px.bar(
        readmit,
        x="rate", y="department",
        orientation="h",
        color="rate",
        color_continuous_scale=[
            [0.0, "#0e2a4a"],
            [0.5, AMBER],
            [1.0, RED],
        ],
        text="rate",
    )
    fig_readmit.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside",
        textfont=dict(color=TEXT, size=10.5, family="JetBrains Mono"),
        marker=dict(cornerradius=5, line=dict(width=0)),
        hovertemplate="<b>%{y}</b><br>Readmission rate: %{x:.2f}%<extra></extra>",
    )
    overall = admissions["is_readmission"].mean() * 100
    fig_readmit.add_vline(
        x=overall,
        line=dict(color=CYAN, width=1.5, dash="dash"),
        annotation_text=f"Hospital avg {overall:.1f}%",
        annotation_position="bottom right",
        annotation_font=dict(color=CYAN, size=11),
    )
    style_dark(fig_readmit, height=480)
    fig_readmit.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_title="Readmission rate (%)",
        yaxis_title=None,
        margin=dict(l=30, r=90, t=50, b=60),
    )
    st.plotly_chart(fig_readmit, use_container_width=True,
                    config={"displayModeBar": False})

with c2:
    st.markdown(
        '<div class="section-label">Patients by City</div>',
        unsafe_allow_html=True,
    )
    city_counts = (
        patients.groupby("city", observed=True).size()
        .reset_index(name="count")
        .sort_values("count", ascending=True)
    )
    fig_city = px.bar(
        city_counts,
        x="count", y="city",
        orientation="h",
        color="count",
        color_continuous_scale=[
            [0.0, "#1a1240"],
            [0.5, PURPLE],
            [1.0, "#a855f7"],
        ],
        text="count",
    )
    fig_city.update_traces(
        textposition="outside",
        textfont=dict(color=TEXT, size=11, family="JetBrains Mono"),
        marker=dict(cornerradius=5, line=dict(width=0)),
        hovertemplate="<b>%{y}</b><br>%{x:,} patients<extra></extra>",
    )
    style_dark(fig_city, height=480)
    fig_city.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_title=None, yaxis_title=None,
        margin=dict(l=30, r=90, t=50, b=30),
    )
    st.plotly_chart(fig_city, use_container_width=True,
                    config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "Patient Analytics · Built by Shahan Malik · "
    "Streamlit · SQLite · Plotly · Pandas · 2026"
)
"""
pages/6_👨‍⚕️_Doctors.py
----------------------
Doctor Performance: workload, department comparison, experience analysis,
and consultation economics.
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
    page_title="Doctors · Smart Hospital",
    page_icon="👨‍⚕️",
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


def short_dept(name: str) -> str:
    """Abbreviate long department names for tight KPI captions."""
    mapping = {
        "General Medicine": "Gen. Medicine",
    }
    return mapping.get(name, name)


def short_doctor(name: str) -> str:
    """Use only the surname — KPI card values need to stay compact."""
    if not isinstance(name, str):
        return str(name)
    parts = name.replace("Dr. ", "").split()
    if len(parts) <= 1:
        return name
    return f"Dr. {parts[-1]}"


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
            font-size: clamp(1.1rem, 1.6vw, 1.9rem);
            letter-spacing: -0.02em;
            line-height: 1.2;
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
@st.cache_data(ttl=600, show_spinner="Loading doctor data...")
def get_data() -> dict:
    return load_all()


data = get_data()
doctors = data["doctors"]
departments = data["departments"]
admissions = data["admissions"]


adm_doc = admissions.merge(
    doctors[["doctor_id", "name", "department", "experience_years",
             "consultation_fee"]].rename(
        columns={
            "name": "doctor_name",
            "department": "doctor_department",
            "experience_years": "doctor_experience",
            "consultation_fee": "doctor_fee",
        }
    ),
    on="doctor_id",
    how="left",
)


# ---------------------------------------------------------------------------
# Per-doctor aggregates
# ---------------------------------------------------------------------------
doctor_stats = (
    adm_doc.groupby(
        ["doctor_id", "doctor_name", "doctor_department",
         "doctor_experience", "doctor_fee"],
        observed=True,
    )
    .agg(
        admissions=("admission_id", "count"),
        unique_patients=("patient_id", "nunique"),
        avg_los=("length_of_stay", "mean"),
        readmit_rate=("is_readmission", "mean"),
    )
    .reset_index()
)

doctor_stats["doctor_department"] = doctor_stats["doctor_department"].astype(str)


# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.markdown('<div class="page-title">Doctor Performance</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-sub">'
    "Workload distribution, department-level comparisons, and experience "
    "analysis across the medical staff. Identifies over-loaded doctors, "
    "under-utilised departments, and the relationship between seniority "
    "and patient volume."
    "</div>",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# KPI row — four distinct facts about the medical workforce.
# ---------------------------------------------------------------------------
total_doctors = len(doctors)
num_departments = doctors["department"].nunique()
avg_adm_per_doc = doctor_stats["admissions"].mean()
avg_experience = doctors["experience_years"].mean()
median_experience = doctors["experience_years"].median()
senior_share = (doctors["experience_years"] >= 15).mean() * 100

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Total Doctors", f"{total_doctors:,}")
    st.markdown(
        f'<div class="metric-sub">across {num_departments} departments</div>',
        unsafe_allow_html=True,
    )

with c2:
    st.metric("Avg Admissions/Doctor", f"{avg_adm_per_doc:.0f}")
    st.markdown(
        '<div class="metric-sub">per doctor over the 3-year period</div>',
        unsafe_allow_html=True,
    )

with c3:
    st.metric("Avg Experience", f"{avg_experience:.1f} yrs")
    st.markdown(
        f'<div class="metric-sub">median {median_experience:.0f} yrs '
        f'across the staff</div>',
        unsafe_allow_html=True,
    )

with c4:
    st.metric("Senior Share", f"{senior_share:.0f}%")
    st.markdown(
        '<div class="metric-sub">doctors with 15+ years experience</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Top 15 doctors by patient count
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="section-label">Top 15 Doctors by Patient Count</div>',
    unsafe_allow_html=True,
)

top_docs = (
    doctor_stats.nlargest(15, "unique_patients")
    .sort_values("unique_patients", ascending=True)
)

fig_top = px.bar(
    top_docs,
    x="unique_patients", y="doctor_name",
    orientation="h",
    color="doctor_department",
    color_discrete_map=DEPT_COLORS,
    text="unique_patients",
)
fig_top.update_traces(
    textposition="outside",
    textfont=dict(color=TEXT, size=11, family="JetBrains Mono"),
    marker=dict(cornerradius=5, line=dict(width=0)),
    hovertemplate=(
        "<b>%{y}</b><br>"
        "%{x} unique patients<br>"
        "Department: %{fullData.name}<extra></extra>"
    ),
)
style_dark(fig_top, height=520)

max_pat = top_docs["unique_patients"].max()
fig_top.update_layout(
    showlegend=False,
    xaxis=dict(
        title=dict(text="Unique patients treated",
                   font=dict(color=TEXT_DIM, size=12)),
        range=[0, max_pat * 1.15],
    ),
    yaxis_title=None,
    margin=dict(l=30, r=40, t=50, b=40),
)
st.plotly_chart(fig_top, use_container_width=True,
                config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Department workload + Bubble chart
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.markdown(
        '<div class="section-label">Department Workload · Admissions per Doctor</div>',
        unsafe_allow_html=True,
    )
    dept_work = (
        doctor_stats.groupby("doctor_department", observed=True)
        .agg(
            doctors=("doctor_id", "count"),
            total_admissions=("admissions", "sum"),
        )
        .reset_index()
    )
    dept_work["per_doctor"] = dept_work["total_admissions"] / dept_work["doctors"]
    dept_work = dept_work.sort_values("per_doctor", ascending=True)

    fig_work = px.bar(
        dept_work,
        x="per_doctor", y="doctor_department",
        orientation="h",
        color="per_doctor",
        color_continuous_scale=[
            [0.0, "#0e2a4a"],
            [0.5, CYAN_DEEP],
            [1.0, CYAN],
        ],
        text="per_doctor",
    )
    fig_work.update_traces(
        texttemplate="%{text:.0f}",
        textposition="outside",
        textfont=dict(color=TEXT, size=11, family="JetBrains Mono"),
        marker=dict(cornerradius=5, line=dict(width=0)),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "%{x:.0f} admissions per doctor<extra></extra>"
        ),
    )
    style_dark(fig_work, height=500)

    max_work = dept_work["per_doctor"].max()
    fig_work.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        xaxis=dict(
            title=dict(text="Admissions per doctor",
                       font=dict(color=TEXT_DIM, size=12)),
            range=[0, max_work * 1.18],
        ),
        yaxis_title=None,
        margin=dict(l=30, r=50, t=50, b=40),
    )
    st.plotly_chart(fig_work, use_container_width=True,
                    config={"displayModeBar": False})

with c2:
    st.markdown(
        '<div class="section-label">Experience vs Volume · Bubble Chart</div>',
        unsafe_allow_html=True,
    )
    fig_bubble = px.scatter(
        doctor_stats,
        x="doctor_experience",
        y="admissions",
        size="unique_patients",
        color="doctor_fee",
        color_continuous_scale=[
            [0.0, "#1a1240"],
            [0.4, PURPLE],
            [0.7, CYAN_DEEP],
            [1.0, CYAN],
        ],
        size_max=60,
        hover_name="doctor_name",
        custom_data=["doctor_department", "unique_patients"],
    )
    fig_bubble.update_traces(
        marker=dict(
            line=dict(color="rgba(255,255,255,0.35)", width=1),
            opacity=0.55,
        ),
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Department: %{customdata[0]}<br>"
            "Experience: %{x} yrs<br>"
            "Admissions: %{y}<br>"
            "Unique patients: %{customdata[1]}<br>"
            "Fee: ₹%{marker.color:,.0f}<extra></extra>"
        ),
    )
    style_dark(fig_bubble, height=500)
    fig_bubble.update_layout(
        xaxis=dict(
            title=dict(text="Years of experience",
                       font=dict(color=TEXT_DIM, size=12)),
            range=[-1, 33],
        ),
        yaxis=dict(
            title=dict(text="Total admissions handled",
                       font=dict(color=TEXT_DIM, size=12)),
        ),
        coloraxis_colorbar=dict(
            title=dict(text="Fee (₹)", font=dict(color=TEXT_DIM, size=11)),
            tickfont=dict(color=TEXT_DIM),
            outlinewidth=0,
            thickness=12,
        ),
        margin=dict(l=30, r=30, t=50, b=40),
    )
    st.plotly_chart(fig_bubble, use_container_width=True,
                    config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Heatmap: Department × Experience bucket
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="section-label">Department × Experience · Admissions Workload</div>',
    unsafe_allow_html=True,
)

exp_bins = [0, 6, 12, 18, 24, 100]
exp_labels = ["0-5 yrs", "6-11 yrs", "12-17 yrs", "18-23 yrs", "24+ yrs"]
doctor_stats["exp_bucket"] = pd.cut(
    doctor_stats["doctor_experience"],
    bins=exp_bins,
    labels=exp_labels,
    right=False,
)

heat_doc = (
    doctor_stats.groupby(
        ["doctor_department", "exp_bucket"], observed=True
    )["admissions"]
    .sum()
    .unstack(fill_value=0)
)
heat_doc = heat_doc.loc[
    heat_doc.sum(axis=1).sort_values(ascending=False).index
]
heat_doc = heat_doc.reindex(columns=exp_labels, fill_value=0)

fig_heat = px.imshow(
    heat_doc,
    aspect="auto",
    color_continuous_scale=[
        [0.0, "#0a0e1a"],
        [0.35, "#0e3a5f"],
        [0.7, CYAN_DEEP],
        [1.0, CYAN],
    ],
)
fig_heat.update_traces(
    hovertemplate=(
        "<b>%{y}</b><br>%{x}<br>%{z:,} admissions<extra></extra>"
    ),
)
style_dark(fig_heat, height=480)
fig_heat.update_layout(
    xaxis=dict(
        title=None,
        tickfont=dict(color=TEXT_DIM, size=11),
    ),
    yaxis=dict(
        title=None,
        tickfont=dict(color=TEXT_DIM, size=11.5),
    ),
    coloraxis_colorbar=dict(
        title=dict(text="Admissions", font=dict(color=TEXT_DIM, size=11)),
        tickfont=dict(color=TEXT_DIM),
        outlinewidth=0,
        thickness=12,
    ),
    margin=dict(l=30, r=30, t=40, b=40),
)
st.plotly_chart(fig_heat, use_container_width=True,
                config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Experience distribution + Consultation fee by department
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.markdown(
        '<div class="section-label">Experience Distribution · Departments with ≥5 Doctors</div>',
        unsafe_allow_html=True,
    )
    dept_counts = doctors.groupby("department", observed=True).size()
    valid_depts = dept_counts[dept_counts >= 5].index.tolist()

    docs_plot = doctors.copy()
    docs_plot["department"] = docs_plot["department"].astype(str)
    docs_plot = docs_plot[docs_plot["department"].isin(valid_depts)]

    fig_exp = px.box(
        docs_plot,
        x="experience_years",
        y="department",
        color="department",
        color_discrete_map=DEPT_COLORS,
        points="all",
        orientation="h",
    )
    fig_exp.update_traces(
        marker=dict(size=7, opacity=0.75,
                    line=dict(color=DARK, width=0.8)),
        line=dict(width=1.5),
        hovertemplate="<b>%{y}</b><br>%{x} years<extra></extra>",
    )
    style_dark(fig_exp, height=520)
    fig_exp.update_layout(
        showlegend=False,
        xaxis=dict(title=dict(text="Years of experience",
                              font=dict(color=TEXT_DIM, size=12))),
        yaxis_title=None,
        margin=dict(l=30, r=30, t=40, b=40),
    )
    st.plotly_chart(fig_exp, use_container_width=True,
                    config={"displayModeBar": False})

with c2:
    st.markdown(
        '<div class="section-label">Average Consultation Fee by Department</div>',
        unsafe_allow_html=True,
    )
    fee_dept = (
        doctors.groupby("department", observed=True)["consultation_fee"]
        .mean()
        .reset_index()
        .sort_values("consultation_fee", ascending=True)
    )
    fee_dept["department"] = fee_dept["department"].astype(str)
    fee_dept["label"] = fee_dept["consultation_fee"].apply(lambda v: f"₹{v:,.0f}")

    fig_fee = px.bar(
        fee_dept,
        x="consultation_fee", y="department",
        orientation="h",
        color="consultation_fee",
        color_continuous_scale=[
            [0.0, "#1a1240"],
            [0.5, PURPLE],
            [1.0, "#a855f7"],
        ],
        text="label",
    )
    fig_fee.update_traces(
        textposition="outside",
        textfont=dict(color=TEXT, size=11, family="JetBrains Mono"),
        marker=dict(cornerradius=5, line=dict(width=0)),
        hovertemplate="<b>%{y}</b><br>₹%{x:,.0f} average fee<extra></extra>",
    )
    style_dark(fig_fee, height=520)

    max_fee = fee_dept["consultation_fee"].max()
    fig_fee.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        xaxis=dict(
            title=dict(text="Average consultation fee (₹)",
                       font=dict(color=TEXT_DIM, size=12)),
            range=[0, max_fee * 1.25],
        ),
        yaxis_title=None,
        margin=dict(l=30, r=40, t=40, b=40),
    )
    st.plotly_chart(fig_fee, use_container_width=True,
                    config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Workforce summary — four distinct workforce insights.
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="section-label">Workforce Summary</div>',
    unsafe_allow_html=True,
)

busiest_doctor_row = doctor_stats.nlargest(1, "admissions").iloc[0]
busiest_dept_row = dept_work.iloc[-1]
quietest_dept_row = dept_work.iloc[0]
load_imbalance = (
    busiest_dept_row["per_doctor"] / quietest_dept_row["per_doctor"]
)

top_n = max(1, int(len(doctor_stats) * 0.10))
top_n_admissions = doctor_stats.nlargest(top_n, "admissions")["admissions"].sum()
total_admissions = doctor_stats["admissions"].sum()
top_share = top_n_admissions / total_admissions * 100

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        label="Busiest Doctor",
        value=short_doctor(busiest_doctor_row["doctor_name"]),
    )
    st.markdown(
        f'<div class="metric-sub">'
        f'{busiest_doctor_row["admissions"]:,} admissions · '
        f'{short_dept(busiest_doctor_row["doctor_department"])}'
        f'</div>',
        unsafe_allow_html=True,
    )

with c2:
    st.metric(
        label="Busiest Department",
        value=short_dept(busiest_dept_row["doctor_department"]),
    )
    st.markdown(
        f'<div class="metric-sub">'
        f'{busiest_dept_row["per_doctor"]:.0f} admissions per doctor'
        f'</div>',
        unsafe_allow_html=True,
    )

with c3:
    st.metric(
        label="Load Imbalance",
        value=f"{load_imbalance:.1f}×",
    )
    st.markdown(
        f'<div class="metric-sub">'
        f'{short_dept(busiest_dept_row["doctor_department"])} vs '
        f'{short_dept(quietest_dept_row["doctor_department"])}'
        f'</div>',
        unsafe_allow_html=True,
    )

with c4:
    st.metric(
        label="Top 10% Workload",
        value=f"{top_share:.1f}%",
    )
    st.markdown(
        f'<div class="metric-sub">'
        f'of admissions from {top_n} doctors'
        f'</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "Doctor Performance · Built by Shahan Malik · "
    "Streamlit · SQLite · Plotly · Pandas · 2026"
)
"""
pages/6_👨‍⚕️_Doctors.py
----------------------
Doctor Performance with cross-page filters.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.loader import load_all
from utils.filters import render_filters, apply_filters
from utils.theme import (
    apply_page_style, style_dark, section_label, page_header,
    CYAN, CYAN_DEEP, PURPLE, TEXT, TEXT_DIM, DARK, DEPT_COLORS,
)


st.set_page_config(
    page_title="Doctors · Smart Hospital",
    page_icon="👨‍⚕️",
    layout="wide",
)
apply_page_style()


def short_dept(name):
    return {"General Medicine": "Gen. Medicine"}.get(name, name)


def short_doctor(name):
    if not isinstance(name, str):
        return str(name)
    parts = name.replace("Dr. ", "").split()
    return name if len(parts) <= 1 else f"Dr. {parts[-1]}"


@st.cache_data(ttl=600, show_spinner="Loading doctor data...")
def get_data() -> dict:
    return load_all()


data = get_data()
doctors_raw = data["doctors"]
admissions_raw = data["admissions"]

filters = render_filters(data)

admissions = apply_filters(admissions_raw, filters)
doctors = doctors_raw.copy()
if filters["doctors"]:
    doctors = doctors[doctors["name"].isin(filters["doctors"])]


page_header(
    "Doctor Performance",
    "Workload distribution, department-level comparisons, and experience "
    "analysis across the medical staff. Identifies over-loaded doctors, "
    "under-utilised departments, and the relationship between seniority "
    "and patient volume."
)

if admissions.empty or doctors.empty:
    st.warning("No data matches the current filters. Adjust or reset the filters in the sidebar.")
    st.stop()


# Merge doctor info into filtered admissions.
adm_doc = admissions.merge(
    doctors[["doctor_id", "name", "department", "experience_years",
             "consultation_fee"]].rename(
        columns={"name": "doctor_name", "department": "doctor_department",
                 "experience_years": "doctor_experience",
                 "consultation_fee": "doctor_fee"}
    ),
    on="doctor_id", how="inner",
)

doctor_stats = (
    adm_doc.groupby(["doctor_id", "doctor_name", "doctor_department",
                     "doctor_experience", "doctor_fee"], observed=True)
    .agg(admissions=("admission_id", "count"),
         unique_patients=("patient_id", "nunique"),
         avg_los=("length_of_stay", "mean"),
         readmit_rate=("is_readmission", "mean"))
    .reset_index()
)
doctor_stats["doctor_department"] = doctor_stats["doctor_department"].astype(str)


# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
total_doctors = len(doctors)
num_departments = doctors["department"].nunique()
avg_adm_per_doc = doctor_stats["admissions"].mean()
avg_experience = doctors["experience_years"].mean()
median_experience = doctors["experience_years"].median()
senior_share = (doctors["experience_years"] >= 15).mean() * 100

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Doctors in View", f"{total_doctors:,}")
    st.markdown(f'<div class="metric-sub">across {num_departments} departments</div>',
                unsafe_allow_html=True)
with c2:
    st.metric("Avg Admissions/Doctor", f"{avg_adm_per_doc:.0f}")
    st.markdown('<div class="metric-sub">within the current filter scope</div>',
                unsafe_allow_html=True)
with c3:
    st.metric("Avg Experience", f"{avg_experience:.1f} yrs")
    st.markdown(f'<div class="metric-sub">median {median_experience:.0f} yrs</div>',
                unsafe_allow_html=True)
with c4:
    st.metric("Senior Share", f"{senior_share:.0f}%")
    st.markdown('<div class="metric-sub">doctors with 15+ years</div>',
                unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Top 15 doctors
# ---------------------------------------------------------------------------
section_label("Top 15 Doctors by Patient Count")
top_docs = (
    doctor_stats.nlargest(15, "unique_patients").sort_values("unique_patients", ascending=True)
)
fig_top = px.bar(
    top_docs, x="unique_patients", y="doctor_name", orientation="h",
    color="doctor_department", color_discrete_map=DEPT_COLORS, text="unique_patients",
)
fig_top.update_traces(
    textposition="outside",
    textfont=dict(color=TEXT, size=11, family="JetBrains Mono"),
    marker=dict(cornerradius=5, line=dict(width=0)),
    hovertemplate=("<b>%{y}</b><br>%{x} unique patients<br>"
                   "Department: %{fullData.name}<extra></extra>"),
)
style_dark(fig_top, height=520)
max_pat = top_docs["unique_patients"].max()
fig_top.update_layout(
    showlegend=False,
    xaxis=dict(title=dict(text="Unique patients treated",
                          font=dict(color=TEXT_DIM, size=12)),
               range=[0, max_pat * 1.15]),
    yaxis_title=None, margin=dict(l=30, r=40, t=50, b=40),
)
st.plotly_chart(fig_top, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Dept workload + Bubble
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    section_label("Department Workload · Admissions per Doctor")
    dept_work = (
        doctor_stats.groupby("doctor_department", observed=True)
        .agg(doctors=("doctor_id", "count"),
             total_admissions=("admissions", "sum"))
        .reset_index()
    )
    dept_work["per_doctor"] = dept_work["total_admissions"] / dept_work["doctors"]
    dept_work = dept_work.sort_values("per_doctor", ascending=True)

    fig_work = px.bar(
        dept_work, x="per_doctor", y="doctor_department", orientation="h",
        color="per_doctor",
        color_continuous_scale=[[0.0, "#0e2a4a"], [0.5, CYAN_DEEP], [1.0, CYAN]],
        text="per_doctor",
    )
    fig_work.update_traces(
        texttemplate="%{text:.0f}", textposition="outside",
        textfont=dict(color=TEXT, size=11, family="JetBrains Mono"),
        marker=dict(cornerradius=5, line=dict(width=0)),
        hovertemplate="<b>%{y}</b><br>%{x:.0f} admissions per doctor<extra></extra>",
    )
    style_dark(fig_work, height=500)
    max_work = dept_work["per_doctor"].max()
    fig_work.update_layout(
        showlegend=False, coloraxis_showscale=False,
        xaxis=dict(title=dict(text="Admissions per doctor",
                              font=dict(color=TEXT_DIM, size=12)),
                   range=[0, max_work * 1.18]),
        yaxis_title=None, margin=dict(l=30, r=50, t=50, b=40),
    )
    st.plotly_chart(fig_work, use_container_width=True, config={"displayModeBar": False})

with c2:
    section_label("Experience vs Volume · Bubble Chart")
    fig_bubble = px.scatter(
        doctor_stats, x="doctor_experience", y="admissions",
        size="unique_patients", color="doctor_fee",
        color_continuous_scale=[
            [0.0, "#1a1240"], [0.4, PURPLE], [0.7, CYAN_DEEP], [1.0, CYAN],
        ],
        size_max=60, hover_name="doctor_name",
        custom_data=["doctor_department", "unique_patients"],
    )
    fig_bubble.update_traces(
        marker=dict(line=dict(color="rgba(255,255,255,0.35)", width=1), opacity=0.55),
        hovertemplate=("<b>%{hovertext}</b><br>Department: %{customdata[0]}<br>"
                       "Experience: %{x} yrs<br>Admissions: %{y}<br>"
                       "Unique patients: %{customdata[1]}<br>"
                       "Fee: ₹%{marker.color:,.0f}<extra></extra>"),
    )
    style_dark(fig_bubble, height=500)
    fig_bubble.update_layout(
        xaxis=dict(title=dict(text="Years of experience",
                              font=dict(color=TEXT_DIM, size=12)), range=[-1, 33]),
        yaxis=dict(title=dict(text="Total admissions handled",
                              font=dict(color=TEXT_DIM, size=12))),
        coloraxis_colorbar=dict(
            title=dict(text="Fee (₹)", font=dict(color=TEXT_DIM, size=11)),
            tickfont=dict(color=TEXT_DIM), outlinewidth=0, thickness=12,
        ),
        margin=dict(l=30, r=30, t=50, b=40),
    )
    st.plotly_chart(fig_bubble, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Heatmap
# ---------------------------------------------------------------------------
section_label("Department × Experience · Admissions Workload")
exp_bins = [0, 6, 12, 18, 24, 100]
exp_labels = ["0-5 yrs", "6-11 yrs", "12-17 yrs", "18-23 yrs", "24+ yrs"]
doctor_stats["exp_bucket"] = pd.cut(
    doctor_stats["doctor_experience"], bins=exp_bins, labels=exp_labels, right=False,
)
heat_doc = (
    doctor_stats.groupby(["doctor_department", "exp_bucket"], observed=True)["admissions"]
    .sum().unstack(fill_value=0)
)
heat_doc = heat_doc.loc[heat_doc.sum(axis=1).sort_values(ascending=False).index]
heat_doc = heat_doc.reindex(columns=exp_labels, fill_value=0)

fig_heat = px.imshow(
    heat_doc, aspect="auto",
    color_continuous_scale=[
        [0.0, "#0a0e1a"], [0.35, "#0e3a5f"], [0.7, CYAN_DEEP], [1.0, CYAN],
    ],
)
fig_heat.update_traces(
    hovertemplate="<b>%{y}</b><br>%{x}<br>%{z:,} admissions<extra></extra>",
)
style_dark(fig_heat, height=480)
fig_heat.update_layout(
    xaxis=dict(title=None, tickfont=dict(color=TEXT_DIM, size=11)),
    yaxis=dict(title=None, tickfont=dict(color=TEXT_DIM, size=11.5)),
    coloraxis_colorbar=dict(
        title=dict(text="Admissions", font=dict(color=TEXT_DIM, size=11)),
        tickfont=dict(color=TEXT_DIM), outlinewidth=0, thickness=12,
    ),
    margin=dict(l=30, r=30, t=40, b=40),
)
st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Experience dist + Fee
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    section_label("Experience Distribution · Departments with ≥3 Doctors")
    dept_counts = doctors.groupby("department", observed=True).size()
    valid_depts = dept_counts[dept_counts >= 3].index.tolist()
    docs_plot = doctors.copy()
    docs_plot["department"] = docs_plot["department"].astype(str)
    docs_plot = docs_plot[docs_plot["department"].isin(valid_depts)]

    fig_exp = px.box(
        docs_plot, x="experience_years", y="department", color="department",
        color_discrete_map=DEPT_COLORS, points="all", orientation="h",
    )
    fig_exp.update_traces(
        marker=dict(size=7, opacity=0.75, line=dict(color=DARK, width=0.8)),
        line=dict(width=1.5),
        hovertemplate="<b>%{y}</b><br>%{x} years<extra></extra>",
    )
    style_dark(fig_exp, height=520)
    fig_exp.update_layout(
        showlegend=False,
        xaxis=dict(title=dict(text="Years of experience",
                              font=dict(color=TEXT_DIM, size=12))),
        yaxis_title=None, margin=dict(l=30, r=30, t=40, b=40),
    )
    st.plotly_chart(fig_exp, use_container_width=True, config={"displayModeBar": False})

with c2:
    section_label("Average Consultation Fee by Department")
    fee_dept = (
        doctors.groupby("department", observed=True)["consultation_fee"].mean()
        .reset_index().sort_values("consultation_fee", ascending=True)
    )
    fee_dept["department"] = fee_dept["department"].astype(str)
    fee_dept["label"] = fee_dept["consultation_fee"].apply(lambda v: f"₹{v:,.0f}")

    fig_fee = px.bar(
        fee_dept, x="consultation_fee", y="department", orientation="h",
        color="consultation_fee",
        color_continuous_scale=[[0.0, "#1a1240"], [0.5, PURPLE], [1.0, "#a855f7"]],
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
        showlegend=False, coloraxis_showscale=False,
        xaxis=dict(title=dict(text="Average consultation fee (₹)",
                              font=dict(color=TEXT_DIM, size=12)),
                   range=[0, max_fee * 1.25]),
        yaxis_title=None, margin=dict(l=30, r=40, t=40, b=40),
    )
    st.plotly_chart(fig_fee, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Workforce summary
# ---------------------------------------------------------------------------
section_label("Workforce Summary")
busiest_doctor_row = doctor_stats.nlargest(1, "admissions").iloc[0]
busiest_dept_row = dept_work.iloc[-1]
quietest_dept_row = dept_work.iloc[0]
load_imbalance = (busiest_dept_row["per_doctor"] / quietest_dept_row["per_doctor"]
                  if quietest_dept_row["per_doctor"] > 0 else 0)
top_n = max(1, int(len(doctor_stats) * 0.10))
top_n_admissions = doctor_stats.nlargest(top_n, "admissions")["admissions"].sum()
total_admissions = doctor_stats["admissions"].sum()
top_share = top_n_admissions / total_admissions * 100 if total_admissions else 0

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Busiest Doctor", short_doctor(busiest_doctor_row["doctor_name"]))
    st.markdown(f'<div class="metric-sub">'
                f'{busiest_doctor_row["admissions"]:,} admissions · '
                f'{short_dept(busiest_doctor_row["doctor_department"])}</div>',
                unsafe_allow_html=True)
with c2:
    st.metric("Busiest Department", short_dept(busiest_dept_row["doctor_department"]))
    st.markdown(f'<div class="metric-sub">'
                f'{busiest_dept_row["per_doctor"]:.0f} admissions per doctor</div>',
                unsafe_allow_html=True)
with c3:
    st.metric("Load Imbalance", f"{load_imbalance:.1f}×")
    st.markdown(f'<div class="metric-sub">'
                f'{short_dept(busiest_dept_row["doctor_department"])} vs '
                f'{short_dept(quietest_dept_row["doctor_department"])}</div>',
                unsafe_allow_html=True)
with c4:
    st.metric("Top 10% Workload", f"{top_share:.1f}%")
    st.markdown(f'<div class="metric-sub">of admissions from {top_n} doctors</div>',
                unsafe_allow_html=True)

st.divider()
st.caption("Doctor Performance · Built by Shahan Malik · Streamlit · SQLite · Plotly · Pandas · 2026")
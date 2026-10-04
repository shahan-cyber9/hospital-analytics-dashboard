"""
pages/2_👥_Patient_Analytics.py
-------------------------------
Patient Analytics with cross-page filters.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.loader import load_all
from utils.filters import render_filters, apply_filters, apply_filters_by_admission_id
from utils.theme import (
    apply_page_style, style_dark, section_label, page_header,
    CYAN, CYAN_BRIGHT, CYAN_DEEP, PURPLE, PINK, GREEN, AMBER, RED,
    TEXT, TEXT_DIM, DEPT_COLORS,
)


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Patient Analytics · Smart Hospital",
    page_icon="👥",
    layout="wide",
)
apply_page_style()


GENDER_COLORS = {"Female": CYAN, "Male": PINK}


# ---------------------------------------------------------------------------
# Load data + filters
# ---------------------------------------------------------------------------
@st.cache_data(ttl=600, show_spinner="Loading patient data...")
def get_data() -> dict:
    return load_all()


data = get_data()
patients_raw = data["patients"]
doctors = data["doctors"]
admissions_raw = data["admissions"]

filters = render_filters(data)

admissions = apply_filters(admissions_raw, filters)

# Patients scoped to those who had any admission matching current filters.
active_patient_ids = set(admissions["patient_id"])
patients = patients_raw[patients_raw["patient_id"].isin(active_patient_ids)]


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
page_header(
    "Patient Analytics",
    "A demographic and clinical profile of the patient population, from "
    "age and gender distribution to disease frequency, department mix, "
    "and readmission behaviour."
)

if admissions.empty:
    st.warning("No data matches the current filters. Adjust or reset the filters in the sidebar.")
    st.stop()


# ---------------------------------------------------------------------------
# Enriched admissions
# ---------------------------------------------------------------------------
admissions_enriched = admissions.merge(
    patients_raw[["patient_id", "age_group", "gender", "city"]].rename(
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
# KPI row
# ---------------------------------------------------------------------------
female_share = (patients["gender"] == "Female").mean() * 100 if not patients.empty else 0
avg_age = patients["age"].mean() if not patients.empty else 0
readmit_rate = admissions["is_readmission"].mean() * 100
unique_diagnoses = admissions["diagnosis"].nunique()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Patients in View", f"{len(patients):,}")
c2.metric("Average Age", f"{avg_age:.1f} years")
c3.metric("Female Share", f"{female_share:.1f}%")
c4.metric("Unique Diagnoses", f"{unique_diagnoses}")


# ---------------------------------------------------------------------------
# Age + Gender
# ---------------------------------------------------------------------------
c1, c2 = st.columns([2, 1])

with c1:
    section_label("Age Distribution by Gender")
    fig_age = px.histogram(
        patients, x="age", color="gender",
        nbins=25, barmode="overlay",
        color_discrete_map=GENDER_COLORS, opacity=0.55,
    )
    fig_age.update_traces(
        marker=dict(line=dict(width=1.2)),
        hovertemplate="<b>Age %{x}</b><br>%{fullData.name}: %{y}<extra></extra>",
    )
    style_dark(fig_age, height=400)
    fig_age.update_layout(
        xaxis_title="Age (years)", yaxis_title="Number of Patients", bargap=0.05,
    )
    st.plotly_chart(fig_age, use_container_width=True, config={"displayModeBar": False})

with c2:
    section_label("Gender Split")
    gender_counts = (
        patients.groupby("gender", observed=True).size().reset_index(name="count")
    )
    fig_gender = px.pie(
        gender_counts, names="gender", values="count", hole=0.55,
        color="gender", color_discrete_map=GENDER_COLORS,
    )
    fig_gender.update_traces(
        textposition="outside", textinfo="label+percent",
        textfont=dict(color=TEXT, size=13),
        hovertemplate="<b>%{label}</b><br>%{value:,} patients<br>%{percent}<extra></extra>",
    )
    style_dark(fig_gender, height=400)
    fig_gender.update_layout(
        showlegend=False, margin=dict(l=80, r=80, t=40, b=40),
    )
    st.plotly_chart(fig_gender, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Diagnoses
# ---------------------------------------------------------------------------
section_label("Top 15 Diagnoses by Admission Volume")
top_diag = (
    admissions.groupby("diagnosis").size().reset_index(name="count")
    .nlargest(15, "count").sort_values("count", ascending=True)
)
fig_diag = px.bar(
    top_diag, x="count", y="diagnosis", orientation="h",
    color="count",
    color_continuous_scale=[
        [0.0, "#0e2a4a"], [0.3, "#0e5a7f"], [0.6, CYAN_DEEP], [1.0, CYAN],
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
    showlegend=False, coloraxis_showscale=False,
    xaxis_title=None, yaxis_title=None,
    margin=dict(l=30, r=90, t=50, b=30),
)
st.plotly_chart(fig_diag, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Heatmap
# ---------------------------------------------------------------------------
section_label("Department Mix Across Age Groups")
heat_data = (
    admissions_enriched
    .groupby(["department", "patient_age_group"], observed=True)
    .size().unstack(fill_value=0)
)
heat_data = heat_data.loc[heat_data.sum(axis=1).sort_values(ascending=False).index]
age_order = ["0-17", "18-29", "30-44", "45-59", "60-74", "75+"]
heat_data = heat_data.reindex(
    columns=[c for c in age_order if c in heat_data.columns]
)
text_vals = [
    [f"{int(v)}" if v > 0 else "" for v in row]
    for row in heat_data.values
]
fig_heat = px.imshow(
    heat_data, aspect="auto",
    color_continuous_scale=[
        [0.0, "#0a0e1a"], [0.4, "#0e3a5f"], [0.7, CYAN_DEEP], [1.0, CYAN],
    ],
)
fig_heat.update_traces(
    text=text_vals, texttemplate="%{text}",
    hovertemplate="<b>%{y}</b><br>Age %{x}<br>%{z:,} admissions<extra></extra>",
    textfont=dict(size=11, family="JetBrains Mono", color=TEXT),
)
style_dark(fig_heat, height=520)
fig_heat.update_layout(
    xaxis_title=None, yaxis_title=None,
    coloraxis_colorbar=dict(
        title=dict(text="Admissions", font=dict(color=TEXT_DIM)),
        tickfont=dict(color=TEXT_DIM), outlinewidth=0,
    ),
    margin=dict(l=30, r=30, t=40, b=30),
)
st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Readmission + City
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    section_label("Readmission Rate by Department")
    readmit = (
        admissions.groupby("department", observed=True)
        .agg(admissions=("admission_id", "count"),
             readmits=("is_readmission", "sum"))
        .reset_index()
    )
    readmit["rate"] = readmit["readmits"] / readmit["admissions"] * 100
    readmit = readmit.sort_values("rate", ascending=True)

    fig_readmit = px.bar(
        readmit, x="rate", y="department", orientation="h",
        color="rate",
        color_continuous_scale=[[0.0, "#0e2a4a"], [0.5, AMBER], [1.0, RED]],
        text="rate",
    )
    fig_readmit.update_traces(
        texttemplate="%{text:.2f}%", textposition="outside",
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
        showlegend=False, coloraxis_showscale=False,
        xaxis_title="Readmission rate (%)", yaxis_title=None,
        margin=dict(l=30, r=90, t=50, b=60),
    )
    st.plotly_chart(fig_readmit, use_container_width=True, config={"displayModeBar": False})

with c2:
    section_label("Patients by City")
    city_counts = (
        patients.groupby("city", observed=True).size().reset_index(name="count")
        .sort_values("count", ascending=True)
    )
    fig_city = px.bar(
        city_counts, x="count", y="city", orientation="h",
        color="count",
        color_continuous_scale=[
            [0.0, "#1a1240"], [0.5, PURPLE], [1.0, "#a855f7"],
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
        showlegend=False, coloraxis_showscale=False,
        xaxis_title=None, yaxis_title=None,
        margin=dict(l=30, r=90, t=50, b=30),
    )
    st.plotly_chart(fig_city, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption("Patient Analytics · Built by Shahan Malik · Streamlit · SQLite · Plotly · Pandas · 2026")
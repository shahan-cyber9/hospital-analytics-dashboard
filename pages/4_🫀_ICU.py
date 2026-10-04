"""
pages/4_🫀_ICU.py
-----------------
ICU Dashboard with cross-page filters.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.loader import load_all
from utils.filters import render_filters, apply_filters, apply_filters_by_admission_id
from utils.theme import (
    apply_page_style, style_dark, section_label, page_header,
    CYAN, CYAN_BRIGHT, CYAN_DEEP, PURPLE, SKY, GREEN, AMBER, RED,
    TEXT, TEXT_DIM, DARK,
)


st.set_page_config(
    page_title="ICU · Smart Hospital",
    page_icon="🫀",
    layout="wide",
)
apply_page_style()


TOTAL_ICU_BEDS = 30


def make_gauge(value, title, suffix="%", max_val=100,
               thresholds=(60, 80, 90), primary_color=CYAN):
    green_max, cyan_max, amber_max = thresholds
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": suffix,
                "font": {"color": primary_color, "size": 44,
                         "family": "JetBrains Mono, monospace"}},
        title={"text": f"<span style='font-size:13px; color:{TEXT_DIM}; "
                       f"letter-spacing:0.08em;'>{title.upper()}</span>",
               "font": {"family": "Inter, sans-serif"}},
        gauge={
            "axis": {"range": [0, max_val], "tickcolor": TEXT_DIM,
                     "tickfont": {"color": TEXT_DIM, "size": 10},
                     "tickwidth": 1, "nticks": 6},
            "bar": {"color": primary_color, "thickness": 0.28},
            "bgcolor": "rgba(255,255,255,0.03)", "borderwidth": 0,
            "steps": [
                {"range": [0, green_max], "color": "rgba(34, 197, 94, 0.18)"},
                {"range": [green_max, cyan_max], "color": "rgba(0, 212, 255, 0.18)"},
                {"range": [cyan_max, amber_max], "color": "rgba(245, 158, 11, 0.20)"},
                {"range": [amber_max, max_val], "color": "rgba(239, 68, 68, 0.20)"},
            ],
            "threshold": {"line": {"color": RED, "width": 3},
                          "thickness": 0.8, "value": amber_max},
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": TEXT, "family": "Inter, sans-serif"},
        height=290, margin=dict(l=30, r=30, t=60, b=10),
    )
    return fig


@st.cache_data(ttl=600, show_spinner="Loading ICU data...")
def get_data() -> dict:
    return load_all()


@st.cache_data(ttl=600, show_spinner="Computing ICU census...")
def compute_icu_census(icu_df: pd.DataFrame) -> pd.Series:
    all_days = []
    for start, days in zip(icu_df["icu_admit_date"], icu_df["icu_days"]):
        all_days.extend(pd.date_range(start=start, periods=int(days), freq="D"))
    return pd.Series(all_days).value_counts().sort_index()


data = get_data()
admissions_raw = data["admissions"]
icu_raw = data["icu"]

filters = render_filters(data)

admissions = apply_filters(admissions_raw, filters)
icu = apply_filters_by_admission_id(icu_raw, admissions)
icu_full = icu.merge(
    admissions[["admission_id", "department", "outcome", "diagnosis"]],
    on="admission_id", how="left",
)


page_header(
    "ICU Dashboard",
    "Intensive care load and resource utilisation. Occupancy is derived from "
    f"individual ICU stays and compared against an assumed capacity of "
    f"{TOTAL_ICU_BEDS} beds."
)

if icu.empty:
    st.warning("No data matches the current filters. Adjust or reset the filters in the sidebar.")
    st.stop()


census = compute_icu_census(icu)
avg_icu_days = icu["icu_days"].mean()
avg_census = census.mean()
peak_census = int(census.max())
avg_occupancy = (avg_census / TOTAL_ICU_BEDS) * 100
peak_occupancy = (peak_census / TOTAL_ICU_BEDS) * 100
vent_share = icu["ventilator_used"].mean() * 100
oxy_share = icu["oxygen_required"].mean() * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total ICU Stays", f"{len(icu):,}")
c2.metric("Avg Length of Stay", f"{avg_icu_days:.1f} days")
c3.metric("Avg Occupancy", f"{avg_occupancy:.0f}%")
c4.metric("Peak Occupancy", f"{peak_occupancy:.0f}%")


# ---------------------------------------------------------------------------
# Gauges
# ---------------------------------------------------------------------------
section_label("Critical Care Utilisation")
g1, g2, g3 = st.columns(3)
with g1:
    st.plotly_chart(make_gauge(min(avg_occupancy, 100), "ICU Occupancy",
                                thresholds=(60, 80, 90), primary_color=CYAN),
                    use_container_width=True, config={"displayModeBar": False})
with g2:
    st.plotly_chart(make_gauge(vent_share, "Ventilator Use",
                                thresholds=(30, 50, 70), primary_color=PURPLE),
                    use_container_width=True, config={"displayModeBar": False})
with g3:
    st.plotly_chart(make_gauge(oxy_share, "Oxygen Support",
                                thresholds=(50, 75, 90), primary_color=SKY),
                    use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# LOS + Trend
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    section_label("ICU Length of Stay Distribution")
    median_los = icu["icu_days"].median()
    fig_los = px.histogram(icu, x="icu_days", nbins=20,
                            color_discrete_sequence=[CYAN])
    fig_los.update_traces(
        marker=dict(line=dict(color=CYAN_BRIGHT, width=0.5)),
        opacity=0.85,
        hovertemplate="<b>%{x} days</b><br>%{y} stays<extra></extra>",
    )
    fig_los.add_vline(
        x=median_los, line=dict(color=AMBER, width=2, dash="dash"),
        annotation_text=f"Median {median_los:.0f}d",
        annotation_position="top right",
        annotation_font=dict(color=AMBER, size=11),
    )
    style_dark(fig_los, height=400)
    fig_los.update_layout(xaxis_title="ICU days",
                          yaxis_title="Number of stays", bargap=0.05)
    st.plotly_chart(fig_los, use_container_width=True, config={"displayModeBar": False})

with c2:
    section_label("Monthly ICU Admissions")
    anchor = icu["icu_admit_date"].max()
    current_month_start = anchor.replace(day=1)
    icu_trend = icu[icu["icu_admit_date"] < current_month_start].copy()
    icu_trend["ym"] = icu_trend["icu_admit_date"].dt.strftime("%Y-%m")
    monthly = icu_trend.groupby("ym").size().reset_index(name="stays").sort_values("ym")
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=monthly["ym"], y=monthly["stays"],
        mode="lines+markers",
        line=dict(color=CYAN, width=3, shape="spline", smoothing=0.5),
        marker=dict(size=7, color=CYAN, line=dict(color="#0a0e1a", width=2)),
        fill="tozeroy", fillcolor="rgba(0, 212, 255, 0.10)",
        hovertemplate="<b>%{x}</b><br>%{y} ICU stays<extra></extra>",
    ))
    style_dark(fig_trend, height=400)
    fig_trend.update_layout(showlegend=False, xaxis_title=None, yaxis_title="ICU stays")
    st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Department + Outcomes
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    section_label("ICU Load by Department")
    dept_icu = (
        icu_full.groupby("department", observed=True)
        .agg(stays=("icu_id", "count"), avg_days=("icu_days", "mean"),
             vent=("ventilator_used", "sum"))
        .reset_index().sort_values("stays", ascending=True)
    )
    dept_icu["department"] = dept_icu["department"].astype(str)
    fig_dept = px.bar(
        dept_icu, x="stays", y="department", orientation="h",
        color="stays",
        color_continuous_scale=[
            [0.0, "#0e2a4a"], [0.5, CYAN_DEEP], [1.0, CYAN],
        ], text="stays",
    )
    fig_dept.update_traces(
        textposition="outside",
        textfont=dict(color=TEXT, size=11, family="JetBrains Mono"),
        marker=dict(cornerradius=5, line=dict(width=0)),
        hovertemplate="<b>%{y}</b><br>%{x} ICU stays<extra></extra>",
    )
    style_dark(fig_dept, height=460)
    fig_dept.update_layout(showlegend=False, coloraxis_showscale=False,
                            xaxis_title=None, yaxis_title=None,
                            margin=dict(l=30, r=70, t=50, b=30))
    st.plotly_chart(fig_dept, use_container_width=True, config={"displayModeBar": False})

with c2:
    section_label("Outcome Mix · ICU vs Non-ICU")
    icu_ids = set(icu["admission_id"])
    adm_tagged = admissions.copy()
    adm_tagged["had_icu"] = adm_tagged["admission_id"].isin(icu_ids)
    adm_tagged["cohort"] = adm_tagged["had_icu"].map({True: "ICU", False: "Non-ICU"})

    outcome_mix = (
        adm_tagged.groupby(["cohort", "outcome"], observed=True)
        .size().reset_index(name="count")
    )
    totals = outcome_mix.groupby("cohort")["count"].transform("sum")
    outcome_mix["share"] = outcome_mix["count"] / totals
    outcome_order = ["Recovered", "Discharged", "Transferred", "Deceased"]
    outcome_mix["outcome"] = pd.Categorical(
        outcome_mix["outcome"], categories=outcome_order, ordered=True
    )
    outcome_mix = outcome_mix.sort_values(["cohort", "outcome"])

    fig_out = px.bar(
        outcome_mix, x="cohort", y="share", color="outcome", barmode="stack",
        category_orders={"cohort": ["ICU", "Non-ICU"], "outcome": outcome_order},
        color_discrete_map={
            "Recovered": CYAN, "Discharged": GREEN,
            "Transferred": AMBER, "Deceased": RED,
        },
        custom_data=["count"],
    )
    fig_out.update_traces(
        marker=dict(line=dict(width=0)),
        hovertemplate=("<b>%{x}</b><br>%{fullData.name}: "
                       "%{y:.1%} (%{customdata[0]:,} admissions)<extra></extra>"),
    )
    style_dark(fig_out, height=460)
    fig_out.update_layout(
        xaxis_title=None,
        yaxis=dict(title=dict(text="Share of admissions",
                              font=dict(color=TEXT_DIM, size=12)),
                   tickformat=".0%", range=[0, 1]),
        margin=dict(l=30, r=30, t=60, b=40),
    )
    st.plotly_chart(fig_out, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Operational summary
# ---------------------------------------------------------------------------
section_label("Operational Summary")
avg_stay_vent = icu[icu["ventilator_used"]]["icu_days"].mean() if icu["ventilator_used"].any() else 0
avg_stay_no_vent = icu[~icu["ventilator_used"]]["icu_days"].mean() if (~icu["ventilator_used"]).any() else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("On Ventilator", f"{int(icu['ventilator_used'].sum()):,} stays",
          delta=f"avg {avg_stay_vent:.1f} days", delta_color="off")
c2.metric("No Ventilator", f"{int((~icu['ventilator_used']).sum()):,} stays",
          delta=f"avg {avg_stay_no_vent:.1f} days", delta_color="off")
c3.metric("On Oxygen", f"{int(icu['oxygen_required'].sum()):,} stays",
          delta=f"{oxy_share:.0f}% of ICU", delta_color="off")
c4.metric("Peak Census", f"{peak_census} patients",
          delta=f"capacity {TOTAL_ICU_BEDS} beds", delta_color="off")

st.divider()
st.caption("ICU Dashboard · Built by Shahan Malik · Streamlit · SQLite · Plotly · Pandas · 2026")
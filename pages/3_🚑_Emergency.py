"""
pages/3_🚑_Emergency.py
-----------------------
Emergency Analytics with cross-page filters.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.loader import load_all
from utils.filters import render_filters, apply_filters, apply_filters_by_admission_id
from utils.theme import (
    apply_page_style, style_dark, section_label, page_header,
    CYAN, CYAN_BRIGHT, CYAN_DEEP, PURPLE, RED, AMBER, GREEN,
    TEXT, TEXT_DIM,
)


st.set_page_config(
    page_title="Emergency · Smart Hospital",
    page_icon="🚑",
    layout="wide",
)
apply_page_style()


SEVERITY_COLORS = {
    "Critical": RED, "Serious": AMBER, "Moderate": CYAN, "Stable": GREEN,
}
SEVERITY_ORDER = ["Critical", "Serious", "Moderate", "Stable"]
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday",
             "Friday", "Saturday", "Sunday"]


@st.cache_data(ttl=600, show_spinner="Loading emergency data...")
def get_data() -> dict:
    return load_all()


data = get_data()
emergency_raw = data["emergency"]
admissions_raw = data["admissions"]

filters = render_filters(data)

admissions = apply_filters(admissions_raw, filters)
emergency = apply_filters_by_admission_id(emergency_raw, admissions)

# Apply severity filter on top of the ID-scoped emergency rows.
if filters["severity"]:
    emergency = emergency[emergency["severity"].isin(filters["severity"])]


page_header(
    "Emergency Analytics",
    "An operational view of the emergency department: when patients arrive, "
    "how long they wait, how severity shapes triage, and the rhythm of "
    "ambulance arrivals across the week."
)

if emergency.empty:
    st.warning("No data matches the current filters. Adjust or reset the filters in the sidebar.")
    st.stop()


# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
total_er = len(emergency)
avg_wait = emergency["wait_minutes"].mean()
ambulance_share = emergency["ambulance_arrival"].mean() * 100
critical_share = (emergency["severity"] == "Critical").mean() * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total ER Visits", f"{total_er:,}")
c2.metric("Avg Wait Time", f"{avg_wait:.1f} min")
c3.metric("Ambulance Arrivals", f"{ambulance_share:.1f}%")
c4.metric("Critical Cases", f"{critical_share:.1f}%")


# ---------------------------------------------------------------------------
# Peak hours heatmap
# ---------------------------------------------------------------------------
section_label("Peak Emergency Hours · Day × Hour")
heat_ed = (
    emergency.groupby(["arrival_dow", "arrival_hour"])
    .size().unstack(fill_value=0).reindex(DAY_ORDER)
)
heat_ed = heat_ed.reindex(columns=range(24), fill_value=0)

fig_heat = px.imshow(
    heat_ed, aspect="auto",
    color_continuous_scale=[
        [0.00, "#0a0e1a"], [0.30, "#0e3a5f"],
        [0.55, CYAN_DEEP], [0.80, CYAN], [1.00, CYAN_BRIGHT],
    ],
)
fig_heat.update_traces(
    hovertemplate="<b>%{y}</b><br>Hour %{x}:00<br>%{z} ER visits<extra></extra>",
)
style_dark(fig_heat, height=380)
fig_heat.update_layout(
    xaxis=dict(
        title=dict(text="Hour of Day", font=dict(color=TEXT_DIM, size=12)),
        tickmode="linear", tick0=0, dtick=2,
        tickfont=dict(color=TEXT_DIM, size=11),
    ),
    yaxis=dict(title=None, tickfont=dict(color=TEXT_DIM, size=11.5)),
    coloraxis_colorbar=dict(
        title=dict(text="Visits", font=dict(color=TEXT_DIM)),
        tickfont=dict(color=TEXT_DIM), outlinewidth=0,
    ),
    margin=dict(l=30, r=30, t=40, b=50),
)
st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Box plot + hourly wait
# ---------------------------------------------------------------------------
c1, c2 = st.columns([1, 1])

with c1:
    section_label("Wait Time Distribution by Severity")
    fig_box = px.box(
        emergency, x="severity", y="wait_minutes", color="severity",
        category_orders={"severity": SEVERITY_ORDER},
        color_discrete_map=SEVERITY_COLORS, points="outliers",
    )
    fig_box.update_traces(
        marker=dict(size=4, opacity=0.6), line=dict(width=1.5),
        hovertemplate="<b>%{x}</b><br>Wait: %{y} min<extra></extra>",
    )
    style_dark(fig_box, height=440)
    fig_box.update_layout(
        showlegend=False, xaxis_title=None,
        yaxis=dict(title=dict(text="Wait time (minutes)",
                              font=dict(color=TEXT_DIM, size=12))),
        margin=dict(l=30, r=30, t=50, b=40),
    )
    st.plotly_chart(fig_box, use_container_width=True, config={"displayModeBar": False})

with c2:
    section_label("Average Wait · Hour of Arrival")
    hourly_wait = (
        emergency.groupby("arrival_hour")
        .agg(avg_wait=("wait_minutes", "mean"), visits=("er_id", "count"))
        .reset_index()
    )
    fig_hour = go.Figure()
    fig_hour.add_trace(go.Scatter(
        x=hourly_wait["arrival_hour"], y=hourly_wait["avg_wait"],
        mode="lines+markers",
        line=dict(color=CYAN, width=3, shape="spline", smoothing=0.6),
        marker=dict(size=8, color=CYAN, line=dict(color="#0a0e1a", width=2)),
        fill="tozeroy", fillcolor="rgba(0, 212, 255, 0.10)",
        hovertemplate="<b>%{x}:00</b><br>Avg wait: %{y:.1f} min<extra></extra>",
        name="Avg wait",
    ))
    fig_hour.add_vrect(
        x0=18, x1=22, fillcolor="rgba(239, 68, 68, 0.08)",
        line_width=0, layer="below",
        annotation_text="Peak window", annotation_position="top left",
        annotation_font=dict(color=RED, size=11),
    )
    style_dark(fig_hour, height=440)
    fig_hour.update_layout(
        showlegend=False,
        xaxis=dict(
            title=dict(text="Hour of day", font=dict(color=TEXT_DIM, size=12)),
            tickmode="linear", tick0=0, dtick=3,
        ),
        yaxis=dict(title=dict(text="Average wait (min)",
                              font=dict(color=TEXT_DIM, size=12))),
        margin=dict(l=30, r=30, t=50, b=40),
    )
    st.plotly_chart(fig_hour, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Ambulance + Severity mix
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    section_label("Ambulance vs Walk-in · Monthly Volume")
    er_monthly = emergency.copy()
    er_monthly["ym"] = er_monthly["arrival_time"].dt.strftime("%Y-%m")
    er_monthly["arrival_type"] = er_monthly["ambulance_arrival"].map(
        {True: "Ambulance", False: "Walk-in"}
    )
    monthly_type = (
        er_monthly.groupby(["ym", "arrival_type"]).size().reset_index(name="visits")
    )
    fig_amb = px.area(
        monthly_type, x="ym", y="visits", color="arrival_type",
        color_discrete_map={"Ambulance": RED, "Walk-in": CYAN},
    )
    fig_amb.update_traces(
        line=dict(width=1.5),
        hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y} visits<extra></extra>",
    )
    style_dark(fig_amb, height=420)
    fig_amb.update_layout(
        xaxis_title=None,
        yaxis=dict(title=dict(text="ER visits", font=dict(color=TEXT_DIM, size=12))),
        margin=dict(l=30, r=30, t=60, b=40),
    )
    st.plotly_chart(fig_amb, use_container_width=True, config={"displayModeBar": False})

with c2:
    section_label("Severity Mix by Day of Week")
    sev_day = (
        emergency.groupby(["arrival_dow", "severity"]).size().reset_index(name="visits")
    )
    sev_day["arrival_dow"] = pd.Categorical(sev_day["arrival_dow"],
                                             categories=DAY_ORDER, ordered=True)
    sev_day["severity"] = pd.Categorical(sev_day["severity"],
                                          categories=SEVERITY_ORDER, ordered=True)
    sev_day = sev_day.sort_values(["arrival_dow", "severity"])
    fig_sev = px.bar(
        sev_day, x="arrival_dow", y="visits", color="severity",
        barmode="stack",
        category_orders={"arrival_dow": DAY_ORDER, "severity": SEVERITY_ORDER},
        color_discrete_map=SEVERITY_COLORS,
    )
    fig_sev.update_traces(
        marker=dict(line=dict(width=0)),
        hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y} visits<extra></extra>",
    )
    style_dark(fig_sev, height=420)
    fig_sev.update_layout(
        xaxis_title=None,
        yaxis=dict(title=dict(text="ER visits", font=dict(color=TEXT_DIM, size=12))),
        margin=dict(l=30, r=30, t=60, b=40),
    )
    st.plotly_chart(fig_sev, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Summary cards
# ---------------------------------------------------------------------------
section_label("Severity Throughput Summary")
summary = (
    emergency.groupby("severity")
    .agg(visits=("er_id", "count"), avg_wait=("wait_minutes", "mean"),
         max_wait=("wait_minutes", "max"), ambulance=("ambulance_arrival", "sum"))
    .reindex(SEVERITY_ORDER).reset_index()
)
summary["ambulance_pct"] = summary["ambulance"] / summary["visits"] * 100

c1, c2, c3, c4 = st.columns(4)
for col, (_, row) in zip([c1, c2, c3, c4], summary.iterrows()):
    col.metric(
        label=f"{row['severity']} · {int(row['visits']):,} visits",
        value=f"{row['avg_wait']:.1f} min",
        help=f"Ambulance: {row['ambulance_pct']:.1f}% · Max wait: {int(row['max_wait'])} min",
    )

st.divider()
st.caption("Emergency Analytics · Built by Shahan Malik · Streamlit · SQLite · Plotly · Pandas · 2026")
"""
pages/3_🚑_Emergency.py
-----------------------
Emergency Analytics: peak hours, wait times, ambulance arrivals, and severity.

Focuses on the emergency department's operational rhythm across hours,
days, and severity levels.
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
    page_title="Emergency · Smart Hospital",
    page_icon="🚑",
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
TEXT_FAINT = "#6b7f9e"

SEVERITY_COLORS = {
    "Critical": RED,
    "Serious": AMBER,
    "Moderate": CYAN,
    "Stable": GREEN,
}
SEVERITY_ORDER = ["Critical", "Serious", "Moderate", "Stable"]


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
@st.cache_data(ttl=600, show_spinner="Loading emergency data...")
def get_data() -> dict:
    return load_all()


data = get_data()
emergency = data["emergency"]
admissions = data["admissions"]


# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.markdown('<div class="page-title">Emergency Analytics</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-sub">'
    "An operational view of the emergency department: when patients arrive, "
    "how long they wait, how severity shapes triage, and the rhythm of "
    "ambulance arrivals across the week."
    "</div>",
    unsafe_allow_html=True,
)


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
# Peak hours heatmap (Hour x Day)
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="section-label">Peak Emergency Hours · Day × Hour</div>',
    unsafe_allow_html=True,
)

day_order = ["Monday", "Tuesday", "Wednesday", "Thursday",
             "Friday", "Saturday", "Sunday"]

heat_ed = (
    emergency.groupby(["arrival_dow", "arrival_hour"])
    .size()
    .unstack(fill_value=0)
    .reindex(day_order)
)
heat_ed = heat_ed.reindex(columns=range(24), fill_value=0)

fig_heat = px.imshow(
    heat_ed,
    aspect="auto",
    color_continuous_scale=[
        [0.00, "#0a0e1a"],
        [0.30, "#0e3a5f"],
        [0.55, CYAN_DEEP],
        [0.80, CYAN],
        [1.00, CYAN_BRIGHT],
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
    yaxis=dict(
        title=None,
        tickfont=dict(color=TEXT_DIM, size=11.5),
    ),
    coloraxis_colorbar=dict(
        title=dict(text="Visits", font=dict(color=TEXT_DIM)),
        tickfont=dict(color=TEXT_DIM),
        outlinewidth=0,
    ),
    margin=dict(l=30, r=30, t=40, b=50),
)
st.plotly_chart(fig_heat, use_container_width=True,
                config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Wait time distribution + Hourly wait curve
# ---------------------------------------------------------------------------
c1, c2 = st.columns([1, 1])

with c1:
    st.markdown(
        '<div class="section-label">Wait Time Distribution by Severity</div>',
        unsafe_allow_html=True,
    )
    fig_box = px.box(
        emergency,
        x="severity",
        y="wait_minutes",
        color="severity",
        category_orders={"severity": SEVERITY_ORDER},
        color_discrete_map=SEVERITY_COLORS,
        points="outliers",
    )
    fig_box.update_traces(
        marker=dict(size=4, opacity=0.6),
        line=dict(width=1.5),
        hovertemplate="<b>%{x}</b><br>Wait: %{y} min<extra></extra>",
    )
    style_dark(fig_box, height=440)
    fig_box.update_layout(
        showlegend=False,
        xaxis_title=None,
        yaxis=dict(title=dict(text="Wait time (minutes)",
                              font=dict(color=TEXT_DIM, size=12))),
        margin=dict(l=30, r=30, t=50, b=40),
    )
    st.plotly_chart(fig_box, use_container_width=True,
                    config={"displayModeBar": False})

with c2:
    st.markdown(
        '<div class="section-label">Average Wait · Hour of Arrival</div>',
        unsafe_allow_html=True,
    )
    hourly_wait = (
        emergency.groupby("arrival_hour")
        .agg(avg_wait=("wait_minutes", "mean"),
             visits=("er_id", "count"))
        .reset_index()
    )

    fig_hour = go.Figure()
    fig_hour.add_trace(go.Scatter(
        x=hourly_wait["arrival_hour"],
        y=hourly_wait["avg_wait"],
        mode="lines+markers",
        line=dict(color=CYAN, width=3, shape="spline", smoothing=0.6),
        marker=dict(size=8, color=CYAN, line=dict(color="#0a0e1a", width=2)),
        fill="tozeroy",
        fillcolor="rgba(0, 212, 255, 0.10)",
        hovertemplate="<b>%{x}:00</b><br>Avg wait: %{y:.1f} min<extra></extra>",
        name="Avg wait",
    ))
    fig_hour.add_vrect(
        x0=18, x1=22,
        fillcolor="rgba(239, 68, 68, 0.08)",
        line_width=0,
        layer="below",
        annotation_text="Peak window",
        annotation_position="top left",
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
    st.plotly_chart(fig_hour, use_container_width=True,
                    config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Ambulance trend + Severity mix
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.markdown(
        '<div class="section-label">Ambulance vs Walk-in · Monthly Volume</div>',
        unsafe_allow_html=True,
    )
    er_monthly = emergency.copy()
    er_monthly["ym"] = er_monthly["arrival_time"].dt.strftime("%Y-%m")
    er_monthly["arrival_type"] = er_monthly["ambulance_arrival"].map(
        {True: "Ambulance", False: "Walk-in"}
    )

    monthly_type = (
        er_monthly.groupby(["ym", "arrival_type"])
        .size()
        .reset_index(name="visits")
    )

    fig_amb = px.area(
        monthly_type,
        x="ym", y="visits",
        color="arrival_type",
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
    st.plotly_chart(fig_amb, use_container_width=True,
                    config={"displayModeBar": False})

with c2:
    st.markdown(
        '<div class="section-label">Severity Mix by Day of Week</div>',
        unsafe_allow_html=True,
    )
    sev_day = (
        emergency.groupby(["arrival_dow", "severity"])
        .size()
        .reset_index(name="visits")
    )
    sev_day["arrival_dow"] = pd.Categorical(
        sev_day["arrival_dow"], categories=day_order, ordered=True
    )
    sev_day["severity"] = pd.Categorical(
        sev_day["severity"], categories=SEVERITY_ORDER, ordered=True
    )
    sev_day = sev_day.sort_values(["arrival_dow", "severity"])

    fig_sev = px.bar(
        sev_day,
        x="arrival_dow", y="visits",
        color="severity",
        barmode="stack",
        category_orders={
            "arrival_dow": day_order,
            "severity": SEVERITY_ORDER,
        },
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
    st.plotly_chart(fig_sev, use_container_width=True,
                    config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Severity throughput summary
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="section-label">Severity Throughput Summary</div>',
    unsafe_allow_html=True,
)

summary = (
    emergency.groupby("severity")
    .agg(
        visits=("er_id", "count"),
        avg_wait=("wait_minutes", "mean"),
        max_wait=("wait_minutes", "max"),
        ambulance=("ambulance_arrival", "sum"),
    )
    .reindex(SEVERITY_ORDER)
    .reset_index()
)
summary["ambulance_pct"] = summary["ambulance"] / summary["visits"] * 100

# Each card shows the average wait time as the headline value.
# The label carries the severity level and visit count, so there's no
# misleading "up/down" arrow for purely informational numbers.
c1, c2, c3, c4 = st.columns(4)
for col, (_, row) in zip([c1, c2, c3, c4], summary.iterrows()):
    col.metric(
        label=f"{row['severity']} · {int(row['visits']):,} visits",
        value=f"{row['avg_wait']:.1f} min",
        help=f"Ambulance arrivals: {row['ambulance_pct']:.1f}% · Max wait: {int(row['max_wait'])} min",
    )


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "Emergency Analytics · Built by Shahan Malik · "
    "Streamlit · SQLite · Plotly · Pandas · 2026"
)
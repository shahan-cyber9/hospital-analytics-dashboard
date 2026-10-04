"""
pages/5_💰_Finance.py
---------------------
Financial Analytics: revenue trends, department contributions, insurance
mix, and payment efficiency.

Uses px.treemap with distinct colours per department for instant readability.
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
    page_title="Finance · Smart Hospital",
    page_icon="💰",
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


# Distinct bright colours per department — one per category.
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

# Distinct colours for insurance providers.
INSURER_COLORS = {
    "Star Health":    "#22d3ee",
    "HDFC Ergo":      "#a78bfa",
    "ICICI Lombard":  "#fb7185",
    "Niva Bupa":      "#fbbf24",
    "Bajaj Allianz":  "#4ade80",
    "Care Health":    "#c084fc",
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


def fmt_rupees(value: float, unit: str = "Cr") -> str:
    """Format a rupee amount in crores (Cr)."""
    if unit == "Cr":
        return f"₹{value / 1e7:,.2f} Cr"
    return f"₹{value / 1e5:,.2f} L"


def fmt_compact_rupees(value: float) -> str:
    """Compact rupee label for chart text."""
    if value >= 1e7:
        return f"₹{value / 1e7:.1f} Cr"
    if value >= 1e5:
        return f"₹{value / 1e5:.1f} L"
    return f"₹{value:,.0f}"


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
        .metric-sub {
            color: #A0AAB8;
            font-size: 0.78rem;
            margin-top: 6px;
            letter-spacing: 0.02em;
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
@st.cache_data(ttl=600, show_spinner="Loading financial data...")
def get_data() -> dict:
    return load_all()


data = get_data()
admissions = data["admissions"]
billing = data["billing"]


billing_full = billing.merge(
    admissions[["admission_id", "department", "admission_date",
                "length_of_stay", "admission_ym"]],
    on="admission_id",
    how="left",
)


# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.markdown('<div class="page-title">Financial Analytics</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-sub">'
    "Revenue performance across departments, payment modes, and time. "
    "Identifies the biggest contributors to hospital income and the "
    "balance between insurance-covered and self-paid care."
    "</div>",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
total_revenue = billing["amount"].sum()
avg_bill = billing["amount"].mean()
insurance_bills = billing[billing["payment_mode"] == "Insurance"]
insurance_share = len(insurance_bills) / len(billing) * 100
total_self_pay = (billing["amount"] - billing["insurance_covered"]).sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Billed", fmt_rupees(total_revenue))
c2.metric("Average Bill", f"₹{avg_bill:,.0f}")
c3.metric("Insurance Share", f"{insurance_share:.1f}%")
c4.metric("Out-of-Pocket", fmt_rupees(total_self_pay))


# ---------------------------------------------------------------------------
# Monthly revenue + 6-month rolling average
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="section-label">Monthly Revenue · Last 24 Complete Months</div>',
    unsafe_allow_html=True,
)

anchor = billing_full["admission_date"].max()
current_month_start = anchor.replace(day=1)

rev_trend = billing_full[billing_full["admission_date"] < current_month_start].copy()
rev_trend["ym"] = rev_trend["admission_date"].dt.strftime("%Y-%m")
monthly_rev = (
    rev_trend.groupby("ym")["amount"].sum()
    .reset_index(name="revenue")
    .sort_values("ym")
)

monthly_rev["rolling_6"] = monthly_rev["revenue"].rolling(window=6).mean()
rolling_view = monthly_rev.dropna(subset=["rolling_6"])

fig_rev = go.Figure()
fig_rev.add_trace(go.Bar(
    x=monthly_rev["ym"],
    y=monthly_rev["revenue"],
    name="Monthly revenue",
    marker=dict(
        color="rgba(0, 212, 255, 0.45)",
        line=dict(color="rgba(0, 212, 255, 0.9)", width=1),
        cornerradius=4,
    ),
    hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>",
))
fig_rev.add_trace(go.Scatter(
    x=rolling_view["ym"],
    y=rolling_view["rolling_6"],
    name="6-month average",
    mode="lines+markers",
    line=dict(color=PURPLE, width=3),
    marker=dict(size=6, color=PURPLE,
                line=dict(color=DARK, width=1.5)),
    hovertemplate="<b>%{x}</b><br>6-mo avg: ₹%{y:,.0f}<extra></extra>",
))
style_dark(fig_rev, height=440)
fig_rev.update_layout(
    yaxis=dict(title=dict(text="Revenue (₹)", font=dict(color=TEXT_DIM, size=12))),
    xaxis_title=None,
    hovermode="x unified",
    bargap=0.15,
)
st.plotly_chart(fig_rev, use_container_width=True,
                config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Treemap + Insurance donut
# ---------------------------------------------------------------------------
c1, c2 = st.columns([2, 1])

with c1:
    st.markdown(
        '<div class="section-label">Revenue by Department · Treemap</div>',
        unsafe_allow_html=True,
    )
    dept_rev = (
        billing_full.groupby("department", observed=True)["amount"]
        .sum()
        .reset_index()
        .sort_values("amount", ascending=False)
    )
    # Cast to plain str — Plotly treemap internals try to max the category.
    dept_rev["department"] = dept_rev["department"].astype(str)

    fig_tree = px.treemap(
        dept_rev,
        path=["department"],
        values="amount",
        color="department",
        color_discrete_map=DEPT_COLORS,
    )
    fig_tree.update_traces(
        texttemplate="<b>%{label}</b><br>%{percentRoot:.0%}",
        textfont=dict(size=13, family="Inter, sans-serif", color=DARK),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Revenue: ₹%{value:,.0f}<br>"
            "Share: %{percentRoot:.2%}<extra></extra>"
        ),
        marker=dict(line=dict(color=DARK, width=2)),
    )
    fig_tree.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=20, b=20),
        height=460,
        font=dict(family="Inter, sans-serif", color=TEXT),
    )
    st.plotly_chart(fig_tree, use_container_width=True,
                    config={"displayModeBar": False})

with c2:
    st.markdown(
        '<div class="section-label">Payment Mode Split</div>',
        unsafe_allow_html=True,
    )
    pay_split = (
        billing.groupby("payment_mode", observed=True)["amount"]
        .sum()
        .reset_index()
        .sort_values("amount", ascending=False)
    )
    fig_pay = px.pie(
        pay_split,
        names="payment_mode",
        values="amount",
        hole=0.55,
        color="payment_mode",
        color_discrete_map={"Insurance": CYAN, "Self-Pay": PURPLE},
    )
    fig_pay.update_traces(
        textposition="outside",
        textinfo="percent+label",
        textfont=dict(color=TEXT, size=13),
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>",
    )
    fig_pay.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=TEXT),
        showlegend=False,
        margin=dict(l=70, r=70, t=20, b=20),
        height=460,
    )
    st.plotly_chart(fig_pay, use_container_width=True,
                    config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Payment mode over time + Revenue per bed-day
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.markdown(
        '<div class="section-label">Monthly Revenue by Payment Mode</div>',
        unsafe_allow_html=True,
    )
    pay_monthly = (
        rev_trend.groupby(["ym", "payment_mode"], observed=True)["amount"]
        .sum()
        .reset_index()
        .sort_values("ym")
    )
    fig_paytrend = px.area(
        pay_monthly,
        x="ym", y="amount",
        color="payment_mode",
        color_discrete_map={"Insurance": CYAN, "Self-Pay": PURPLE},
    )
    fig_paytrend.update_traces(
        line=dict(width=1.8),
        hovertemplate="<b>%{x}</b><br>%{fullData.name}: ₹%{y:,.0f}<extra></extra>",
    )
    style_dark(fig_paytrend, height=500)

    # Headroom above the peak so the area doesn't hit the top edge.
    peak_pm = pay_monthly.groupby("ym")["amount"].sum().max()
    fig_paytrend.update_layout(
        xaxis_title=None,
        yaxis=dict(
            title=dict(text="Revenue (₹)", font=dict(color=TEXT_DIM, size=12)),
            range=[0, peak_pm * 1.15],
            tickformat=".2s",
        ),
        margin=dict(l=30, r=30, t=70, b=40),
        legend_title_text="",
    )
    st.plotly_chart(fig_paytrend, use_container_width=True,
                    config={"displayModeBar": False})

with c2:
    st.markdown(
        '<div class="section-label">Revenue per Bed-Day by Department</div>',
        unsafe_allow_html=True,
    )
    dept_eff = (
        billing_full.groupby("department", observed=True)
        .apply(
            lambda g: pd.Series({
                "revenue": g["amount"].sum(),
                "bed_days": g["length_of_stay"].sum(),
            }),
            include_groups=False,
        )
        .reset_index()
    )
    dept_eff["department"] = dept_eff["department"].astype(str)
    dept_eff["rev_per_day"] = dept_eff["revenue"] / dept_eff["bed_days"]
    dept_eff = dept_eff.sort_values("rev_per_day", ascending=True)
    dept_eff["label"] = dept_eff["rev_per_day"].apply(lambda v: f"₹{v:,.0f}")

    fig_eff = px.bar(
        dept_eff,
        x="rev_per_day", y="department",
        orientation="h",
        color="rev_per_day",
        color_continuous_scale=[
            [0.0, "#1a1240"],
            [0.5, PURPLE],
            [1.0, "#a855f7"],
        ],
        text="label",
    )
    fig_eff.update_traces(
        textposition="outside",
        textfont=dict(color=TEXT, size=11, family="JetBrains Mono"),
        marker=dict(cornerradius=5, line=dict(width=0)),
        hovertemplate="<b>%{y}</b><br>₹%{x:,.0f} per bed-day<extra></extra>",
    )
    style_dark(fig_eff, height=500)

    max_eff = dept_eff["rev_per_day"].max()
    fig_eff.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        xaxis=dict(
            title=dict(text="Revenue per bed-day (₹)",
                       font=dict(color=TEXT_DIM, size=12)),
            range=[0, max_eff * 1.30],
        ),
        yaxis_title=None,
        margin=dict(l=30, r=30, t=50, b=40),
    )
    st.plotly_chart(fig_eff, use_container_width=True,
                    config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Top insurance providers + Bill distribution
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.markdown(
        '<div class="section-label">Top Insurance Providers · Total Billed</div>',
        unsafe_allow_html=True,
    )
    providers = (
        billing[billing["payment_mode"] == "Insurance"]
        .groupby("insurance_provider", observed=True)["amount"]
        .sum()
        .reset_index()
        .sort_values("amount", ascending=True)
    )
    providers["insurance_provider"] = providers["insurance_provider"].astype(str)
    providers["label"] = providers["amount"].apply(fmt_compact_rupees)

    # Distinct colour per insurer — no more uniform cyan bars.
    fig_prov = px.bar(
        providers,
        x="amount", y="insurance_provider",
        orientation="h",
        text="label",
        color="insurance_provider",
        color_discrete_map=INSURER_COLORS,
    )
    fig_prov.update_traces(
        textposition="outside",
        textfont=dict(color=TEXT, size=11, family="JetBrains Mono"),
        marker=dict(cornerradius=5, line=dict(width=0)),
        hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>",
    )
    style_dark(fig_prov, height=420)

    max_prov = providers["amount"].max()
    fig_prov.update_layout(
        showlegend=False,
        xaxis=dict(
            title=None,
            range=[0, max_prov * 1.22],
            tickformat=".2s",
        ),
        yaxis_title=None,
        margin=dict(l=30, r=30, t=50, b=30),
    )
    st.plotly_chart(fig_prov, use_container_width=True,
                    config={"displayModeBar": False})

with c2:
    st.markdown(
        '<div class="section-label">Bill Amount Distribution by Payment Mode</div>',
        unsafe_allow_html=True,
    )
    fig_box = px.box(
        billing,
        x="payment_mode",
        y="amount",
        color="payment_mode",
        color_discrete_map={"Insurance": CYAN, "Self-Pay": PURPLE},
        points=False,
    )
    fig_box.update_traces(
        line=dict(width=2),
        hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
    )
    style_dark(fig_box, height=420)
    fig_box.update_layout(
        showlegend=False,
        xaxis_title=None,
        yaxis=dict(
            title=dict(text="Bill amount (₹)", font=dict(color=TEXT_DIM, size=12)),
            tickformat=".2s",
        ),
        margin=dict(l=30, r=30, t=50, b=40),
    )
    st.plotly_chart(fig_box, use_container_width=True,
                    config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Revenue efficiency summary
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="section-label">Revenue Efficiency Summary</div>',
    unsafe_allow_html=True,
)

total_bed_days = billing_full["length_of_stay"].sum()
revenue_per_bed_day = total_revenue / total_bed_days
avg_insurance_coverage = (
    insurance_bills["insurance_covered"].sum()
    / insurance_bills["amount"].sum() * 100
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Total Bed-Days", f"{int(total_bed_days):,}")
    st.markdown(
        f'<div class="metric-sub">across {len(admissions):,} admissions</div>',
        unsafe_allow_html=True,
    )

with c2:
    st.metric("Revenue per Bed-Day", f"₹{revenue_per_bed_day:,.0f}")
    st.markdown(
        '<div class="metric-sub">hospital-wide average</div>',
        unsafe_allow_html=True,
    )

with c3:
    st.metric("Avg Insurance Coverage", f"{avg_insurance_coverage:.1f}%")
    st.markdown(
        '<div class="metric-sub">of insured bills</div>',
        unsafe_allow_html=True,
    )

with c4:
    st.metric("Self-Pay Total", fmt_rupees(total_self_pay))
    st.markdown(
        f'<div class="metric-sub">{100 - insurance_share:.1f}% of all bills</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "Financial Analytics · Built by Shahan Malik · "
    "Streamlit · SQLite · Plotly · Pandas · 2026"
)
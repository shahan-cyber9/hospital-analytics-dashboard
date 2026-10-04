"""
pages/5_💰_Finance.py
---------------------
Financial Analytics with cross-page filters.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.loader import load_all
from utils.filters import render_filters, apply_filters, apply_filters_by_admission_id
from utils.theme import (
    apply_page_style, style_dark, section_label, page_header,
    CYAN, CYAN_BRIGHT, CYAN_DEEP, PURPLE, GREEN, AMBER, RED,
    TEXT, TEXT_DIM, DARK, DEPT_COLORS,
)


st.set_page_config(
    page_title="Finance · Smart Hospital",
    page_icon="💰",
    layout="wide",
)
apply_page_style()


INSURER_COLORS = {
    "Star Health":   "#22d3ee",
    "HDFC Ergo":     "#a78bfa",
    "ICICI Lombard": "#fb7185",
    "Niva Bupa":     "#fbbf24",
    "Bajaj Allianz": "#4ade80",
    "Care Health":   "#c084fc",
}


def fmt_rupees(v, unit="Cr"):
    return f"₹{v / 1e7:,.2f} Cr" if unit == "Cr" else f"₹{v / 1e5:,.2f} L"


def fmt_compact_rupees(v):
    if v >= 1e7: return f"₹{v / 1e7:.1f} Cr"
    if v >= 1e5: return f"₹{v / 1e5:.1f} L"
    return f"₹{v:,.0f}"


@st.cache_data(ttl=600, show_spinner="Loading financial data...")
def get_data() -> dict:
    return load_all()


data = get_data()
admissions_raw = data["admissions"]
billing_raw = data["billing"]

filters = render_filters(data)

admissions = apply_filters(admissions_raw, filters)
billing = apply_filters_by_admission_id(billing_raw, admissions)

billing_full = billing.merge(
    admissions[["admission_id", "department", "admission_date",
                "length_of_stay", "admission_ym"]],
    on="admission_id", how="left",
)


page_header(
    "Financial Analytics",
    "Revenue performance across departments, payment modes, and time. "
    "Identifies the biggest contributors to hospital income and the "
    "balance between insurance-covered and self-paid care."
)

if billing.empty:
    st.warning("No data matches the current filters. Adjust or reset the filters in the sidebar.")
    st.stop()


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
# Monthly revenue + rolling avg
# ---------------------------------------------------------------------------
section_label("Monthly Revenue · Last 24 Complete Months")
anchor = billing_full["admission_date"].max()
current_month_start = anchor.replace(day=1)

rev_trend = billing_full[billing_full["admission_date"] < current_month_start].copy()
rev_trend["ym"] = rev_trend["admission_date"].dt.strftime("%Y-%m")
monthly_rev = (
    rev_trend.groupby("ym")["amount"].sum()
    .reset_index(name="revenue").sort_values("ym")
)
monthly_rev["rolling_6"] = monthly_rev["revenue"].rolling(window=6).mean()
rolling_view = monthly_rev.dropna(subset=["rolling_6"])

fig_rev = go.Figure()
fig_rev.add_trace(go.Bar(
    x=monthly_rev["ym"], y=monthly_rev["revenue"],
    name="Monthly revenue",
    marker=dict(color="rgba(0, 212, 255, 0.45)",
                line=dict(color="rgba(0, 212, 255, 0.9)", width=1),
                cornerradius=4),
    hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>",
))
fig_rev.add_trace(go.Scatter(
    x=rolling_view["ym"], y=rolling_view["rolling_6"],
    name="6-month average", mode="lines+markers",
    line=dict(color=PURPLE, width=3),
    marker=dict(size=6, color=PURPLE, line=dict(color=DARK, width=1.5)),
    hovertemplate="<b>%{x}</b><br>6-mo avg: ₹%{y:,.0f}<extra></extra>",
))
style_dark(fig_rev, height=440)
fig_rev.update_layout(
    yaxis=dict(title=dict(text="Revenue (₹)", font=dict(color=TEXT_DIM, size=12))),
    xaxis_title=None, hovermode="x unified", bargap=0.15,
)
st.plotly_chart(fig_rev, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Treemap + Donut
# ---------------------------------------------------------------------------
c1, c2 = st.columns([2, 1])

with c1:
    section_label("Revenue by Department · Treemap")
    dept_rev = (
        billing_full.groupby("department", observed=True)["amount"].sum()
        .reset_index().sort_values("amount", ascending=False)
    )
    dept_rev["department"] = dept_rev["department"].astype(str)

    fig_tree = px.treemap(
        dept_rev, path=["department"], values="amount",
        color="department", color_discrete_map=DEPT_COLORS,
    )
    fig_tree.update_traces(
        texttemplate="<b>%{label}</b><br>%{percentRoot:.0%}",
        textfont=dict(size=13, family="Inter, sans-serif", color=DARK),
        hovertemplate=("<b>%{label}</b><br>Revenue: ₹%{value:,.0f}<br>"
                       "Share: %{percentRoot:.2%}<extra></extra>"),
        marker=dict(line=dict(color=DARK, width=2)),
    )
    fig_tree.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=20, b=20), height=460,
        font=dict(family="Inter, sans-serif", color=TEXT),
    )
    st.plotly_chart(fig_tree, use_container_width=True, config={"displayModeBar": False})

with c2:
    section_label("Payment Mode Split")
    pay_split = (
        billing.groupby("payment_mode", observed=True)["amount"].sum()
        .reset_index().sort_values("amount", ascending=False)
    )
    fig_pay = px.pie(
        pay_split, names="payment_mode", values="amount", hole=0.55,
        color="payment_mode",
        color_discrete_map={"Insurance": CYAN, "Self-Pay": PURPLE},
    )
    fig_pay.update_traces(
        textposition="outside", textinfo="percent+label",
        textfont=dict(color=TEXT, size=13),
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>",
    )
    fig_pay.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=TEXT),
        showlegend=False, margin=dict(l=70, r=70, t=20, b=20), height=460,
    )
    st.plotly_chart(fig_pay, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Payment trend + Rev per bed-day
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    section_label("Monthly Revenue by Payment Mode")
    pay_monthly = (
        rev_trend.groupby(["ym", "payment_mode"], observed=True)["amount"].sum()
        .reset_index().sort_values("ym")
    )
    fig_paytrend = px.area(
        pay_monthly, x="ym", y="amount", color="payment_mode",
        color_discrete_map={"Insurance": CYAN, "Self-Pay": PURPLE},
    )
    fig_paytrend.update_traces(
        line=dict(width=1.8),
        hovertemplate="<b>%{x}</b><br>%{fullData.name}: ₹%{y:,.0f}<extra></extra>",
    )
    style_dark(fig_paytrend, height=500)
    peak_pm = pay_monthly.groupby("ym")["amount"].sum().max() if not pay_monthly.empty else 1
    fig_paytrend.update_layout(
        xaxis_title=None,
        yaxis=dict(title=dict(text="Revenue (₹)", font=dict(color=TEXT_DIM, size=12)),
                   range=[0, peak_pm * 1.15], tickformat=".2s"),
        margin=dict(l=30, r=30, t=70, b=40), legend_title_text="",
    )
    st.plotly_chart(fig_paytrend, use_container_width=True, config={"displayModeBar": False})

with c2:
    section_label("Revenue per Bed-Day by Department")
    dept_eff = (
        billing_full.groupby("department", observed=True)
        .apply(lambda g: pd.Series({
            "revenue": g["amount"].sum(),
            "bed_days": g["length_of_stay"].sum(),
        }), include_groups=False).reset_index()
    )
    dept_eff["department"] = dept_eff["department"].astype(str)
    dept_eff["rev_per_day"] = dept_eff["revenue"] / dept_eff["bed_days"]
    dept_eff = dept_eff.sort_values("rev_per_day", ascending=True)
    dept_eff["label"] = dept_eff["rev_per_day"].apply(lambda v: f"₹{v:,.0f}")

    fig_eff = px.bar(
        dept_eff, x="rev_per_day", y="department", orientation="h",
        color="rev_per_day",
        color_continuous_scale=[[0.0, "#1a1240"], [0.5, PURPLE], [1.0, "#a855f7"]],
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
        showlegend=False, coloraxis_showscale=False,
        xaxis=dict(title=dict(text="Revenue per bed-day (₹)",
                              font=dict(color=TEXT_DIM, size=12)),
                   range=[0, max_eff * 1.30]),
        yaxis_title=None, margin=dict(l=30, r=30, t=50, b=40),
    )
    st.plotly_chart(fig_eff, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Providers + Box
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    section_label("Top Insurance Providers · Total Billed")
    providers = (
        billing[billing["payment_mode"] == "Insurance"]
        .groupby("insurance_provider", observed=True)["amount"].sum()
        .reset_index().sort_values("amount", ascending=True)
    )
    providers["insurance_provider"] = providers["insurance_provider"].astype(str)
    providers["label"] = providers["amount"].apply(fmt_compact_rupees)

    fig_prov = px.bar(
        providers, x="amount", y="insurance_provider", orientation="h",
        text="label", color="insurance_provider",
        color_discrete_map=INSURER_COLORS,
    )
    fig_prov.update_traces(
        textposition="outside",
        textfont=dict(color=TEXT, size=11, family="JetBrains Mono"),
        marker=dict(cornerradius=5, line=dict(width=0)),
        hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>",
    )
    style_dark(fig_prov, height=420)
    max_prov = providers["amount"].max() if not providers.empty else 1
    fig_prov.update_layout(
        showlegend=False,
        xaxis=dict(title=None, range=[0, max_prov * 1.22], tickformat=".2s"),
        yaxis_title=None, margin=dict(l=30, r=30, t=50, b=30),
    )
    st.plotly_chart(fig_prov, use_container_width=True, config={"displayModeBar": False})

with c2:
    section_label("Bill Amount Distribution by Payment Mode")
    fig_box = px.box(
        billing, x="payment_mode", y="amount", color="payment_mode",
        color_discrete_map={"Insurance": CYAN, "Self-Pay": PURPLE},
        points=False,
    )
    fig_box.update_traces(
        line=dict(width=2),
        hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
    )
    style_dark(fig_box, height=420)
    fig_box.update_layout(
        showlegend=False, xaxis_title=None,
        yaxis=dict(title=dict(text="Bill amount (₹)", font=dict(color=TEXT_DIM, size=12)),
                   tickformat=".2s"),
        margin=dict(l=30, r=30, t=50, b=40),
    )
    st.plotly_chart(fig_box, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Efficiency summary
# ---------------------------------------------------------------------------
section_label("Revenue Efficiency Summary")
total_bed_days = billing_full["length_of_stay"].sum()
revenue_per_bed_day = total_revenue / total_bed_days if total_bed_days else 0
avg_insurance_coverage = (
    insurance_bills["insurance_covered"].sum() / insurance_bills["amount"].sum() * 100
    if not insurance_bills.empty else 0
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total Bed-Days", f"{int(total_bed_days):,}")
    st.markdown(f'<div class="metric-sub">across {len(admissions):,} admissions</div>',
                unsafe_allow_html=True)
with c2:
    st.metric("Revenue per Bed-Day", f"₹{revenue_per_bed_day:,.0f}")
    st.markdown('<div class="metric-sub">hospital-wide average</div>',
                unsafe_allow_html=True)
with c3:
    st.metric("Avg Insurance Coverage", f"{avg_insurance_coverage:.1f}%")
    st.markdown('<div class="metric-sub">of insured bills</div>',
                unsafe_allow_html=True)
with c4:
    st.metric("Self-Pay Total", fmt_rupees(total_self_pay))
    st.markdown(f'<div class="metric-sub">{100 - insurance_share:.1f}% of all bills</div>',
                unsafe_allow_html=True)

st.divider()
st.caption("Financial Analytics · Built by Shahan Malik · Streamlit · SQLite · Plotly · Pandas · 2026")
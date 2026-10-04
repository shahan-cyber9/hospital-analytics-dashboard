"""
app.py
------
Smart Hospital Analytics Dashboard
Entry point for the Streamlit app.

Run:
    streamlit run app.py
"""

import streamlit as st

from utils.loader import load_all


# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Smart Hospital Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Data loading (cached)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=600, show_spinner="Loading hospital data...")
def get_data() -> dict:
    """Load all 7 tables once. Cached for 10 minutes."""
    return load_all()


# ---------------------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
        /* ---- Fonts ---- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

        html, body, [class*="css"], .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        /* ---- App background with subtle radial glow ---- */
        .stApp {
            background:
                radial-gradient(ellipse at top left, rgba(0, 212, 255, 0.06), transparent 55%),
                radial-gradient(ellipse at bottom right, rgba(123, 47, 247, 0.05), transparent 55%),
                linear-gradient(180deg, #0a0e1a 0%, #0c1220 50%, #0a0e1a 100%);
            color: #F0F2F6;
        }

        /* ---- Sidebar ---- */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(12, 18, 32, 0.98), rgba(10, 14, 26, 0.98));
            border-right: 1px solid rgba(0, 212, 255, 0.12);
        }
        [data-testid="stSidebar"] * {
            color: #c9d7ee;
            font-family: 'Inter', sans-serif;
        }
        [data-testid="stSidebarNav"] > ul > li:first-child { display: none; }

        /* ---- Metric cards ---- */
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, rgba(20, 30, 50, 0.7), rgba(15, 22, 38, 0.65));
            border: 1px solid rgba(0, 212, 255, 0.14);
            border-left: 3px solid #00d4ff;
            border-radius: 14px;
            padding: 20px 22px;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow:
                0 1px 3px rgba(0, 0, 0, 0.25),
                0 0 0 rgba(0, 212, 255, 0);
            animation: fadeInUp 0.6s ease both;
            min-width: 160px;
            overflow: hidden;
        }
        [data-testid="stMetric"]:hover {
            border-left-color: #7b2ff7;
            border-color: rgba(0, 212, 255, 0.35);
            box-shadow:
                0 12px 32px rgba(0, 212, 255, 0.12),
                0 0 24px rgba(0, 212, 255, 0.08);
            transform: translateY(-3px);
        }
        [data-testid="stMetricValue"] {
            color: #00d4ff;
            font-family: 'JetBrains Mono', 'Inter', monospace;
            font-weight: 700;
            font-variant-numeric: tabular-nums;
            font-size: clamp(1.4rem, 1.8vw, 2.1rem);
            letter-spacing: -0.02em;
            line-height: 1.15;
        }
        [data-testid="stMetricLabel"] {
            color: #A0AAB8;
            font-size: clamp(0.68rem, 0.85vw, 0.82rem);
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            white-space: normal;
            line-height: 1.35;
            min-height: 2.3em;
        }
        [data-testid="stMetricDelta"] {
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
        }

        /* ---- Prevent column collapse on zoom-out ---- */
        [data-testid="column"] {
            min-width: 150px !important;
            padding: 0 6px;
        }

        /* ---- Hero title ---- */
        .hero-title {
            font-size: clamp(2rem, 3.6vw, 3.2rem);
            font-weight: 800;
            background: linear-gradient(90deg, #00d4ff 0%, #7b2ff7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.3rem;
            letter-spacing: -0.03em;
            line-height: 1.15;
            padding-top: 0.4rem;
            animation: fadeInUp 0.8s ease both;
        }
        .hero-subtitle {
            color: #A0AAB8;
            font-size: clamp(0.95rem, 1.1vw, 1.15rem);
            font-weight: 400;
            line-height: 1.6;
            margin-bottom: 2rem;
            max-width: 780px;
            animation: fadeInUp 0.9s ease both;
        }

        /* ---- Sidebar nav polish ---- */
        [data-testid="stSidebar"] ul { padding-left: 0.5rem; }
        [data-testid="stSidebar"] li {
            list-style: none;
            padding: 8px 12px;
            margin: 3px 0;
            border-radius: 9px;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            font-weight: 500;
        }
        [data-testid="stSidebar"] li:hover {
            background: linear-gradient(90deg, rgba(0, 212, 255, 0.1), rgba(0, 212, 255, 0.02));
            padding-left: 16px;
            color: #00d4ff;
        }

        /* ---- Dividers ---- */
        hr {
            border: none;
            border-top: 1px solid rgba(0, 212, 255, 0.1);
            margin: 1.6rem 0;
        }

        /* ---- Section headers ---- */
        h4 {
            font-weight: 700;
            letter-spacing: -0.01em;
            color: #F0F2F6;
        }

        /* ---- Keyframes ---- */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(10px); }
            to   { opacity: 1; transform: translateY(0);    }
        }

        /* ---- Hide Streamlit chrome ---- */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
data = get_data()
patients = data["patients"]
doctors = data["doctors"]
departments = data["departments"]
admissions = data["admissions"]
icu = data["icu"]
emergency = data["emergency"]
billing = data["billing"]


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        "<h3 style='margin:0; font-weight:700; letter-spacing:-0.01em;'>"
        "🏥 Smart Hospital</h3>"
        "<p style='margin:2px 0 0 0; color:#A0AAB8; font-size:0.9rem;'>"
        "Analytics Dashboard</p>",
        unsafe_allow_html=True,
    )
    st.caption("Version 1.0 · Mentor Mode")
    st.divider()
    st.markdown(
        f"<p style='color:#6b7f9e; font-size:0.78rem; letter-spacing:0.05em; "
        f"text-transform:uppercase; margin-bottom:6px;'>Data Coverage</p>"
        f"<p style='color:#c9d7ee; font-size:0.88rem; line-height:1.9; margin:0;'>"
        f"Patients &nbsp;<b style='color:#00d4ff;'>{len(patients):,}</b><br>"
        f"Admissions &nbsp;<b style='color:#00d4ff;'>{len(admissions):,}</b><br>"
        f"Time span &nbsp;<b>{admissions['admission_date'].min().strftime('%b %Y')}"
        f" to {admissions['admission_date'].max().strftime('%b %Y')}</b>"
        f"</p>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Hero section
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="hero-title">Smart Hospital Analytics</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero-subtitle">'
    "A unified operational view spanning patient flow, emergency response, "
    "intensive care load, and financial performance. "
    "Powered by more than 66,000 records across 15 departments."
    "</div>",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# KPI row 1
# ---------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Patients", f"{len(patients):,}")
col2.metric("Total Admissions", f"{len(admissions):,}")
col3.metric("Doctors on Staff", f"{len(doctors):,}")
col4.metric("Departments", f"{len(departments)}")


# ---------------------------------------------------------------------------
# KPI row 2
# ---------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

total_revenue = billing["amount"].sum()
avg_los = admissions["length_of_stay"].mean()

col1.metric("Total Revenue", f"₹{total_revenue / 1e7:.0f} Cr")
col2.metric("Avg Length of Stay", f"{avg_los:.1f} days")
col3.metric("ICU Stays", f"{len(icu):,}")
col4.metric("Emergency Visits", f"{len(emergency):,}")


# ---------------------------------------------------------------------------
# Roadmap
# ---------------------------------------------------------------------------
st.divider()
st.markdown("#### What's coming next")
st.markdown(
    """
    <p style='color:#A0AAB8; line-height:1.9; font-size:0.95rem;'>
    <b style='color:#00d4ff;'>Patient Analytics</b> explores age, gender,
    diagnosis, and readmission patterns.<br>
    <b style='color:#00d4ff;'>Emergency</b> surfaces peak hours and wait time
    trends across severity levels.<br>
    <b style='color:#00d4ff;'>ICU</b> tracks occupancy, ventilator use, and
    oxygen demand.<br>
    <b style='color:#00d4ff;'>Finance</b> breaks down revenue by department
    and payment mode.<br>
    <b style='color:#00d4ff;'>Doctors</b> compares workload and department
    performance.
    </p>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "Built by Shahan Malik · Streamlit · SQLite · Plotly · Pandas · 2026"
)
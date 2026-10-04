"""
app.py
------
Smart Hospital Analytics Dashboard — Homepage.
Entry point for the Streamlit app.

Run:
    streamlit run app.py
"""

import streamlit as st

from utils.loader import load_all


# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
# st.set_page_config MUST be the first Streamlit call in the script.
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
    """
    Load all 7 tables once. Cached for 10 minutes (ttl=600 seconds).

    First run: reads CSVs.
    Every rerun within 10 minutes: returns cached DataFrames instantly.
    """
    return load_all()


# ---------------------------------------------------------------------------
# Custom CSS — dark theme, glass-morphism, hover effects
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
        /* ---------- App background ---------- */
        .stApp {
            background: linear-gradient(180deg, #0a0e1a 0%, #0f1525 100%);
            color: #e6edf7;
        }

        /* ---------- Sidebar ---------- */
        [data-testid="stSidebar"] {
            background: rgba(15, 21, 37, 0.95);
            border-right: 1px solid rgba(0, 200, 255, 0.15);
        }
        [data-testid="stSidebar"] * {
            color: #c9d7ee;
        }

        /* ---------- Metric cards ---------- */
        [data-testid="stMetric"] {
            background: rgba(20, 30, 50, 0.55);
            border: 1px solid rgba(0, 200, 255, 0.18);
            border-radius: 14px;
            padding: 18px 20px;
            backdrop-filter: blur(8px);
            transition: all 0.25s ease;
            box-shadow: 0 0 0 rgba(0, 212, 255, 0);
            animation: fadeInUp 0.6s ease both;
        }
        [data-testid="stMetric"]:hover {
            border-color: rgba(0, 212, 255, 0.45);
            box-shadow: 0 8px 24px rgba(0, 212, 255, 0.15);
            transform: translateY(-2px);
        }
        [data-testid="stMetricValue"] {
            color: #00d4ff;
            font-weight: 700;
        }
        [data-testid="stMetricLabel"] {
            color: #8ba3c7;
            font-size: 0.85rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        /* ---------- Hero title ---------- */
        .hero-title {
            font-size: 3.2rem;
            font-weight: 800;
            background: linear-gradient(90deg, #00d4ff 0%, #7b2ff7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.2rem;
            letter-spacing: -0.02em;
            padding-top: 0.4rem;
            line-height: 1.25;
            animation: fadeInUp 0.8s ease both;
        }
        .hero-subtitle {
            color: #8ba3c7;
            font-size: 1.1rem;
            margin-bottom: 2rem;
            max-width: 780px;
            animation: fadeInUp 0.9s ease both;
        }

        /* ---------- Sidebar nav list ---------- */
        [data-testid="stSidebar"] ul {
            padding-left: 0.6rem;
        }
        [data-testid="stSidebar"] li {
            list-style: none;
            padding: 6px 10px;
            margin: 2px 0;
            border-radius: 8px;
            transition: background 0.2s ease, padding-left 0.2s ease;
        }
        [data-testid="stSidebar"] li:hover {
            background: rgba(0, 212, 255, 0.08);
            padding-left: 14px;
        }

        /* ---------- Dividers ---------- */
        hr {
            border-color: rgba(0, 200, 255, 0.12);
        }

        /* ---------- Keyframes ---------- */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(8px); }
            to   { opacity: 1; transform: translateY(0);   }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Load data once
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
    st.markdown("### 🏥 Smart Hospital")
    st.markdown("**Analytics Dashboard**")
    st.caption("v1.0 · Mentor Mode")
    st.divider()
    st.markdown("#### Navigation")
    st.markdown(
        """
        - 🏠 **Home** *(you are here)*
        - 📊 Executive Overview *(Ch 6)*
        - 👥 Patient Analytics *(Ch 7)*
        - 🚑 Emergency *(Ch 8)*
        - 🫀 ICU *(Ch 9)*
        - 💰 Finance *(Ch 10)*
        - 👨‍⚕️ Doctors *(Ch 11)*
        """
    )
    st.divider()
    st.caption(f"Patients: {len(patients):,}")
    st.caption(f"Admissions: {len(admissions):,}")
    st.caption(
        f"Date range: {admissions['admission_date'].min().date()} "
        f"→ {admissions['admission_date'].max().date()}"
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
    "A unified view of patients, admissions, emergency response, "
    "ICU load, and hospital finances — powered by 66,000+ records."
    "</div>",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# KPI row 1 — hospital scale
# ---------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Patients", f"{len(patients):,}")
col2.metric("Total Admissions", f"{len(admissions):,}")
col3.metric("Doctors on Staff", f"{len(doctors):,}")
col4.metric("Departments", f"{len(departments)}")


# ---------------------------------------------------------------------------
# KPI row 2 — operational & financial
# ---------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

total_revenue = billing["amount"].sum()
avg_los = admissions["length_of_stay"].mean()

col1.metric("Total Revenue", f"₹{total_revenue / 1e7:.0f} Cr")
col2.metric("Avg Length of Stay", f"{avg_los:.1f} days")
col3.metric("ICU Stays", f"{len(icu):,}")
col4.metric("Emergency Visits", f"{len(emergency):,}")


# ---------------------------------------------------------------------------
# Placeholder for future chapters
# ---------------------------------------------------------------------------
st.divider()
st.markdown("#### Coming Next")
st.markdown(
    """
    - **Chapter 6** — Executive Overview with trend indicators
    - **Chapter 7** — Patient analytics: age, gender, disease, readmission
    - **Chapter 8** — Emergency peak hours and wait time trends
    - **Chapter 9** — ICU occupancy gauges and ventilator utilisation
    - **Chapter 10** — Revenue by department, insurance vs self-pay
    - **Chapter 11** — Doctor performance and department comparison
    - **Chapter 12–15** — Interactive filters, advanced Plotly, reports
    """
)


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "Built by **Shahan Malik** · Streamlit · SQLite · Plotly · Pandas"
)
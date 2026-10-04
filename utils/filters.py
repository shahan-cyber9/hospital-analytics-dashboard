"""
filters.py
----------
Cross-page filter system for the Smart Hospital Analytics Dashboard.

We deliberately do NOT use `key=` on the widgets. Streamlit's widget-key
behaviour can reset values across page navigation. Instead, we store the
value directly in st.session_state and pass it back as the widget's
`default=`/`value=` on every render. This is bulletproof.

Public API:
    render_filters(data)                     -> dict
    apply_filters(admissions, filters)       -> DataFrame
    apply_filters_by_admission_id(df, adm_f) -> DataFrame
"""

import pandas as pd
import streamlit as st


# Persistent-value keys (NOT widget keys).
KEY_DATE_RANGE = "flt_date_range"
KEY_DEPARTMENTS = "flt_departments"
KEY_DOCTORS = "flt_doctors"
KEY_SEVERITY = "flt_severity"


# ---------------------------------------------------------------------------
# Defaults / reset
# ---------------------------------------------------------------------------
def _default_date_range(data: dict) -> tuple:
    adm = data["admissions"]
    return (
        adm["admission_date"].min().date(),
        adm["admission_date"].max().date(),
    )


def _reset_all(data: dict) -> None:
    """Callback target for Reset button. Runs before widgets on next rerun."""
    st.session_state[KEY_DATE_RANGE] = _default_date_range(data)
    st.session_state[KEY_DEPARTMENTS] = []
    st.session_state[KEY_DOCTORS] = []
    st.session_state[KEY_SEVERITY] = []


# ---------------------------------------------------------------------------
# Sidebar UI
# ---------------------------------------------------------------------------
def render_filters(data: dict) -> dict:
    """
    Render sidebar filters and return current values as a dict.

    Call this near the top of every page. The sidebar UI is identical
    everywhere, and values live in session_state so they survive navigation.
    """
    adm = data["admissions"]
    doctors = data["doctors"]

    min_date, max_date = _default_date_range(data)

    # Seed on first call.
    if KEY_DATE_RANGE not in st.session_state:
        st.session_state[KEY_DATE_RANGE] = (min_date, max_date)
    if KEY_DEPARTMENTS not in st.session_state:
        st.session_state[KEY_DEPARTMENTS] = []
    if KEY_DOCTORS not in st.session_state:
        st.session_state[KEY_DOCTORS] = []
    if KEY_SEVERITY not in st.session_state:
        st.session_state[KEY_SEVERITY] = []

    with st.sidebar:
        st.markdown("### 🎛️ Filters")
        st.caption("Applies to every page")

        # --- Date range ---
        # `value=` supplies the current stored range. No key= needed.
        current_range = st.session_state[KEY_DATE_RANGE]
        date_val = st.date_input(
            "Date range",
            value=current_range,
            min_value=min_date,
            max_value=max_date,
        )
        # date_input can transiently return a 1-tuple mid-selection.
        if isinstance(date_val, tuple) and len(date_val) == 2:
            st.session_state[KEY_DATE_RANGE] = date_val

        # --- Departments ---
        all_depts = sorted(adm["department"].astype(str).unique().tolist())
        dept_val = st.multiselect(
            "Departments",
            options=all_depts,
            default=st.session_state[KEY_DEPARTMENTS],
            placeholder="All departments",
        )
        st.session_state[KEY_DEPARTMENTS] = dept_val

        # --- Doctors ---
        all_doctors = sorted(doctors["name"].astype(str).unique().tolist())
        doc_val = st.multiselect(
            "Doctors",
            options=all_doctors,
            default=st.session_state[KEY_DOCTORS],
            placeholder="All doctors",
        )
        st.session_state[KEY_DOCTORS] = doc_val

        # --- Severity ---
        all_sev = ["Critical", "Serious", "Moderate", "Stable"]
        sev_val = st.multiselect(
            "ER severity",
            options=all_sev,
            default=st.session_state[KEY_SEVERITY],
            placeholder="All severity levels",
        )
        st.session_state[KEY_SEVERITY] = sev_val

        st.divider()

        # --- Reset via callback (runs before widgets on next rerun) ---
        st.button(
            "Reset all filters",
            on_click=_reset_all,
            args=(data,),
            use_container_width=True,
        )

        # --- Active filter summary ---
        active = []
        if st.session_state[KEY_DEPARTMENTS]:
            active.append(f"{len(st.session_state[KEY_DEPARTMENTS])} depts")
        if st.session_state[KEY_DOCTORS]:
            active.append(f"{len(st.session_state[KEY_DOCTORS])} doctors")
        if st.session_state[KEY_SEVERITY]:
            active.append(f"{len(st.session_state[KEY_SEVERITY])} severity")
        if st.session_state[KEY_DATE_RANGE] != (min_date, max_date):
            active.append("custom date range")

        if active:
            st.caption("Active: " + " · ".join(active))
        else:
            st.caption("No filters active — showing all data")

    return {
        "date_range": st.session_state[KEY_DATE_RANGE],
        "departments": st.session_state[KEY_DEPARTMENTS],
        "doctors": st.session_state[KEY_DOCTORS],
        "severity": st.session_state[KEY_SEVERITY],
    }


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------
def apply_filters(admissions: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Filter an admissions DataFrame by date range and department.
    Requires columns: admission_date, department.
    """
    if admissions.empty:
        return admissions
    df = admissions.copy()
    start, end = filters["date_range"]
    df = df[
        (df["admission_date"].dt.date >= start)
        & (df["admission_date"].dt.date <= end)
    ]
    if filters["departments"]:
        df = df[df["department"].astype(str).isin(filters["departments"])]
    return df


def apply_filters_by_admission_id(df: pd.DataFrame,
                                   admissions_filtered: pd.DataFrame) -> pd.DataFrame:
    """Filter a DataFrame with an admission_id column down to matching rows."""
    if df.empty or "admission_id" not in df.columns:
        return df
    valid_ids = set(admissions_filtered["admission_id"])
    return df[df["admission_id"].isin(valid_ids)]
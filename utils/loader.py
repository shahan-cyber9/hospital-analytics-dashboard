"""
loader.py
---------
Central data-loading module for the Smart Hospital Analytics Dashboard.

Every page of the dashboard imports from this file — no page reads CSVs directly.
This guarantees consistent cleaning, types, and feature engineering everywhere.

Public API:
    load_patients()      -> DataFrame
    load_doctors()       -> DataFrame
    load_departments()   -> DataFrame
    load_admissions()    -> DataFrame
    load_icu()           -> DataFrame
    load_emergency()     -> DataFrame
    load_billing()       -> DataFrame
    load_all()           -> dict[str, DataFrame]
    clear_cache()        -> None  (used in testing)
"""

from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Paths and caching
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Simple module-level cache. Streamlit will add a fancier one in Chapter 16.
_cache: dict[str, pd.DataFrame] = {}


def clear_cache() -> None:
    """Empty the cache. Call this in tests, or after regenerating CSVs."""
    _cache.clear()


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------
def _load_csv(name: str) -> pd.DataFrame:
    """Read data/<name>.csv, raising a helpful error if it doesn't exist."""
    path = DATA_DIR / f"{name}.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}.\n"
            f"Run:  python data/generate_data.py"
        )
    return pd.read_csv(path)


# Indian seasons by month (IMD convention).
_SEASON_BY_MONTH = {
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Summer", 4: "Summer", 5: "Summer",
    6: "Monsoon", 7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
    10: "Post-Monsoon", 11: "Post-Monsoon",
}


def _add_age_group(df: pd.DataFrame) -> pd.DataFrame:
    """Add an age_group column using sensible medical brackets."""
    bins = [0, 18, 30, 45, 60, 75, 200]
    labels = ["0-17", "18-29", "30-44", "45-59", "60-74", "75+"]
    df["age_group"] = pd.cut(df["age"], bins=bins, labels=labels, right=False)
    return df


# ---------------------------------------------------------------------------
# Public loaders
# ---------------------------------------------------------------------------
def load_patients() -> pd.DataFrame:
    """Patients with dates parsed, categoricals set, and age_group added."""
    if "patients" in _cache:
        return _cache["patients"]

    df = _load_csv("patients")
    df["registration_date"] = pd.to_datetime(df["registration_date"])
    df["gender"] = df["gender"].astype("category")
    df["blood_group"] = df["blood_group"].astype("category")
    df["city"] = df["city"].astype("category")
    df = _add_age_group(df)

    _cache["patients"] = df
    return df


def load_doctors() -> pd.DataFrame:
    """Doctors with join_date parsed and department as categorical."""
    if "doctors" in _cache:
        return _cache["doctors"]

    df = _load_csv("doctors")
    df["join_date"] = pd.to_datetime(df["join_date"])
    df["department"] = df["department"].astype("category")

    _cache["doctors"] = df
    return df


def load_departments() -> pd.DataFrame:
    """Departments lookup table."""
    if "departments" in _cache:
        return _cache["departments"]

    df = _load_csv("departments")
    df["department"] = df["department"].astype("category")

    _cache["departments"] = df
    return df


def load_admissions() -> pd.DataFrame:
    """
    Admissions with dates parsed, booleans, and engineered features:
        admission_year, admission_month, admission_month_name,
        admission_ym, admission_quarter, admission_dow, season
    """
    if "admissions" in _cache:
        return _cache["admissions"]

    df = _load_csv("admissions")
    df["admission_date"] = pd.to_datetime(df["admission_date"])
    df["discharge_date"] = pd.to_datetime(df["discharge_date"])
    df["is_readmission"] = df["is_readmission"].astype(bool)
    df["department"] = df["department"].astype("category")
    df["outcome"] = df["outcome"].astype("category")

    # Feature engineering from the admission date.
    df["admission_year"] = df["admission_date"].dt.year
    df["admission_month"] = df["admission_date"].dt.month
    df["admission_month_name"] = df["admission_date"].dt.strftime("%b")
    df["admission_ym"] = df["admission_date"].dt.strftime("%Y-%m")
    df["admission_quarter"] = df["admission_date"].dt.quarter
    df["admission_dow"] = df["admission_date"].dt.day_name()
    df["season"] = df["admission_month"].map(_SEASON_BY_MONTH)

    _cache["admissions"] = df
    return df


def load_icu() -> pd.DataFrame:
    """ICU stays with dates parsed and booleans set."""
    if "icu" in _cache:
        return _cache["icu"]

    df = _load_csv("icu")
    df["icu_admit_date"] = pd.to_datetime(df["icu_admit_date"])
    df["icu_discharge_date"] = pd.to_datetime(df["icu_discharge_date"])
    df["ventilator_used"] = df["ventilator_used"].astype(bool)
    df["oxygen_required"] = df["oxygen_required"].astype(bool)

    _cache["icu"] = df
    return df


def load_emergency() -> pd.DataFrame:
    """
    Emergency visits with arrival_time parsed, severity as ordered categorical,
    plus arrival_hour, arrival_dow, and is_peak_hour.
    """
    if "emergency" in _cache:
        return _cache["emergency"]

    df = _load_csv("emergency")
    df["arrival_time"] = pd.to_datetime(df["arrival_time"])
    df["ambulance_arrival"] = df["ambulance_arrival"].astype(bool)
    df["severity"] = pd.Categorical(
        df["severity"],
        categories=["Critical", "Serious", "Moderate", "Stable"],
        ordered=True,
    )

    df["arrival_hour"] = df["arrival_time"].dt.hour
    df["arrival_dow"] = df["arrival_time"].dt.day_name()
    df["is_peak_hour"] = df["arrival_hour"].between(18, 22)

    _cache["emergency"] = df
    return df


def load_billing() -> pd.DataFrame:
    """
    Billing with a derived self_pay_amount column:
        amount - insurance_covered
    """
    if "billing" in _cache:
        return _cache["billing"]

    df = _load_csv("billing")
    df["payment_mode"] = df["payment_mode"].astype("category")
    df["insurance_provider"] = df["insurance_provider"].astype("category")
    df["self_pay_amount"] = df["amount"] - df["insurance_covered"]

    _cache["billing"] = df
    return df


def load_all() -> dict[str, pd.DataFrame]:
    """Load every table once. Returns a dict of DataFrames."""
    return {
        "patients":    load_patients(),
        "doctors":     load_doctors(),
        "departments": load_departments(),
        "admissions":  load_admissions(),
        "icu":         load_icu(),
        "emergency":   load_emergency(),
        "billing":     load_billing(),
    }
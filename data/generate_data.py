"""
generate_data.py
----------------
Generates realistic Indian hospital data for the Smart Hospital Analytics Dashboard.

Produces 7 CSV files inside the data/ folder:
    patients.csv      — 10,000 patients
    doctors.csv       — 200 doctors
    departments.csv   — 15 departments (lookup table)
    admissions.csv    — 25,000 hospital admissions (with readmission flag)
    icu.csv           — ICU stays (subset of admissions)
    emergency.csv     — Emergency room visits (hour-weighted wait times)
    billing.csv       — One bill per admission (with insurance coverage split)

Every run produces identical output (random seed = 42), so the dashboard
is reproducible.

Run once:
    python data/generate_data.py
"""

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
SEED = 42
random.seed(SEED)
Faker.seed(SEED)

fake = Faker("en_IN")

DATA_DIR = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------
DEPARTMENTS = [
    # name,               weight, avg_bill, icu_chance
    ("General Medicine",      22,     18_000, 0.05),
    ("Cardiology",            14,     85_000, 0.30),
    ("Orthopedics",           12,     60_000, 0.10),
    ("Pediatrics",            11,     15_000, 0.04),
    ("Emergency",             10,     22_000, 0.15),
    ("Gynecology",             9,     45_000, 0.08),
    ("Neurology",              7,     95_000, 0.25),
    ("Pulmonology",            5,     40_000, 0.18),
    ("Oncology",               4,    120_000, 0.20),
    ("Urology",                3,     55_000, 0.10),
    ("ENT",                    3,     25_000, 0.03),
    ("Dermatology",            2,     12_000, 0.01),
    ("Psychiatry",             2,     20_000, 0.02),
    ("Radiology",              1,     30_000, 0.05),
    ("ICU",                    1,    150_000, 0.95),
]

DIAGNOSES = {
    "General Medicine":  ["Viral Fever", "Dengue", "Typhoid", "Diabetes Check-up",
                          "Hypertension Follow-up", "Anemia", "Gastritis"],
    "Cardiology":        ["Coronary Artery Disease", "Myocardial Infarction",
                          "Heart Failure", "Arrhythmia", "Angina", "Hypertension"],
    "Orthopedics":       ["Fracture - Femur", "Fracture - Tibia", "ACL Tear",
                          "Arthritis", "Spinal Disc Herniation", "Joint Replacement"],
    "Pediatrics":        ["Neonatal Jaundice", "Bronchiolitis", "Viral Fever",
                          "Hand Foot Mouth Disease", "Pneumonia", "Malnutrition"],
    "Emergency":         ["Road Traffic Accident", "Poisoning", "Acute Trauma",
                          "Burn Injury", "Snake Bite", "Acute Abdomen"],
    "Gynecology":        ["Normal Delivery", "C-Section", "PCOS", "Fibroids",
                          "Ectopic Pregnancy", "Endometriosis"],
    "Neurology":         ["Stroke", "Epilepsy", "Migraine", "Meningitis",
                          "Parkinson's Disease", "Bell's Palsy"],
    "Pulmonology":       ["Asthma Exacerbation", "COPD", "Pneumonia",
                          "Pulmonary Embolism", "Tuberculosis", "Pleural Effusion"],
    "Oncology":          ["Breast Cancer - Chemo", "Lung Cancer - Chemo",
                          "Leukemia", "Colorectal Cancer", "Lymphoma", "Radiotherapy"],
    "Urology":           ["Kidney Stones", "UTI", "Prostate Enlargement",
                          "Renal Failure", "Bladder Surgery", "Hematuria"],
    "ENT":               ["Tonsillitis", "Sinusitis", "Septoplasty",
                          "Hearing Loss Evaluation", "Vertigo", "Otitis Media"],
    "Dermatology":       ["Psoriasis", "Eczema", "Fungal Infection",
                          "Acne Vulgaris", "Urticaria", "Vitiligo"],
    "Psychiatry":        ["Depression", "Anxiety Disorder", "Bipolar Disorder",
                          "Schizophrenia", "OCD", "Substance Abuse"],
    "Radiology":         ["MRI Evaluation", "CT Scan Follow-up",
                          "Ultrasound Guided Biopsy", "PET Scan",
                          "X-Ray Follow-up", "Angiography"],
    "ICU":               ["Septic Shock", "Respiratory Failure", "Multi-organ Failure",
                          "Post-Surgical Critical Care", "Cardiac Arrest Recovery",
                          "Severe Pneumonia"],
}

MONTH_WEIGHTS = {
    1: 1.20, 2: 1.15, 3: 1.00, 4: 0.90, 5: 0.85, 6: 0.75,
    7: 0.80, 8: 0.85, 9: 0.90, 10: 1.10, 11: 1.20, 12: 1.25,
}

DAY_WEIGHTS = {0: 1.30, 1: 1.15, 2: 1.05, 3: 1.00, 4: 0.95, 5: 0.75, 6: 0.80}

DEPARTMENT_AGE_RANGE = {
    "Pediatrics":       (0, 14),
    "Gynecology":       (18, 50),
    "Cardiology":       (45, 90),
    "Neurology":        (40, 90),
    "Oncology":         (30, 85),
    "Orthopedics":      (10, 85),
    "Pulmonology":      (30, 85),
    "Urology":          (30, 85),
    "Psychiatry":       (15, 75),
}

AVG_STAY_DAYS = {
    "General Medicine":  4,
    "Cardiology":        9,
    "Orthopedics":       7,
    "Pediatrics":        4,
    "Emergency":         2,
    "Gynecology":        4,
    "Neurology":        10,
    "Pulmonology":       7,
    "Oncology":         12,
    "Urology":           5,
    "ENT":               2,
    "Dermatology":       2,
    "Psychiatry":        7,
    "Radiology":         1,
    "ICU":              15,
}

INSURANCE_PROVIDERS = [
    "Star Health", "HDFC Ergo", "ICICI Lombard",
    "Niva Bupa", "Bajaj Allianz", "Care Health",
]

HOUR_WEIGHTS_ER = {
    0: 0.6, 1: 0.4, 2: 0.3, 3: 0.2, 4: 0.2, 5: 0.3,
    6: 0.5, 7: 0.7, 8: 0.9, 9: 1.0, 10: 1.0, 11: 1.1,
    12: 1.2, 13: 1.2, 14: 1.1, 15: 1.1, 16: 1.2, 17: 1.3,
    18: 1.6, 19: 1.8, 20: 1.7, 21: 1.4, 22: 1.1, 23: 0.8,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def random_age() -> int:
    """Return a realistic patient age using weighted buckets."""
    buckets = [
        (0,  14, 0.15),
        (15, 29, 0.20),
        (30, 44, 0.25),
        (45, 59, 0.22),
        (60, 74, 0.13),
        (75, 95, 0.05),
    ]
    r = random.random()
    cumulative = 0.0
    for low, high, weight in buckets:
        cumulative += weight
        if r <= cumulative:
            return random.randint(low, high)
    return 45


def _random_admission_date() -> date:
    """Pick a realistic admission date (seasonal + weekly pattern)."""
    end = date.today()
    start = end - timedelta(days=3 * 365)
    total_days = (end - start).days

    day_offset = random.randint(0, total_days)
    candidate = start + timedelta(days=day_offset)

    month_w = MONTH_WEIGHTS[candidate.month]
    day_w = DAY_WEIGHTS[candidate.weekday()]
    combined = month_w * day_w

    if random.random() < combined / 1.65:
        return candidate
    day_offset = random.randint(0, total_days)
    return start + timedelta(days=day_offset)


def _pick_department_for_age(patient_age: int) -> str:
    """Pick a department appropriate for the patient's age."""
    eligible, weights = [], []
    for name, weight, _avg_bill, _icu_chance in DEPARTMENTS:
        lo, hi = DEPARTMENT_AGE_RANGE.get(name, (0, 95))
        if lo <= patient_age <= hi:
            eligible.append(name)
            weights.append(weight)
    if not eligible:
        return "General Medicine"
    return random.choices(eligible, weights=weights)[0]


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------
def generate_patients(n: int = 10_000) -> pd.DataFrame:
    """Generate n patients with realistic Indian demographics."""
    rows = []
    for i in range(1, n + 1):
        gender = random.choices(["Male", "Female"], weights=[49, 51])[0]
        name = fake.name_male() if gender == "Male" else fake.name_female()

        rows.append({
            "patient_id":   f"P{i:06d}",
            "name":         name,
            "age":          random_age(),
            "gender":       gender,
            "blood_group":  random.choices(
                ["O+", "B+", "A+", "AB+", "O-", "B-", "A-", "AB-"],
                weights=[37, 32, 22, 7, 1, 0.5, 0.4, 0.1],
            )[0],
            "city":         random.choices(
                ["Bengaluru", "Chennai", "Mumbai", "Hyderabad", "Delhi",
                 "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Kochi"],
                weights=[25, 15, 15, 12, 12, 8, 5, 4, 2, 2],
            )[0],
            "phone":        fake.phone_number(),
            "registration_date": fake.date_between(start_date="-3y", end_date="today"),
        })

    return pd.DataFrame(rows)


def generate_doctors(n: int = 200) -> pd.DataFrame:
    """Generate n doctors spread across 15 departments."""
    dept_names   = [d[0] for d in DEPARTMENTS]
    dept_weights = [d[1] for d in DEPARTMENTS]
    dept_avg_bill_map = {d[0]: d[2] for d in DEPARTMENTS}

    rows = []
    for i in range(1, n + 1):
        gender = random.choices(["Male", "Female"], weights=[55, 45])[0]
        name   = fake.name_male() if gender == "Male" else fake.name_female()
        dept   = random.choices(dept_names, weights=dept_weights)[0]

        experience = random.choices([3, 8, 15, 22, 30], weights=[20, 35, 25, 15, 5])[0]

        dept_avg_bill = dept_avg_bill_map[dept]
        fee_base = max(300, dept_avg_bill // 100)
        consultation_fee = fee_base + random.randint(-100, 200)

        rows.append({
            "doctor_id":        f"D{i:03d}",
            "name":             f"Dr. {name}",
            "department":       dept,
            "experience_years": experience,
            "consultation_fee": consultation_fee,
            "join_date":        fake.date_between(
                start_date=f"-{experience + 2}y", end_date="-1y"
            ),
        })

    return pd.DataFrame(rows)


def generate_departments() -> pd.DataFrame:
    """Convert DEPARTMENTS constant into a DataFrame."""
    return pd.DataFrame(
        DEPARTMENTS,
        columns=["department", "weight", "avg_bill", "icu_chance"],
    )


def generate_admissions(patients: pd.DataFrame,
                        doctors: pd.DataFrame,
                        n: int = 25_000) -> pd.DataFrame:
    """
    Generate n admissions linking patients and doctors.

    Includes CHALLENGE A: is_readmission flag (True if same patient
    was admitted within the last 30 days).
    """
    patients_by_id = patients.set_index("patient_id").to_dict("index")

    doctors_by_dept: dict[str, list[dict]] = {}
    for _, doc in doctors.iterrows():
        doctors_by_dept.setdefault(doc["department"], []).append(doc.to_dict())

    patient_ids = patients["patient_id"].tolist()
    rows = []

    for i in range(1, n + 1):
        pid = random.choice(patient_ids)
        patient_age = int(patients_by_id[pid]["age"])
        patient_gender = patients_by_id[pid]["gender"]

        dept = _pick_department_for_age(patient_age)
        if dept == "Gynecology" and patient_gender != "Female":
            dept = "General Medicine"

        dept_doctors = doctors_by_dept.get(dept) or doctors_by_dept["General Medicine"]
        doctor = random.choice(dept_doctors)

        adm_date = _random_admission_date()

        avg_stay = AVG_STAY_DAYS.get(dept, 4)
        jitter = random.uniform(0.6, 1.4)
        los = max(1, int(round(avg_stay * jitter)))
        disch_date = adm_date + timedelta(days=los)

        diagnosis = random.choice(DIAGNOSES[dept])

        death_rate = 0.02
        if dept in ("Oncology", "ICU", "Cardiology"):
            death_rate = 0.06
        elif dept in ("Emergency", "Neurology"):
            death_rate = 0.04

        r = random.random()
        if r < death_rate:
            outcome = "Deceased"
        elif r < death_rate + 0.03:
            outcome = "Transferred"
        elif r < death_rate + 0.15:
            outcome = "Discharged"
        else:
            outcome = "Recovered"

        rows.append({
            "admission_id":   f"A{i:06d}",
            "patient_id":     pid,
            "doctor_id":      doctor["doctor_id"],
            "department":     dept,
            "admission_date": adm_date,
            "discharge_date": disch_date,
            "length_of_stay": los,
            "diagnosis":      diagnosis,
            "outcome":        outcome,
            "is_readmission": False,   # placeholder; filled in next step
        })

    df = pd.DataFrame(rows)

    # ----- CHALLENGE A: compute readmission flag -----
    # Sort by patient and date, then flag any admission where the same patient
    # came back within 30 days of a prior discharge.
    df = df.sort_values(["patient_id", "admission_date"]).reset_index(drop=True)
    df["_prev_discharge"] = df.groupby("patient_id")["discharge_date"].shift(1)
    df["_prev_discharge"] = pd.to_datetime(df["_prev_discharge"])
    df["_adm_dt"] = pd.to_datetime(df["admission_date"])
    gap_days = (df["_adm_dt"] - df["_prev_discharge"]).dt.days
    df["is_readmission"] = (gap_days >= 0) & (gap_days <= 30)
    df = df.drop(columns=["_prev_discharge", "_adm_dt"])

    # Restore original admission_id ordering for output readability.
    df = df.sort_values("admission_id").reset_index(drop=True)

    return df


def generate_icu(admissions: pd.DataFrame) -> pd.DataFrame:
    """Generate ICU records for admissions that needed intensive care."""
    icu_chance_by_dept = {d[0]: d[3] for d in DEPARTMENTS}

    rows = []
    icu_counter = 0
    for _, adm in admissions.iterrows():
        chance = icu_chance_by_dept.get(adm["department"], 0.05)
        if random.random() > chance:
            continue
        icu_counter += 1

        los = adm["length_of_stay"]
        icu_days = max(1, int(round(los * random.uniform(0.6, 1.0))))

        icu_admit = adm["admission_date"] + timedelta(days=random.randint(0, 1))
        icu_disch = icu_admit + timedelta(days=icu_days)

        if adm["department"] == "ICU":
            vent = random.random() < 0.75
            oxy = True
        else:
            vent = random.random() < 0.35
            oxy = random.random() < 0.75

        rows.append({
            "icu_id":             f"ICU{icu_counter:05d}",
            "admission_id":       adm["admission_id"],
            "icu_admit_date":     icu_admit,
            "icu_discharge_date": icu_disch,
            "icu_days":           icu_days,
            "ventilator_used":    vent,
            "oxygen_required":    oxy,
        })

    return pd.DataFrame(rows)


def generate_emergency(admissions: pd.DataFrame) -> pd.DataFrame:
    """
    Generate emergency-room records (~30% of admissions).

    Includes CHALLENGE C: wait times are longer during peak evening hours
    and shorter during early morning.
    """
    rows = []
    er_counter = 0
    for _, adm in admissions.iterrows():
        if random.random() > 0.30:
            continue
        er_counter += 1

        hours = list(HOUR_WEIGHTS_ER.keys())
        weights = list(HOUR_WEIGHTS_ER.values())
        hour = random.choices(hours, weights=weights)[0]
        minute = random.randint(0, 59)

        arrival = pd.Timestamp(adm["admission_date"]) + pd.Timedelta(hours=hour, minutes=minute)

        if adm["department"] in ("Cardiology", "ICU", "Neurology", "Emergency"):
            sev_weights = [0.25, 0.40, 0.25, 0.10]
        else:
            sev_weights = [0.05, 0.20, 0.45, 0.30]
        severity = random.choices(
            ["Critical", "Serious", "Moderate", "Stable"],
            weights=sev_weights,
        )[0]

        if severity == "Critical":
            wait = random.randint(0, 10)
        elif severity == "Serious":
            wait = random.randint(10, 30)
        elif severity == "Moderate":
            wait = random.randint(20, 60)
        else:
            wait = random.randint(30, 120)

        # ----- CHALLENGE C: adjust wait based on hour of arrival -----
        if 18 <= hour <= 22:
            wait = int(wait * 1.5)      # evening peak — ER crowded
        elif 3 <= hour <= 6:
            wait = int(wait * 0.5)      # early morning — ER empty

        ambulance = random.random() < 0.25

        rows.append({
            "er_id":             f"ER{er_counter:05d}",
            "admission_id":      adm["admission_id"],
            "arrival_time":      arrival,
            "wait_minutes":      wait,
            "severity":          severity,
            "ambulance_arrival": ambulance,
        })

    return pd.DataFrame(rows)


def generate_billing(admissions: pd.DataFrame) -> pd.DataFrame:
    """
    Generate one bill per admission.

    Includes CHALLENGE B: insurance_covered column — 80% of the bill for
    insured patients, 0 for self-pay.
    """
    dept_avg_bill = {d[0]: d[2] for d in DEPARTMENTS}

    rows = []
    for i, adm in enumerate(admissions.itertuples(), start=1):
        base = dept_avg_bill.get(adm.department, 20_000)

        scale = min(3.0, max(0.4, adm.length_of_stay / 5.0))
        amount = int(base * scale * random.uniform(0.75, 1.35))
        amount = max(500, amount)

        if random.random() < 0.65:
            payment_mode = "Insurance"
            provider = random.choice(INSURANCE_PROVIDERS)
        else:
            payment_mode = "Self-Pay"
            provider = "N/A"

        # ----- CHALLENGE B: how much insurance covered -----
        insurance_covered = int(amount * 0.80) if payment_mode == "Insurance" else 0

        rows.append({
            "bill_id":            f"B{i:06d}",
            "admission_id":       adm.admission_id,
            "amount":             amount,
            "payment_mode":       payment_mode,
            "insurance_provider": provider,
            "insurance_covered":  insurance_covered,
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("Generating hospital data...")

    patients = generate_patients()
    print(f"  patients:    {len(patients):>6,} rows")
    patients.to_csv(DATA_DIR / "patients.csv", index=False)

    doctors = generate_doctors()
    print(f"  doctors:     {len(doctors):>6,} rows")
    doctors.to_csv(DATA_DIR / "doctors.csv", index=False)

    departments = generate_departments()
    print(f"  departments: {len(departments):>6,} rows")
    departments.to_csv(DATA_DIR / "departments.csv", index=False)

    admissions = generate_admissions(patients, doctors)
    print(f"  admissions:  {len(admissions):>6,} rows")
    admissions.to_csv(DATA_DIR / "admissions.csv", index=False)

    icu = generate_icu(admissions)
    print(f"  icu:         {len(icu):>6,} rows")
    icu.to_csv(DATA_DIR / "icu.csv", index=False)

    emergency = generate_emergency(admissions)
    print(f"  emergency:   {len(emergency):>6,} rows")
    emergency.to_csv(DATA_DIR / "emergency.csv", index=False)

    billing = generate_billing(admissions)
    print(f"  billing:     {len(billing):>6,} rows")
    billing.to_csv(DATA_DIR / "billing.csv", index=False)

    print("Done. CSVs saved to:", DATA_DIR)


if __name__ == "__main__":
    main()
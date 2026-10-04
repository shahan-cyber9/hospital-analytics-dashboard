"""
create_database.py
------------------
Builds database/hospital.db (SQLite) from the 7 CSVs in data/.

This script is idempotent — running it again rebuilds the database from scratch.

Run:
    python database/create_database.py
"""

import sqlite3
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# ROOT_DIR is the project root (one level up from database/).
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH  = Path(__file__).resolve().parent / "hospital.db"


# ---------------------------------------------------------------------------
# Schema — CREATE TABLE statements for all 7 tables
# ---------------------------------------------------------------------------
# Notes:
#   * We DROP tables first so this script is safe to re-run.
#   * PRAGMA foreign_keys = ON enables foreign-key enforcement (off by default in SQLite).
#   * Indexes on FK columns massively speed up JOINs.
SCHEMA = """
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS billing;
DROP TABLE IF EXISTS emergency;
DROP TABLE IF EXISTS icu;
DROP TABLE IF EXISTS admissions;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS patients;

CREATE TABLE patients (
    patient_id        TEXT PRIMARY KEY,
    name              TEXT NOT NULL,
    age               INTEGER NOT NULL,
    gender            TEXT NOT NULL,
    blood_group       TEXT,
    city              TEXT,
    phone             TEXT,
    registration_date DATE NOT NULL
);

CREATE TABLE doctors (
    doctor_id        TEXT PRIMARY KEY,
    name             TEXT NOT NULL,
    department       TEXT NOT NULL,
    experience_years INTEGER NOT NULL,
    consultation_fee INTEGER NOT NULL,
    join_date        DATE NOT NULL
);

CREATE TABLE departments (
    department TEXT PRIMARY KEY,
    weight     INTEGER NOT NULL,
    avg_bill   INTEGER NOT NULL,
    icu_chance REAL NOT NULL
);

CREATE TABLE admissions (
    admission_id   TEXT PRIMARY KEY,
    patient_id     TEXT NOT NULL,
    doctor_id      TEXT NOT NULL,
    department     TEXT NOT NULL,
    admission_date DATE NOT NULL,
    discharge_date DATE NOT NULL,
    length_of_stay INTEGER NOT NULL,
    diagnosis      TEXT NOT NULL,
    outcome        TEXT NOT NULL,
    is_readmission INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id)  REFERENCES doctors(doctor_id)
);

CREATE TABLE icu (
    icu_id             TEXT PRIMARY KEY,
    admission_id       TEXT NOT NULL,
    icu_admit_date     DATE NOT NULL,
    icu_discharge_date DATE NOT NULL,
    icu_days           INTEGER NOT NULL,
    ventilator_used    INTEGER NOT NULL,
    oxygen_required    INTEGER NOT NULL,
    FOREIGN KEY (admission_id) REFERENCES admissions(admission_id)
);

CREATE TABLE emergency (
    er_id             TEXT PRIMARY KEY,
    admission_id      TEXT NOT NULL,
    arrival_time      DATETIME NOT NULL,
    wait_minutes      INTEGER NOT NULL,
    severity          TEXT NOT NULL,
    ambulance_arrival INTEGER NOT NULL,
    FOREIGN KEY (admission_id) REFERENCES admissions(admission_id)
);

CREATE TABLE billing (
    bill_id            TEXT PRIMARY KEY,
    admission_id       TEXT NOT NULL,
    amount             INTEGER NOT NULL,
    payment_mode       TEXT NOT NULL,
    insurance_provider TEXT,
    insurance_covered  INTEGER NOT NULL,
    FOREIGN KEY (admission_id) REFERENCES admissions(admission_id)
);

CREATE INDEX idx_admissions_patient  ON admissions(patient_id);
CREATE INDEX idx_admissions_doctor   ON admissions(doctor_id);
CREATE INDEX idx_admissions_date     ON admissions(admission_date);
CREATE INDEX idx_icu_admission       ON icu(admission_id);
CREATE INDEX idx_emergency_admission ON emergency(admission_id);
CREATE INDEX idx_billing_admission   ON billing(admission_id);
"""

# Load order matters — parents before children (FK dependencies).
LOAD_ORDER = [
    ("patients",    "patients.csv"),
    ("doctors",     "doctors.csv"),
    ("departments", "departments.csv"),
    ("admissions",  "admissions.csv"),
    ("icu",         "icu.csv"),
    ("emergency",   "emergency.csv"),
    ("billing",     "billing.csv"),
]


def main() -> None:
    print("Building hospital.db...")

    # 1. Delete existing DB so this script is idempotent (safe to re-run).
    if DB_PATH.exists():
        DB_PATH.unlink()

    # 2. Connect. This creates the file if it doesn't exist.
    conn = sqlite3.connect(DB_PATH)

    # 3. Create tables and indexes.
    conn.executescript(SCHEMA)
    print("  Schema created (7 tables, 6 indexes)")

    # 4. Load each CSV into its table.
    for table_name, csv_name in LOAD_ORDER:
        csv_path = DATA_DIR / csv_name
        df = pd.read_csv(csv_path)
        df.to_sql(table_name, conn, if_exists="append", index=False)
        print(f"  {table_name:<12} {len(df):>6,} rows loaded")

    # 5. Commit and close.
    conn.commit()
    conn.close()

    size_kb = DB_PATH.stat().st_size / 1024
    print(f"Done. Database saved to: {DB_PATH}")
    print(f"      File size: {size_kb:,.0f} KB")


if __name__ == "__main__":
    main()
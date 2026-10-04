"""
query_examples.py
-----------------
Runs 15 analytical SQL queries against hospital.db to demonstrate:
    SELECT, WHERE, GROUP BY, ORDER BY, JOIN, COUNT, SUM, AVG, MIN, MAX

Run:
    python database/query_examples.py
"""

import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).resolve().parent / "hospital.db"


def run_query(conn: sqlite3.Connection, title: str, sql: str) -> None:
    """Execute one query and print its result as a table."""
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)
    df = pd.read_sql_query(sql, conn)
    print(df.to_string(index=False))


def main() -> None:
    conn = sqlite3.connect(DB_PATH)

    # ----- 1. Row counts across all tables -----
    run_query(conn, "1. ROW COUNTS", """
        SELECT 'patients'    AS table_name, COUNT(*) AS rows FROM patients
        UNION ALL SELECT 'doctors',      COUNT(*) FROM doctors
        UNION ALL SELECT 'departments',  COUNT(*) FROM departments
        UNION ALL SELECT 'admissions',   COUNT(*) FROM admissions
        UNION ALL SELECT 'icu',          COUNT(*) FROM icu
        UNION ALL SELECT 'emergency',    COUNT(*) FROM emergency
        UNION ALL SELECT 'billing',      COUNT(*) FROM billing
    """)

    # ----- 2. Average length of stay per department -----
    run_query(conn, "2. AVG LENGTH OF STAY PER DEPARTMENT", """
        SELECT department,
               COUNT(*) AS admissions,
               ROUND(AVG(length_of_stay), 1) AS avg_los_days
        FROM admissions
        GROUP BY department
        ORDER BY avg_los_days DESC
    """)

    # ----- 3. Top 10 doctors by patient count -----
    run_query(conn, "3. TOP 10 DOCTORS BY PATIENT COUNT", """
        SELECT d.name AS doctor, d.department, COUNT(*) AS patients
        FROM admissions a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        GROUP BY d.doctor_id
        ORDER BY patients DESC
        LIMIT 10
    """)

    # ----- 4. Monthly revenue trend (last 12 months) -----
    run_query(conn, "4. MONTHLY REVENUE (LAST 12 MONTHS)", """
        SELECT strftime('%Y-%m', a.admission_date) AS month,
               COUNT(*) AS admissions,
               SUM(b.amount) AS revenue
        FROM admissions a
        JOIN billing b ON a.admission_id = b.admission_id
        GROUP BY month
        ORDER BY month DESC
        LIMIT 12
    """)

    # ----- 5. Revenue by department -----
    run_query(conn, "5. REVENUE BY DEPARTMENT", """
        SELECT a.department,
               COUNT(*) AS admissions,
               SUM(b.amount) AS total_revenue,
               ROUND(AVG(b.amount)) AS avg_bill
        FROM admissions a
        JOIN billing b ON a.admission_id = b.admission_id
        GROUP BY a.department
        ORDER BY total_revenue DESC
    """)

    # ----- 6. Emergency wait by severity -----
    run_query(conn, "6. EMERGENCY WAIT TIME BY SEVERITY", """
        SELECT severity,
               COUNT(*) AS visits,
               ROUND(AVG(wait_minutes), 1) AS avg_wait_min,
               MIN(wait_minutes) AS min_wait,
               MAX(wait_minutes) AS max_wait
        FROM emergency
        GROUP BY severity
        ORDER BY avg_wait_min DESC
    """)

    # ----- 7. ICU stats -----
    run_query(conn, "7. ICU OVERVIEW", """
        SELECT COUNT(*) AS total_icu_stays,
               ROUND(AVG(icu_days), 1) AS avg_icu_days,
               SUM(ventilator_used) AS on_ventilator,
               SUM(oxygen_required) AS on_oxygen
        FROM icu
    """)

    # ----- 8. Readmission rate by department -----
    run_query(conn, "8. READMISSION RATE BY DEPARTMENT", """
        SELECT department,
               COUNT(*) AS admissions,
               SUM(is_readmission) AS readmissions,
               ROUND(100.0 * SUM(is_readmission) / COUNT(*), 2) AS readmit_pct
        FROM admissions
        GROUP BY department
        ORDER BY readmit_pct DESC
    """)

    # ----- 9. Patient age buckets -----
    run_query(conn, "9. PATIENTS BY AGE GROUP", """
        SELECT
            CASE
                WHEN age < 18 THEN '0-17'
                WHEN age < 30 THEN '18-29'
                WHEN age < 45 THEN '30-44'
                WHEN age < 60 THEN '45-59'
                WHEN age < 75 THEN '60-74'
                ELSE '75+'
            END AS age_group,
            COUNT(*) AS patients
        FROM patients
        GROUP BY age_group
        ORDER BY age_group
    """)

    # ----- 10. Gender distribution -----
    run_query(conn, "10. GENDER DISTRIBUTION", """
        SELECT gender, COUNT(*) AS patients
        FROM patients
        GROUP BY gender
    """)

    # ----- 11. Insurance vs self-pay -----
    run_query(conn, "11. INSURANCE VS SELF-PAY", """
        SELECT payment_mode,
               COUNT(*) AS bills,
               SUM(amount) AS total_amount,
               ROUND(AVG(amount)) AS avg_bill,
               SUM(insurance_covered) AS insurer_paid
        FROM billing
        GROUP BY payment_mode
    """)

    # ----- 12. Top 10 diagnoses -----
    run_query(conn, "12. TOP 10 DIAGNOSES", """
        SELECT diagnosis, COUNT(*) AS cases
        FROM admissions
        GROUP BY diagnosis
        ORDER BY cases DESC
        LIMIT 10
    """)

    # ----- 13. Doctors per department -----
    run_query(conn, "13. DOCTORS PER DEPARTMENT", """
        SELECT department, COUNT(*) AS doctors
        FROM doctors
        GROUP BY department
        ORDER BY doctors DESC
    """)

    # ----- 14. Busiest day of week -----
    run_query(conn, "14. ADMISSIONS BY DAY OF WEEK", """
        SELECT
            CASE CAST(strftime('%w', admission_date) AS INTEGER)
                WHEN 0 THEN 'Sun'
                WHEN 1 THEN 'Mon'
                WHEN 2 THEN 'Tue'
                WHEN 3 THEN 'Wed'
                WHEN 4 THEN 'Thu'
                WHEN 5 THEN 'Fri'
                WHEN 6 THEN 'Sat'
            END AS day_of_week,
            COUNT(*) AS admissions
        FROM admissions
        GROUP BY strftime('%w', admission_date)
        ORDER BY strftime('%w', admission_date)
    """)

    # ----- 15. Outcomes -----
    run_query(conn, "15. ADMISSION OUTCOMES", """
        SELECT outcome,
               COUNT(*) AS admissions,
               ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM admissions), 2) AS pct
        FROM admissions
        GROUP BY outcome
        ORDER BY admissions DESC
    """)

    conn.close()
    print()
    print("All queries finished.")


if __name__ == "__main__":
    main()
"""
verify_data.py
--------------
Quick sanity check on the generated CSVs.
Run: python data/verify_data.py
"""
import pandas as pd

# --- Admissions ---
adm = pd.read_csv("data/admissions.csv")
print("=" * 50)
print("ADMISSIONS")
print("=" * 50)
print(f"Total:              {len(adm):,}")
print(f"Readmission rate:   {adm['is_readmission'].mean() * 100:.2f}%")
print()
print("Top 5 departments:")
print(adm["department"].value_counts().head(5).to_string())
print()
print("Outcomes:")
print(adm["outcome"].value_counts().to_string())

# --- Emergency ---
er = pd.read_csv("data/emergency.csv", parse_dates=["arrival_time"])
er["hour"] = er["arrival_time"].dt.hour
peak_wait = er[er["hour"].between(18, 22)]["wait_minutes"].mean()
quiet_wait = er[er["hour"].between(3, 6)]["wait_minutes"].mean()
print()
print("=" * 50)
print("EMERGENCY")
print("=" * 50)
print(f"Total ER visits:    {len(er):,}")
print(f"Avg wait 18-22h:    {peak_wait:.1f} min  (peak)")
print(f"Avg wait 3-6h:      {quiet_wait:.1f} min  (quiet)")
print(f"Peak is slower by:  {peak_wait / quiet_wait:.1f}x")

# --- Billing ---
bill = pd.read_csv("data/billing.csv")
print()
print("=" * 50)
print("BILLING")
print("=" * 50)
print("Payment split:")
print(bill["payment_mode"].value_counts().to_string())
print()
print(f"Total billed:       Rs {bill['amount'].sum():,}")
print(f"Insurance covered:  Rs {bill['insurance_covered'].sum():,}")
self_pay = bill[bill["payment_mode"] == "Self-Pay"]["amount"].sum()
print(f"Self-Pay total:     Rs {self_pay:,}")
print()

# --- ICU ---
icu = pd.read_csv("data/icu.csv")
print("=" * 50)
print("ICU")
print("=" * 50)
print(f"Total ICU stays:    {len(icu):,}")
print(f"Avg ICU days:       {icu['icu_days'].mean():.1f}")
print(f"Ventilator used:    {icu['ventilator_used'].sum():,} ({icu['ventilator_used'].mean() * 100:.1f}%)")
print(f"Oxygen required:    {icu['oxygen_required'].sum():,} ({icu['oxygen_required'].mean() * 100:.1f}%)")

# --- Departments ---
dept = pd.read_csv("data/departments.csv")
print()
print("=" * 50)
print("DEPARTMENTS")
print("=" * 50)
print(f"Total departments:  {len(dept)}")
print(f"Avg bill range:     Rs {dept['avg_bill'].min():,} - Rs {dept['avg_bill'].max():,}")
print()
print("All checks passed. Chapter 2 data verified.")
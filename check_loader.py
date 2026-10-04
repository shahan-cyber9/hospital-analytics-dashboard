"""
check_loader.py
---------------
Verifies that every loader function returns clean, enriched DataFrames.
Run from project root:  python check_loader.py
"""
from utils.loader import load_all


def main() -> None:
    data = load_all()

    print("=" * 72)
    print("LOADER OUTPUT")
    print("=" * 72)
    for name, df in data.items():
        print(f"{name:<12} {len(df):>6,} rows  {len(df.columns):>2} cols")

    # --- Sample enriched admissions ---
    print()
    print("=" * 72)
    print("SAMPLE ENRICHED ADMISSIONS")
    print("=" * 72)
    adm = data["admissions"]
    sample_cols = [
        "admission_id", "admission_date", "admission_dow",
        "admission_month_name", "season", "is_readmission",
    ]
    print(adm[sample_cols].head(5).to_string(index=False))

    # --- Season distribution ---
    print()
    print("=" * 72)
    print("SEASON DISTRIBUTION")
    print("=" * 72)
    print(adm["season"].value_counts().to_string())

    # --- Day-of-week distribution ---
    print()
    print("=" * 72)
    print("ADMISSIONS BY DAY OF WEEK")
    print("=" * 72)
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday",
                 "Friday", "Saturday", "Sunday"]
    print(adm["admission_dow"].value_counts().reindex(dow_order).to_string())

    # --- Patient age groups ---
    print()
    print("=" * 72)
    print("PATIENTS BY AGE GROUP")
    print("=" * 72)
    print(data["patients"]["age_group"].value_counts().sort_index().to_string())

    # --- Emergency severity (ordered) ---
    print()
    print("=" * 72)
    print("EMERGENCY SEVERITY (ordered categorical)")
    print("=" * 72)
    print(data["emergency"]["severity"].value_counts().sort_index().to_string())

    # --- Billing: self-pay derived column ---
    print()
    print("=" * 72)
    print("BILLING SELF-PAY COLUMN (sample)")
    print("=" * 72)
    bill = data["billing"]
    print(bill[["bill_id", "amount", "insurance_covered", "self_pay_amount"]]
          .head(5).to_string(index=False))

    print()
    print("All checks passed.")


if __name__ == "__main__":
    main()
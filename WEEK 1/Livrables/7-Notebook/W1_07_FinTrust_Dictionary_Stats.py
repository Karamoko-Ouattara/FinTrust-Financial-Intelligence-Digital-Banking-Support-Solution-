"""
FinTrust — Data Dictionary statistics (traceability for W1_02)
================================================================
Recomputes, for every one of the 23 fields across both datasets,
every figure that appears in the Data Dictionary: row count,
non-null count, completeness, distinct-value count, observed
domain / numeric range, and the example value shown in the sheet.

Inputs (read-only):
    FinTrust_Customer_Data.xlsx
    FinTrust_Transaction_Data.xlsx

Run:
    python3 dictionary_stats.py
"""

import pandas as pd

CUSTOMER_FILE = "/mnt/user-data/uploads/FinTrust_Customer_Data.xlsx"
TRANSACTION_FILE = "/mnt/user-data/uploads/FinTrust_Transaction_Data.xlsx"


def profile_field(df: pd.DataFrame, col: str) -> dict:
    """Every figure the Data Dictionary shows for one field."""
    s = df[col]
    n = len(df)
    nonnull = int(s.notna().sum())
    completeness = round(nonnull / n * 100, 2)
    nunique = int(s.nunique(dropna=True))

    if pd.api.types.is_numeric_dtype(s):
        domain = f"min {s.min():,.2f} | median {s.median():,.2f} | max {s.max():,.2f}"
    elif pd.api.types.is_datetime64_any_dtype(s):
        domain = f"{s.min():%Y-%m-%d} to {s.max():%Y-%m-%d}"
    else:
        vals = sorted(s.dropna().unique().tolist())
        domain = ", ".join(map(str, vals)) if len(vals) <= 10 else f"{nunique} distinct values"

    example = s.dropna().iloc[0]
    if isinstance(example, pd.Timestamp):
        example = example.strftime("%Y-%m-%d %H:%M")
    elif isinstance(example, float):
        example = f"{example:,.2f}"

    return {
        "field": col, "records": n, "non_null": nonnull,
        "completeness_pct": completeness, "distinct": nunique,
        "domain_or_range": domain, "example": str(example),
    }


def print_table(title: str, df: pd.DataFrame) -> None:
    print("=" * 100)
    print(title)
    print("=" * 100)
    rows = [profile_field(df, c) for c in df.columns]
    out = pd.DataFrame(rows)
    with pd.option_context("display.max_colwidth", 60, "display.width", 140):
        print(out.to_string(index=False))
    print()


def main() -> None:
    customers = pd.read_excel(CUSTOMER_FILE)
    transactions = pd.read_excel(TRANSACTION_FILE)

    print_table(
        f"CUSTOMER DICTIONARY  ({customers.shape[0]} rows x {customers.shape[1]} columns)",
        customers,
    )
    print_table(
        f"TRANSACTION DICTIONARY  ({transactions.shape[0]} rows x {transactions.shape[1]} columns)",
        transactions,
    )

    # ---- workbook-level completeness figures quoted in the Data Dictionary ----
    print("=" * 100)
    print("WORKBOOK-LEVEL COMPLETENESS  (Model_Notes / footer figures)")
    print("=" * 100)
    cust_cells = customers.size
    cust_nonnull = customers.notna().sum().sum()
    tx_cells = transactions.size
    tx_nonnull = transactions.notna().sum().sum()
    total_cells = cust_cells + tx_cells
    total_nonnull = cust_nonnull + tx_nonnull
    print(f"Customer completeness   : {cust_nonnull}/{cust_cells} = {cust_nonnull / cust_cells * 100:.2f}%")
    print(f"Transaction completeness: {tx_nonnull}/{tx_cells} = {tx_nonnull / tx_cells * 100:.2f}%")
    print(f"Overall cell completeness: {total_nonnull}/{total_cells} = {total_nonnull / total_cells * 100:.2f}%")
    fully_populated = transactions.notna().all(axis=1).mean() * 100
    print(f"Transaction rows fully populated: {fully_populated:.2f}%")

    # ---- reference values (Reference_Values sheet) ----
    print("\n" + "=" * 100)
    print("REFERENCE VALUES  (controlled vocabularies, Reference_Values sheet)")
    print("=" * 100)
    cat_fields = {
        "Customer": (customers, ["Gender", "City", "Customer_Segment", "Account_Type",
                                  "Monthly_Income_Band", "Preferred_Channel", "Account_Status"]),
        "Transaction": (transactions, ["Transaction_Type", "Channel", "Device_Type", "Location",
                                        "International_Transaction", "Transaction_Status", "Risk_Review_Flag"]),
    }
    for dataset, (df, cols) in cat_fields.items():
        for col in cols:
            vc = df[col].value_counts(dropna=False)
            print(f"\n[{dataset}] {col}")
            for val, n in vc.items():
                label = "(blank / missing)" if pd.isna(val) else str(val)
                print(f"    {label:<20} {n:>6}  ({n / len(df) * 100:.2f}%)")


if __name__ == "__main__":
    main()

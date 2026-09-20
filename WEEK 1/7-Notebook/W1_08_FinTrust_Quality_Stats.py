"""
FinTrust — Data Quality statistics (traceability for W1_03)
=============================================================
Recomputes every figure and every statistical test cited in the
Data Quality Assessment Report: the dimension scorecard, and the
evidence behind each finding DQ-01 to DQ-11.

Requires scipy (chi2_contingency). If unavailable:
    pip install scipy --break-system-packages

Inputs (read-only):
    FinTrust_Customer_Data.xlsx
    FinTrust_Transaction_Data.xlsx

Run:
    python3 quality_stats.py
"""

import pandas as pd
from scipy.stats import chi2_contingency

CUSTOMER_FILE = "/mnt/user-data/uploads/FinTrust_Customer_Data.xlsx"
TRANSACTION_FILE = "/mnt/user-data/uploads/FinTrust_Transaction_Data.xlsx"


def independence_test(df: pd.DataFrame, col_a: str, col_b: str) -> float:
    """Chi-square test of independence between two categorical fields.

    A high p-value (> 0.05) means no association is detectable —
    i.e. the two fields behave as if independently sampled.
    """
    ct = pd.crosstab(df[col_a], df[col_b])
    _, p, _, _ = chi2_contingency(ct)
    return p


def section(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def main() -> None:
    C = pd.read_excel(CUSTOMER_FILE)
    T = pd.read_excel(TRANSACTION_FILE)
    M = T.merge(C, on="Customer_ID", how="left")

    # ---------------------------------------------------------------- DQ-scorecard
    section("DIMENSION SCORECARD")
    completeness = (C.notna().sum().sum() + T.notna().sum().sum()) / (C.size + T.size)
    uniqueness = (
        (C.Customer_ID.duplicated().sum() == 0)
        and (T.Transaction_ID.duplicated().sum() == 0)
        and (C.duplicated().sum() == 0)
        and (T.duplicated().sum() == 0)
    )
    orphans = len(set(T.Customer_ID) - set(C.Customer_ID))
    unmatched_customers = len(set(C.Customer_ID) - set(T.Customer_ID))
    print(f"Completeness : {completeness * 100:.2f}%")
    print(f"Uniqueness   : {'100% (no duplicate keys or rows)' if uniqueness else 'FAIL'}")
    print(f"Integrity    : orphan transactions = {orphans}, customers with no transactions = {unmatched_customers}")

    # ---------------------------------------------------------------- DQ-01
    section("DQ-01 — Channel vs Device_Type independence")
    p1 = independence_test(T.dropna(subset=["Device_Type"]), "Channel", "Device_Type")
    ct1 = pd.crosstab(T.Channel, T.Device_Type)
    print(ct1.to_string())
    print(f"\nchi-square p-value = {p1:.4f}  (p > 0.05 => no detectable association)")
    print(f"ATM channel x Android device : {ct1.loc['ATM', 'Android']}")
    print(f"Mobile App channel x POS Terminal device: {ct1.loc['Mobile App', 'POS Terminal']}")

    # ---------------------------------------------------------------- DQ-02
    section("DQ-02 — Missing Device_Type / Location")
    n_dev_null = T.Device_Type.isna().sum()
    n_loc_null = T.Location.isna().sum()
    both_null = ((T.Device_Type.isna()) & (T.Location.isna())).sum()
    any_null_rows = T[["Device_Type", "Location"]].isna().any(axis=1).sum()
    print(f"Device_Type nulls : {n_dev_null} ({n_dev_null / len(T) * 100:.2f}%)")
    print(f"Location nulls    : {n_loc_null} ({n_loc_null / len(T) * 100:.2f}%)")
    print(f"Rows missing both : {both_null}")
    print(f"Rows missing either (188 distinct transactions affected): {any_null_rows}")

    # ---------------------------------------------------------------- DQ-03
    section("DQ-03 — Transaction Location vs customer home City")
    comparable = M.dropna(subset=["Location", "City"])
    match_rate = (comparable.Location == comparable.City).mean()
    p3 = independence_test(comparable, "Location", "City")
    print(f"Location == City match rate : {match_rate * 100:.2f}%  (random expectation with 8 cities ~= 12.5%)")
    print(f"chi-square p-value = {p3:.4f}")

    # ---------------------------------------------------------------- DQ-04
    section("DQ-04 — Customer_Segment vs Account_Type / Monthly_Income_Band")
    p4a = independence_test(C, "Customer_Segment", "Account_Type")
    p4b = independence_test(C, "Customer_Segment", "Monthly_Income_Band")
    print(f"Segment x Account_Type    chi-square p-value = {p4a:.4f}")
    print(f"Segment x Income_Band     chi-square p-value = {p4b:.4f}")
    prem_savings = len(C[(C.Customer_Segment == "Premium") & (C.Account_Type == "Savings")])
    prem_low_income = len(C[(C.Customer_Segment == "Premium") & (C.Monthly_Income_Band == "Below 100k")])
    print(f"Premium segment x Savings account : {prem_savings} of {len(C[C.Customer_Segment == 'Premium'])} Premium customers")
    print(f"Premium segment x 'Below 100k' income : {prem_low_income} customers")
    avg_ticket_by_seg = M.groupby("Customer_Segment").Amount_NGN.mean().round(2)
    print("\nAverage ticket by segment (shows no meaningful spread):")
    print(avg_ticket_by_seg.to_string())

    # ---------------------------------------------------------------- DQ-05
    section("DQ-05 — Dormant / Restricted accounts still transacting")
    for status in ["Dormant", "Restricted", "Active"]:
        seg = M[M.Account_Status == status]
        n_cust = seg.Customer_ID.nunique()
        n_tx = len(seg)
        base_cust = (C.Account_Status == status).sum()
        print(f"{status:<11}: {n_cust}/{base_cust} customers transacted, "
              f"{n_tx} transactions, avg {n_tx / n_cust:.2f} tx/customer")

    # ---------------------------------------------------------------- DQ-06
    section("DQ-06 — Amount_NGN skew and outlier concentration")
    mean_amt, median_amt = T.Amount_NGN.mean(), T.Amount_NGN.median()
    skew = T.Amount_NGN.skew()
    q1, q3 = T.Amount_NGN.quantile([0.25, 0.75])
    iqr = q3 - q1
    fence = q3 + 1.5 * iqr
    outliers = T[T.Amount_NGN > fence]
    print(f"Mean   : {mean_amt:,.2f}")
    print(f"Median : {median_amt:,.2f}  (mean / median = {mean_amt / median_amt:.2f}x)")
    print(f"Skewness: {skew:.2f}")
    print(f"IQR upper fence (Q3 + 1.5*IQR) : {fence:,.2f}")
    print(f"Transactions above fence : {len(outliers)} ({len(outliers) / len(T) * 100:.2f}%)")
    print(f"Value share of those transactions : {outliers.Amount_NGN.sum() / T.Amount_NGN.sum() * 100:.2f}%")
    print(f"99th percentile : {T.Amount_NGN.quantile(0.99):,.2f}")
    print(f"Maximum         : {T.Amount_NGN.max():,.2f}")
    print(f"Zero/negative amounts : {(T.Amount_NGN <= 0).sum()}")

    # ---------------------------------------------------------------- DQ-07
    section("DQ-07 — Preferred_Channel vs observed dominant channel")
    dominant = (
        M.groupby(["Customer_ID", "Channel"]).size().reset_index(name="n")
        .sort_values("n", ascending=False).drop_duplicates("Customer_ID")
        .merge(C[["Customer_ID", "Preferred_Channel"]], on="Customer_ID")
    )
    match = (dominant.Channel == dominant.Preferred_Channel).mean()
    print(f"Preferred_Channel domain : {sorted(C.Preferred_Channel.unique())} (3 options)")
    print(f"Observed Channel domain  : {sorted(T.Channel.unique())} (5 options)")
    print(f"Match rate (stated == dominant observed) : {match * 100:.2f}%")

    # ---------------------------------------------------------------- DQ-08
    section("DQ-08 — Age plausibility within the Student segment")
    student_age = C[C.Customer_Segment == "Student"].Age
    print(f"Student segment age : mean {student_age.mean():.1f}, median {student_age.median():.1f}, "
          f"min {student_age.min()}, max {student_age.max()}")
    print(f"Book-wide age        : mean {C.Age.mean():.1f}")

    # ---------------------------------------------------------------- DQ-09 / DQ-10 / DQ-11
    section("DQ-09 — Customer_Name distinctness")
    print(f"Distinct names : {C.Customer_Name.nunique()} across {len(C)} customers "
          f"(avg {len(C) / C.Customer_Name.nunique():.1f} customers per name)")

    section("DQ-10 — 'Premium' label collision")
    n_acct_premium = (C.Account_Type == "Premium").sum()
    n_seg_premium = (C.Customer_Segment == "Premium").sum()
    overlap = len(C[(C.Account_Type == "Premium") & (C.Customer_Segment == "Premium")])
    print(f"Account_Type == 'Premium'   : {n_acct_premium} customers")
    print(f"Customer_Segment == 'Premium': {n_seg_premium} customers")
    print(f"Overlap (both 'Premium')    : {overlap} customers")

    section("DQ-11 — Monthly_Income_Band sort order")
    print("Alphabetical order  :", sorted(C.Monthly_Income_Band.unique()))
    print("Economic order      : ['Below 100k', '100k-249k', '250k-499k', '500k-999k', '1m+']")


if __name__ == "__main__":
    main()

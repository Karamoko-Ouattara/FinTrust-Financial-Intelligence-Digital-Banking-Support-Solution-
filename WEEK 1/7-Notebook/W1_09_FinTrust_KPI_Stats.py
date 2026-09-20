"""
FinTrust — KPI baseline statistics (traceability for W1_04)
=============================================================
Recomputes the Q1 2026 baseline value for every one of the 22 KPIs
in the KPI Definition Sheet, plus the Baseline_Breakdowns sheet
used to validate the Week 3 Power BI build.

Inputs (read-only):
    FinTrust_Customer_Data.xlsx
    FinTrust_Transaction_Data.xlsx

Run:
    python3 kpi_stats.py
"""

import pandas as pd

CUSTOMER_FILE = "/mnt/user-data/uploads/FinTrust_Customer_Data.xlsx"
TRANSACTION_FILE = "/mnt/user-data/uploads/FinTrust_Transaction_Data.xlsx"


def section(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def main() -> None:
    C = pd.read_excel(CUSTOMER_FILE)
    T = pd.read_excel(TRANSACTION_FILE)
    M = T.merge(C, on="Customer_ID", how="left")

    n_cust = C.Customer_ID.nunique()
    n_tx = len(T)

    kpis = {}

    # ---- Growth & Volume ------------------------------------------------
    kpis["KPI-01 Total Transaction Value"] = f"NGN {T.Amount_NGN.sum():,.0f}"
    kpis["KPI-02 Transaction Count"] = f"{n_tx:,}"
    kpis["KPI-03 Average Transaction Value"] = f"NGN {T.Amount_NGN.mean():,.0f}"
    kpis["KPI-04 Median Transaction Value"] = f"NGN {T.Amount_NGN.median():,.0f}"

    # ---- Operational Performance -----------------------------------------
    succ = (T.Transaction_Status == "Successful").mean()
    fail = T.Transaction_Status.isin(["Failed", "Reversed", "Pending"]).mean()
    kpis["KPI-05 Transaction Success Rate"] = f"{succ * 100:.2f}%"
    kpis["KPI-06 Transaction Failure Rate"] = f"{fail * 100:.2f}%"
    failed_reversed_value = T[T.Transaction_Status.isin(["Failed", "Reversed"])].Amount_NGN.sum()
    kpis["KPI-07 Value at Risk of Failure (Failed+Reversed)"] = f"NGN {failed_reversed_value:,.0f}"

    # ---- Risk & Trust ------------------------------------------------------
    risk = (T.Risk_Review_Flag == "Yes").mean()
    risk_val = T[T.Risk_Review_Flag == "Yes"].Amount_NGN.sum()
    intl = (T.International_Transaction == "Yes").mean()
    intl_risk = (T[T.International_Transaction == "Yes"].Risk_Review_Flag == "Yes").mean()
    q90 = T.Amount_NGN.quantile(0.90)
    hv_risk = (T[T.Amount_NGN >= q90].Risk_Review_Flag == "Yes").mean()
    night = T[T.Transaction_DateTime.dt.hour.isin(range(6))]
    night_risk = (night.Risk_Review_Flag == "Yes").mean()

    kpis["KPI-08 Risk Review Rate"] = f"{risk * 100:.2f}%"
    kpis["KPI-09 Value Under Review"] = f"NGN {risk_val:,.0f}"
    kpis["KPI-10 International Transaction Share"] = f"{intl * 100:.2f}%"
    kpis["KPI-11 Risk Rate on International Tx"] = f"{intl_risk * 100:.2f}%"
    kpis["KPI-12 Risk Rate on High-Value Tx (>=P90)"] = f"{hv_risk * 100:.2f}%  (P90 = NGN {q90:,.0f})"
    kpis["KPI-13 Off-Hours Risk Rate (00:00-05:59)"] = f"{night_risk * 100:.2f}%"

    # ---- Digital Adoption -----------------------------------------------
    digital = T.Channel.isin(["Mobile App", "Web", "USSD"]).mean()
    kpis["KPI-14 Digital Channel Share"] = f"{digital * 100:.2f}%"
    kpis["KPI-15 Average Digital Engagement Score"] = f"{C.Digital_Engagement_Score.mean():.1f} / 100"

    # ---- Customer Value ----------------------------------------------------
    kpis["KPI-16 Transactions per Customer"] = f"{n_tx / n_cust:.1f}"
    kpis["KPI-17 Value per Customer"] = f"NGN {T.Amount_NGN.sum() / n_cust:,.0f}"
    kpis["KPI-18 Active Account Rate"] = f"{(C.Account_Status == 'Active').mean() * 100:.2f}%"
    kpis["KPI-19 Dormancy Rate"] = f"{(C.Account_Status == 'Dormant').mean() * 100:.2f}%"
    kpis["KPI-20 Restricted Account Rate"] = f"{(C.Account_Status == 'Restricted').mean() * 100:.2f}%"
    kpis["KPI-21 Average Customer Tenure"] = f"{C.Tenure_Months.mean():.1f} months"

    # ---- Data Governance ------------------------------------------------
    complete = ((T.Device_Type.notna()) & (T.Location.notna())).mean()
    kpis["KPI-22 Data Completeness Rate"] = f"{complete * 100:.2f}%"

    section("22 KPI BASELINE VALUES — Q1 2026")
    for name, value in kpis.items():
        print(f"{name:<48}: {value}")

    # ---- Baseline_Breakdowns sheet reproduction --------------------------
    section("BASELINE BREAKDOWNS — reconciliation table")
    dims = [
        ("Channel", "Channel"),
        ("Transaction Type", "Transaction_Type"),
        ("Customer Segment", "Customer_Segment"),
        ("Account Type", "Account_Type"),
        ("Customer City", "City"),
    ]
    for label, col in dims:
        print(f"\n--- by {label} ---")
        g = M.groupby(col).agg(
            transactions=("Transaction_ID", "count"),
            total_value=("Amount_NGN", "sum"),
            avg_ticket=("Amount_NGN", "mean"),
            success_rate=("Transaction_Status", lambda s: (s == "Successful").mean() * 100),
            risk_rate=("Risk_Review_Flag", lambda s: (s == "Yes").mean() * 100),
        ).round(2)
        print(g.to_string())

    print("\n--- by Month ---")
    monthly = T.assign(month=T.Transaction_DateTime.dt.strftime("%Y-%m")).groupby("month").agg(
        transactions=("Transaction_ID", "count"),
        total_value=("Amount_NGN", "sum"),
        risk_rate=("Risk_Review_Flag", lambda s: (s == "Yes").mean() * 100),
    ).round(2)
    print(monthly.to_string())


if __name__ == "__main__":
    main()

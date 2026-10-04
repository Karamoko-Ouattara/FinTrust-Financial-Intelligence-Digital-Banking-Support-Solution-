# Detailed Python EDA & Risk Breakdown
fraud_by_type = df.groupby('Transaction_Type')['Is_Fraud'].agg(['count', 'sum', 'mean'])
fraud_by_type.columns = ['Total_Transactions', 'Fraud_Count', 'Fraud_Rate']
fraud_by_type['Fraud_Rate'] = (fraud_by_type['Fraud_Rate'] * 100).round(2)

print("--- Fraud Analysis by Transaction Type ---")
print(fraud_by_type)

# Risk Score vs. Actual Fraud Cross-tabulation
risk_cross_tab = pd.crosstab(df['Risk_Score'], df['Is_Fraud'], normalize='index') * 100
print("\n--- Fraud Occurrence % by Pre-defined Risk Score ---")
print(risk_cross_tab.round(2))
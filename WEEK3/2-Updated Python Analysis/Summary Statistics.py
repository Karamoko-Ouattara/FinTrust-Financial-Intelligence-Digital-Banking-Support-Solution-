import pandas as pd
import numpy as np

# Load datasets
customers = pd.read_csv('FinTrust_Customer_Data_2.csv')
transactions = pd.read_csv('FinTrust_Transaction_Data_2.csv')

# Conversions & Basic Cleaning
customers['Join_Date'] = pd.to_datetime(customers['Join_Date'])
transactions['Transaction_Date'] = pd.to_datetime(transactions['Transaction_Date'])

# Merge datasets for comprehensive analysis
df = pd.merge(transactions, customers, on='Customer_ID', how='inner')

# Summary Statistics
total_customers = customers['Customer_ID'].nunique()
total_txns = len(transactions)
total_volume = transactions['Transaction_Amount'].sum()
avg_txn_val = transactions['Transaction_Amount'].mean()
fraud_rate = (transactions['Is_Fraud'].sum() / total_txns) * 100

print(f"Total Customers: {total_customers}")
print(f"Total Transactions: {total_txns}")
print(f"Total Volume: ${total_volume:,.2f}")
print(f"Average Transaction: ${avg_txn_val:.2f}")
print(f"Fraud Rate: {fraud_rate:.2f}%")
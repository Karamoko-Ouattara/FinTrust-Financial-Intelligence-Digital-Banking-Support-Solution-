WITH RFM_Base AS (
    SELECT 
        c.Customer_ID,
        c.Customer_Name,
        c.Risk_Score,
        MAX(t.Transaction_Date) AS last_txn_date,
        COUNT(t.Transaction_ID) AS frequency,
        SUM(t.Transaction_Amount) AS monetary_value,
        ROUND(AVG(t.Transaction_Amount)::numeric, 2) AS avg_txn_value
    FROM customers c
    LEFT JOIN transactions t ON c.Customer_ID = t.Customer_ID
    GROUP BY c.Customer_ID, c.Customer_Name, c.Risk_Score
)
SELECT 
    Customer_ID,
    Customer_Name,
    Risk_Score,
    frequency,
    monetary_value,
    avg_txn_value,
    NTILE(4) OVER (ORDER BY last_txn_date ASC) AS recency_score,
    NTILE(4) OVER (ORDER BY frequency DESC) AS frequency_score,
    NTILE(4) OVER (ORDER BY monetary_value DESC) AS monetary_score
FROM RFM_Base
ORDER BY monetary_value DESC;
WITH CustomerStats AS (
    SELECT 
        Customer_ID,
        AVG(Transaction_Amount) AS avg_amount,
        STDDEV(Transaction_Amount) AS std_amount
    FROM transactions
    GROUP BY Customer_ID
)
SELECT 
    t.Transaction_ID,
    t.Customer_ID,
    t.Transaction_Date,
    t.Transaction_Amount,
    t.Transaction_Type,
    t.Location,
    cs.avg_amount,
    ROUND((t.Transaction_Amount / NULLIF(cs.avg_amount, 0))::numeric, 2) AS spike_factor,
    CASE 
        WHEN t.Transaction_Amount > (cs.avg_amount + 2 * COALESCE(cs.std_amount, 0)) 
             AND EXTRACT(HOUR FROM t.Transaction_Date) IN (23, 0, 1, 2, 3, 4) THEN 'High Risk'
        WHEN t.Transaction_Amount > (cs.avg_amount + 2 * COALESCE(cs.std_amount, 0)) THEN 'Medium Risk'
        ELSE 'Low Risk'
    END AS risk_category
FROM transactions t
JOIN CustomerStats cs ON t.Customer_ID = cs.Customer_ID
WHERE t.Transaction_Amount > (cs.avg_amount * 2)
ORDER BY t.Transaction_Amount DESC;
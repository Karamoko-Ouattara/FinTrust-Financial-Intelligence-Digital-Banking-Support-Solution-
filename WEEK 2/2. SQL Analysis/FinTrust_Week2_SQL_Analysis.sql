-- 1. CREATE TABLE CUSTOMERS
CREATE TABLE FinTrust_Customer_Data (
    Customer_ID VARCHAR(20) PRIMARY KEY,
    Customer_Name VARCHAR(100),
    Age INT,
    Gender VARCHAR(20),
    City VARCHAR(50),
    Customer_Segment VARCHAR(50),
    Account_Type VARCHAR(50),
    Tenure_Months INT,
    Digital_Engagement_Score NUMERIC(5, 2),
    Monthly_Income_Band VARCHAR(50),
    Preferred_Channel VARCHAR(50),
    Account_Status VARCHAR(20)
);

-- 2. CREATE TABLE transactions
CREATE TABLE FinTrust_Transaction_Data (
    Transaction_ID VARCHAR(20) PRIMARY KEY,
    Customer_ID VARCHAR(20) REFERENCES FinTrust_Customer_Data(Customer_ID),
    Transaction_DateTime TIMESTAMP,
    Transaction_Type VARCHAR(50),
    Amount_NGN NUMERIC(15, 2),
    Channel VARCHAR(50),
    Device_Type VARCHAR(50),
    Location VARCHAR(50),
    International_Transaction VARCHAR(10),
    Transaction_Status VARCHAR(20),
    Risk_Review_Flag VARCHAR(10)
);


--Q1 ---- Nombre total de clients (Customer Behaviour)
--Business Question
---Combien de clients sont enregistres chez FinTrust ?

SELECT COUNT(DISTINCT customer_id) AS total_customers
FROM fintrust_customer_data;

--- Q2 --- Customer Segments
--- Quel segment de clientèle est le plus représenté ?

SELECT
    customer_segment,
    COUNT(*) AS number_of_customers,
    ROUND(COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER(),2) AS percentage
FROM fintrust_customer_data
GROUP BY customer_segment
ORDER BY number_of_customers DESC;

--Q3 --- transaction activity
--- Quels sont les clients ayant réalisé le plus de transactions ?

SELECT
    customer_id,
    COUNT(transaction_id) AS total_transactions
FROM fintrust_transaction_data
GROUP BY customer_id
ORDER BY total_transactions DESC
LIMIT All;

--- Q4 ---Transaction Value
--- Quel est le volume financier traité par FinTrust ?

SELECT
    SUM(amount_ngn) AS total_transaction_value,
    AVG(amount_ngn) AS average_transaction_value,
    MIN(amount_ngn) AS minimum_transaction,
    MAX(amount_ngn) AS maximum_transaction
FROM fintrust_transaction_data;

---Q5 --- Transaction Type
--- Quel type de transaction est le plus utilisé ?

SELECT
    transaction_type,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount_ngn),2) AS total_value
FROM fintrust_transaction_data
GROUP BY transaction_type
ORDER BY transaction_count DESC;


--- Q6 --- Transaction Channel
--- Quel canal digital est le plus utilisé ?

SELECT
    channel,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount_ngn),2) AS total_value
FROM fintrust_transaction_data
GROUP BY channel
ORDER BY total_transactions DESC;

--- Q7 --- Transaction Status
---- Quel est le taux de réussite des transactions ?

SELECT
    transaction_status,
    COUNT(*) AS total_transactions,
    ROUND(COUNT(*)*100.0 /
    SUM(COUNT(*)) OVER(),2) AS percentage
FROM fintrust_transaction_data
GROUP BY transaction_status
ORDER BY total_transactions DESC;

--- Q8 --- Risk Review Patterns
--- Quels clients possèdent le plus de transactions signalées à risque ?

SELECT
    risk_review_flag,
    COUNT(*) AS total_transactions,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
FROM fintrust_transaction_data
GROUP BY risk_review_flag
ORDER BY total_transactions DESC;

--- Q9 --- Customer Segments + Value
--- Quel segment rapporte le plus ?

SELECT
    c.customer_segment,
    ROUND(SUM(t.amount_ngn),2) AS total_value,
    COUNT(t.transaction_id) AS total_transactions
FROM fintrust_customer_data c
JOIN fintrust_transaction_data t
ON c.customer_id = t.customer_id
GROUP BY c.customer_segment
ORDER BY total_value DESC;

--- Q10 --- Monthly Activity
--- Comment évolue l'activité bancaire chaque mois ?

SELECT
    DATE_TRUNC('month', transaction_date) AS month,
    COUNT(*) AS transactions,
    ROUND(SUM(amount_ngn),2) AS transaction_value
FROM fintrust_transaction_data
GROUP BY month
ORDER BY month;

--- Q11 --- Channel most failled
--- Quel canal présente le plus de transactions échouées ?

SELECT
    channel,
    COUNT(*) AS failed_transactions
FROM fintrust_transaction_data
WHERE transaction_status = 'Failed'
GROUP BY channel
ORDER BY failed_transactions DESC;

--- Q12 --- Channel Used
--- Quels clients utilisent plusieurs canaux de paiement ?

SELECT
    customer_id,
    COUNT(DISTINCT channel) AS channels_used
FROM fintrust_transaction_data
GROUP BY customer_id
HAVING COUNT(DISTINCT transaction_channel) >= 3
ORDER BY channels_used DESC;


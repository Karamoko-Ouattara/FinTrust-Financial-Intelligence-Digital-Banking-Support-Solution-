WITH RFM_Base AS (
    SELECT 
        c.customer_id,
        c.customer_segment,
        c.account_type,
        c.account_status,
        MAX(t.transaction_datetime)                               AS last_txn_date,
        COUNT(t.transaction_id)                                   AS frequency,
        COALESCE(SUM(t.amount_ngn), 0)                            AS monetary_value,
        ROUND(COALESCE(AVG(t.amount_ngn), 0)::numeric, 2)         AS avg_txn_value
    FROM fintrust_customer_data c
    LEFT JOIN fintrust_transaction_data t
           ON c.customer_id = t.customer_id
          -- AND t.transaction_status = 'Successful'   -- à adapter selon vos valeurs
    GROUP BY c.customer_id, c.customer_segment, c.account_type, c.account_status
)
SELECT 
    customer_id,
    customer_segment,
    account_type,
    account_status,
    last_txn_date,
    CURRENT_DATE - last_txn_date::date AS days_since_last_txn,
    frequency,
    monetary_value,
    avg_txn_value,
    NTILE(4) OVER (ORDER BY last_txn_date ASC NULLS FIRST, customer_id) AS recency_score,
    NTILE(4) OVER (ORDER BY frequency ASC, customer_id)                 AS frequency_score,
    NTILE(4) OVER (ORDER BY monetary_value ASC, customer_id)            AS monetary_score
FROM RFM_Base
ORDER BY monetary_value DESC, customer_id;

-------------------------------------------------------------------------------------------------------


WITH RFM_Base AS (
    SELECT 
        c.customer_id,
        c.customer_segment,
        c.preferred_channel,
        MAX(t.transaction_datetime)        AS last_txn_date,
        COUNT(t.transaction_id)            AS frequency,
        COALESCE(SUM(t.amount_ngn), 0)     AS monetary_value
    FROM fintrust_customer_data c
    LEFT JOIN fintrust_transaction_data t
           ON c.customer_id = t.customer_id
          -- AND t.transaction_status = 'Successful'   -- à adapter
    GROUP BY c.customer_id, c.customer_segment, c.preferred_channel
),
RFM_Scores AS (
    SELECT *,
        NTILE(4) OVER (ORDER BY last_txn_date ASC NULLS FIRST, customer_id) AS r,
        NTILE(4) OVER (ORDER BY frequency ASC, customer_id)                 AS f,
        NTILE(4) OVER (ORDER BY monetary_value ASC, customer_id)            AS m
    FROM RFM_Base
),
RFM_Profiles AS (
    SELECT *,
        CASE
            WHEN frequency = 0                  THEN 'Inactifs (aucune transaction)'
            WHEN r >= 3 AND f >= 3 AND m >= 3   THEN 'Champions'
            WHEN r >= 3 AND f >= 3              THEN 'Fidèles'
            WHEN r >= 3 AND f <= 2              THEN 'Nouveaux / récents'
            WHEN r <= 2 AND f >= 3 AND m >= 3   THEN 'À risque (forte valeur)'
            WHEN r = 1  AND f <= 2              THEN 'Perdus'
            ELSE                                     'À réactiver'
        END AS profil
    FROM RFM_Scores
)
SELECT customer_segment,
       profil,
       COUNT(*)                                                                          AS nb_clients,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY customer_segment), 1)   AS pct_du_segment,
       ROUND(SUM(monetary_value)::numeric, 0)                                            AS montant_total_ngn
FROM RFM_Profiles
GROUP BY customer_segment, profil
ORDER BY customer_segment, nb_clients DESC;

--------------------------------------------------------------------

WITH CustomerStats AS (
    SELECT 
        customer_id,
        COUNT(*)           AS nb_txn,
        AVG(amount_ngn)    AS avg_amount,
        STDDEV(amount_ngn) AS std_amount
    FROM fintrust_transaction_data
    -- WHERE transaction_status = 'Successful'   -- à adapter
    GROUP BY customer_id
)
SELECT 
    t.transaction_id,
    t.customer_id,
    t.transaction_datetime,
    t.amount_ngn,
    t.transaction_type,
    t.location,
    t.risk_review_flag,
    cs.nb_txn,
    ROUND(cs.avg_amount::numeric, 2)                                  AS avg_amount,
    ROUND((t.amount_ngn / NULLIF(cs.avg_amount, 0))::numeric, 2)      AS spike_factor,
    CASE 
        WHEN EXTRACT(HOUR FROM t.transaction_datetime) IN (23, 0, 1, 2, 3, 4)
            THEN 'High Risk'
        ELSE 'Medium Risk'
    END AS risk_category
FROM fintrust_transaction_data t
JOIN CustomerStats cs ON t.customer_id = cs.customer_id
WHERE cs.nb_txn >= 5
  AND t.amount_ngn > cs.avg_amount + 2 * COALESCE(cs.std_amount, 0)
ORDER BY spike_factor DESC NULLS LAST, t.amount_ngn DESC;
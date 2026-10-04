
--- STATS CUSTOMERS ---

SELECT
    City,

    -- Moyennes
    ROUND(AVG(Age), 2)                       AS Avg_Age,
    ROUND(AVG(Tenure_Months), 2)             AS Avg_Tenure_Months,
    ROUND(AVG(Digital_Engagement_Score), 2)  AS Avg_Digital_Engagement_Score,
    ROUND(AVG(
        CASE Monthly_Income_Band
            WHEN 'Below 100k' THEN 1
            WHEN '100k-249k'  THEN 2
            WHEN '250k-499k'  THEN 3
            WHEN '500k-999k'  THEN 4
            WHEN '1m+'        THEN 5
        END
    ), 2)                                    AS Avg_Income_Band_Rank,

    -- Genre
    SUM(CASE WHEN Gender = 'Female' THEN 1 ELSE 0 END) AS Nb_Female,
    SUM(CASE WHEN Gender = 'Male'   THEN 1 ELSE 0 END) AS Nb_Male,

    -- Segment client
    SUM(CASE WHEN Customer_Segment = 'Everyday' THEN 1 ELSE 0 END) AS Nb_Segment_Everyday,
    SUM(CASE WHEN Customer_Segment = 'Premium'  THEN 1 ELSE 0 END) AS Nb_Segment_Premium,
    SUM(CASE WHEN Customer_Segment = 'Student'  THEN 1 ELSE 0 END) AS Nb_Segment_Student,
    SUM(CASE WHEN Customer_Segment = 'SME'      THEN 1 ELSE 0 END) AS Nb_Segment_SME,

    -- Type de compte
    SUM(CASE WHEN Account_Type = 'Savings' THEN 1 ELSE 0 END) AS Nb_Account_Savings,
    SUM(CASE WHEN Account_Type = 'Current' THEN 1 ELSE 0 END) AS Nb_Account_Current,
    SUM(CASE WHEN Account_Type = 'Premium' THEN 1 ELSE 0 END) AS Nb_Account_Premium,

    -- Contrôle
    COUNT(*)                                 AS Nb_Customers
FROM FinTrust_Customer_Data
GROUP BY City
ORDER BY City;

--- STATS TRANSACTIONS ---

SELECT
    City,
    SUM(CASE WHEN Account_Status = 'Active'     THEN 1 ELSE 0 END) AS Nb_Active,
    SUM(CASE WHEN Account_Status = 'Dormant'    THEN 1 ELSE 0 END) AS Nb_Dormant,
    SUM(CASE WHEN Account_Status = 'Restricted' THEN 1 ELSE 0 END) AS Nb_Restricted,
    COUNT(*)                                                       AS Nb_Customers,
    ROUND(100.0 * SUM(CASE WHEN Account_Status = 'Active'     THEN 1 ELSE 0 END) / COUNT(*), 1) AS Pct_Active,
    ROUND(100.0 * SUM(CASE WHEN Account_Status = 'Dormant'    THEN 1 ELSE 0 END) / COUNT(*), 1) AS Pct_Dormant,
    ROUND(100.0 * SUM(CASE WHEN Account_Status = 'Restricted' THEN 1 ELSE 0 END) / COUNT(*), 1) AS Pct_Restricted
FROM FinTrust_Customer_Data
GROUP BY City
ORDER BY City;

SELECT
    Location                                   AS City,
    COUNT(*)                                   AS Nb_Transactions,
    ROUND(AVG(Amount_NGN), 2)                  AS Avg_Amount_NGN,

    -- Transaction_Type
    SUM(CASE WHEN Transaction_Type = 'Transfer'        THEN 1 ELSE 0 END) AS Nb_Type_Transfer,
    SUM(CASE WHEN Transaction_Type = 'Card Purchase'   THEN 1 ELSE 0 END) AS Nb_Type_Card_Purchase,
    SUM(CASE WHEN Transaction_Type = 'Bill Payment'    THEN 1 ELSE 0 END) AS Nb_Type_Bill_Payment,
    SUM(CASE WHEN Transaction_Type = 'Cash Withdrawal' THEN 1 ELSE 0 END) AS Nb_Type_Cash_Withdrawal,
    SUM(CASE WHEN Transaction_Type = 'Deposit'         THEN 1 ELSE 0 END) AS Nb_Type_Deposit,
    SUM(CASE WHEN Transaction_Type = 'Airtime/Data'    THEN 1 ELSE 0 END) AS Nb_Type_Airtime_Data,

    -- Channel
    SUM(CASE WHEN Channel = 'Mobile App' THEN 1 ELSE 0 END) AS Nb_Channel_Mobile_App,
    SUM(CASE WHEN Channel = 'POS'        THEN 1 ELSE 0 END) AS Nb_Channel_POS,
    SUM(CASE WHEN Channel = 'Web'        THEN 1 ELSE 0 END) AS Nb_Channel_Web,
    SUM(CASE WHEN Channel = 'ATM'        THEN 1 ELSE 0 END) AS Nb_Channel_ATM,
    SUM(CASE WHEN Channel = 'USSD'       THEN 1 ELSE 0 END) AS Nb_Channel_USSD,

    -- Device_Type
    SUM(CASE WHEN Device_Type = 'Android'      THEN 1 ELSE 0 END) AS Nb_Device_Android,
    SUM(CASE WHEN Device_Type = 'iOS'          THEN 1 ELSE 0 END) AS Nb_Device_iOS,
    SUM(CASE WHEN Device_Type = 'POS Terminal' THEN 1 ELSE 0 END) AS Nb_Device_POS_Terminal,
    SUM(CASE WHEN Device_Type = 'Web Browser'  THEN 1 ELSE 0 END) AS Nb_Device_Web_Browser,
    SUM(CASE WHEN Device_Type = 'ATM Terminal' THEN 1 ELSE 0 END) AS Nb_Device_ATM_Terminal,
    SUM(CASE WHEN Device_Type = 'Unknown'      THEN 1 ELSE 0 END) AS Nb_Device_Unknown,

    -- International_Transaction
    SUM(CASE WHEN International_Transaction = 'Yes' THEN 1 ELSE 0 END) AS Nb_International,
    SUM(CASE WHEN International_Transaction = 'No'  THEN 1 ELSE 0 END) AS Nb_Domestic,

    -- Transaction_Status
    SUM(CASE WHEN Transaction_Status = 'Successful' THEN 1 ELSE 0 END) AS Nb_Status_Successful,
    SUM(CASE WHEN Transaction_Status = 'Failed'     THEN 1 ELSE 0 END) AS Nb_Status_Failed,
    SUM(CASE WHEN Transaction_Status = 'Reversed'   THEN 1 ELSE 0 END) AS Nb_Status_Reversed,
    SUM(CASE WHEN Transaction_Status = 'Pending'    THEN 1 ELSE 0 END) AS Nb_Status_Pending,

    -- Risk_Review_Flag
    SUM(CASE WHEN Risk_Review_Flag = 'Yes' THEN 1 ELSE 0 END) AS Nb_Risk_Flagged,
    SUM(CASE WHEN Risk_Review_Flag = 'No'  THEN 1 ELSE 0 END) AS Nb_Risk_Not_Flagged
FROM FinTrust_Transaction_Data
GROUP BY Location
ORDER BY Location;
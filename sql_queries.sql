WITH CustomerSummary AS (
    SELECT 
        CustomerID,
        MAX(InvoiceDate) AS LastPurchaseDate,
        COUNT(DISTINCT InvoiceNo) AS Frequency,
        SUM(Quantity * UnitPrice) AS MonetaryValue
    FROM online_retail
    WHERE CustomerID IS NOT NULL 
      AND Quantity > 0 
      AND UnitPrice > 0
    GROUP BY CustomerID
),
ReferenceDateCTE AS (
    SELECT MAX(LastPurchaseDate) + INTERVAL '1 day' AS SnapshotDate
    FROM CustomerSummary
),
RFM_Calculated AS (
    SELECT 
        c.CustomerID,
        DATE_PART('day', r.SnapshotDate - c.LastPurchaseDate) AS RecencyDays,
        c.Frequency,
        ROUND(CAST(c.MonetaryValue AS NUMERIC), 2) AS Monetary
    FROM CustomerSummary c
    CROSS JOIN ReferenceDateCTE r
)
SELECT 
    CustomerID,
    RecencyDays,
    Frequency,
    Monetary,
    NTILE(5) OVER (ORDER BY RecencyDays DESC) AS R_Score,
    NTILE(5) OVER (ORDER BY Frequency ASC)   AS F_Score,
    NTILE(5) OVER (ORDER BY Monetary ASC)    AS M_Score
FROM RFM_Calculated;
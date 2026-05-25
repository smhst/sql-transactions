-- RFM-анализ: Recency (давность), Frequency (частота), Monetary (деньги)
WITH customer_tx AS (
    SELECT 
        c.customer_id,
        MAX(t.transaction_date) AS last_tx,
        COUNT(t.transaction_id) AS frequency,
        SUM(CASE WHEN t.status='approved' THEN t.amount ELSE 0 END) AS monetary
    FROM customers c
    JOIN cards cd ON c.customer_id = cd.customer_id
    JOIN transactions t ON cd.card_id = t.card_id
    WHERE t.status = 'approved'
    GROUP BY c.customer_id
),
rfm_scores AS (
    SELECT 
        customer_id,
        julianday('2025-01-01') - julianday(last_tx) AS recency,
        frequency,
        monetary,
        NTILE(4) OVER (ORDER BY julianday('2025-01-01') - julianday(last_tx) DESC) AS r_quartile,
        NTILE(4) OVER (ORDER BY frequency) AS f_quartile,
        NTILE(4) OVER (ORDER BY monetary) AS m_quartile
    FROM customer_tx
)
SELECT 
    customer_id,
    recency,
    frequency,
    monetary,
    r_quartile,
    f_quartile,
    m_quartile,
    CASE 
        WHEN r_quartile >= 3 AND f_quartile >= 3 AND m_quartile >= 3 THEN 'VIP'
        WHEN r_quartile >= 3 AND f_quartile >= 2 THEN 'Loyal'
        WHEN r_quartile <= 2 THEN 'At Risk'
        ELSE 'Regular'
    END AS segment
FROM rfm_scores
ORDER BY customer_id;

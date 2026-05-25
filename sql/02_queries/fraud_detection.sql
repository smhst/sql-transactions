-- Поиск транзакций, которые ночные, на большую сумму или в другой стране
WITH tx_enriched AS (
    SELECT 
        t.transaction_id,
        t.amount,
        t.transaction_date,
        t.fraud_flag,
        cd.customer_id,
        c.country AS home_country,
        m.country AS tx_country,
        CAST(strftime('%H', t.transaction_date) AS INTEGER) AS hour
    FROM transactions t
    JOIN cards cd ON t.card_id = cd.card_id
    JOIN customers c ON cd.customer_id = c.customer_id
    JOIN merchants m ON t.merchant_id = m.merchant_id
)
SELECT 
    transaction_id,
    amount,
    transaction_date,
    hour,
    home_country,
    tx_country,
    CASE 
        WHEN amount > 100000 THEN 'High amount'
        WHEN hour BETWEEN 0 AND 5 AND tx_country != home_country THEN 'Night foreign'
        WHEN hour BETWEEN 0 AND 5 THEN 'Night'
        WHEN tx_country != home_country THEN 'Foreign'
        ELSE 'Normal'
    END AS alert_reason
FROM tx_enriched
WHERE alert_reason != 'Normal' OR fraud_flag = 1
ORDER BY amount DESC;

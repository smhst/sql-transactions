-- Когорты по месяцу первой транзакции
WITH first_month AS (
    SELECT 
        cd.customer_id,
        strftime('%Y-%m', MIN(t.transaction_date)) AS cohort
    FROM transactions t
    JOIN cards cd ON t.card_id = cd.card_id
    GROUP BY cd.customer_id
),
activity AS (
    SELECT DISTINCT
        cd.customer_id,
        strftime('%Y-%m', t.transaction_date) AS active_month
    FROM transactions t
    JOIN cards cd ON t.card_id = cd.card_id
)
SELECT 
    fm.cohort,
    a.active_month,
    COUNT(DISTINCT fm.customer_id) AS users
FROM first_month fm
JOIN activity a ON fm.customer_id = a.customer_id
WHERE a.active_month >= fm.cohort
GROUP BY fm.cohort, a.active_month
ORDER BY fm.cohort, a.active_month;

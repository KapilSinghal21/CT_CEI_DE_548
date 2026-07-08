-- cohort_analysis.sql
-- Queries 15-16: Cohort/Retention analysis and Market Basket analysis

-- 15. Complex CTE: Cohort analysis by registration month
WITH cohorts AS (
    SELECT
        customer_id,
        strftime('%Y-%m', registration_date) AS cohort_month
    FROM customers
),
customer_order_months AS (
    SELECT
        o.customer_id,
        strftime('%Y-%m', o.order_date) AS order_month
    FROM orders o
    WHERE o.customer_id IS NOT NULL
),
cohort_activity AS (
    SELECT
        c.cohort_month,
        c.customer_id,
        com.order_month,
        CAST(
            (CAST(strftime('%Y', com.order_month || '-01') AS INTEGER) - CAST(strftime('%Y', c.cohort_month || '-01') AS INTEGER)) * 12
            + (CAST(strftime('%m', com.order_month || '-01') AS INTEGER) - CAST(strftime('%m', c.cohort_month || '-01') AS INTEGER))
        AS INTEGER) AS month_number
    FROM cohorts c
    JOIN customer_order_months com ON com.customer_id = c.customer_id
),
cohort_size AS (
    SELECT cohort_month, COUNT(DISTINCT customer_id) AS cohort_customers
    FROM cohorts
    GROUP BY cohort_month
)
SELECT
    ca.cohort_month,
    ca.month_number,
    COUNT(DISTINCT ca.customer_id) AS active_customers,
    cs.cohort_customers,
    ROUND(COUNT(DISTINCT ca.customer_id) * 100.0 / cs.cohort_customers, 2) AS retention_rate_percent
FROM cohort_activity ca
JOIN cohort_size cs ON cs.cohort_month = ca.cohort_month
WHERE ca.month_number BETWEEN 0 AND 3
GROUP BY ca.cohort_month, ca.month_number
ORDER BY ca.cohort_month, ca.month_number;


-- 16. Self-join with window function: products frequently bought together
-- (pairs within the same order, deduplicated so A-B and B-A count once)
SELECT
    p_a.product_name AS product_a,
    p_b.product_name AS product_b,
    COUNT(*) AS times_bought_together
FROM order_items oi_a
JOIN order_items oi_b
    ON oi_a.order_id = oi_b.order_id
    AND oi_a.product_id < oi_b.product_id  -- ensures each pair counted once, no self-pairs
JOIN products p_a ON p_a.product_id = oi_a.product_id
JOIN products p_b ON p_b.product_id = oi_b.product_id
WHERE oi_a.quantity > 0 AND oi_b.quantity > 0
GROUP BY p_a.product_name, p_b.product_name
ORDER BY times_bought_together DESC
LIMIT 50;

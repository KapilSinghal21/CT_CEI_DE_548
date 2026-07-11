-- ============================================================
-- SQL Layer
-- ============================================================

-- 1. Sales by category with running total
WITH category_sales AS (
    SELECT
        p.product_category_name_english AS category,
        SUM(oi.price) AS total_revenue,
        COUNT(DISTINCT oi.order_id) AS total_orders
    FROM delta.`/Volumes/workspace/default/raw_data/silver/order_items` oi
    JOIN delta.`/Volumes/workspace/default/raw_data/silver/products` p ON oi.product_id = p.product_id
    GROUP BY p.product_category_name_english
)
SELECT
    category,
    total_revenue,
    total_orders,
    SUM(total_revenue) OVER (ORDER BY total_revenue DESC) AS running_total_revenue,
    RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank
FROM category_sales
ORDER BY total_revenue DESC;


-- 2. Month-over-month revenue trend
WITH monthly_revenue AS (
    SELECT
        DATE_FORMAT(o.order_purchase_timestamp, 'yyyy-MM') AS month,
        SUM(p.payment_value) AS revenue
    FROM delta.`/Volumes/workspace/default/raw_data/silver/orders` o
    JOIN delta.`/Volumes/workspace/default/raw_data/silver/order_payments` p ON o.order_id = p.order_id
    GROUP BY DATE_FORMAT(o.order_purchase_timestamp, 'yyyy-MM')
)
SELECT
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month) AS prev_month_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month) * 100, 2
    ) AS mom_growth_pct
FROM monthly_revenue
ORDER BY month;


-- 3. Late delivery rate by state
SELECT
    c.customer_state,
    COUNT(*) AS total_orders,
    SUM(CASE
            WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1
            ELSE 0
        END) AS late_orders,
    ROUND(SUM(CASE
            WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1
            ELSE 0
        END) * 100.0 / COUNT(*), 2) AS late_pct
FROM delta.`/Volumes/workspace/default/raw_data/silver/orders` o
JOIN delta.`/Volumes/workspace/default/raw_data/silver/customers` c ON o.customer_id = c.customer_id
WHERE o.order_delivered_customer_date IS NOT NULL
GROUP BY c.customer_state
ORDER BY late_pct DESC;


-- 4. Top 5 sellers per state
WITH seller_revenue AS (
    SELECT
        s.seller_id,
        s.seller_state,
        SUM(oi.price) AS revenue
    FROM delta.`/Volumes/workspace/default/raw_data/silver/order_items` oi
    JOIN delta.`/Volumes/workspace/default/raw_data/silver/sellers` s ON oi.seller_id = s.seller_id
    GROUP BY s.seller_id, s.seller_state
)
SELECT *
FROM (
    SELECT
        seller_id,
        seller_state,
        revenue,
        ROW_NUMBER() OVER (PARTITION BY seller_state ORDER BY revenue DESC) AS rank_in_state
    FROM seller_revenue
) ranked
WHERE rank_in_state <= 5
ORDER BY seller_state, rank_in_state;


-- 5. Customer RFM segments
WITH customer_orders AS (
    SELECT
        o.customer_id,
        MAX(o.order_purchase_timestamp) AS last_order_date,
        COUNT(DISTINCT o.order_id) AS frequency,
        SUM(p.payment_value) AS monetary
    FROM delta.`/Volumes/workspace/default/raw_data/silver/orders` o
    JOIN delta.`/Volumes/workspace/default/raw_data/silver/order_payments` p ON o.order_id = p.order_id
    GROUP BY o.customer_id
),
rfm_scored AS (
    SELECT
        customer_id,
        DATEDIFF(
            (SELECT MAX(order_purchase_timestamp) FROM delta.`/Volumes/workspace/default/raw_data/silver/orders`),
            last_order_date
        ) AS recency_days,
        frequency,
        monetary
    FROM customer_orders
)
SELECT
    customer_id,
    recency_days,
    frequency,
    monetary,
    CASE
        WHEN recency_days <= 90 AND frequency >= 3 THEN 'Loyal'
        WHEN recency_days <= 90 AND frequency < 3 THEN 'Recent'
        WHEN recency_days > 180 THEN 'Churned'
        ELSE 'At Risk'
    END AS customer_segment
FROM rfm_scored;

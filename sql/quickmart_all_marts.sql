-- QuickMart 单月最终版 Data Mart SQL
-- 观察窗口：2026-04-01 ~ 2026-04-30
-- 异常期：2026-04-21 ~ 2026-04-26
--
-- 口径说明：
-- 1. 行为类集市统一采用 order_id + product_id 交易链路口径
-- 2. 首页同时保留两个不同用途的转化指标：
--    - first_order_pay_rate：支付用户数 / 新用户数
--    - checkout_to_paid_rate：支付链路数 / 结算链路数
-- 3. 留存、反馈、A/B 使用各自独立底表

-- =========================================================
-- Step 0：交易链路临时表
-- =========================================================
CREATE TEMP TABLE event_chain_level AS
SELECT
    CAST(mock_date AS DATE) AS mock_date,
    CASE
        WHEN CAST(mock_date AS DATE) BETWEEN DATE '2026-04-21' AND DATE '2026-04-26' THEN '2. 异常期'
        ELSE '1. 正常期'
    END AS period,
    channel,
    city,
    is_top20_product,
    CAST(order_id AS BIGINT) * 1000000 + CAST(product_id AS BIGINT) AS chain_id,
    MAX(CASE WHEN action = '曝光' THEN 1 ELSE 0 END) AS has_exposure,
    MAX(CASE WHEN action = '点击' THEN 1 ELSE 0 END) AS has_click,
    MAX(CASE WHEN action = '加购' THEN 1 ELSE 0 END) AS has_cart,
    MAX(CASE WHEN action = '结算' THEN 1 ELSE 0 END) AS has_checkout,
    MAX(CASE WHEN action = '支付' THEN 1 ELSE 0 END) AS has_paid
FROM event_log
GROUP BY 1, 2, 3, 4, 5, 6;

-- =========================================================
-- mart_01_executive_summary.csv
-- 首页高管总览集市
-- =========================================================
WITH daily_base AS (
    SELECT
        CAST(mock_date AS DATE) AS mock_date,
        COUNT(DISTINCT CASE WHEN action = '曝光' THEN user_id END) AS daily_new_users,
        COUNT(DISTINCT CASE WHEN action = '支付' THEN user_id END) AS paid_user_uv,
        COUNT(DISTINCT CASE WHEN action = '结算' THEN CAST(order_id AS BIGINT) * 1000000 + CAST(product_id AS BIGINT) END) AS checkout_users,
        COUNT(DISTINCT CASE WHEN action = '支付' THEN CAST(order_id AS BIGINT) * 1000000 + CAST(product_id AS BIGINT) END) AS paid_users
    FROM event_log
    GROUP BY 1
),
retention_daily AS (
    SELECT
        CAST(cohort_date AS DATE) AS mock_date,
        ROUND(AVG(is_retained_d1), 4) AS d1_retention_rate
    FROM retention_base
    GROUP BY 1
),
feedback_daily AS (
    SELECT
        CAST(mock_date AS DATE) AS mock_date,
        COUNT(*) AS total_feedback_count,
        SUM(is_stockout_related) AS stockout_feedback_count
    FROM feedback_base
    GROUP BY 1
),
daily_metrics AS (
    SELECT
        b.mock_date,
        b.daily_new_users,
        b.paid_user_uv,
        b.checkout_users,
        b.paid_users,
        ROUND(b.paid_user_uv * 1.0 / NULLIF(b.daily_new_users, 0), 4) AS first_order_pay_rate,
        ROUND(b.paid_users * 1.0 / NULLIF(b.checkout_users, 0), 4) AS checkout_to_paid_rate,
        COALESCE(r.d1_retention_rate, 0) AS d1_retention_rate,
        COALESCE(f.total_feedback_count, 0) AS total_feedback_count,
        COALESCE(f.stockout_feedback_count, 0) AS stockout_feedback_count,
        ROUND(COALESCE(f.stockout_feedback_count, 0) * 1.0 / NULLIF(COALESCE(f.total_feedback_count, 0), 0), 4) AS stockout_feedback_rate,
        CASE
            WHEN b.mock_date BETWEEN DATE '2026-04-21' AND DATE '2026-04-26'
                THEN ROUND(b.paid_users * (90 + random() * 18), 2)
            ELSE ROUND(b.paid_users * (92 + random() * 16), 2)
        END AS first_order_gmv
    FROM daily_base b
    LEFT JOIN retention_daily r
        ON b.mock_date = r.mock_date
    LEFT JOIN feedback_daily f
        ON b.mock_date = f.mock_date
)
SELECT
    mock_date,
    daily_new_users,
    paid_user_uv,
    checkout_users,
    paid_users,
    first_order_pay_rate,
    checkout_to_paid_rate,
    d1_retention_rate,
    total_feedback_count,
    stockout_feedback_count,
    stockout_feedback_rate,
    first_order_gmv,
    ROUND(first_order_gmv * 1.0 / NULLIF(paid_users, 0), 2) AS first_order_aov
FROM daily_metrics
ORDER BY mock_date;

-- =========================================================
-- mart_02_overall_funnel.csv
-- 整体漏斗集市
-- =========================================================
SELECT
    period,
    SUM(has_exposure) AS exposure_uv,
    SUM(has_click) AS click_uv,
    SUM(has_cart) AS cart_uv,
    SUM(has_checkout) AS checkout_uv,
    SUM(has_paid) AS paid_uv,
    ROUND(SUM(has_click) * 1.0 / NULLIF(SUM(has_exposure), 0), 4) AS exposure_to_click_rate,
    ROUND(SUM(has_cart) * 1.0 / NULLIF(SUM(has_click), 0), 4) AS click_to_cart_rate,
    ROUND(SUM(has_checkout) * 1.0 / NULLIF(SUM(has_cart), 0), 4) AS cart_to_checkout_rate,
    ROUND(SUM(has_paid) * 1.0 / NULLIF(SUM(has_checkout), 0), 4) AS checkout_to_paid_rate
FROM event_chain_level
GROUP BY 1
ORDER BY period;

-- =========================================================
-- mart_03_funnel_channel.csv
-- 渠道漏斗集市
-- =========================================================
SELECT
    period,
    channel,
    SUM(has_exposure) AS exposure_uv,
    SUM(has_click) AS click_uv,
    SUM(has_cart) AS cart_uv,
    SUM(has_checkout) AS checkout_uv,
    SUM(has_paid) AS paid_uv,
    ROUND(SUM(has_click) * 1.0 / NULLIF(SUM(has_exposure), 0), 4) AS exposure_to_click_rate,
    ROUND(SUM(has_cart) * 1.0 / NULLIF(SUM(has_click), 0), 4) AS click_to_cart_rate,
    ROUND(SUM(has_checkout) * 1.0 / NULLIF(SUM(has_cart), 0), 4) AS cart_to_checkout_rate,
    ROUND(SUM(has_paid) * 1.0 / NULLIF(SUM(has_checkout), 0), 4) AS checkout_to_paid_rate
FROM event_chain_level
GROUP BY 1, 2
ORDER BY period, channel;

-- =========================================================
-- mart_04_daily_city_oos.csv
-- 城市日级缺货与支付率集市
-- =========================================================
SELECT
    mock_date,
    city,
    SUM(has_checkout) AS checkout_uv,
    SUM(has_paid) AS paid_uv,
    ROUND(SUM(has_paid) * 1.0 / NULLIF(SUM(has_checkout), 0), 4) AS overall_pay_rate,
    SUM(CASE WHEN is_top20_product = 1 THEN has_checkout ELSE 0 END) AS top20_checkout_uv,
    SUM(CASE WHEN is_top20_product = 1 THEN has_paid ELSE 0 END) AS top20_paid_uv,
    ROUND(
        1 - (
            SUM(CASE WHEN is_top20_product = 1 THEN has_paid ELSE 0 END) * 1.0
            / NULLIF(SUM(CASE WHEN is_top20_product = 1 THEN has_checkout ELSE 0 END), 0)
        ),
        4
    ) AS oos_rate
FROM event_chain_level
GROUP BY 1, 2
ORDER BY mock_date, city;

-- =========================================================
-- mart_05_anomaly_trigger_diagnostic.csv
-- 定向异常触发证据集市
-- =========================================================
SELECT
    period,
    channel,
    city,
    is_top20_product,
    SUM(has_checkout) AS checkout_uv,
    SUM(has_paid) AS paid_uv,
    SUM(CASE WHEN has_checkout = 1 AND has_paid = 0 THEN 1 ELSE 0 END) AS blocked_uv,
    ROUND(SUM(has_paid) * 1.0 / NULLIF(SUM(has_checkout), 0), 4) AS checkout_to_pay_rate,
    ROUND(
        SUM(CASE WHEN has_checkout = 1 AND has_paid = 0 THEN 1 ELSE 0 END) * 1.0
        / NULLIF(SUM(has_checkout), 0),
        4
    ) AS blocked_rate
FROM event_chain_level
GROUP BY 1, 2, 3, 4
ORDER BY period, channel, city, is_top20_product;

-- =========================================================
-- mart_06_retention_first_order_vs_non.csv
-- 首单用户 vs 未首单用户 D1 留存集市
-- =========================================================
SELECT
    CASE
        WHEN CAST(cohort_date AS DATE) BETWEEN DATE '2026-04-21' AND DATE '2026-04-26' THEN '2. 异常期'
        ELSE '1. 正常期'
    END AS period,
    CASE
        WHEN is_first_order_user = 1 THEN '首单用户'
        ELSE '未首单用户'
    END AS user_segment,
    COUNT(*) AS total_users,
    SUM(is_retained_d1) AS retained_users,
    ROUND(AVG(is_retained_d1), 4) AS d1_retention_rate
FROM retention_base
GROUP BY 1, 2
ORDER BY period, user_segment;

-- =========================================================
-- mart_07_feedback_oos_diagnostic.csv
-- 反馈 / 客诉 / 缺货辅助证据集市
-- =========================================================
WITH checkout_city AS (
    SELECT
        period,
        city,
        SUM(has_checkout) AS checkout_uv
    FROM event_chain_level
    GROUP BY 1, 2
),
feedback_city AS (
    SELECT
        CASE
            WHEN CAST(mock_date AS DATE) BETWEEN DATE '2026-04-21' AND DATE '2026-04-26' THEN '2. 异常期'
            ELSE '1. 正常期'
        END AS period,
        city,
        COUNT(*) AS feedback_count,
        SUM(is_stockout_related) AS stockout_feedback_count,
        SUM(CASE WHEN severity_level = '高' THEN 1 ELSE 0 END) AS high_severity_feedback_count
    FROM feedback_base
    GROUP BY 1, 2
)
SELECT
    c.period,
    c.city,
    c.checkout_uv,
    COALESCE(f.feedback_count, 0) AS feedback_count,
    COALESCE(f.stockout_feedback_count, 0) AS stockout_feedback_count,
    COALESCE(f.high_severity_feedback_count, 0) AS high_severity_feedback_count,
    ROUND(COALESCE(f.feedback_count, 0) * 1.0 / NULLIF(c.checkout_uv, 0), 4) AS feedback_rate,
    ROUND(COALESCE(f.stockout_feedback_count, 0) * 1.0 / NULLIF(COALESCE(f.feedback_count, 0), 0), 4) AS stockout_feedback_rate
FROM checkout_city c
LEFT JOIN feedback_city f
    ON c.period = f.period
   AND c.city = f.city
ORDER BY c.period, c.city;

-- =========================================================
-- mart_08_ab_test_summary.csv
-- A/B 实验汇总集市
-- =========================================================
WITH city_level AS (
    SELECT
        "group" AS experiment_group,
        city,
        COUNT(*) AS total_users,
        SUM(is_paid) AS paid_users,
        ROUND(SUM(is_paid) * 1.0 / NULLIF(COUNT(*), 0), 4) AS conversion_rate
    FROM ab_test
    GROUP BY 1, 2
),
overall_level AS (
    SELECT
        "group" AS experiment_group,
        'ALL' AS city,
        COUNT(*) AS total_users,
        SUM(is_paid) AS paid_users,
        ROUND(SUM(is_paid) * 1.0 / NULLIF(COUNT(*), 0), 4) AS conversion_rate
    FROM ab_test
    GROUP BY 1
)
SELECT * FROM city_level
UNION ALL
SELECT * FROM overall_level
ORDER BY experiment_group, city;

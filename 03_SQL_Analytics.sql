-- Databricks notebook source
-- ============================================
-- QUERY 1: Currency Analysis with Categories
-- ============================================
WITH currency_summary AS (
    SELECT 
        target_currency,
        COUNT(*) as total_days,
        ROUND(MIN(exchange_rate), 4) as min_rate,
        ROUND(MAX(exchange_rate), 4) as max_rate,
        ROUND(AVG(exchange_rate), 4) as avg_rate,
        ROUND(STDDEV(exchange_rate), 4) as volatility,
        AVG(daily_change_percent) as avg_daily_change
    FROM currency_project.cleaned_data.exchange_rates
    GROUP BY target_currency
)
SELECT 
    target_currency as currency,
    total_days,
    min_rate,
    max_rate,
    avg_rate,
    volatility,
    ROUND(avg_daily_change, 2) as avg_daily_change_pct,
    CASE 
        WHEN avg_rate < 0.5 THEN 'Very Low'
        WHEN avg_rate < 1 THEN 'Low'
        WHEN avg_rate < 2 THEN 'Medium'
        WHEN avg_rate < 5 THEN 'High'
        ELSE 'Very High'
    END as rate_category,
    CASE 
        WHEN ABS(avg_daily_change) > 1 THEN 'High Volatility'
        WHEN ABS(avg_daily_change) > 0.5 THEN 'Medium Volatility'
        ELSE 'Low Volatility'
    END as volatility_category
FROM currency_summary
WHERE total_days >= 10  -- Only currencies with sufficient data
ORDER BY avg_rate DESC
LIMIT 10;

-- ============================================
-- QUERY 2: Daily Performance Analysis
-- ============================================
SELECT 
    date,
    target_currency as currency,
    ROUND(daily_avg, 4) as average_rate,
    ROUND(daily_min, 4) as minimum_rate,
    ROUND(daily_max, 4) as maximum_rate,
    ROUND(avg_daily_change, 2) as daily_change_percent,
    CASE 
        WHEN avg_daily_change > 1 THEN 'Strong Increase'
        WHEN avg_daily_change > 0.5 THEN 'Moderate Increase'
        WHEN avg_daily_change > 0 THEN 'Slight Increase'
        WHEN avg_daily_change = 0 THEN 'No Change'
        WHEN avg_daily_change > -0.5 THEN 'Slight Decrease'
        WHEN avg_daily_change > -1 THEN 'Moderate Decrease'
        ELSE 'Strong Decrease'
    END as change_description
FROM currency_project.analytics.daily_summary
WHERE target_currency IN ('USD', 'GBP', 'JPY')
    AND date >= DATE_SUB(CURRENT_DATE(), 7)
ORDER BY date DESC, currency;

-- ============================================
-- QUERY 3: Currency Pair Analysis (Simple)
-- ============================================
SELECT 
    'EUR to USD' as pair,
    ROUND(AVG(CASE WHEN target_currency = 'USD' THEN exchange_rate END), 4) as avg_rate,
    ROUND(MIN(CASE WHEN target_currency = 'USD' THEN exchange_rate END), 4) as min_rate,
    ROUND(MAX(CASE WHEN target_currency = 'USD' THEN exchange_rate END), 4) as max_rate
FROM currency_project.cleaned_data.exchange_rates
UNION ALL
SELECT 
    'EUR to GBP' as pair,
    ROUND(AVG(CASE WHEN target_currency = 'GBP' THEN exchange_rate END), 4) as avg_rate,
    ROUND(MIN(CASE WHEN target_currency = 'GBP' THEN exchange_rate END), 4) as min_rate,
    ROUND(MAX(CASE WHEN target_currency = 'GBP' THEN exchange_rate END), 4) as max_rate
FROM currency_project.cleaned_data.exchange_rates
UNION ALL
SELECT 
    'EUR to JPY' as pair,
    ROUND(AVG(CASE WHEN target_currency = 'JPY' THEN exchange_rate END), 4) as avg_rate,
    ROUND(MIN(CASE WHEN target_currency = 'JPY' THEN exchange_rate END), 4) as min_rate,
    ROUND(MAX(CASE WHEN target_currency = 'JPY' THEN exchange_rate END), 4) as max_rate
FROM currency_project.cleaned_data.exchange_rates
ORDER BY avg_rate DESC;
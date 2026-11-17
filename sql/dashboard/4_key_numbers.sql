-- Headline KPIs: number of orders, total revenue and average order value (SAR, before VAT).
SELECT COUNT(*) AS total_orders,
       SUM(amount_untaxed) AS total_revenue_sar,
       ROUND(AVG(amount_untaxed), 0) AS avg_order_value_sar
FROM sale_order
WHERE state = 'sale';

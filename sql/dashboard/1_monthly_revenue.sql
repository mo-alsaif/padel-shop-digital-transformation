-- Monthly revenue (SAR, before VAT) from confirmed sales orders.
-- Odoo stores times in UTC, so 3 hours are added to group by Riyadh time.
SELECT date_trunc('month', date_order + interval '3 hours')::date AS month,
       SUM(amount_untaxed) AS revenue_sar
FROM sale_order
WHERE state = 'sale'
GROUP BY 1
ORDER BY 1;

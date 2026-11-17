-- Top 10 products by revenue (SAR, before VAT).
-- Product names are stored as translated JSON in Odoo 18, so the English name is read with ->> 'en_US'.
SELECT pt.name->>'en_US' AS product,
       SUM(sol.price_subtotal) AS revenue_sar
FROM sale_order_line sol
JOIN sale_order so ON so.id = sol.order_id
JOIN product_product pp ON pp.id = sol.product_id
JOIN product_template pt ON pt.id = pp.product_tmpl_id
WHERE so.state = 'sale'
GROUP BY 1
ORDER BY revenue_sar DESC
LIMIT 10;

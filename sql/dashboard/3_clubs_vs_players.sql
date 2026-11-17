-- Revenue split between business customers (padel clubs) and individual players.
SELECT CASE WHEN COALESCE(rp.is_company, false)
            THEN 'Padel clubs' ELSE 'Individual players' END AS customer_type,
       SUM(so.amount_untaxed) AS revenue_sar
FROM sale_order so
JOIN res_partner rp ON rp.id = so.partner_id
WHERE so.state = 'sale'
GROUP BY 1;

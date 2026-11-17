-- Used by the n8n workflow every morning at 9:00.
-- Lists products with fewer than 5 units available in the warehouse.
-- "Available" = on hand minus stock already reserved for confirmed orders.
SELECT pt.name->>'en_US' AS product,
       ROUND(SUM(sq.quantity - sq.reserved_quantity)) AS available
FROM stock_quant sq
JOIN stock_location sl ON sl.id = sq.location_id
JOIN product_product pp ON pp.id = sq.product_id
JOIN product_template pt ON pt.id = pp.product_tmpl_id
WHERE sl.usage = 'internal'
GROUP BY 1
HAVING SUM(sq.quantity - sq.reserved_quantity) < 5
ORDER BY available;

-- Top 10 AWS services by cost
SELECT
    line_item_product_code AS service,
    SUM(line_item_unblended_cost) AS total_cost,
    COUNT(*) AS line_items
FROM
    cur_database.cur_table
WHERE
    year = '2024'
    AND month = '11'
GROUP BY
    line_item_product_code
ORDER BY
    total_cost DESC
LIMIT 10;

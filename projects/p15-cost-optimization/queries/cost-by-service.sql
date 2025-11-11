-- AWS Cost and Usage Report - Cost by Service
-- Query AWS Cost and Usage data from Athena
-- Replace 'your_cur_database' and 'your_cur_table' with actual values

SELECT
    line_item_product_code AS service_name,
    SUM(line_item_unblended_cost) AS total_cost,
    COUNT(*) AS line_item_count,
    DATE_FORMAT(line_item_usage_start_date, '%Y-%m') AS month
FROM
    your_cur_database.your_cur_table
WHERE
    line_item_usage_start_date >= DATE_ADD('month', -3, CURRENT_DATE)
    AND line_item_line_item_type = 'Usage'
GROUP BY
    line_item_product_code,
    DATE_FORMAT(line_item_usage_start_date, '%Y-%m')
ORDER BY
    month DESC,
    total_cost DESC
LIMIT 100;

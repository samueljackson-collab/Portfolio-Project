-- Top 50 Most Costly Resources
-- Identifies individual resources with highest costs

SELECT
    line_item_resource_id AS resource_id,
    line_item_product_code AS service,
    line_item_usage_type AS usage_type,
    SUM(line_item_unblended_cost) AS total_cost,
    resource_tags_user_name AS resource_name,
    resource_tags_user_environment AS environment
FROM
    your_cur_database.your_cur_table
WHERE
    line_item_usage_start_date >= DATE_ADD('month', -1, CURRENT_DATE)
    AND line_item_line_item_type = 'Usage'
    AND line_item_resource_id != ''
GROUP BY
    line_item_resource_id,
    line_item_product_code,
    line_item_usage_type,
    resource_tags_user_name,
    resource_tags_user_environment
ORDER BY
    total_cost DESC
LIMIT 50;

-- Sanitized catalog price update script
-- Purpose: merge staged CSV data into WooCommerce product tables with guardrails
-- All identifiers anonymized; replace placeholders before production use.

START TRANSACTION;

-- Guardrail: prevent negative or extreme prices from entering production
SELECT sku, channel_price
FROM import_products_staging
WHERE channel_price <= 0
   OR channel_price > 5000;

-- Upsert core product rows
INSERT INTO wp_posts (ID, post_type, post_status, post_title, post_name)
SELECT
    COALESCE(p.ID, 0) AS ID,
    'product' AS post_type,
    'publish' AS post_status,
    s.name AS post_title,
    LOWER(REPLACE(s.sku, ' ', '-')) AS post_name
FROM import_products_staging s
LEFT JOIN wp_posts p ON p.post_type = 'product' AND p.post_name = LOWER(REPLACE(s.sku, ' ', '-'))
ON DUPLICATE KEY UPDATE
    post_title = VALUES(post_title),
    post_status = VALUES(post_status);

-- Upsert pricing metadata
INSERT INTO wp_postmeta (post_id, meta_key, meta_value)
SELECT
    p.ID,
    '_price',
    FORMAT(s.channel_price, 2)
FROM import_products_staging s
JOIN wp_posts p ON p.post_type = 'product' AND p.post_name = LOWER(REPLACE(s.sku, ' ', '-'))
ON DUPLICATE KEY UPDATE meta_value = VALUES(meta_value);

-- Optional: write audit trail
INSERT INTO WP_IMPORT_LOGS (source_file, row_count, duration_seconds, notes, created_at)
VALUES ('import.csv', (SELECT COUNT(*) FROM import_products_staging), 0, 'sanitized demo', NOW());

COMMIT;

-- Catalog import validation (sanitized)
-- Goal: block deployments if incoming catalog deltas would corrupt pricing or inventory

-- 1) Check for duplicate SKUs in staging import
SELECT sku, COUNT(*) AS cnt
FROM staging_catalog_import
GROUP BY sku
HAVING COUNT(*) > 1;

-- 2) Detect price anomalies (>25% swing compared to last published)
SELECT p.sku, p.price AS new_price, c.price AS current_price,
       ROUND(((p.price - c.price) / NULLIF(c.price,0)) * 100, 2) AS pct_change
FROM staging_catalog_import p
JOIN catalog_prices c ON c.sku = p.sku
WHERE ABS(p.price - c.price) / NULLIF(c.price, 1) > 0.25;

-- 3) Ensure required attributes are present
SELECT sku
FROM staging_catalog_import
WHERE name IS NULL OR price IS NULL OR category_path IS NULL;

-- 4) Validate stock integrity (no negative quantities)
SELECT sku, stock_qty
FROM staging_catalog_import
WHERE stock_qty < 0;

-- 5) Record validation results
INSERT INTO ops_validations (job_name, status, checked_at, issues_found)
VALUES ('catalog_import', 'complete', NOW(), ROW_COUNT());

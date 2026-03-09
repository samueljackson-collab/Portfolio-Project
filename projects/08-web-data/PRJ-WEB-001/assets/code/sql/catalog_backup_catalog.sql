-- Catalog backup workflow (sanitized)
-- Purpose: capture consistent snapshot prior to weekly imports

SET @backup_ts = DATE_FORMAT(NOW(), '%Y%m%d_%H%i');
SET @backup_path = CONCAT('/backups/staging/catalog_', @backup_ts, '.sql');

-- 1) Lock tables for read to prevent drift during export
FLUSH TABLES WITH READ LOCK;

-- 2) Record manifest entry
INSERT INTO ops_jobs (job_name, status, started_at, metadata)
VALUES ('catalog_backup', 'running', NOW(), JSON_OBJECT('environment','staging','path',@backup_path));

-- 3) Export schema + data (executed via shell wrapper)
-- mysqldump -u backup_user -h localhost --single-transaction --quick \
--   --databases commerce_db --tables \
--   catalog_products catalog_prices catalog_inventory catalog_media \
--   booking_reservations booking_units booking_rate_rules \
--   > @backup_path

-- 4) Unlock tables after dump completes
UNLOCK TABLES;

-- 5) Close manifest entry
UPDATE ops_jobs
SET status = 'success', completed_at = NOW()
WHERE job_name = 'catalog_backup'
ORDER BY started_at DESC
LIMIT 1;

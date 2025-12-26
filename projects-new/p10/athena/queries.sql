-- P10 Sample Athena/Trino Queries for Iceberg Tables

-- ====================
-- Current Data Queries
-- ====================

-- Query current snapshot
SELECT
    date,
    category,
    event_count,
    total_amount,
    avg_amount
FROM glue_catalog.gold.daily_aggregates
WHERE date >= DATE '2025-01-01'
ORDER BY date DESC, event_count DESC
LIMIT 100;

-- Join across zones
SELECT
    g.date,
    g.category,
    g.event_count,
    s.raw_event_count,
    g.event_count - s.raw_event_count AS cleansing_loss
FROM glue_catalog.gold.daily_aggregates g
LEFT JOIN glue_catalog.silver.event_counts s
    ON g.date = s.date AND g.category = s.category
WHERE g.date >= CURRENT_DATE - INTERVAL '7' DAY;

-- ====================
-- Time Travel Queries
-- ====================

-- Query data as of specific timestamp
SELECT *
FROM glue_catalog.silver.transactions
FOR SYSTEM_TIME AS OF TIMESTAMP '2025-01-14 00:00:00'
WHERE customer_id = 12345
LIMIT 10;

-- Query specific snapshot by ID
SELECT *
FROM glue_catalog.silver.transactions
FOR SYSTEM_VERSION AS OF 1234567890
LIMIT 10;

-- Compare current vs historical snapshot
WITH current AS (
    SELECT category, SUM(amount) AS current_total
    FROM glue_catalog.silver.transactions
    WHERE date = DATE '2025-01-15'
    GROUP BY category
),
historical AS (
    SELECT category, SUM(amount) AS historical_total
    FROM glue_catalog.silver.transactions
    FOR SYSTEM_TIME AS OF TIMESTAMP '2025-01-14 00:00:00'
    WHERE date = DATE '2025-01-15'
    GROUP BY category
)
SELECT
    c.category,
    c.current_total,
    h.historical_total,
    c.current_total - h.historical_total AS delta
FROM current c
JOIN historical h ON c.category = h.category;

-- ====================
-- Metadata Queries
-- ====================

-- Show table snapshots
SELECT
    snapshot_id,
    parent_id,
    committed_at,
    summary['total-records'] AS total_records,
    summary['total-data-files'] AS data_files
FROM glue_catalog.silver.transactions.snapshots
ORDER BY committed_at DESC
LIMIT 10;

-- Show table history
SELECT
    made_current_at,
    snapshot_id,
    is_current_ancestor
FROM glue_catalog.silver.transactions.history
ORDER BY made_current_at DESC
LIMIT 20;

-- Show data files
SELECT
    file_path,
    file_format,
    record_count,
    file_size_in_bytes / 1024 / 1024 AS size_mb,
    partition
FROM glue_catalog.silver.transactions.files
WHERE partition.year = 2025 AND partition.month = 1
LIMIT 100;

-- ====================
-- Maintenance Queries
-- ====================

-- Identify small files needing compaction
SELECT
    partition,
    COUNT(*) AS file_count,
    AVG(file_size_in_bytes / 1024 / 1024) AS avg_size_mb,
    SUM(record_count) AS total_records
FROM glue_catalog.silver.transactions.files
GROUP BY partition
HAVING COUNT(*) > 50 OR AVG(file_size_in_bytes / 1024 / 1024) < 64
ORDER BY file_count DESC;

-- Find old snapshots eligible for expiry
SELECT
    snapshot_id,
    committed_at,
    DATEDIFF('day', committed_at, CURRENT_TIMESTAMP) AS age_days
FROM glue_catalog.silver.transactions.snapshots
WHERE committed_at < CURRENT_TIMESTAMP - INTERVAL '7' DAY
    AND snapshot_id NOT IN (
        SELECT snapshot_id
        FROM glue_catalog.silver.transactions.history
        WHERE is_current_ancestor = true
    );

-- ====================
-- Validation Queries
-- ====================

-- Check for duplicates
SELECT
    id,
    COUNT(*) AS duplicate_count
FROM glue_catalog.silver.transactions
GROUP BY id
HAVING COUNT(*) > 1;

-- Validate partition alignment
SELECT
    partition.year,
    partition.month,
    MIN(date) AS min_date,
    MAX(date) AS max_date,
    COUNT(*) AS record_count
FROM glue_catalog.silver.transactions
GROUP BY partition.year, partition.month
ORDER BY partition.year DESC, partition.month DESC;

-- Data freshness check
SELECT
    MAX(ingestion_timestamp) AS last_ingestion,
    DATEDIFF('hour', MAX(ingestion_timestamp), CURRENT_TIMESTAMP) AS hours_since_last_update,
    COUNT(*) AS total_records
FROM glue_catalog.bronze.raw_events;

-- ====================
-- CREATE VIEW Examples
-- ====================

CREATE OR REPLACE VIEW glue_catalog.gold.recent_transactions AS
SELECT
    t.*,
    c.customer_name,
    c.customer_segment
FROM glue_catalog.silver.transactions t
LEFT JOIN glue_catalog.silver.customers c
    ON t.customer_id = c.customer_id
WHERE t.date >= CURRENT_DATE - INTERVAL '30' DAY;

CREATE OR REPLACE VIEW glue_catalog.gold.category_metrics_7d AS
SELECT
    category,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount,
    STDDEV(amount) AS stddev_amount,
    APPROX_PERCENTILE(amount, 0.5) AS median_amount,
    APPROX_PERCENTILE(amount, 0.95) AS p95_amount
FROM glue_catalog.silver.transactions
WHERE date >= CURRENT_DATE - INTERVAL '7' DAY
GROUP BY category;

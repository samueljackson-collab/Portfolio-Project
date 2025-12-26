SELECT
  schemaname,
  relname AS table_name,
  idx_scan,
  seq_scan,
  round(idx_scan::numeric / NULLIF(idx_scan + seq_scan, 0) * 100, 2) AS index_usage_pct
FROM pg_stat_user_tables
ORDER BY seq_scan DESC
LIMIT 50;

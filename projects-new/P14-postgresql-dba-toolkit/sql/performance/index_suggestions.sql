SELECT
  schemaname,
  relname AS table_name,
  seq_scan,
  seq_tup_read,
  idx_scan,
  n_live_tup
FROM pg_stat_user_tables
WHERE seq_scan > 100
  AND seq_tup_read > 10000
ORDER BY seq_tup_read DESC
LIMIT 50;

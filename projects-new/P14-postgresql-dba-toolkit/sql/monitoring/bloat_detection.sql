SELECT
  schemaname,
  relname,
  n_dead_tup,
  n_live_tup,
  round(n_dead_tup::numeric / NULLIF(n_live_tup, 0) * 100, 2) AS dead_tuple_pct
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 50;

SELECT
  datname AS database,
  numbackends AS active_connections,
  xact_commit,
  xact_rollback,
  blks_read,
  blks_hit,
  round(blks_hit::numeric / NULLIF(blks_hit + blks_read, 0) * 100, 2) AS cache_hit_ratio
FROM pg_stat_database
ORDER BY numbackends DESC;

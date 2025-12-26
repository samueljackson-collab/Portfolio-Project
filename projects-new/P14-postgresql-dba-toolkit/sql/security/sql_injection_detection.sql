SELECT
  queryid,
  calls,
  total_time,
  substring(query, 1, 120) AS query_sample
FROM pg_stat_statements
WHERE query ~* '(union\s+select|pg_sleep|--|;\s*drop)'
ORDER BY total_time DESC
LIMIT 50;

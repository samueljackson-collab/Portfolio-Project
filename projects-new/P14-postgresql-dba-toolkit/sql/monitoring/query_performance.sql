SELECT
  queryid,
  calls,
  total_time,
  mean_time,
  rows,
  substring(query, 1, 120) AS query_sample
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 50;

SELECT query,
       calls,
       total_exec_time,
       mean_exec_time,
       rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 15;

SELECT query,
       calls,
       rows,
       total_exec_time
FROM pg_stat_statements
WHERE rows = 0
ORDER BY total_exec_time DESC
LIMIT 15;

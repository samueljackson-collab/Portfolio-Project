SELECT query,
       calls,
       total_exec_time
FROM pg_stat_statements
WHERE query ILIKE '%--%'
   OR query ILIKE '%/*%*/%'
   OR query ~* 'union\s+select'
ORDER BY total_exec_time DESC
LIMIT 20;

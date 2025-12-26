SELECT pid,
       usename,
       datname,
       now() - query_start AS runtime,
       state,
       query
FROM pg_stat_activity
WHERE state = 'active'
  AND now() - query_start > interval '30 minutes';

-- To terminate sessions (review first):
-- SELECT pg_terminate_backend(pid)
-- FROM pg_stat_activity
-- WHERE state = 'active'
--   AND now() - query_start > interval '30 minutes';

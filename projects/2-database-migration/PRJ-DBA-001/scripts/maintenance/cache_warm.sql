CREATE EXTENSION IF NOT EXISTS pg_prewarm;

SELECT pg_prewarm(relid)
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 10;

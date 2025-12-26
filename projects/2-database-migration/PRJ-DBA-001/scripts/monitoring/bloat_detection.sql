SELECT schemaname,
       relname,
       n_live_tup,
       n_dead_tup,
       round(n_dead_tup::numeric / nullif(n_live_tup + n_dead_tup, 0) * 100, 2) AS dead_tuple_pct
FROM pg_stat_user_tables
ORDER BY dead_tuple_pct DESC NULLS LAST;

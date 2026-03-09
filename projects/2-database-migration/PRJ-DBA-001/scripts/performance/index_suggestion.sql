SELECT schemaname,
       relname,
       seq_scan,
       seq_tup_read,
       idx_scan,
       n_live_tup
FROM pg_stat_user_tables
WHERE seq_scan > 1000
ORDER BY seq_scan DESC;

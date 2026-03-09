SELECT usename,
       client_addr,
       application_name,
       state,
       backend_start
FROM pg_stat_activity
ORDER BY backend_start DESC;

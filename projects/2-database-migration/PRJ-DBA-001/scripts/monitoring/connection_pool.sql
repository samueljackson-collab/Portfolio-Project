SELECT datname,
       state,
       count(*) AS connections
FROM pg_stat_activity
GROUP BY datname, state
ORDER BY datname, state;

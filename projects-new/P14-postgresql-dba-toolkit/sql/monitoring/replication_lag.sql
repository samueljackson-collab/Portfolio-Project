SELECT
  client_addr,
  state,
  sync_state,
  write_lag,
  flush_lag,
  replay_lag
FROM pg_stat_replication
ORDER BY replay_lag DESC NULLS LAST;

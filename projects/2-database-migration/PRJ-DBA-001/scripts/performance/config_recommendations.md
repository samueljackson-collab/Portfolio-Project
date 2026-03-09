# Configuration Recommendations

Use these as starting points, then validate with workload tests.

## Memory
- `shared_buffers`: 25-40% of RAM for dedicated DB hosts.
- `work_mem`: 4-16MB per connection (adjust for concurrency).
- `maintenance_work_mem`: 256MB+ for large index builds.

## WAL & Checkpoints
- `max_wal_size`: 2-4GB for moderate workloads.
- `checkpoint_completion_target`: 0.7-0.9.
- `wal_compression`: on (reduces WAL volume).

## Autovacuum
- `autovacuum_vacuum_scale_factor`: 0.1 for large tables.
- `autovacuum_analyze_scale_factor`: 0.05 for large tables.

## Logging
- `log_min_duration_statement`: 500ms for slow query sampling.
- Enable `pg_stat_statements` for detailed query metrics.

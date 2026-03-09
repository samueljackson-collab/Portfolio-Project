# Troubleshooting

## Backup failures
- Validate `pg_dump` is installed and credentials are correct.
- Check filesystem permissions for `BACKUP_DIR`.

## Slow queries
- Run `sql/monitoring/query_performance.sql` to identify expensive queries.
- Use `scripts/performance/explain_analyze.sh` to inspect a query plan.

## Replication lag
- Run `sql/monitoring/replication_lag.sql` and confirm network throughput.

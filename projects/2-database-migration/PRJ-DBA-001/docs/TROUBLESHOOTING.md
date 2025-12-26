# Troubleshooting

## Backup Failures
- Verify `PGHOST`, `PGUSER`, and `PGPASSWORD` are set.
- Ensure the `BACKUP_ROOT` directory is writable.
- Check `pg_dump` version compatibility with server.

## PITR Not Restoring
- Validate `archive_mode=on` and correct `archive_command`.
- Confirm WAL files exist in `WAL_ARCHIVE_DIR`.
- Set `restore_command` correctly for the target environment.

## Slow Queries
- Confirm `pg_stat_statements` is enabled and populated.
- Run `scripts/monitoring/query_performance.sql`.
- Use `scripts/performance/explain_analyzer.py` to review plans.

## Autovacuum Lag
- Check `scripts/monitoring/bloat_detection.sql` output.
- Increase autovacuum settings for large tables.
- Schedule manual vacuum for critical tables.

## Connection Saturation
- Use `scripts/monitoring/connection_pool.sql` for insight.
- Add PgBouncer or increase `max_connections` with caution.
- Review application connection reuse.


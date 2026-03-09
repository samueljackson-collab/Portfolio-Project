# Best Practices

## Backup & Recovery
- Run daily logical backups and validate them with verification tooling.
- Test restores quarterly using a staging environment.
- Encrypt backups at rest (S3 SSE-KMS) and in transit (TLS).
- Store WAL archives separately from base backups for PITR.

## Monitoring
- Track connection usage, replication lag, and long-running queries.
- Keep pg_stat_statements enabled for query performance insights.
- Alert on storage growth trends and autovacuum thresholds.

## Maintenance
- Schedule regular VACUUM (ANALYZE) and periodic REINDEX during off-peak hours.
- Review bloat weekly and take corrective action.
- Update statistics after major data loads or migrations.

## Security
- Rotate credentials regularly and enforce strong password policies.
- Use least-privilege roles and review grants quarterly.
- Enable TLS connections for all clients.

## Performance
- Tune shared_buffers, work_mem, and effective_cache_size based on workload.
- Use connection pooling for high-concurrency applications.
- Keep indexes aligned to query patterns; remove unused indexes.


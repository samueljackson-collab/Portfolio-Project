# Tool Reference

## Backup & Recovery

| Tool | Purpose | Notes |
| --- | --- | --- |
| `scripts/backup/pg_backup.sh` | Create logical backups with `pg_dump`. | Supports custom, directory, and plain formats. |
| `scripts/backup/verify_backup.sh` | Validate backup integrity. | Uses `pg_restore --list` or `pg_verifybackup` (directory format). |
| `scripts/backup/restore.sh` | Restore backups to a target database. | Supports custom/directory/SQL. |
| `scripts/backup/setup_pitr.sh` | Print PITR configuration hints. | Generates recommended settings for WAL archiving. |
| `scripts/backup/s3_backup.sh` | Upload backups to S3 with encryption. | Uses SSE-S3 or SSE-KMS via AWS CLI. |
| `scripts/backup/retention.sh` | Enforce retention policy for local backups. | Deletes backups older than `BACKUP_RETENTION_DAYS`. |

## Monitoring (SQL)

| Tool | Purpose |
| --- | --- |
| `scripts/monitoring/connection_pool.sql` | Monitor active/idle connections per database. |
| `scripts/monitoring/query_performance.sql` | Top slow queries by total time. |
| `scripts/monitoring/bloat_detection.sql` | Estimate table and index bloat. |
| `scripts/monitoring/index_usage.sql` | Identify unused or low-usage indexes. |
| `scripts/monitoring/replication_lag.sql` | Measure replication lag for streaming replicas. |
| `scripts/monitoring/size_report.sql` | Table/index size breakdown. |

## Maintenance

| Tool | Purpose |
| --- | --- |
| `scripts/maintenance/vacuum.sh` | Run `VACUUM (ANALYZE)` on all databases. |
| `scripts/maintenance/reindex.sh` | Reindex databases or specific tables. |
| `scripts/maintenance/update_stats.sh` | Update statistics using `ANALYZE`. |
| `scripts/maintenance/kill_connections.sql` | Terminate long-running connections. |
| `scripts/maintenance/cache_warm.sql` | Prewarm frequently used tables and indexes. |

## Performance

| Tool | Purpose |
| --- | --- |
| `scripts/performance/config_recommendations.md` | Baseline configuration tuning guidance. |
| `scripts/performance/query_helpers.sql` | Helper queries for slow query analysis. |
| `scripts/performance/index_suggestion.sql` | Candidate indexes based on `pg_stat_user_tables`. |
| `scripts/performance/explain_analyzer.py` | Summarize JSON explain plans. |
| `scripts/performance/connection_pool_tuning.md` | Guidance for PgBouncer sizing. |

## Security

| Tool | Purpose |
| --- | --- |
| `scripts/security/user_audit.sql` | List users and last login. |
| `scripts/security/permission_review.sql` | Review role memberships and grants. |
| `scripts/security/password_policy.sql` | Check password policy related settings. |
| `scripts/security/encryption_verification.sql` | Verify encryption settings. |
| `scripts/security/connection_audit.sql` | Review active connections by client/IP. |
| `scripts/security/sql_injection_detection.sql` | Identify potential injection patterns. |

## Migration

| Tool | Purpose |
| --- | --- |
| `scripts/migration/migrate.py` | Apply ordered schema migrations. |
| `scripts/migration/data_migration.sh` | Example data migration script template. |
| `scripts/migration/schema_migrations/` | Version-controlled migration files. |

## Prometheus Integration

Recommended setup for `postgres_exporter`:

```yaml
scrape_configs:
  - job_name: postgres
    static_configs:
      - targets: ['postgres-exporter:9187']
```

Example alerting rules:

```yaml
groups:
  - name: postgres
    rules:
      - alert: PostgresHighConnectionUsage
        expr: pg_stat_activity_count / pg_settings_max_connections > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL connection usage > 90%"
```


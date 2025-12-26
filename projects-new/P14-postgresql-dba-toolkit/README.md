# PostgreSQL DBA Toolkit

A practical PostgreSQL Database Administration toolkit focused on backup/recovery, monitoring, maintenance, security, and migration workflows. The toolkit is designed for RDS-compatible deployments (PROMPT 3 dependency) while remaining usable on self-managed PostgreSQL.

## Quick Start

```bash
cd projects-new/P14-postgresql-dba-toolkit
cp .env.example .env
source .env

# Example: run a monitoring report
./scripts/monitoring/run_report.sh sql/monitoring/index_usage.sql
```

## Tooling Map

### A. Backup & Recovery
- `scripts/backup/pg_dump_backup.sh`: Automated `pg_dump` with compression + optional S3 upload (SSE).
- `scripts/backup/verify_backup.sh`: Verifies backup integrity via `pg_restore --list`.
- `scripts/backup/restore_backup.sh`: Restore procedures for `.dump` files.
- `scripts/backup/retention_cleanup.sh`: Retention policy enforcement.
- `docs/backup_recovery.md`: PITR setup, validation checklist, and runbook.

### B. Monitoring Scripts
- `sql/monitoring/connection_pool_monitor.sql`
- `sql/monitoring/query_performance.sql`
- `sql/monitoring/bloat_detection.sql`
- `sql/monitoring/index_usage.sql`
- `sql/monitoring/replication_lag.sql`
- `sql/monitoring/table_index_sizes.sql`
- `scripts/monitoring/run_report.sh`: execute SQL report and export CSV.

### C. Maintenance Scripts
- `scripts/maintenance/vacuum_analyze.sh`
- `scripts/maintenance/reindex.sh`
- `scripts/maintenance/update_stats.sh`
- `scripts/maintenance/kill_connections.sh`
- `scripts/maintenance/warm_cache.sh`
- `docs/maintenance.md`: upgrade procedures + scheduling guidance.

### D. Performance Tuning
- `scripts/performance/config_recommendations.sh`
- `sql/performance/index_suggestions.sql`
- `scripts/performance/explain_analyze.sh`
- `sql/performance/pool_tuning.sql`
- `docs/performance_tuning.md`

### E. Security Tools
- `sql/security/user_audit.sql`
- `sql/security/permission_review.sql`
- `sql/security/password_policy.sql`
- `sql/security/encryption_verification.sql`
- `sql/security/connection_audit.sql`
- `sql/security/sql_injection_detection.sql`
- `docs/security.md`

### F. Migration Tools
- `scripts/migration/apply_migrations.sh`
- `scripts/migration/rollback_migration.sh`
- `scripts/migration/export_schema.sh`
- `docs/migrations.md`

### G. Documentation
- `docs/tool_reference.md`
- `docs/best_practices.md`
- `docs/troubleshooting.md`
- `docs/performance_tuning.md`

## Success Metrics Coverage
- Backup/restore: `docs/backup_recovery.md` includes test runbook.
- Monitoring: SQL reports exportable to Prometheus-friendly CSV.
- Performance tools: explained in `docs/performance_tuning.md`.
- Security audit: documented in `docs/security.md`.

## Requirements
- PostgreSQL client tools (`psql`, `pg_dump`, `pg_restore`)
- Optional: AWS CLI for S3 uploads

## Environment Variables
See `.env.example` for the full list.

## License
Internal portfolio project.

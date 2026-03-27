# Database Restore Guide

1. **Assess Incident**
   - Determine scope of data loss and recovery point objective (RPO).
   - Notify stakeholders of planned downtime.
2. **Retrieve Backup**
   - Access the latest verified PostgreSQL backup from storage.
   - Verify integrity using `pg_verifybackup` or checksums.
3. **Restore Steps**
   - Stop application services or isolate database traffic.
   - Run `pg_restore` (for logical backups) or `pg_basebackup` (for physical) into a clean instance.
   - Apply Alembic migrations if required to reach the target schema.
4. **Validation**
   - Execute smoke tests and data quality checks.
   - Re-enable application services and monitor for anomalies.

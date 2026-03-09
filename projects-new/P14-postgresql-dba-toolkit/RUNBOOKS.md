# Runbooks

## Backup Verification
1. Generate backup: `./scripts/backup/pg_dump_backup.sh`
2. Verify archive: `./scripts/backup/verify_backup.sh <backup-file>`
3. Perform test restore to staging: `./scripts/backup/restore_backup.sh <backup-file> <target-db>`

## Replication Lag Check
Run `./scripts/monitoring/run_report.sh sql/monitoring/replication_lag.sql` and alert if lag exceeds SLOs.

## Emergency Connection Kill
`./scripts/maintenance/kill_connections.sh <database> <username>`

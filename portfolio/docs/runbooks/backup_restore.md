# Backup and Restore Runbook

## Database Backup
1. Trigger snapshot using `scripts/backup.sh` (placeholder).
2. Verify snapshot integrity by listing backup artifacts in object storage.
3. Record backup metadata in the STATUS_BOARD.md.

## Database Restore
1. Halt application deployments (`make down`).
2. Provision restoration database from selected snapshot.
3. Run Alembic migrations to align schema.
4. Validate application health (`/healthz`) before resuming traffic.

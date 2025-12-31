# Runbooks

## Restore Request
1. Validate the request ticket for authorization.
2. Fetch the required database snapshot from the S3 backup bucket.
3. Run `scripts/restore_database.sh --snapshot <snapshot_id>`.
4. Verify data integrity by running checksums against the restored database.
5. Re-enable database replication once validation is complete.

## Backup Failure
1. Inspect backup logs for error details.
2. Attempt to re-run the backup script: `scripts/backup_database.sh`.
3. If it fails again, create an incident record.
4. After resolving, adjust the schedule or script as needed.

## Ransomware Drill
1. Lock down all access to production systems.
2. Validate the integrity and accessibility of immutable backups in the offsite vault.
3. Restore the latest valid backup to a clean, isolated subnet.
4. Rotate all credentials for the affected systems.

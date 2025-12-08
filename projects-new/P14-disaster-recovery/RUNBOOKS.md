# Runbooks

- Restore request: validate ticket -> fetch snapshot -> run scripts/restore_database.sh -> verify checksums -> re-enable replications
- Backup failure: inspect logs, rerun scripts/backup_database.sh, create incident record and adjust schedule
- Ransomware drill: lock access, validate immutable backups, restore to clean subnet, rotate credentials

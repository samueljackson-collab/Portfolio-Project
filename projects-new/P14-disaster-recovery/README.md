# P14 – Disaster Recovery & Backups

Backup and restore playbooks for databases and file stores with RPO/RTO targets enforced by automated drills.

## Quick start
- Stack: Bash/PowerShell scripts, Postgres/MySQL snapshots, S3/Glacier for offsite copies.
- Flow: Nightly backups captured, integrity verified, copied to offsite bucket, and periodic drills restore to sandbox and validate checksums.
- Run: make lint-scripts then pytest tests/test_restore_paths.py
- Operate: Rotate encryption keys monthly, verify backup completion dashboards, and track RPO/RTO in status sheet.

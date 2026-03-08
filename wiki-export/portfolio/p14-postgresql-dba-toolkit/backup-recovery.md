---
title: Backup & Recovery
description: 1. Ensure `.env` is configured. 2. Run `./scripts/backup/pg_dump_backup.sh`. 3. Verify: `./scripts/backup/verify_backup.sh <backup-file>`. - Enable WAL archiving in `postgresql.conf`: - `archive_mode 
tags: [documentation, portfolio]
path: portfolio/p14-postgresql-dba-toolkit/backup-recovery
created: 2026-03-08T22:19:13.783616+00:00
updated: 2026-03-08T22:04:37.926902+00:00
---

# Backup & Recovery

## Backup Procedure
1. Ensure `.env` is configured.
2. Run `./scripts/backup/pg_dump_backup.sh`.
3. Verify: `./scripts/backup/verify_backup.sh <backup-file>`.

## PITR Setup (Conceptual)
- Enable WAL archiving in `postgresql.conf`:
  - `archive_mode = on`
  - `archive_command = 'test ! -f /archive/%f && cp %p /archive/%f'`
- Ensure `wal_level = replica` (or `logical` as needed).
- Use `pg_basebackup` to capture base backups.

## Restore Procedure
- Create target DB.
- Run `./scripts/backup/restore_backup.sh <backup-file> <db-name>`.
- Validate application connectivity.

## Backup Validation Checklist
- Restore to staging monthly.
- Run application smoke tests.
- Record checksum of backup artifacts.

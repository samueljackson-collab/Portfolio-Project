---
title: Runbooks
description: 1. Generate backup: `./scripts/backup/pg_dump_backup.sh` 2. Verify archive: `./scripts/backup/verify_backup.sh <backup-file>` 3. Perform test restore to staging: `./scripts/backup/restore_backup.sh <b
tags: [documentation, portfolio]
path: portfolio/p14-postgresql-dba-toolkit/runbooks
created: 2026-03-08T22:19:13.778848+00:00
updated: 2026-03-08T22:04:37.926902+00:00
---

# Runbooks

## Backup Verification
1. Generate backup: `./scripts/backup/pg_dump_backup.sh`
2. Verify archive: `./scripts/backup/verify_backup.sh <backup-file>`
3. Perform test restore to staging: `./scripts/backup/restore_backup.sh <backup-file> <target-db>`

## Replication Lag Check
Run `./scripts/monitoring/run_report.sh sql/monitoring/replication_lag.sql` and alert if lag exceeds SLOs.

## Emergency Connection Kill
`./scripts/maintenance/kill_connections.sh <database> <username>`

---
title: Tool Reference
description: Portfolio documentation page
tags: [documentation, portfolio]
path: portfolio/p14-postgresql-dba-toolkit/tool-reference
created: 2026-03-08T22:19:13.783181+00:00
updated: 2026-03-08T22:04:37.928902+00:00
---

# Tool Reference

| Area | Tool | Description |
| --- | --- | --- |
| Backup | `scripts/backup/pg_dump_backup.sh` | Creates compressed backups with optional S3 upload |
| Backup | `scripts/backup/verify_backup.sh` | Validates backups using `pg_restore --list` |
| Monitoring | `scripts/monitoring/run_report.sh` | Executes SQL report and writes CSV |
| Maintenance | `scripts/maintenance/vacuum_analyze.sh` | Runs `VACUUM (ANALYZE)` on a database |
| Security | `sql/security/user_audit.sql` | Lists roles, superuser, and login privileges |
| Migration | `scripts/migration/apply_migrations.sh` | Applies SQL migrations with tracking |

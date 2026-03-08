---
title: Maintenance
description: - Daily `VACUUM (ANALYZE)` on high-churn tables. - Weekly `REINDEX` on heavily updated indexes. - Monthly `ANALYZE` on full schema. 1. Export schema: `./scripts/migration/export_schema.sh`. 2. Validat
tags: [documentation, portfolio]
path: portfolio/p14-postgresql-dba-toolkit/maintenance
created: 2026-03-08T22:19:13.781465+00:00
updated: 2026-03-08T22:04:37.927902+00:00
---

# Maintenance

## Routine Tasks
- Daily `VACUUM (ANALYZE)` on high-churn tables.
- Weekly `REINDEX` on heavily updated indexes.
- Monthly `ANALYZE` on full schema.

## Upgrade Procedure (High-level)
1. Export schema: `./scripts/migration/export_schema.sh`.
2. Validate extensions + compatibility.
3. Use `pg_upgrade` in a staging environment.
4. Perform cutover during a maintenance window.

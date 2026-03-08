---
title: Migrations
description: - Store SQL migrations in `migrations/` with numeric prefix: `001_init.sql`. - Apply migrations: `./scripts/migration/apply_migrations.sh`. - Roll back last migration: `./scripts/migration/rollback_mi
tags: [documentation, portfolio]
path: portfolio/p14-postgresql-dba-toolkit/migrations
created: 2026-03-08T22:19:13.782772+00:00
updated: 2026-03-08T22:04:37.927902+00:00
---

# Migrations

## Workflow
- Store SQL migrations in `migrations/` with numeric prefix: `001_init.sql`.
- Apply migrations: `./scripts/migration/apply_migrations.sh`.
- Roll back last migration: `./scripts/migration/rollback_migration.sh`.

## Zero-Downtime Tips
- Add columns with defaults in two steps.
- Use `CREATE INDEX CONCURRENTLY` for large tables.
- Avoid long-running locks during peak hours.

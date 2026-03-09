---
title: Migration Guide
description: - Place ordered SQL migrations in `scripts/migration/schema_migrations/`. - Apply with `python3 scripts/migration/migrate.py`. - Migrations are tracked in the `schema_migrations` table. - Write revers
tags: [analytics, data-engineering, documentation, pipeline, portfolio]
path: portfolio/2-database-migration/migration-guide
created: 2026-03-08T22:19:13.256508+00:00
updated: 2026-03-08T22:04:38.596902+00:00
---

# Migration Guide

## Schema Migration Framework
- Place ordered SQL migrations in `scripts/migration/schema_migrations/`.
- Apply with `python3 scripts/migration/migrate.py`.
- Migrations are tracked in the `schema_migrations` table.

## Rollback Procedures
- Write reversible migrations where possible (e.g., `DROP INDEX` for created indexes).
- Maintain rollback SQL files alongside forward migrations (e.g., `002_add_index.rollback.sql`).
- Use transactional DDL for supported operations and validate in staging.

## Zero-Downtime Migrations
- Add new columns as nullable, backfill in batches, then enforce constraints.
- Create indexes concurrently:
  ```sql
  CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
  ```
- Avoid table locks by using phased deployments and feature flags.
- Keep application code backward-compatible during the migration window.

## Data Migration Tips
- Batch updates to reduce lock contention.
- Use `LIMIT` and `ORDER BY` for chunking large tables.
- Monitor replication lag during heavy migrations.

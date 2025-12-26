# Migrations

## Workflow
- Store SQL migrations in `migrations/` with numeric prefix: `001_init.sql`.
- Apply migrations: `./scripts/migration/apply_migrations.sh`.
- Roll back last migration: `./scripts/migration/rollback_migration.sh`.

## Zero-Downtime Tips
- Add columns with defaults in two steps.
- Use `CREATE INDEX CONCURRENTLY` for large tables.
- Avoid long-running locks during peak hours.

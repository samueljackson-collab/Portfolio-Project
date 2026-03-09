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

# Schema Migrations

Place ordered migration files in this directory, prefixed with an incrementing number.

Example:
- `001_init.sql`
- `002_add_index.sql`

The `migrate.py` script applies migrations in filename order and records them in the `schema_migrations` table.

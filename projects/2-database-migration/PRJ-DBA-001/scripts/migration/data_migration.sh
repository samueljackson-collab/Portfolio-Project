#!/usr/bin/env bash
set -euo pipefail

: "${PGHOST:?PGHOST is required}"
: "${PGPORT:=5432}"
: "${PGDATABASE:?PGDATABASE is required}"
: "${PGUSER:?PGUSER is required}"
: "${PGPASSWORD:?PGPASSWORD is required}"

export PGPASSWORD

psql -d "${PGDATABASE}" <<'SQL'
-- Example data migration: update legacy status values.
UPDATE customers
SET status = 'active'
WHERE status = 'legacy_active';
SQL


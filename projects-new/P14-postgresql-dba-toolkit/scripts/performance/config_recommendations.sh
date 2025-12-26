#!/usr/bin/env bash
set -euo pipefail

psql --set ON_ERROR_STOP=on <<'SQL'
SELECT name, setting, unit, context
FROM pg_settings
WHERE name IN (
  'shared_buffers',
  'work_mem',
  'maintenance_work_mem',
  'effective_cache_size',
  'max_connections'
)
ORDER BY name;
SQL

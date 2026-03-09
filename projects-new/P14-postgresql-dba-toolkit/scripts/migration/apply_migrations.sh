#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "${SCRIPT_DIR}/../.." && pwd)

if [[ -f "${PROJECT_ROOT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${PROJECT_ROOT}/.env"
  set +a
fi

MIGRATIONS_DIR=${MIGRATIONS_DIR:-${PROJECT_ROOT}/migrations}

psql --set ON_ERROR_STOP=on <<'SQL'
CREATE TABLE IF NOT EXISTS schema_migrations (
  id serial primary key,
  filename text not null unique,
  applied_at timestamptz not null default now()
);
SQL

for file in "${MIGRATIONS_DIR}"/*.sql; do
  [[ -e "${file}" ]] || continue
  filename=$(basename "${file}")
  applied=$(psql --tuples-only --set ON_ERROR_STOP=on -c "SELECT 1 FROM schema_migrations WHERE filename='${filename}'" | tr -d '[:space:]')
  if [[ -z "${applied}" ]]; then
    echo "Applying ${filename}"
    psql --set ON_ERROR_STOP=on --file "${file}"
    psql --set ON_ERROR_STOP=on -c "INSERT INTO schema_migrations (filename) VALUES ('${filename}')"
  else
    echo "Skipping ${filename} (already applied)"
  fi
done

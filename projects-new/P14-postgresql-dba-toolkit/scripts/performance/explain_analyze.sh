#!/usr/bin/env bash
set -euo pipefail

QUERY=${1:-}

if [[ -z "${QUERY}" ]]; then
  echo "Usage: $0 <sql-query>" >&2
  exit 1
fi

psql --set ON_ERROR_STOP=on -c "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) ${QUERY}"

#!/usr/bin/env bash
set -euo pipefail

REPORT_SQL=${1:-}

if [[ -z "${REPORT_SQL}" ]]; then
  echo "Usage: $0 <sql-file>" >&2
  exit 1
fi

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "${SCRIPT_DIR}/../.." && pwd)

if [[ -f "${PROJECT_ROOT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${PROJECT_ROOT}/.env"
  set +a
fi

REPORT_DIR=${REPORT_DIR:-${PROJECT_ROOT}/reports}
mkdir -p "${REPORT_DIR}"

BASENAME=$(basename "${REPORT_SQL}" .sql)
OUTPUT_FILE="${REPORT_DIR}/${BASENAME}_$(date +"%Y%m%d_%H%M%S").csv"

psql --set ON_ERROR_STOP=on --csv --file "${REPORT_SQL}" > "${OUTPUT_FILE}"

echo "Report written to ${OUTPUT_FILE}"

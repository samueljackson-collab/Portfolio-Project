#!/usr/bin/env bash
set -euo pipefail

OUTPUT_FILE=${1:-schema_$(date +"%Y%m%d_%H%M%S").sql}

pg_dump --schema-only --file "${OUTPUT_FILE}"

echo "Schema exported to ${OUTPUT_FILE}"

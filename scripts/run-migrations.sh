#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<USAGE
Usage: $(basename "$0") --env <environment> [--target <version>]

Executes Flyway migrations against the Aurora cluster.
USAGE
}

ENVIRONMENT=""
TARGET=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env)
      ENVIRONMENT="$2"
      shift 2
      ;;
    --target)
      TARGET="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "${ENVIRONMENT}" ]]; then
  echo "--env is required" >&2
  usage
  exit 1
fi

SECRET_NAME="portfolio/${ENVIRONMENT}/database"

DB_JSON=$(aws secretsmanager get-secret-value --secret-id "${SECRET_NAME}" --query SecretString --output text)
DB_HOST=$(echo "${DB_JSON}" | jq -r '.host')
DB_USER=$(echo "${DB_JSON}" | jq -r '.username')
DB_PASS=$(echo "${DB_JSON}" | jq -r '.password')
DB_NAME=$(echo "${DB_JSON}" | jq -r '.dbname')

FLYWAY_CMD=(flyway migrate
  -url="jdbc:postgresql://${DB_HOST}:5432/${DB_NAME}"
  -user="${DB_USER}"
  -password="${DB_PASS}"
  -locations="filesystem:$(cd "$(dirname "$0")/../infrastructure/database/migrations" && pwd)")

if [[ -n "${TARGET}" ]]; then
  FLYWAY_CMD+=("-target=${TARGET}")
fi

printf '[migrations] executing %s\n' "${FLYWAY_CMD[*]}"
"${FLYWAY_CMD[@]}"

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
DEFAULT_TERRAFORM_DIR="${SCRIPT_DIR}/../terraform"
TERRAFORM_DIR="${DR_DRILL_TERRAFORM_DIR:-$DEFAULT_TERRAFORM_DIR}"
TF_OUTPUT_NAME="${DR_DRILL_TF_OUTPUT_NAME:-}"
AWS_CLI="${DR_DRILL_AWS_CLI:-aws}"
DB_INSTANCE_OVERRIDE="${DR_DRILL_DB_INSTANCE_ID:-}"

usage() {
  cat <<'USAGE'
Usage: dr-drill.sh <command> [options]

Commands:
  report                        Show the DB instance identifier that will be targeted.
  failover                      Initiate a Multi-AZ failover by rebooting the DB instance.

Options:
  --db-instance-id <id>         Explicit DB instance identifier to target.
  --terraform-dir <dir>         Directory containing Terraform state (default: ../terraform).
  --terraform-output-name <key> Terraform output name that holds the DB instance identifier.
  -h, --help                    Show this help message.

Environment overrides:
  DR_DRILL_DB_INSTANCE_ID       Same as --db-instance-id.
  DR_DRILL_TERRAFORM_DIR        Same as --terraform-dir.
  DR_DRILL_TF_OUTPUT_NAME       Same as --terraform-output-name.
  DR_DRILL_AWS_CLI              Alternate aws CLI executable (e.g. for testing).
USAGE
}

log() {
  local level="$1"; shift
  printf '%s [%s] %s\n' "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "$level" "$*"
}

info() {
  log INFO "$@"
}

error() {
  log ERROR "$@" >&2
}

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    error "Required command '$cmd' not found in PATH"
    exit 1
  fi
}

terraform_output_raw() {
  local key="$1"
  local output
  if output=$(terraform -chdir="$TERRAFORM_DIR" output -raw "$key" 2>/dev/null); then
    [[ -n "$output" ]] || return 1
    printf '%s\n' "$output"
    return 0
  fi
  return 1
}

terraform_output_detect() {
  local json
  if ! json=$(terraform -chdir="$TERRAFORM_DIR" output -json 2>/dev/null); then
    return 1
  fi
  python3 - "$@" <<'PY'
import json
import re
import sys

pattern = re.compile(r"(db[_-]?instance|primary).*?(identifier|id)", re.IGNORECASE)

data = json.load(sys.stdin)
preferred = sys.argv[1:]

# First pass: explicit preferred keys in order.
for key in preferred:
    if key in data and isinstance(data[key], dict):
        value = data[key].get("value")
        if isinstance(value, str) and value:
            print(value)
            sys.exit(0)

# Second pass: heuristic match on key name.
for key, value in data.items():
    if not isinstance(value, dict):
        continue
    if not pattern.search(key):
        continue
    str_value = value.get("value")
    if isinstance(str_value, str) and str_value:
        print(str_value)
        sys.exit(0)

# Third pass: any first string output.
for value in data.values():
    if isinstance(value, dict):
        str_value = value.get("value")
        if isinstance(str_value, str) and str_value:
            print(str_value)
            sys.exit(0)

sys.exit(1)
PY
}

resolve_db_instance_identifier() {
  local preferred_keys=("${TF_OUTPUT_NAME}")
  local heuristics=(
    "primary_db_instance_identifier"
    "db_instance_identifier"
    "primary_rds_instance_id"
    "db_instance_id"
  )

  if [[ -n "$DB_INSTANCE_OVERRIDE" ]]; then
    printf '%s\n' "$DB_INSTANCE_OVERRIDE"
    return 0
  fi

  require_cmd terraform

  if [[ -n "${TF_OUTPUT_NAME}" ]]; then
    if terraform_output_raw "$TF_OUTPUT_NAME"; then
      return 0
    fi
  fi

  local key
  for key in "${heuristics[@]}"; do
    if terraform_output_raw "$key"; then
      return 0
    fi
  done

  if terraform_output_detect "${preferred_keys[@]}"; then
    return 0
  fi

  error "Unable to determine DB instance identifier from Terraform outputs"
  exit 1
}

perform_report() {
  local identifier
  identifier=$(resolve_db_instance_identifier)
  info "Disaster recovery drill target DB instance: ${identifier}"
}

perform_failover() {
  local identifier
  identifier=$(resolve_db_instance_identifier)
  require_cmd "$AWS_CLI"
  info "Initiating Multi-AZ failover for DB instance '${identifier}'"
  "$AWS_CLI" rds reboot-db-instance --db-instance-identifier "$identifier" --force-failover
  info "Failover command submitted. Monitor RDS events/CloudWatch for completion."
}

COMMAND=""
DB_INSTANCE_OVERRIDE="${DB_INSTANCE_OVERRIDE}"

if [[ $# -eq 0 ]]; then
  usage
  exit 1
fi

COMMAND="$1"
shift

while [[ $# -gt 0 ]]; do
  case "$1" in
    --db-instance-id)
      [[ $# -ge 2 ]] || { error "--db-instance-id requires a value"; exit 1; }
      DB_INSTANCE_OVERRIDE="$2"
      shift 2
      ;;
    --terraform-dir)
      [[ $# -ge 2 ]] || { error "--terraform-dir requires a value"; exit 1; }
      TERRAFORM_DIR="$2"
      shift 2
      ;;
    --terraform-output-name)
      [[ $# -ge 2 ]] || { error "--terraform-output-name requires a value"; exit 1; }
      TF_OUTPUT_NAME="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      error "Unknown option: $1"
      usage
      exit 1
      ;;
  esac
done

case "$COMMAND" in
  report)
    perform_report
    ;;
  failover)
    perform_failover
    ;;
  *)
    error "Unknown command: $COMMAND"
    usage
    exit 1
    ;;
esac

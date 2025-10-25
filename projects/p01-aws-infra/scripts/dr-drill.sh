#!/usr/bin/env bash
set -euo pipefail

MODE="report"
INSTANCE_ID=""
TF_DIR=""
TF_OUTPUT_KEY="${DR_DRILL_TF_OUTPUT:-}"
AWS_PROFILE="${AWS_PROFILE:-}"
AWS_REGION="${AWS_REGION:-}"
AWS_CLI="${DR_DRILL_AWS_CLI:-aws}"
TERRAFORM_CLI="${DR_DRILL_TERRAFORM_CLI:-terraform}"
DRY_RUN=false

usage() {
  cat <<USAGE
Usage: $0 [options]

Options:
  -m, --mode <report|failover>   Operation mode (default: report)
  -i, --instance <identifier>    Explicit DB instance identifier
  -o, --tf-output <name>         Terraform output name for the instance identifier
  -d, --tf-dir <path>            Terraform working directory (default: current directory)
      --profile <profile>        AWS CLI profile to use
      --region <region>          AWS region to target
      --dry-run                  Show the AWS CLI commands instead of running them
      --aws-cli <path>           Override the AWS CLI executable (default: aws)
      --terraform-cli <path>     Override the Terraform CLI executable (default: terraform)
  -h, --help                     Show this message
USAGE
}

log() {
  local level="$1"
  shift
  printf '[%s] %s\n' "$level" "$*" >&2
}

fatal() {
  log "ERROR" "$*"
  exit 1
}

detect_terraform_instance() {
  if [[ -n "$INSTANCE_ID" ]]; then
    return
  fi

  if [[ -n "${DR_DRILL_INSTANCE_IDENTIFIER:-}" ]]; then
    INSTANCE_ID="${DR_DRILL_INSTANCE_IDENTIFIER}"
    log INFO "Using instance identifier from DR_DRILL_INSTANCE_IDENTIFIER"
    return
  fi

  if ! command -v "$TERRAFORM_CLI" >/dev/null 2>&1; then
    if [[ -n "$TF_OUTPUT_KEY" ]]; then
      fatal "Terraform CLI '$TERRAFORM_CLI' not found but terraform output key was provided. Install Terraform or provide --instance."
    fi
    log WARN "Terraform CLI '$TERRAFORM_CLI' not found. Provide --instance or install Terraform."
    return
  fi

  local tf_dir
  tf_dir="${TF_DIR:-.}"

  if [[ -n "$TF_OUTPUT_KEY" ]]; then
    log INFO "Fetching instance identifier from terraform output '$TF_OUTPUT_KEY' in '$tf_dir'"
    if ! INSTANCE_ID="$($TERRAFORM_CLI -chdir="$tf_dir" output -raw "$TF_OUTPUT_KEY" 2>/dev/null)"; then
      fatal "Unable to read terraform output '$TF_OUTPUT_KEY'. Ensure the output exists or provide --instance."
    fi
    if [[ -z "$INSTANCE_ID" ]]; then
      fatal "Terraform output '$TF_OUTPUT_KEY' is empty."
    fi
    return
  fi

  log INFO "Attempting to auto-detect terraform output containing an instance identifier"
  local outputs_json
  if ! outputs_json="$($TERRAFORM_CLI -chdir="$tf_dir" output -json 2>/dev/null)"; then
    log WARN "Unable to read terraform outputs from '$tf_dir'. Provide --instance."
    return
  fi

  if ! command -v jq >/dev/null 2>&1; then
    log WARN "jq is required to auto-detect terraform outputs. Provide --instance or install jq."
    return
  fi

  local key
  key=$(jq -r '
    to_entries[]
    | select(.value.type == "string")
    | select(.key | test("(instance(_|-)?identifier|db_instance_id)$"; "i"))
    | .key
  ' <<<"$outputs_json" | head -n1)

  if [[ -z "$key" ]]; then
    log WARN "No terraform output ending in 'instance_identifier' or 'db_instance_id' was found. Provide --instance."
    return
  fi

  TF_OUTPUT_KEY="$key"
  INSTANCE_ID=$(jq -r --arg key "$key" '.[$key].value' <<<"$outputs_json")
  if [[ -z "$INSTANCE_ID" || "$INSTANCE_ID" == "null" ]]; then
    fatal "Terraform output '$key' is empty."
  fi
  log INFO "Detected terraform output '$TF_OUTPUT_KEY' for instance identifier"
}

validate_mode() {
  case "$MODE" in
    report|failover) ;;
    *)
      fatal "Unknown mode '$MODE'. Use 'report' or 'failover'."
      ;;
  esac
}

aws_cli() {
  local args=()
  if [[ -n "$AWS_PROFILE" ]]; then
    args+=(--profile "$AWS_PROFILE")
  fi
  if [[ -n "$AWS_REGION" ]]; then
    args+=(--region "$AWS_REGION")
  fi
  args+=("$@")
  if [[ "$DRY_RUN" == true ]]; then
    printf '[DRY RUN] %s' "$AWS_CLI"
    local arg
    for arg in "${args[@]}"; do
      printf ' %q' "$arg"
    done
    printf '\n'
    return 0
  fi
  "$AWS_CLI" "${args[@]}"
}

report_instance() {
  log INFO "Gathering status for instance '$INSTANCE_ID'"
  aws_cli rds describe-db-instances \
    --db-instance-identifier "$INSTANCE_ID" \
    --output table \
    --query 'DBInstances[0].{Identifier:DBInstanceIdentifier,Status:DBInstanceStatus,AZ:AvailabilityZone,MultiAZ:MultiAZ,PendingMaint:PendingModifiedValues}'
}

perform_failover() {
  log INFO "Triggering Multi-AZ failover for instance '$INSTANCE_ID'"
  aws_cli rds reboot-db-instance \
    --db-instance-identifier "$INSTANCE_ID" \
    --force-failover
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -m|--mode)
        [[ $# -lt 2 ]] && fatal "Missing argument for $1"
        MODE="$(printf '%s' "$2" | tr '[:upper:]' '[:lower:]')"
        shift 2
        ;;
      -i|--instance)
        [[ $# -lt 2 ]] && fatal "Missing argument for $1"
        INSTANCE_ID="$2"
        shift 2
        ;;
      -o|--tf-output)
        [[ $# -lt 2 ]] && fatal "Missing argument for $1"
        TF_OUTPUT_KEY="$2"
        shift 2
        ;;
      -d|--tf-dir)
        [[ $# -lt 2 ]] && fatal "Missing argument for $1"
        TF_DIR="$2"
        shift 2
        ;;
      --profile)
        [[ $# -lt 2 ]] && fatal "Missing argument for $1"
        AWS_PROFILE="$2"
        shift 2
        ;;
      --region)
        [[ $# -lt 2 ]] && fatal "Missing argument for $1"
        AWS_REGION="$2"
        shift 2
        ;;
      --dry-run)
        DRY_RUN=true
        shift
        ;;
      --aws-cli)
        [[ $# -lt 2 ]] && fatal "Missing argument for $1"
        AWS_CLI="$2"
        shift 2
        ;;
      --terraform-cli)
        [[ $# -lt 2 ]] && fatal "Missing argument for $1"
        TERRAFORM_CLI="$2"
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      --)
        shift
        break
        ;;
      *)
        fatal "Unknown option '$1'"
        ;;
    esac
  done
}

main() {
  parse_args "$@"
  validate_mode
  detect_terraform_instance

  if [[ -z "$INSTANCE_ID" ]]; then
    fatal "No DB instance identifier resolved. Provide --instance or configure terraform output."
  fi

  case "$MODE" in
    report)
      report_instance
      ;;
    failover)
      perform_failover
      ;;
  esac
}

main "$@"

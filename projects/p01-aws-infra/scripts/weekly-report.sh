#!/usr/bin/env bash
set -euo pipefail

PROGRAM_NAME=$(basename "$0")
AWS_CLI=${AWS_CLI:-aws}
DEFAULT_REGION=${AWS_REGION:-${AWS_DEFAULT_REGION:-us-west-2}}
PROFILE=""
REGION="$DEFAULT_REGION"
START_DATE=""
END_DATE=""
METRIC="UnblendedCost"
GRANULARITY="WEEKLY"

usage() {
  cat <<USAGE
Usage: $PROGRAM_NAME [OPTIONS]

Generate a weekly AWS cost report using Cost Explorer.

Options:
  -p, --profile PROFILE        AWS CLI profile to use.
  -r, --region REGION          AWS region for regional API calls (default: $DEFAULT_REGION).
      --start-date YYYY-MM-DD  Override the cost report start date.
      --end-date YYYY-MM-DD    Override the cost report end date.
  -h, --help                   Show this help message and exit.

Note: AWS Cost Explorer is a us-east-1-only service endpoint. The script
automatically uses us-east-1 for the Cost Explorer query even when another
--region value is provided. The supplied region is still honored for every other
AWS API call performed by the script.
USAGE
}

error() {
  echo "[ERROR] $*" >&2
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    error "Required command '$1' not found in PATH"
    exit 1
  fi
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -h|--help)
        usage
        exit 0
        ;;
      -p|--profile)
        if [[ $# -lt 2 ]]; then
          error "Missing value for $1"
          usage
          exit 1
        fi
        PROFILE="$2"
        shift 2
        ;;
      -r|--region)
        if [[ $# -lt 2 ]]; then
          error "Missing value for $1"
          usage
          exit 1
        fi
        REGION="$2"
        shift 2
        ;;
      --start-date)
        if [[ $# -lt 2 ]]; then
          error "Missing value for $1"
          usage
          exit 1
        fi
        START_DATE="$2"
        shift 2
        ;;
      --end-date)
        if [[ $# -lt 2 ]]; then
          error "Missing value for $1"
          usage
          exit 1
        fi
        END_DATE="$2"
        shift 2
        ;;
      --)
        shift
        break
        ;;
      *)
        error "Unknown option: $1"
        usage
        exit 1
        ;;
    esac
  done
}

calculate_dates() {
  if [[ -z "$END_DATE" ]]; then
    END_DATE=$(date -u -d 'yesterday' +%F)
  fi

  if [[ -z "$START_DATE" ]]; then
    START_DATE=$(date -u -d "$END_DATE -6 days" +%F)
  fi
}

main() {
  require_command "$AWS_CLI"
  require_command date

  parse_args "$@"
  calculate_dates

  AWS_ARGS=(--output json)
  if [[ -n "$PROFILE" ]]; then
    AWS_ARGS+=(--profile "$PROFILE")
  fi
  if [[ -n "$REGION" ]]; then
    AWS_ARGS+=(--region "$REGION")
    export AWS_DEFAULT_REGION="$REGION"
  fi

  echo "Generating weekly AWS cost report"
  echo "  Profile : ${PROFILE:-<default>}"
  echo "  Region  : $REGION"
  echo "  Period  : $START_DATE to $END_DATE"

  echo "Verifying caller identity in target region..." >&2
  "$AWS_CLI" "${AWS_ARGS[@]}" sts get-caller-identity >/dev/null

  COST_REGION="us-east-1"
  COST_ARGS=(--output json)
  if [[ -n "$PROFILE" ]]; then
    COST_ARGS+=(--profile "$PROFILE")
  fi
  COST_ARGS+=(--region "$COST_REGION")

  echo "Requesting Cost Explorer data from $COST_REGION..." >&2
  # Cost Explorer is available only in us-east-1, so we override the region
  # exclusively for this API call to avoid authentication errors when the user
  # selects another region for the rest of the workflow.
  "$AWS_CLI" "${COST_ARGS[@]}" ce get-cost-and-usage \
    --time-period Start="$START_DATE",End="$END_DATE" \
    --granularity "$GRANULARITY" \
    --metrics "$METRIC"
}

main "$@"

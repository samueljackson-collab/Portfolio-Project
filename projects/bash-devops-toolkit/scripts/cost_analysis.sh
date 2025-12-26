#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/../lib/common.sh"

usage() {
  cat <<'USAGE'
Usage: cost_analysis.sh [options]

Summarizes AWS cost for the last 7 days.

Options:
  --region REGION     AWS region override
  --dry-run           Show actions without executing
  --log-level LEVEL   debug|info|warn|error
  -h, --help          Show this help
USAGE
}

AWS_REGION=${AWS_REGION:-""}

parse_common_flags "$@"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --region)
      AWS_REGION="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      break
      ;;
  esac
 done

require_command aws

region_args=()
if [[ -n ${AWS_REGION} ]]; then
  region_args=(--region "${AWS_REGION}")
fi

start=$(date -d "7 days ago" +%Y-%m-%d)
end=$(date +%Y-%m-%d)

log info "Fetching AWS cost from ${start} to ${end}"
run_cmd aws ce get-cost-and-usage "${region_args[@]}" --time-period Start=${start},End=${end} \
  --granularity DAILY --metrics "UnblendedCost" --output json

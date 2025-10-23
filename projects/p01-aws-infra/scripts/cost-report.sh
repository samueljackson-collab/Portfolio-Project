#!/usr/bin/env bash
set -euo pipefail

PROFILE="default"
REGION="us-west-2"
START_DATE="$(date -u -d '30 days ago' +%Y-%m-%d)"
END_DATE="$(date -u +%Y-%m-%d)"
FORMAT="table"

usage() {
  cat <<USAGE
Usage: $0 [--profile PROFILE] [--region REGION] [--start YYYY-MM-DD] [--end YYYY-MM-DD] [--format table|json]
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      PROFILE="$2"
      shift 2
      ;;
    --region)
      REGION="$2"
      shift 2
      ;;
    --start)
      START_DATE="$2"
      shift 2
      ;;
    --end)
      END_DATE="$2"
      shift 2
      ;;
    --format)
      FORMAT="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

DATA=$(aws ce get-cost-and-usage \
  --time-period Start="$START_DATE",End="$END_DATE" \
  --granularity DAILY \
  --metrics "UnblendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE \
  --profile "$PROFILE" \
  --region "$REGION" \
  --output json)

if [[ "$FORMAT" == "json" ]]; then
  echo "$DATA" | jq '.'
else
  echo "$DATA" | jq -r '.ResultsByTime[] | .TimePeriod.Start as $date | .Groups[] | [$date, .Keys[0], (.Metrics.UnblendedCost.Amount | tonumber)] | @tsv' \
    | column -t -s $'\t'
fi


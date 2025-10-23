#!/usr/bin/env bash
set -euo pipefail

OUT_FILE="reports/weekly-$(date -u +%Y%V).md"
PROFILE="default"
REGION="us-west-2"
# Cost Explorer API is only served from us-east-1.
COST_REGION="us-east-1"

usage() {
  cat <<USAGE
Usage: $0 [--profile PROFILE] [--region REGION] [--out FILE]
Note: AWS Cost Explorer requests are sent to us-east-1 regardless of --region.
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
    --out)
      OUT_FILE="$2"
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

mkdir -p "$(dirname "$OUT_FILE")"

cat <<HEADER > "$OUT_FILE"
# Weekly Operations Report — Week $(date -u +%V)
- Profile: $PROFILE
- Region: $REGION
- Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)

## Reliability
HEADER

aws autoscaling describe-auto-scaling-groups \
  --profile "$PROFILE" \
  --region "$REGION" \
  --query 'AutoScalingGroups[].{Name:AutoScalingGroupName,Desired:DesiredCapacity,InService:Instances[?LifecycleState==`InService`]|length(@)}' \
  --output table >> "$OUT_FILE"

echo -e "\n## Cost" >> "$OUT_FILE"
# Cost Explorer calls must target us-east-1 regardless of workload region.
aws ce get-cost-and-usage \
  --time-period Start="$(date -u -d '7 days ago' +%Y-%m-%d)",End="$(date -u +%Y-%m-%d)" \
  --granularity DAILY \
  --metrics "UnblendedCost" \
  --profile "$PROFILE" \
  --region "$COST_REGION" \
  --output json | jq '.ResultsByTime[] | "- " + .TimePeriod.Start + ": $" + (.Total.UnblendedCost.Amount | tonumber | tostring)' >> "$OUT_FILE"

echo -e "\n## Security" >> "$OUT_FILE"
aws accessanalyzer list-findings \
  --profile "$PROFILE" \
  --region "$REGION" \
  --status ACTIVE \
  --max-results 50 \
  --query 'findings[].{Id:id,Resource:resource,Issue:status}' \
  --output table >> "$OUT_FILE"

echo -e "\n## Actions" >> "$OUT_FILE"
cat <<ACTIONS >> "$OUT_FILE"
- [ ] Review IAM findings and remediate
- [ ] Confirm budgets and anomaly alerts
- [ ] Schedule DR drill if not performed this month
ACTIONS

echo "Weekly report written to $OUT_FILE"


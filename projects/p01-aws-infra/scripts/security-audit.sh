#!/usr/bin/env bash
set -euo pipefail

PROFILE="default"
REGION="us-west-2"
OUTPUT="reports/security-$(date -u +%Y%m%dT%H%M%SZ).md"

usage() {
  cat <<USAGE
Usage: $0 [--profile PROFILE] [--region REGION] [--output FILE]
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
    --output)
      OUTPUT="$2"
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

mkdir -p "$(dirname "$OUTPUT")"

cat <<HEADER > "$OUTPUT"
# Security Audit Snapshot — $(date -u +%Y-%m-%dT%H:%M:%SZ)
- Profile: $PROFILE
- Region: $REGION

HEADER

echo "Collecting IAM Access Analyzer findings..."
aws accessanalyzer list-findings \
  --profile "$PROFILE" \
  --region "$REGION" \
  --status ACTIVE \
  --max-results 100 \
  --query 'findings[].{Id:id,Resource:resource,Issue:status,Created:resourceOwnerAccount}' \
  --output table >> "$OUTPUT"

echo -e "\n## GuardDuty High Severity Findings" >> "$OUTPUT"
DETECTOR_ID=$(aws guardduty list-detectors --profile "$PROFILE" --region "$REGION" --query 'DetectorIds[0]' --output text)
if [[ "$DETECTOR_ID" == "None" || -z "$DETECTOR_ID" ]]; then
  echo "GuardDuty detector not configured" >> "$OUTPUT"
else
  aws guardduty list-findings \
    --detector-id "$DETECTOR_ID" \
    --finding-criteria '{"Criterion":{"severity":{"Gte":7}}}' \
    --max-results 20 \
    --profile "$PROFILE" \
    --region "$REGION" | jq '.FindingIds' >> "$OUTPUT"
fi

echo -e "\n## Terraform Security Scan" >> "$OUTPUT"
if command -v tfsec >/dev/null 2>&1; then
  tfsec ../infra --format json | jq '.' >> "$OUTPUT"
else
  echo "tfsec not installed; run tfsec ../infra locally." >> "$OUTPUT"
fi

echo "Security audit report saved to $OUTPUT"


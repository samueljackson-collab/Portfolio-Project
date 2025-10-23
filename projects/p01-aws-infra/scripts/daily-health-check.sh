#!/usr/bin/env bash
set -euo pipefail

PROFILE="default"
REGION="us-west-2"
OUTPUT_DIR="reports"
PARAM_PREFIX="/p01-landing-zone/prod"

usage() {
  cat <<USAGE
Usage: $0 [--profile PROFILE] [--region REGION] [--output-dir DIR] [--param-prefix PREFIX]
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
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --param-prefix)
      PARAM_PREFIX="$2"
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

mkdir -p "$OUTPUT_DIR"
REPORT="$OUTPUT_DIR/health-$(date -u +%Y%m%dT%H%M%SZ).md"

cat <<HEADER > "$REPORT"
# Daily Health Check — $(date -u +%Y-%m-%d)
- Profile: $PROFILE
- Region: $REGION
- Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)

HEADER

echo "Checking CloudWatch alarms..."
aws cloudwatch describe-alarms \
  --state-value ALARM \
  --profile "$PROFILE" \
  --region "$REGION" \
  --query 'MetricAlarms[].{Name:AlarmName, State:StateValue, Updated:StateUpdatedTimestamp}' \
  --output table >> "$REPORT"

echo "Listing unhealthy ALB targets..."
aws elbv2 describe-target-health \
  --profile "$PROFILE" \
  --region "$REGION" \
  --target-group-arn "$(aws ssm get-parameter --name "${PARAM_PREFIX}/target_group_arn" --query 'Parameter.Value' --output text --profile "$PROFILE" --region "$REGION" 2>/dev/null || echo 'missing')" \
  --query 'TargetHealthDescriptions[?TargetHealth.State!=`healthy`].[Target.Id,TargetHealth.State]' \
  --output table >> "$REPORT" || echo "Target group ARN missing; skip ALB health." >> "$REPORT"

echo "Checking RDS status..."
aws rds describe-db-instances \
  --profile "$PROFILE" \
  --region "$REGION" \
  --query 'DBInstances[].{DBInstanceIdentifier:DBInstanceIdentifier,Status:DBInstanceStatus,MultiAZ:MultiAZ}' \
  --output table >> "$REPORT"

echo "Verifying backups..."
aws backup list-backup-jobs \
  --profile "$PROFILE" \
  --region "$REGION" \
  --by-created-after "$(date -u -d '1 day ago' +%Y-%m-%dT%H:%M:%SZ)" \
  --query 'BackupJobs[].[BackupJobId,State,ResourceType,CreationDate]' \
  --output table >> "$REPORT"

echo "Report generated at $REPORT"


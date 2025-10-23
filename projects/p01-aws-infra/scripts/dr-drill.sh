#!/usr/bin/env bash
set -euo pipefail

MODE="report"
PROFILE="default"
REGION_PRIMARY="us-west-2"
REGION_DR="us-east-1"
DB_INSTANCE_ID="p01-landing-zone-prod-db"

usage() {
  cat <<USAGE
Usage: $0 [--mode report|failover] [--profile PROFILE] [--primary REGION] [--dr REGION] [--db-instance IDENTIFIER]
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="$2"
      shift 2
      ;;
    --profile)
      PROFILE="$2"
      shift 2
      ;;
    --primary)
      REGION_PRIMARY="$2"
      shift 2
      ;;
    --dr)
      REGION_DR="$2"
      shift 2
      ;;
    --db-instance)
      DB_INSTANCE_ID="$2"
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

start=$(date -u +%s)

echo "Starting DR drill in $MODE mode"

if [[ "$MODE" == "failover" ]]; then
  echo "Forcing Multi-AZ failover for instance $DB_INSTANCE_ID in $REGION_PRIMARY"
  aws rds reboot-db-instance \
    --db-instance-identifier "$DB_INSTANCE_ID" \
    --force-failover \
    --profile "$PROFILE" \
    --region "$REGION_PRIMARY"

  echo "Waiting for instance to become available"
  aws rds wait db-instance-available \
    --db-instance-identifier "$DB_INSTANCE_ID" \
    --profile "$PROFILE" \
    --region "$REGION_PRIMARY"

  echo "Updating Route53 health checks"
  if [[ ! -f dr-failover.json ]]; then
    echo "Error: change batch file dr-failover.json not found in $(pwd)." >&2
    exit 1
  fi
  aws route53 change-resource-record-sets \
    --hosted-zone-id ZONEID \
    --change-batch file://dr-failover.json \
    --profile "$PROFILE" \
    --region "$REGION_PRIMARY"
else
  echo "Running readiness report"
  aws backup list-recovery-points-by-backup-vault \
    --backup-vault-name "p01-landing-zone" \
    --profile "$PROFILE" \
    --region "$REGION_PRIMARY" \
    --max-results 5
fi

end=$(date -u +%s)
duration=$((end-start))

echo "DR drill complete in ${duration}s"


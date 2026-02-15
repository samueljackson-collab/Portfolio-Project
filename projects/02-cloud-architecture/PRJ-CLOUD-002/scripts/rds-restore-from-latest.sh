#!/usr/bin/env bash
# Restore the PostgreSQL database from the most recent automated snapshot.
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
TF_DIR="${ROOT_DIR}/terraform"

for cmd in terraform aws jq; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    exit 1
  fi
done

RDS_ID=$(terraform -chdir="${TF_DIR}" output -raw rds_instance_id)
TARGET_ID=${1:-"${RDS_ID}-restore"}

LATEST_SNAPSHOT=$(aws rds describe-db-snapshots \
  --db-instance-identifier "$RDS_ID" \
  --query 'reverse(sort_by(DBSnapshots, &SnapshotCreateTime))[0].DBSnapshotIdentifier' \
  --output text)

if [[ -z "${LATEST_SNAPSHOT}" || "${LATEST_SNAPSHOT}" == "None" ]]; then
  echo "No snapshots found for ${RDS_ID}." >&2
  exit 1
fi

echo "Restoring snapshot ${LATEST_SNAPSHOT} to instance ${TARGET_ID}..."
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier "$TARGET_ID" \
  --db-snapshot-identifier "$LATEST_SNAPSHOT"

echo "Restore initiated. Monitor status with:\n  aws rds describe-db-instances --db-instance-identifier ${TARGET_ID} --query 'DBInstances[0].DBInstanceStatus' --output text"

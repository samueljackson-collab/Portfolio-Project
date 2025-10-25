#!/bin/bash
set -euo pipefail

PRIMARY_REGION=${PRIMARY_REGION:-us-east-1}
SECONDARY_REGION=${SECONDARY_REGION:-us-west-2}
GLOBAL_DB_ID=${GLOBAL_DB_ID:?"Set GLOBAL_DB_ID"}

aws rds failover-global-cluster \
  --global-cluster-identifier "$GLOBAL_DB_ID" \
  --target-db-cluster-identifier arn:aws:rds:${SECONDARY_REGION}:123456789012:cluster:${GLOBAL_DB_ID}-secondary

echo "Failover initiated. Monitoring status..."
aws rds describe-global-clusters --global-cluster-identifier "$GLOBAL_DB_ID" --query 'GlobalClusters[0].GlobalClusterMembers'

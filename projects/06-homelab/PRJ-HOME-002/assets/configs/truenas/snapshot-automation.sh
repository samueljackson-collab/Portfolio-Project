#!/bin/bash
# TrueNAS Snapshot Automation
# Creates rolling snapshots for homelab datasets

set -euo pipefail

POOL_NAME=${POOL_NAME:-tank}
DATASET_ROOT="${POOL_NAME}/homelab"
TIMESTAMP=$(date +%Y%m%d%H%M)
RETENTION_DAYS=${RETENTION_DAYS:-30}

zfs snapshot -r ${DATASET_ROOT}@auto-${TIMESTAMP}

# Cleanup old snapshots
for snap in $(zfs list -H -t snapshot -o name -s creation | grep "${DATASET_ROOT}@auto-"); do
  snap_date=$(echo "$snap" | awk -F'@' '{print $2}' | sed 's/auto-//')
  if [[ -n $snap_date ]]; then
    snap_epoch=$(date -d ${snap_date} +%s || true)
    cutoff_epoch=$(date -d "-${RETENTION_DAYS} days" +%s)
    if [[ $snap_epoch -lt $cutoff_epoch ]]; then
      echo "Destroying snapshot $snap"
      zfs destroy -r "$snap"
    fi
  fi
done

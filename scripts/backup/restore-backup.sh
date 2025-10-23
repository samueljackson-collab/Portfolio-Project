#!/usr/bin/env bash
set -euo pipefail

BACKUP_FILE=${1:?"Usage: $0 <backup-archive.tar.gz>"}

if [ ! -f "$BACKUP_FILE" ]; then
  echo "Backup archive $BACKUP_FILE not found" >&2
  exit 1
fi

WORK_DIR="restore-temp"
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR"

tar -xzf "$BACKUP_FILE" -C "$WORK_DIR"

if [ -f "$WORK_DIR/k8s-resources.yaml" ] && command -v kubectl >/dev/null 2>&1; then
  kubectl apply -f "$WORK_DIR/k8s-resources.yaml"
fi

echo "Restore completed"

#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/../lib/common.sh"

usage() {
  cat <<'USAGE'
Usage: aws_cleanup.sh [options]

Cleans tagged AWS snapshots.

Options:
  --tag-key KEY         Tag key to match (default: Cleanup)
  --tag-value VALUE     Tag value to match (default: true)
  --region REGION       AWS region override
  --dry-run             Show actions without executing
  --log-level LEVEL     debug|info|warn|error
  -h, --help            Show this help
USAGE
}

TAG_KEY=${TAG_KEY:-"Cleanup"}
TAG_VALUE=${TAG_VALUE:-"true"}
AWS_REGION=${AWS_REGION:-""}

parse_common_flags "$@"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag-key)
      TAG_KEY="$2"
      shift 2
      ;;
    --tag-value)
      TAG_VALUE="$2"
      shift 2
      ;;
    --region)
      AWS_REGION="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      break
      ;;
  esac
 done

require_command aws

region_args=()
if [[ -n ${AWS_REGION} ]]; then
  region_args=(--region "${AWS_REGION}")
fi

log info "Finding snapshots tagged ${TAG_KEY}=${TAG_VALUE}"

snapshot_ids=$(aws ec2 describe-snapshots "${region_args[@]}" \
  --owner-ids self \
  --filters "Name=tag:${TAG_KEY},Values=${TAG_VALUE}" \
  --query 'Snapshots[].SnapshotId' --output text)

if [[ -z ${snapshot_ids} ]]; then
  log info "No snapshots found"
  exit 0
fi

for snapshot_id in ${snapshot_ids}; do
  log info "Deleting snapshot ${snapshot_id}"
  run_cmd aws ec2 delete-snapshot "${region_args[@]}" --snapshot-id "${snapshot_id}"
 done

#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/../lib/common.sh"

usage() {
  cat <<'USAGE'
Usage: s3_backup.sh [options]

Creates a tar archive and uploads to S3.

Options:
  --source DIR        Source directory
  --bucket BUCKET     S3 bucket name
  --prefix PREFIX     S3 key prefix
  --gpg-key KEY       Optional GPG key for encryption
  --dry-run           Show actions without executing
  --log-level LEVEL   debug|info|warn|error
  -h, --help          Show this help
USAGE
}

SOURCE=${SOURCE:-""}
BUCKET=${BUCKET:-""}
PREFIX=${PREFIX:-"backups"}
GPG_KEY=${GPG_KEY:-""}

parse_common_flags "$@"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source)
      SOURCE="$2"
      shift 2
      ;;
    --bucket)
      BUCKET="$2"
      shift 2
      ;;
    --prefix)
      PREFIX="$2"
      shift 2
      ;;
    --gpg-key)
      GPG_KEY="$2"
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

if [[ -z ${SOURCE} || -z ${BUCKET} ]]; then
  usage
  exit 1
fi

require_command tar
require_command aws

archive="/tmp/backup-$(date +%Y%m%d%H%M%S).tar.gz"
log info "Creating archive ${archive}"
run_cmd tar -czf "${archive}" -C "${SOURCE}" .

if [[ -n ${GPG_KEY} ]]; then
  require_command gpg
  encrypted="${archive}.gpg"
  log info "Encrypting archive with GPG key ${GPG_KEY}"
  run_cmd gpg --batch --yes --recipient "${GPG_KEY}" --output "${encrypted}" --encrypt "${archive}"
  archive="${encrypted}"
fi

key="${PREFIX}/$(basename "${archive}")"
log info "Uploading ${archive} to s3://${BUCKET}/${key}"
run_cmd aws s3 cp "${archive}" "s3://${BUCKET}/${key}"

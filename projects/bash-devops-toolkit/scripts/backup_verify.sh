#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/../lib/common.sh"

usage() {
  cat <<'USAGE'
Usage: backup_verify.sh [options] archive

Verify a backup archive using SHA256 checksum.

Options:
  --checksum FILE     Checksum file path
  --dry-run           Show actions without executing
  --log-level LEVEL   debug|info|warn|error
  -h, --help          Show this help
USAGE
}

CHECKSUM_FILE=""

parse_common_flags "$@"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --checksum)
      CHECKSUM_FILE="$2"
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

if [[ $# -eq 0 ]]; then
  usage
  exit 1
fi

archive="$1"
require_command sha256sum

if [[ -z ${CHECKSUM_FILE} ]]; then
  CHECKSUM_FILE="${archive}.sha256"
fi

if [[ ! -f ${CHECKSUM_FILE} ]]; then
  log info "Generating checksum ${CHECKSUM_FILE}"
  run_cmd sha256sum "${archive}" > "${CHECKSUM_FILE}"
  exit 0
fi

log info "Verifying checksum"
run_cmd sha256sum -c "${CHECKSUM_FILE}"

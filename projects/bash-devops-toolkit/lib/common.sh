#!/usr/bin/env bash
set -euo pipefail

LOG_LEVEL=${LOG_LEVEL:-"info"}
DRY_RUN=${DRY_RUN:-"false"}

log() {
  local level=$1
  shift
  local message=$*
  local timestamp
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  case "${LOG_LEVEL}" in
    debug) ;;
    info) [[ ${level} == "debug" ]] && return 0 ;;
    warn) [[ ${level} == "debug" || ${level} == "info" ]] && return 0 ;;
    error) [[ ${level} != "error" ]] && return 0 ;;
  esac

  printf '%s [%s] %s\n' "${timestamp}" "${level}" "${message}"
}

run_cmd() {
  if [[ ${DRY_RUN} == "true" ]]; then
    log info "dry-run: $*"
    return 0
  fi
  log debug "running: $*"
  "$@"
}

require_command() {
  local command=$1
  if ! command -v "${command}" >/dev/null 2>&1; then
    log error "missing required command: ${command}"
    exit 1
  fi
}

print_help() {
  cat <<'USAGE'
Usage: script [options]

Options:
  -h, --help     Show this help message
  --dry-run      Show commands without executing
  --log-level    Set log level (debug, info, warn, error)
USAGE
}

parse_common_flags() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dry-run)
        DRY_RUN="true"
        shift
        ;;
      --log-level)
        LOG_LEVEL="$2"
        shift 2
        ;;
      -h|--help)
        print_help
        exit 0
        ;;
      *)
        break
        ;;
    esac
  done
}

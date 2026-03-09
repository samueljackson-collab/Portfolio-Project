#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/../lib/common.sh"

usage() {
  cat <<'USAGE'
Usage: metric_collect.sh [options]

Outputs node metrics in Prometheus textfile format.

Options:
  --output FILE       Output file (default: /var/lib/node_exporter/custom.prom)
  --dry-run           Show actions without executing
  --log-level LEVEL   debug|info|warn|error
  -h, --help          Show this help
USAGE
}

OUTPUT_FILE=${OUTPUT_FILE:-"/var/lib/node_exporter/custom.prom"}

parse_common_flags "$@"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output)
      OUTPUT_FILE="$2"
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

cpu_idle=$(vmstat 1 2 | tail -1 | awk '{print $15}')
mem_free=$(free -m | awk '/Mem/ {print $4}')

log info "Writing metrics to ${OUTPUT_FILE}"
if [[ ${DRY_RUN} == "true" ]]; then
  log info "dry-run: would write metrics"
  exit 0
fi

cat <<METRICS > "${OUTPUT_FILE}"
# HELP custom_cpu_idle_percent CPU idle percentage
# TYPE custom_cpu_idle_percent gauge
custom_cpu_idle_percent ${cpu_idle}
# HELP custom_memory_free_mb Free memory in MB
# TYPE custom_memory_free_mb gauge
custom_memory_free_mb ${mem_free}
METRICS

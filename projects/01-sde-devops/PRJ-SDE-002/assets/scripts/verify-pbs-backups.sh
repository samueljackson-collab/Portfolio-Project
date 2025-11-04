#!/usr/bin/env bash
# verify-pbs-backups.sh
# ------------------------------------------------------------------
# Proxmox Backup Server verification utility for homelab deployments.
# Performs job health checks, snapshot validation, datastore review,
# and mails an HTML report. Designed for cron-based daily execution.

set -euo pipefail

SCRIPT_NAME=$(basename "$0")
VERSION="1.0.0"
LOG_FILE="/var/log/backup-verification.log"
REPORT_FILE="/tmp/pbs-verification-report.html"
PBS_ENDPOINT="https://192.168.1.15:8007"
PBS_DATASTORE="homelab-backups"
EMAIL_RECIPIENT="admin@homelab.local"
VERBOSE=false
DRY_RUN=false
EXIT_CODE=0

COLOR_GREEN="\033[1;32m"
COLOR_YELLOW="\033[1;33m"
COLOR_RED="\033[1;31m"
COLOR_RESET="\033[0m"

# usage prints the script name and version, a brief usage synopsis with supported flags (-v, -d, -h), and the required PBS_TOKEN environment variable.
usage() {
  cat <<USAGE
${SCRIPT_NAME} v${VERSION}
Usage: ${SCRIPT_NAME} [-v] [-d] [-h]
  -v    Verbose output (echo log lines to STDOUT)
  -d    Dry run (skip email delivery)
  -h    Show help

Environment:
  PBS_TOKEN   Proxmox Backup Server API token (required)
USAGE
}

while getopts "vdh" opt; do
  case ${opt} in
    v) VERBOSE=true ;;
    d) DRY_RUN=true ;;
    h) usage; exit 0 ;;
    *) usage >&2; exit 1 ;;
  esac
done

# log writes a timestamped message with a level to the log file and, if VERBOSE is true, echoes the same message to stdout with the provided color.
log() {
  local level=$1 color=$2
  shift 2
  local timestamp
  timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  local message="${timestamp} [${level}] $*"
  echo -e "${message}" >> "$LOG_FILE"
  if [[ $VERBOSE == true ]]; then
    echo -e "${color}${message}${COLOR_RESET}"
  fi
}

# require_token ensures the PBS_TOKEN environment variable is set; logs an error and exits with code 2 if it is missing.
require_token() {
  if [[ -z "${PBS_TOKEN:-}" ]]; then
    log ERROR "$COLOR_RED" "PBS_TOKEN environment variable is required"
    exit 2
  fi
}

# api_call performs an HTTP request against the Proxmox Backup Server API at PBS_ENDPOINT using PBS_TOKEN and echoes curl's response.
# It accepts an HTTP method, an API path (appended to PBS_ENDPOINT), and optional JSON data to send as the request body.
api_call() {
  local method=$1 path=$2 data=${3:-}
  local url="${PBS_ENDPOINT}${path}"
  local opts=(
    --silent --show-error --fail --insecure
    --request "$method"
    -H "Authorization: PBSAPIToken=${PBS_TOKEN}"
    -H 'Content-Type: application/json'
    "$url"
  )
  if [[ -n $data ]]; then
    opts+=(--data "$data")
  fi
  curl "${opts[@]}"
}

# Containers for report content
JOB_ROWS=()
SNAPSHOT_ROWS=()
DATASTORE_SUMMARY="Not available"
DATASTORE_WARNINGS=()

# fetch_jobs fetches backup entries for the configured PBS datastore and writes each entry as a compact JSON object on separate lines to stdout.
fetch_jobs() {
  log INFO "$COLOR_GREEN" "Fetching backup jobs"
  api_call GET "/api2/json/admin/datastore/${PBS_DATASTORE}/backups" | jq -c '.data[]'
}

# process_jobs reads newline-delimited JSON job objects from stdin, evaluates each backup's health (last run presence and age, last run status, duration, and size regression), updates EXIT_CODE accordingly, and appends an HTML table row for each job to the JOB_ROWS array.
# For jobs it records human-readable issue notes and sets a CSS class of pass/warn/fail based on detected problems.
process_jobs() {
  while IFS= read -r job; do
    [[ -z $job ]] && continue
    local name last_time status duration size prev_size
    name=$(jq -r '."backup-id"' <<<"$job")
    last_time=$(jq -r '."last-run".time // empty' <<<"$job")
    status=$(jq -r '."last-run".status // "unknown"' <<<"$job")
    duration=$(jq -r '."last-run".duration // 0' <<<"$job")
    size=$(jq -r '."last-run".size // 0' <<<"$job")
    prev_size=$(jq -r '."previous-run".size // 0' <<<"$job")

    local issues=()
    if [[ -z $last_time ]]; then
      issues+=('No successful run recorded')
      EXIT_CODE=$(( EXIT_CODE < 1 ? 1 : EXIT_CODE ))
    else
      local last_epoch now_epoch
      last_epoch=$last_time
      now_epoch=$(date +%s)
      if (( now_epoch - last_epoch > 86400 )); then
        issues+=('Last run >24h ago')
        EXIT_CODE=$(( EXIT_CODE < 1 ? 1 : EXIT_CODE ))
      fi
    fi

    if [[ ${status,,} != ok ]]; then
      issues+=("Status ${status}")
      EXIT_CODE=2
    fi

    if (( duration > 3600 )); then
      issues+=("Duration ${duration}s > 1h")
      EXIT_CODE=$(( EXIT_CODE < 1 ? 1 : EXIT_CODE ))
    fi

    if (( prev_size > 0 )); then
      local half=$(( prev_size / 2 ))
      if (( size < half )); then
        issues+=("Size drop ${size} vs ${prev_size}")
        EXIT_CODE=$(( EXIT_CODE < 1 ? 1 : EXIT_CODE ))
      fi
    fi

    local color_class="pass"
    local status_text=${status}
    if [[ ${status,,} != ok ]]; then
      color_class="fail"
    elif ((${#issues[@]} > 0)); then
      color_class="warn"
    fi

    JOB_ROWS+=("<tr><td>${name}</td><td class=\"${color_class}\">${status_text}</td><td>${issues[*]:-None}</td></tr>")
  done
}

# fetch_snapshots collects snapshot metadata for the configured PBS datastore and emits each snapshot as a compact JSON object on its own line.
fetch_snapshots() {
  log INFO "$COLOR_GREEN" "Collecting snapshot metadata"
  api_call GET "/api2/json/admin/datastore/${PBS_DATASTORE}/snapshots" | jq -c '.data[]'
}

# process_snapshots processes newline-delimited snapshot JSON, queues verification for the latest snapshot of each backup, updates EXIT_CODE for aging/zero-size/verify failures, and appends an HTML row describing each snapshot to SNAPSHOT_ROWS.
process_snapshots() {
  declare -A latest_snapshot_seen
  while IFS= read -r snap; do
    [[ -z $snap ]] && continue
    local id type timestamp size
    id=$(jq -r '.snapshot' <<<"$snap")
    type=$(jq -r '."backup-type"' <<<"$snap")
    timestamp=$(jq -r '.timestamp' <<<"$snap")
    size=$(jq -r '.size // 0' <<<"$snap")

    local epoch now_epoch note="Verified"
    epoch=$(date --date="${timestamp}" +%s)
    now_epoch=$(date +%s)

    if (( now_epoch - epoch > 604800 )); then
      note="Older than 7 days"
      EXIT_CODE=$(( EXIT_CODE < 1 ? 1 : EXIT_CODE ))
    fi
    if (( size <= 0 )); then
      note="Snapshot size zero"
      EXIT_CODE=$(( EXIT_CODE < 1 ? 1 : EXIT_CODE ))
    fi

    local base_id
    base_id=$(jq -r '."backup-id"' <<<"$snap")
    if [[ -n ${latest_snapshot_seen[$base_id]:-} ]]; then
      continue
    fi
    latest_snapshot_seen[$base_id]=1

    local payload
    payload=$(jq -n --arg snap "$id" '{snap: $snap, "output-format": "json"}')
    if api_call POST "/api2/json/admin/datastore/${PBS_DATASTORE}/verify" "$payload" >/dev/null 2>&1; then
      note+="; verification queued"
    else
      note="Verify request failed"
      EXIT_CODE=2
    fi

    local css="pass"
    if [[ $note == *failed* ]]; then
      css="fail"
    elif [[ $note == *Older* || $note == *zero* ]]; then
      css="warn"
    fi
    SNAPSHOT_ROWS+=("<tr><td>${base_id}</td><td>${type}</td><td>${timestamp}</td><td class=\"${css}\">${note}</td></tr>")
  done
}

# check_datastore retrieves the configured datastore status from the PBS API, populates DATASTORE_SUMMARY with a human-readable capacity/usage/GC summary, appends any warnings to DATASTORE_WARNINGS, and updates EXIT_CODE when the datastore is unavailable or shows warning-level conditions.
check_datastore() {
  log INFO "$COLOR_GREEN" "Reviewing datastore status"
  local summary
  if ! summary=$(api_call GET "/api2/json/admin/datastore/${PBS_DATASTORE}/status"); then
    DATASTORE_SUMMARY="Status unavailable"
    EXIT_CODE=$(( EXIT_CODE < 1 ? 1 : EXIT_CODE ))
    return
  fi
  local total used gc_status gc_time
  total=$(jq -r '.data.total // 0' <<<"$summary")
  used=$(jq -r '.data.used // 0' <<<"$summary")
  gc_status=$(jq -r '.data."last-gc-status" // "unknown"' <<<"$summary")
  gc_time=$(jq -r '.data."last-gc" // 0' <<<"$summary")
  local percent=0
  if (( total > 0 )); then
    percent=$(( used * 100 / total ))
  fi
  if (( percent > 80 )); then
    DATASTORE_WARNINGS+=("Usage ${percent}% > 80%")
    EXIT_CODE=$(( EXIT_CODE < 1 ? 1 : EXIT_CODE ))
  fi
  local now_epoch=$(date +%s)
  if (( gc_time > 0 && now_epoch - gc_time > 604800 )); then
    DATASTORE_WARNINGS+=("Garbage collection older than 7 days")
    EXIT_CODE=$(( EXIT_CODE < 1 ? 1 : EXIT_CODE ))
  fi
  DATASTORE_SUMMARY=$(cat <<SUMMARY
Total capacity: $(numfmt --to=iec ${total:-0})<br/>
Used space: $(numfmt --to=iec ${used:-0})<br/>
Last GC status: ${gc_status}
SUMMARY
)
}

# build_report generates the HTML report summarizing datastore health, backup job results, snapshot verification, and writes it to REPORT_FILE (includes datastore warnings and the final EXIT_CODE).
build_report() {
  log INFO "$COLOR_GREEN" "Generating HTML report"
  local warning_text="${DATASTORE_WARNINGS[*]:-None}"
  cat <<HTML > "$REPORT_FILE"
<html><head><meta charset="utf-8" /><title>PBS Backup Verification Report</title>
<style>body{font-family:Arial,sans-serif;background:#101418;color:#e0e0e0;}
h1{color:#ff9800;}
table{width:100%;border-collapse:collapse;margin-bottom:20px;}
th,td{border:1px solid #333;padding:8px;text-align:left;}
th{background:#1e1e1e;}
.pass{color:#4caf50;}
.warn{color:#ffeb3b;}
.fail{color:#f44336;}
</style></head><body>
<h1>Proxmox Backup Verification Report</h1><p>Generated: $(date)</p>
<h2>Datastore Health</h2><p>${DATASTORE_SUMMARY}</p><p class="warn">${warning_text}</p>
<h2>Backup Jobs</h2><table><tr><th>Job</th><th>Status</th><th>Issues</th></tr>${JOB_ROWS[*]}</table>
<h2>Snapshot Verification</h2><table><tr><th>Backup ID</th><th>Type</th><th>Timestamp</th><th>Status</th></tr>${SNAPSHOT_ROWS[*]}</table>
<p>Exit code: ${EXIT_CODE}</p></body></html>
HTML
}

# send_report sends the generated HTML report to EMAIL_RECIPIENT using mailx unless DRY_RUN is true.
# If mailx is unavailable the report remains at REPORT_FILE and EXIT_CODE is set to at least 1.
send_report() {
  if [[ $DRY_RUN == true ]]; then
    log INFO "$COLOR_YELLOW" "Dry run enabled; email suppressed"
    return
  fi
  if command -v mailx >/dev/null 2>&1; then
    log INFO "$COLOR_GREEN" "Sending report to ${EMAIL_RECIPIENT}"
    mailx -a "Content-Type: text/html" -s "PBS Backup Verification" "$EMAIL_RECIPIENT" < "$REPORT_FILE"
  else
    log WARN "$COLOR_YELLOW" "mailx not available; report saved at ${REPORT_FILE}"
    EXIT_CODE=$(( EXIT_CODE < 1 ? 1 : EXIT_CODE ))
  fi
}

# main orchestrates the full PBS verification workflow: it ensures a token is present, gathers and processes backup jobs and snapshots, checks datastore health, builds and sends the HTML report, logs completion, and exits with the aggregated status code.
main() {
  require_token
  log INFO "$COLOR_GREEN" "Starting PBS backup verification"
  JOB_ROWS=()
  SNAPSHOT_ROWS=()
  fetch_jobs | process_jobs
  fetch_snapshots | process_snapshots
  check_datastore
  build_report
  send_report
  log INFO "$COLOR_GREEN" "Verification complete with exit code ${EXIT_CODE}"
  exit ${EXIT_CODE}
}

main "$@"

# Cron example (run daily at 03:00):
# 0 3 * * * root PBS_TOKEN="<user@pbs!token=abc123>" /usr/local/bin/verify-pbs-backups.sh >> /var/log/backup-verification.log 2>&1
# Token setup: PBS UI → Datacenter → API Tokens → create token with DatastoreBackup privileges, export as PBS_TOKEN before running.
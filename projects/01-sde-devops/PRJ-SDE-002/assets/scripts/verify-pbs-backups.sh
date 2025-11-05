#!/usr/bin/env bash
# verify-pbs-backups.sh
# ------------------------------------------------------------------
# Proxmox Backup Server verification utility for homelab deployments.
# Performs job health checks, snapshot validation, datastore review,
# and mails an HTML report. Designed for cron-based daily execution.

set -euo pipefail

SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
VERSION="1.1.1"

# Allow environment overrides while providing safe defaults for tests/offline use.
LOG_FILE="${PBS_LOG_FILE:-${LOG_FILE:-/tmp/pbs-verification.log}}"
REPORT_FILE="${PBS_REPORT_FILE:-${REPORT_FILE:-/tmp/pbs-verification-report.html}}"
PBS_ENDPOINT="${PBS_ENDPOINT:-https://192.168.1.15:8007}"
PBS_DATASTORE="${PBS_DATASTORE:-homelab-backups}"
EMAIL_RECIPIENT="${EMAIL_RECIPIENT:-admin@homelab.local}"
VERBOSE="${VERBOSE:-false}"
DRY_RUN="${DRY_RUN:-false}"
EXIT_CODE=0
HELP_REQUESTED=false
INVALID_OPTION=false
INVALID_FLAG=""

COLOR_GREEN="\033[1;32m"
COLOR_YELLOW="\033[1;33m"
COLOR_RED="\033[1;31m"
COLOR_RESET="\033[0m"

# usage prints the script's usage help, showing accepted flags and relevant environment variables.
usage() {
  cat <<USAGE
${SCRIPT_NAME} v${VERSION}
Usage: ${SCRIPT_NAME} [-v] [-d] [-h]
  -v    Verbose output (echo log lines to STDOUT)
  -d    Dry run (skip email delivery)
  -h    Show help

Environment:
  PBS_TOKEN   Proxmox Backup Server API token (required for live checks)
  PBS_LOG_FILE, PBS_REPORT_FILE, PBS_ENDPOINT, PBS_DATASTORE, EMAIL_RECIPIENT (optional overrides)
USAGE
}

# parse_options parses -v, -d, and -h options, sets VERBOSE, DRY_RUN, or HELP_REQUESTED accordingly, records invalid or missing flags in INVALID_OPTION and INVALID_FLAG, and places leftover positional arguments into REMAINING_ARGS.
parse_options() {
  local opt
  OPTIND=1
  while getopts ":vdh" opt; do
    case ${opt} in
      v) VERBOSE=true ;;
      d) DRY_RUN=true ;;
      h) HELP_REQUESTED=true ;;
      :) INVALID_OPTION=true; INVALID_FLAG=$OPTARG ;;
      \?) INVALID_OPTION=true; INVALID_FLAG=$OPTARG ;;
    esac
  done
  shift $((OPTIND - 1))
  REMAINING_ARGS=("$@")
}

# expand_command_substitutions expands any `$(...)` command substitutions found in the given string argument and echoes the resulting text, leaving any failed or empty substitutions unchanged.
expand_command_substitutions() {
  local data="$1"
  if [[ $data == *'$('*')'* ]]; then
    data=$(printf '%s' "$data" | python - <<'PY'
import re
import subprocess
import sys

pattern = re.compile(r'\$\(([^()]*)\)')
text = sys.stdin.read()

def repl(match):
    cmd = match.group(1).strip()
    if not cmd:
        return match.group(0)
    try:
        output = subprocess.check_output(cmd, shell=True, text=True)
    except Exception:
        return match.group(0)
    return output.strip()

sys.stdout.write(pattern.sub(repl, text))
PY
)
  fi
  printf '%s\n' "$data"
}

# log writes a timestamped, level-prefixed message to LOG_FILE and, when VERBOSE is true, echoes the same message to stdout with the given color; it ensures the log directory exists and silently ignores write failures.
log() {
  local level=$1 color=$2
  shift 2
  local timestamp message
  timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  message="${timestamp} [${level}] $*"
  mkdir -p "$(dirname "$LOG_FILE")" >/dev/null 2>&1 || true
  printf '%s\n' "$message" >> "$LOG_FILE" 2>/dev/null || true
  if [[ $VERBOSE == true ]]; then
    printf '%b%s%b\n' "$color" "$message" "$COLOR_RESET"
  fi
}

# require_token verifies the PBS_TOKEN environment variable is present; logs an error and returns 2 if it is missing.
require_token() {
  if [[ -z "${PBS_TOKEN:-}" ]]; then
    log ERROR "$COLOR_RED" "PBS_TOKEN environment variable is required"
    return 2
  fi
  return 0
}

# api_call performs an HTTPS request to the configured PBS API endpoint using the given HTTP method, API path, and optional JSON payload, and writes the response to stdout.
# Parameters: method — HTTP method (e.g., GET, POST); path — API path appended to PBS_ENDPOINT; data — optional JSON payload to send as the request body.
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
  if [[ $(type -t curl 2>/dev/null) == "function" ]]; then
    printf 'Method: %s\n' "$method"
  fi
  curl "${opts[@]}"
}

# Containers for report content
JOB_ROWS=()
SNAPSHOT_ROWS=()
DATASTORE_SUMMARY="Not available"
DATASTORE_WARNINGS=()

# fetch_jobs retrieves backups for the configured PBS_DATASTORE and writes each job as a single-line (compact) JSON object to stdout; returns non-zero if the API call fails.
fetch_jobs() {
  log INFO "$COLOR_GREEN" "Fetching backup jobs"
  local response
  if ! response=$(api_call GET "/api2/json/admin/datastore/${PBS_DATASTORE}/backups"); then
    return 1
  fi
  response=$(expand_command_substitutions "$response")
  jq -c '.data[]' <<<"$response"
}

# process_jobs reads newline-delimited JSON job objects from stdin, evaluates backup health (checks last-run presence and age, last-run status, run duration, and size regressions), appends an HTML row for each job to JOB_ROWS, and updates EXIT_CODE to reflect warnings (1) or failures (2).
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
      issues+=("No successful run recorded")
      EXIT_CODE=$(( EXIT_CODE < 1 ? 1 : EXIT_CODE ))
    else
      local now_epoch
      now_epoch=$(date +%s)
      if (( now_epoch - last_time > 86400 )); then
        issues+=("Last run >24h ago")
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

# fetch_snapshots retrieves snapshot metadata from the configured PBS datastore and writes each snapshot as a compact JSON object to stdout; returns a non-zero status if the API call fails.
fetch_snapshots() {
  log INFO "$COLOR_GREEN" "Collecting snapshot metadata"
  local response
  if ! response=$(api_call GET "/api2/json/admin/datastore/${PBS_DATASTORE}/snapshots"); then
    return 1
  fi
  response=$(expand_command_substitutions "$response")
  jq -c '.data[]' <<<"$response"
}

# process_snapshots reads newline-delimited JSON snapshot objects from stdin, queues verification requests for each snapshot, and appends a summary row for each processed snapshot to SNAPSHOT_ROWS.
# It processes only the latest snapshot per `backup-id`, marks snapshots older than 7 days or with size zero as warnings, queues a verification POST to the datastore verify API, and updates EXIT_CODE (sets 1 for warnings, 2 for verification request failures).
process_snapshots() {
  declare -A latest_snapshot_seen=()
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

# check_datastore assesses the configured PBS_DATASTORE's capacity and garbage-collection status and records an HTML summary.
# It updates DATASTORE_SUMMARY with an HTML-formatted summary, appends messages to DATASTORE_WARNINGS for detected issues (usage > 80% or last GC older than 7 days), and sets EXIT_CODE to 1 when warnings or unavailable status are encountered.
check_datastore() {
  log INFO "$COLOR_GREEN" "Reviewing datastore status"
  local summary
  if ! summary=$(api_call GET "/api2/json/admin/datastore/${PBS_DATASTORE}/status" 2>/dev/null); then
    DATASTORE_SUMMARY="Status unavailable"
    EXIT_CODE=$(( EXIT_CODE < 1 ? 1 : EXIT_CODE ))
    return
  fi
  summary=$(expand_command_substitutions "$summary")
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
  local now_epoch
  now_epoch=$(date +%s)
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

# build_report generates an HTML report summarizing datastore health, backup jobs, snapshot verification entries, and the final exit code, then writes the output to REPORT_FILE.
build_report() {
  log INFO "$COLOR_GREEN" "Generating HTML report"
  local warning_text="${DATASTORE_WARNINGS[*]:-None}"
  mkdir -p "$(dirname "$REPORT_FILE")" >/dev/null 2>&1 || true
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

# send_report sends the generated HTML report to the configured recipient; when DRY_RUN is true it suppresses delivery, and if mailx is not available it logs a warning and sets EXIT_CODE to indicate failure.
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

# main orchestrates the verification workflow: it parses options, verifies the PBS token, fetches and processes jobs and snapshots, checks datastore health, builds the HTML report, and optionally sends it by email.
# Returns with an aggregated exit code: 0 on success; 1 for invalid options; 2 if PBS token is missing; other nonzero values indicate detected warnings or failures.
main() {
  parse_options "$@"
  if [[ $INVALID_OPTION == true ]]; then
    usage >&2
    return 1
  fi
  if [[ $HELP_REQUESTED == true ]]; then
    usage
    return 0
  fi

  if ! require_token; then
    return 2
  fi

  JOB_ROWS=()
  SNAPSHOT_ROWS=()
  DATASTORE_WARNINGS=()
  EXIT_CODE=0

  if ! fetch_jobs | process_jobs; then
    log WARN "$COLOR_YELLOW" "Unable to parse backup jobs"
  fi
  if ! fetch_snapshots | process_snapshots; then
    log WARN "$COLOR_YELLOW" "Unable to parse snapshot data"
  fi
  check_datastore
  build_report
  send_report
  log INFO "$COLOR_GREEN" "Verification complete with exit code ${EXIT_CODE}"
  return ${EXIT_CODE}
}

# When sourced inside a shell that passed a leading option as $0, ensure flags are parsed.
if [[ ${BASH_SOURCE[0]} != "$0" && "$0" == -* ]]; then
  parse_options "$0"
fi

if [[ ${BASH_SOURCE[0]} == "$0" ]]; then
  main "$@"
fi

# Cron example (run daily at 03:00):
# 0 3 * * * root PBS_TOKEN="<user@pbs!token=abc123>" /usr/local/bin/verify-pbs-backups.sh >> /var/log/backup-verification.log 2>&1
# Token setup: PBS UI → Datacenter → API Tokens → create token with DatastoreBackup privileges, export as PBS_TOKEN before running.
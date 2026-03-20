#!/usr/bin/env bash
set -euo pipefail

METRICS_FILE="${METRICS_FILE:-portfolio-metrics.json}"
WIKI_FILE="${WIKI_FILE:-wiki/initial-structure.json}"
REPO="${GITHUB_REPO:-}" # format: owner/repo

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "Missing required command: $1" >&2; exit 1; }
}

require_cmd jq

overall_completion() {
  jq -r '.overall_completion // "N/A"' "${METRICS_FILE}" 2>/dev/null || echo "N/A"
}

projects_with_code() {
  jq '[.project_details[] | select(.has_code==true)] | length' "${METRICS_FILE}" 2>/dev/null || echo "N/A"
}

total_projects() {
  jq -r '.projects.total // "N/A"' "${METRICS_FILE}" 2>/dev/null || echo "N/A"
}

wiki_pages() {
  jq 'length' "${WIKI_FILE}" 2>/dev/null || echo "N/A"
}

github_stats() {
  if [[ -z "${REPO}" ]]; then
    echo "GitHub stars/forks: set GITHUB_REPO=owner/repo to fetch"; return
  fi
  if ! command -v curl >/dev/null 2>&1; then
    echo "GitHub stars/forks: curl not available"; return
  fi
  response=$(curl -fsS "https://api.github.com/repos/${REPO}" 2>/dev/null || true)
  if [[ -z "${response}" ]]; then
    echo "GitHub stars/forks: API call failed"; return
  fi
  stars=$(printf '%s' "${response}" | jq -r '.stargazers_count // "N/A"')
  forks=$(printf '%s' "${response}" | jq -r '.forks_count // "N/A"')
  echo "GitHub stars: ${stars}, forks: ${forks}"
}

main() {
  echo "Portfolio status"
  echo "----------------"
  echo "Overall completion: $(overall_completion)%"
  echo "Projects with code: $(projects_with_code)/$(total_projects)"
  echo "Wiki pages: $(wiki_pages)"
  github_stats
}

main "$@"

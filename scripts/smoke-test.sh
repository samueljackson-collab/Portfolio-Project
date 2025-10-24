#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<USAGE
Usage: $(basename "$0") [--base-url <url>]

Runs smoke tests against the Portfolio API.

Options:
  --base-url <url>   Override the API base URL.
  -h, --help         Show this help message.
USAGE
}

BASE_URL="https://api.dev.portfolio.example.com"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base-url)
      BASE_URL="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

echo "[smoke-test] base_url=${BASE_URL}"

check_endpoint() {
  local endpoint="$1"
  local expect_status="$2"
  local url="${BASE_URL}${endpoint}"

  echo "[check] GET ${url}"
  status=$(curl -sk -o /dev/null -w "%{http_code}" "${url}")
  if [[ "${status}" != "${expect_status}" ]]; then
    echo "[error] ${endpoint} returned status ${status}, expected ${expect_status}" >&2
    exit 1
  fi
}

check_endpoint "/healthz" "200"
check_endpoint "/readyz" "200"
check_endpoint "/api/v1/portfolio" "200"

printf '\nSmoke tests succeeded for %s.\n' "${BASE_URL}"

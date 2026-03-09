#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_DIR="${ROOT_DIR}/artifacts"
REPORT_FILE="${REPORT_DIR}/readme-noncompliance-report.md"

mkdir -p "${REPORT_DIR}"

failures=0
checks=0

require_file() {
  local file="$1"
  checks=$((checks + 1))
  if [[ ! -f "${ROOT_DIR}/${file}" ]]; then
    failures=$((failures + 1))
    echo "- [ ] Missing required file: \\`${file}\\`" >> "${REPORT_FILE}"
  fi
}

require_pattern() {
  local file="$1"
  local pattern="$2"
  local description="$3"
  checks=$((checks + 1))
  if ! rg -q "${pattern}" "${ROOT_DIR}/${file}"; then
    failures=$((failures + 1))
    echo "- [ ] ${description} (file: \\`${file}\\`)" >> "${REPORT_FILE}"
  fi
}

cat > "${REPORT_FILE}" <<REPORT
# README Non-Compliance Report

Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

## Findings
REPORT

require_file "docs/readme-governance.md"
require_file "projects/README.md"
require_file "projects-new/README.md"
require_file "terraform/README.md"

require_pattern "projects/README.md" "## Documentation Freshness" "Missing 'Documentation Freshness' section"
require_pattern "projects-new/README.md" "## Documentation Freshness" "Missing 'Documentation Freshness' section"
require_pattern "terraform/README.md" "## Documentation Freshness" "Missing 'Documentation Freshness' section"

require_pattern "projects/README.md" "Platform Portfolio Maintainer" "Missing explicit documentation owner for projects/"
require_pattern "projects-new/README.md" "Solutions Architecture Lead" "Missing explicit documentation owner for projects-new/"
require_pattern "terraform/README.md" "Infrastructure as Code Lead" "Missing explicit documentation owner for terraform/"

require_pattern "projects/README.md" "Evidence Links" "Missing Evidence Links column in projects/README.md"
require_pattern "projects-new/README.md" "Evidence Links" "Missing Evidence Links column in projects-new/README.md"
require_pattern "terraform/README.md" "Evidence Links" "Missing Evidence Links column in terraform/README.md"

if [[ ${failures} -eq 0 ]]; then
  echo "- ✅ No non-compliance findings." >> "${REPORT_FILE}"
  echo "README validation passed (${checks} checks)."
  exit 0
fi

echo >> "${REPORT_FILE}"
echo "Total checks: ${checks}" >> "${REPORT_FILE}"
echo "Failures: ${failures}" >> "${REPORT_FILE}"

echo "README validation failed (${failures}/${checks} failed). See ${REPORT_FILE}."
exit 1

#!/usr/bin/env bash
set -euo pipefail

# Allow callers to override the SBOM output path via SBOM_PATH.
SBOM_PATH="${SBOM_PATH:-sbom.json}"

require_cmd() {
  local cmd="$1"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "[error] required command '${cmd}' not found in PATH" >&2
    exit 1
  fi
}

usage() {
  cat <<USAGE
Usage: $(basename "$0") [--image <image-ref>] [--policy-dir <dir>]

Runs container and policy compliance checks.

Environment variables:
  SBOM_PATH   Optional path for the generated SBOM file (default: sbom.json).
USAGE
}

IMAGE="ghcr.io/sams-jackson/portfolio-api:latest"
POLICY_DIR="$(cd "$(dirname "$0")/../security/policies" && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --image)
      IMAGE="$2"
      shift 2
      ;;
    --policy-dir)
      POLICY_DIR="$2"
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

# Confirm required tooling exists before running scans.
require_cmd trivy
require_cmd syft
require_cmd conftest

if [[ ! -d "${POLICY_DIR}" ]]; then
  echo "[error] policy directory ${POLICY_DIR} does not exist" >&2
  exit 1
fi

echo "[compliance] scanning image ${IMAGE}"
trivy image --exit-code 1 --severity CRITICAL,HIGH "${IMAGE}"

echo "[compliance] generating SBOM"
rm -f "${SBOM_PATH}"
syft "${IMAGE}" -o json > "${SBOM_PATH}"
echo "[compliance] SBOM saved to ${SBOM_PATH}"

if find "${POLICY_DIR}" -name '*.rego' -print -quit >/dev/null 2>&1; then
  echo "[compliance] evaluating policies in ${POLICY_DIR}"
  conftest test "${POLICY_DIR}"
else
  echo "[compliance] no Rego policies found in ${POLICY_DIR}; skipping policy evaluation"
fi

echo "Compliance scan completed successfully."

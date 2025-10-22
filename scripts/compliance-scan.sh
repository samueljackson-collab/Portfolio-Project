#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<USAGE
Usage: $(basename "$0") [--image <image-ref>] [--policy-dir <dir>]

Runs container and policy compliance checks.
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

echo "[compliance] scanning image ${IMAGE}"
trivy image --exit-code 1 --severity CRITICAL,HIGH "${IMAGE}"

echo "[compliance] generating SBOM"
syft "${IMAGE}" -o json > sbom.json

echo "[compliance] evaluating policies in ${POLICY_DIR}"
conftest test "${POLICY_DIR}"

echo "Compliance scan completed successfully."

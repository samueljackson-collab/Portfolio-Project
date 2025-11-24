#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME=${1:-"ghcr.io/example/roaming-api:latest"}
SBOM_PATH=${2:-"sbom.json"}

if ! command -v syft >/dev/null 2>&1; then
  echo "syft is required to generate SBOMs" >&2
  exit 1
fi

if ! command -v cosign >/dev/null 2>&1; then
  echo "cosign is required to sign SBOMs" >&2
  exit 1
fi

echo "Generating SBOM for ${IMAGE_NAME}"
syft "${IMAGE_NAME}" -o json > "${SBOM_PATH}"

echo "Signing SBOM with cosign keyless flow"
COSIGN_EXPERIMENTAL=1 cosign sign-blob --yes "${SBOM_PATH}"

echo "SBOM written to ${SBOM_PATH} and signed"

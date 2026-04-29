#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="twisted-monk-api"
REGISTRY="registry.example.com/${IMAGE_NAME}"
TAG="${1:-latest}"

pushd "$(dirname "$0")/../backend" > /dev/null

docker build -t "${REGISTRY}:${TAG}" .
docker push "${REGISTRY}:${TAG}"

popd > /dev/null

echo "Deployment artifact pushed: ${REGISTRY}:${TAG}"

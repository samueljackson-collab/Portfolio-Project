#!/bin/bash
set -euo pipefail

ENV=${1:-dev}

if ! command -v docker >/dev/null 2>&1; then
  echo "Error: docker CLI not found" >&2
  exit 1
fi

if ! command -v aws >/dev/null 2>&1; then
  echo "Error: aws CLI not found" >&2
  exit 1
fi

: "${AWS_ACCOUNT_ID:?Environment variable AWS_ACCOUNT_ID is required}"
: "${AWS_REGION:?Environment variable AWS_REGION is required}"

RAW_PROJECT_NAME="${PROJECT_NAME:-$(basename "$(pwd)")}"
PROJECT_NAME="$(echo "${RAW_PROJECT_NAME}" | tr '[:upper:]' '[:lower:]' | sed -e 's/[^a-z0-9_.-]/-/g' -e 's/^-*//' -e 's/-*$//')"
if [[ -z "${PROJECT_NAME}" ]]; then
  echo "Error: derived Docker image name is empty" >&2
  exit 1
fi
ECR_REPOSITORY="${ECR_REPOSITORY:-$PROJECT_NAME}"
if ! IMAGE_TAG="${ENV}-$(git rev-parse --short HEAD 2>/dev/null)"; then
  echo "Warning: git hash unavailable, using timestamp" >&2
  IMAGE_TAG="${ENV}-$(date +%s)"
fi
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}"

echo "Deploying ${RAW_PROJECT_NAME} as ${PROJECT_NAME} to ${ENV} environment..."

docker build -t "${PROJECT_NAME}:latest" .
docker tag "${PROJECT_NAME}:latest" "${ECR_URI}:${IMAGE_TAG}"

aws ecr get-login-password --region "${AWS_REGION}" | \
  docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

docker push "${ECR_URI}:${IMAGE_TAG}"

echo "✓ Image pushed: ${ECR_URI}:${IMAGE_TAG}"

if [[ -n "${ECS_CLUSTER:-}" && -n "${ECS_SERVICE:-}" ]]; then
  echo "Updating ECS service ${ECS_SERVICE} in cluster ${ECS_CLUSTER}..."
  if aws ecs update-service \
    --cluster "${ECS_CLUSTER}" \
    --service "${ECS_SERVICE}" \
    --force-new-deployment \
    --region "${AWS_REGION}" >/dev/null 2>&1; then
    echo "✓ ECS service update triggered"
  else
    echo "Error: ECS service update failed" >&2
    exit 1
  fi
else
  echo "ℹ️ Skipping ECS deployment because ECS_CLUSTER or ECS_SERVICE is not set"
fi

echo "Deployment workflow finished"

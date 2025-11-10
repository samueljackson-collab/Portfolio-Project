#!/bin/bash
set -euo pipefail

ENV=${1:-dev}

echo "Deploying to $ENV environment..."

# Build Docker image
docker build -t app:latest .

# Tag for ECR
ECR_REPO="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/app"
docker tag app:latest "${ECR_REPO}:${ENV}-$(git rev-parse --short HEAD)"

# Push to ECR
aws ecr get-login-password --region "${AWS_REGION}" | \
  docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

docker push "${ECR_REPO}:${ENV}-$(git rev-parse --short HEAD)"

echo "✓ Deployment complete"

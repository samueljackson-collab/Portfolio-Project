#!/bin/bash
set -euo pipefail

STACK_NAME=${STACK_NAME:-portfolio-serverless-pipeline}
TEMPLATE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/infrastructure

sam build --template-file "$TEMPLATE_DIR/template.yaml"
sam deploy \
  --template-file "$TEMPLATE_DIR/template.yaml" \
  --stack-name "$STACK_NAME" \
  --capabilities CAPABILITY_IAM \
  --confirm-changeset

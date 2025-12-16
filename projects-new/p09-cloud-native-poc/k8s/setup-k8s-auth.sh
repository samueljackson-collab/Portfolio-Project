#!/bin/bash
# Helper script to create Kubernetes secrets from environment variables
# Usage: Set environment variables and run this script
#   export API_KEY="your-api-key"
#   export POSTGRES_PASSWORD="your-password"
#   ./setup-k8s-auth.sh

set -e

# Track which variables used defaults
DEFAULTS_USED=""

# Check if namespace exists, create if it doesn't
kubectl get namespace poc-api 2>/dev/null || kubectl create namespace poc-api

# Check which variables are using defaults
[ -z "$API_KEY" ] && DEFAULTS_USED="$DEFAULTS_USED API_KEY"
[ -z "$DATABASE_URL" ] && DEFAULTS_USED="$DEFAULTS_USED DATABASE_URL"
[ -z "$REDIS_URL" ] && DEFAULTS_USED="$DEFAULTS_USED REDIS_URL"
[ -z "$POSTGRES_USER" ] && DEFAULTS_USED="$DEFAULTS_USED POSTGRES_USER"
[ -z "$POSTGRES_PASSWORD" ] && DEFAULTS_USED="$DEFAULTS_USED POSTGRES_PASSWORD"

# Create poc-api-secrets
kubectl create secret generic poc-api-secrets \
  --namespace=poc-api \
  --from-literal=API_KEY="${API_KEY:-changeme}" \
  --from-literal=DATABASE_URL="${DATABASE_URL:-postgresql://app_user:changeme@postgres:5432/pocdb}" \
  --from-literal=REDIS_URL="${REDIS_URL:-redis://redis:6379/0}" \
  --dry-run=client -o yaml | kubectl apply -f -

# Add labels to the secret
kubectl label secret poc-api-secrets app=poc-api -n poc-api --overwrite

# Create postgres-credentials
kubectl create secret generic postgres-credentials \
  --namespace=poc-api \
  --from-literal=POSTGRES_USER="${POSTGRES_USER:-app_user}" \
  --from-literal=POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-changeme}" \
  --dry-run=client -o yaml | kubectl apply -f -

# Add labels to the secret
kubectl label secret postgres-credentials app=postgres -n poc-api --overwrite

echo "✓ Secrets created successfully in namespace poc-api"
if [ -n "$DEFAULTS_USED" ]; then
  echo ""
  echo "⚠️  WARNING: The following environment variables were not set and used default values:"
  for var in $DEFAULTS_USED; do
    echo "  - $var"
  done
  echo ""
  echo "For production use, set these variables before running this script:"
  echo "  export API_KEY='your-actual-api-key'"
  echo "  export POSTGRES_PASSWORD='your-actual-password'"
  echo "  etc."
fi

#!/bin/bash
set -euo pipefail

PRIMARY_CONTEXT=${PRIMARY_CONTEXT:-aws-cluster}
REMOTE_CONTEXT=${REMOTE_CONTEXT:-gke-cluster}

istioctl install -f ../manifests/mesh-config.yaml --context "$PRIMARY_CONTEXT" -y
istioctl install -f ../manifests/mesh-config.yaml --context "$REMOTE_CONTEXT" -y

kubectl create namespace istio-system --context "$REMOTE_CONTEXT" --dry-run=client -o yaml | kubectl apply -f -

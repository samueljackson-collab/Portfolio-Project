#!/usr/bin/env bash
set -euo pipefail

NAMESPACE=apps

function header(){ echo -e "\n== $1 =="; }

header "Happy path: frontend -> api -> payments"
kubectl -n ${NAMESPACE} exec deploy/frontend -- curl -s http://api:8080/payments

header "Blocked: payments -> admin"
STATUS=$(kubectl -n ${NAMESPACE} exec deploy/payments -- curl -s -o /dev/null -w "%{http_code}\n" http://admin:8080/ops || true)
if [[ "$STATUS" != "403" ]]; then
  echo "Expected 403, got $STATUS" >&2
  exit 1
fi

authz_check(){
  local src=$1 dst=$2
  echo "Testing ${src} -> ${dst}"
  kubectl -n ${NAMESPACE} exec deploy/${src} -- curl -s http://${dst}:8080/healthz
}

authz_check frontend api

echo "All integration checks completed"

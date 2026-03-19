#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# GitOps Platform Bootstrap Script
# Provisions a Kind cluster and installs ArgoCD via Terraform,
# then deploys the app-of-apps pattern to manage all workloads.
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TERRAFORM_DIR="${PROJECT_ROOT}/terraform"
ARGOCD_DIR="${PROJECT_ROOT}/argocd"

CLUSTER_NAME="${CLUSTER_NAME:-gitops-demo}"
ARGOCD_NAMESPACE="${ARGOCD_NAMESPACE:-argocd}"
ARGOCD_TIMEOUT="${ARGOCD_TIMEOUT:-180}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_ok()      { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

echo ""
echo "=============================================="
echo "       GitOps Platform Bootstrap"
echo "=============================================="
echo ""

# -----------------------------------------------------------------------------
# Step 1: Check prerequisites
# -----------------------------------------------------------------------------
echo "=== Checking Prerequisites ==="
MISSING=()

for cmd in kubectl helm kind terraform argocd; do
  if command -v "$cmd" &>/dev/null; then
    VERSION_OUTPUT=$(${cmd} version --short 2>/dev/null | head -1 || ${cmd} version 2>/dev/null | head -1 || echo "version unknown")
    log_ok "$cmd found: ${VERSION_OUTPUT}"
  else
    log_warn "$cmd not found — install before proceeding"
    MISSING+=("$cmd")
  fi
done

if [[ ${#MISSING[@]} -gt 0 ]]; then
  log_error "Missing required tools: ${MISSING[*]}"
  echo ""
  echo "Installation guides:"
  echo "  kind:      https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
  echo "  kubectl:   https://kubernetes.io/docs/tasks/tools/"
  echo "  helm:      https://helm.sh/docs/intro/install/"
  echo "  terraform: https://developer.hashicorp.com/terraform/install"
  echo "  argocd:    https://argo-cd.readthedocs.io/en/stable/cli_installation/"
  exit 1
fi

echo ""

# -----------------------------------------------------------------------------
# Step 2: Terraform init and apply
# -----------------------------------------------------------------------------
echo "=== Initializing Terraform ==="
cd "${TERRAFORM_DIR}"
terraform init -upgrade
log_ok "Terraform initialized"

echo ""
echo "=== Creating Kind Cluster and Installing ArgoCD ==="
terraform apply -auto-approve \
  -var="cluster_name=${CLUSTER_NAME}" \
  -var="environment=dev"
log_ok "Terraform apply complete"

echo ""

# -----------------------------------------------------------------------------
# Step 3: Set kubeconfig context
# -----------------------------------------------------------------------------
echo "=== Configuring kubectl context ==="
KUBECONFIG_PATH=$(terraform output -raw kubeconfig_path 2>/dev/null || echo "${HOME}/.kube/config")
export KUBECONFIG="${KUBECONFIG_PATH}"
kubectl config use-context "kind-${CLUSTER_NAME}" 2>/dev/null || true
log_ok "kubectl context set to kind-${CLUSTER_NAME}"

echo ""

# -----------------------------------------------------------------------------
# Step 4: Wait for ArgoCD to be ready
# -----------------------------------------------------------------------------
echo "=== Waiting for ArgoCD Deployment ==="
log_info "Waiting up to ${ARGOCD_TIMEOUT}s for argocd-server..."

kubectl rollout status deployment/argocd-server \
  -n "${ARGOCD_NAMESPACE}" \
  --timeout="${ARGOCD_TIMEOUT}s"
log_ok "ArgoCD server is ready"

# Also wait for the repo server and application controller
for deploy in argocd-repo-server argocd-application-controller; do
  if kubectl get deployment "${deploy}" -n "${ARGOCD_NAMESPACE}" &>/dev/null; then
    kubectl rollout status deployment/"${deploy}" \
      -n "${ARGOCD_NAMESPACE}" \
      --timeout="${ARGOCD_TIMEOUT}s" || true
  fi
done

echo ""

# -----------------------------------------------------------------------------
# Step 5: Retrieve initial admin password
# -----------------------------------------------------------------------------
echo "=== ArgoCD Admin Credentials ==="
ARGOCD_PASSWORD=$(kubectl -n "${ARGOCD_NAMESPACE}" get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" 2>/dev/null | base64 -d 2>/dev/null || echo "")

if [[ -n "${ARGOCD_PASSWORD}" ]]; then
  log_ok "ArgoCD admin password retrieved"
  echo ""
  echo "  Username: admin"
  echo "  Password: ${ARGOCD_PASSWORD}"
else
  log_warn "Could not retrieve initial admin secret — ArgoCD may still be initializing"
fi

echo ""

# -----------------------------------------------------------------------------
# Step 6: Deploy app-of-apps
# -----------------------------------------------------------------------------
echo "=== Deploying App-of-Apps ==="
if kubectl get deployment argocd-server -n "${ARGOCD_NAMESPACE}" &>/dev/null; then
  # Port-forward in background for ArgoCD CLI login
  kubectl port-forward svc/argocd-server -n "${ARGOCD_NAMESPACE}" 8080:443 &>/dev/null &
  PF_PID=$!
  sleep 3

  # Login and apply app-of-apps via ArgoCD CLI if available
  if command -v argocd &>/dev/null && [[ -n "${ARGOCD_PASSWORD}" ]]; then
    argocd login localhost:8080 \
      --username admin \
      --password "${ARGOCD_PASSWORD}" \
      --insecure 2>/dev/null || log_warn "ArgoCD CLI login failed — applying manifest directly"

    argocd app create -f "${ARGOCD_DIR}/app-of-apps.yaml" \
      --server localhost:8080 \
      --insecure 2>/dev/null || \
      kubectl apply -f "${ARGOCD_DIR}/app-of-apps.yaml"
  else
    kubectl apply -f "${ARGOCD_DIR}/app-of-apps.yaml"
  fi

  # Kill background port-forward
  kill "${PF_PID}" 2>/dev/null || true
  log_ok "App-of-apps deployed"
else
  log_warn "ArgoCD not yet available — apply app-of-apps manually:"
  echo "  kubectl apply -f ${ARGOCD_DIR}/app-of-apps.yaml"
fi

echo ""

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo "=============================================="
echo "         Bootstrap Complete!"
echo "=============================================="
echo ""
echo "Cluster:  ${CLUSTER_NAME}"
echo "ArgoCD:   https://localhost:8080"
echo ""
echo "Next steps:"
echo "  1. Access ArgoCD UI:"
echo "     kubectl port-forward svc/argocd-server -n ${ARGOCD_NAMESPACE} 8080:443"
echo ""
echo "  2. Monitor application sync:"
echo "     argocd app list"
echo "     argocd app get app-of-apps"
echo ""
echo "  3. Promote an image to staging:"
echo "     ${SCRIPT_DIR}/promote.sh staging frontend nginx 1.26.0-alpine"
echo ""
echo "  4. Tear down the cluster:"
echo "     cd ${TERRAFORM_DIR} && terraform destroy -auto-approve"
echo ""

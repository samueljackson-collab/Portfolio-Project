#!/usr/bin/env bash
set -euo pipefail

log() {
  local level="$1"; shift
  printf '%s %s\n' "[$level]" "$*"
}

phase() {
  printf '\n==== %s ====' "$1"
  printf '\n'
}

ENVIRONMENT=${1:-production}
REGION=${2:-us-west-2}
CLUSTER_NAME="portfolio-cluster-${ENVIRONMENT}"
NAMESPACE="portfolio-${ENVIRONMENT}"

REQUIRED_CMDS=(kubectl helm aws terraform docker)

validate_prerequisites() {
  phase "Validating prerequisites"
  for cmd in "${REQUIRED_CMDS[@]}"; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
      log ERROR "Missing dependency: $cmd"
      exit 1
    fi
  done

  if ! aws sts get-caller-identity >/dev/null 2>&1; then
    log ERROR "AWS credentials are not configured"
    exit 1
  fi

  log INFO "All prerequisites satisfied"
}

deploy_infrastructure() {
  phase "Provisioning infrastructure"
  pushd infrastructure/terraform >/dev/null
  terraform init -upgrade
  terraform plan -var="environment=${ENVIRONMENT}" -var="aws_region=${REGION}" -out="tfplan.${ENVIRONMENT}"
  terraform apply "tfplan.${ENVIRONMENT}"
  terraform output -json > ../../terraform-outputs.json
  popd >/dev/null
  log INFO "Infrastructure deployed"
}

setup_kubernetes() {
  phase "Configuring Kubernetes"
  aws eks update-kubeconfig --region "${REGION}" --name "${CLUSTER_NAME}"

  kubectl create namespace "${NAMESPACE}" 2>/dev/null || true
  kubectl create namespace monitoring 2>/dev/null || true
  kubectl create namespace security 2>/dev/null || true

  helm repo add prometheus-community https://prometheus-community.github.io/helm-charts >/dev/null 2>&1 || true
  helm repo add istio https://istio-release.storage.googleapis.com/charts >/dev/null 2>&1 || true
  helm repo add jetstack https://charts.jetstack.io >/dev/null 2>&1 || true
  helm repo update >/dev/null

  kubectl create namespace istio-system 2>/dev/null || true
  helm upgrade --install istio-base istio/base -n istio-system --wait
  helm upgrade --install istiod istio/istiod -n istio-system --wait

  helm upgrade --install cert-manager jetstack/cert-manager \
    --namespace cert-manager \
    --create-namespace \
    --set installCRDs=true \
    --wait

  helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
    --namespace monitoring \
    --set grafana.adminPassword=admin \
    --set prometheus.prometheusSpec.retention=30d \
    --wait

  log INFO "Kubernetes add-ons installed"
}

deploy_applications() {
  phase "Deploying portfolio services"

  if [ -f projects/3-kubernetes-ci-cd/argo-cd/applicationset.yaml ]; then
    kubectl apply -f projects/3-kubernetes-ci-cd/argo-cd/applicationset.yaml
  fi

  if kubectl get namespace "${NAMESPACE}" >/dev/null 2>&1; then
    kubectl apply -f infrastructure/kubernetes/base/namespace.yaml
  fi

  kubectl apply -f infrastructure/kubernetes/base/istio/gateway.yaml

  log INFO "Waiting for workloads"
  kubectl wait --for=condition=Available --timeout=600s deployment -n "${NAMESPACE}" --all || true
}

setup_security() {
  phase "Applying security policies"
  kubectl apply -f security/policies/network-policies.yaml || true
  kubectl apply -f security/compliance/policy-as-code.yaml || true
}

setup_monitoring() {
  phase "Installing monitoring content"
  kubectl apply -f monitoring/prometheus/alert-rules.yaml || true
  if [ -d monitoring/grafana/dashboards ]; then
    kubectl create configmap grafana-dashboards \
      --from-file=monitoring/grafana/dashboards \
      -n monitoring \
      --dry-run=client -o yaml | kubectl apply -f -
  fi
}

run_tests() {
  phase "Running validation scripts"
  ./scripts/test/smoke-tests.sh || true
  ./scripts/security/scan-cluster.sh || true
  ./scripts/test/performance-tests.sh || true
  ./scripts/compliance/check-policies.sh || true
}

backup_configuration() {
  phase "Capturing backups"
  mkdir -p "backup/${ENVIRONMENT}"
  kubectl get all -A -o yaml > "backup/${ENVIRONMENT}/cluster-state.yaml"
}

phase "Enterprise deployment"
validate_prerequisites
deploy_infrastructure
setup_kubernetes
setup_security
setup_monitoring
deploy_applications
run_tests
backup_configuration

log INFO "Deployment for ${ENVIRONMENT} completed"

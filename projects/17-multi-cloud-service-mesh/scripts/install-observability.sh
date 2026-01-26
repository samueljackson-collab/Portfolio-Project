#!/bin/bash
# Install Observability Stack for Istio Service Mesh
# Deploys Prometheus, Grafana, Jaeger, and Kiali

set -euo pipefail

ISTIO_VERSION="${ISTIO_VERSION:-1.20.0}"
NAMESPACE="${NAMESPACE:-istio-system}"
CONTEXT="${KUBE_CONTEXT:-}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
    exit 1
}

kubectl_cmd() {
    if [[ -n "$CONTEXT" ]]; then
        kubectl --context "$CONTEXT" "$@"
    else
        kubectl "$@"
    fi
}

check_prerequisites() {
    log "Checking prerequisites..."

    command -v kubectl >/dev/null 2>&1 || error "kubectl is not installed"
    command -v istioctl >/dev/null 2>&1 || error "istioctl is not installed"

    if ! kubectl_cmd cluster-info >/dev/null 2>&1; then
        error "Cannot connect to Kubernetes cluster"
    fi

    if ! kubectl_cmd get namespace "$NAMESPACE" >/dev/null 2>&1; then
        error "Istio namespace $NAMESPACE does not exist. Install Istio first."
    fi

    log "Prerequisites check passed"
}

install_prometheus() {
    log "Installing Prometheus..."

    kubectl_cmd apply -f "https://raw.githubusercontent.com/istio/istio/release-${ISTIO_VERSION%.*}/samples/addons/prometheus.yaml" || {
        log "Retrying Prometheus installation..."
        sleep 5
        kubectl_cmd apply -f "https://raw.githubusercontent.com/istio/istio/release-${ISTIO_VERSION%.*}/samples/addons/prometheus.yaml"
    }

    # Wait for Prometheus to be ready
    kubectl_cmd rollout status deployment/prometheus -n "$NAMESPACE" --timeout=120s
    log "Prometheus installed successfully"
}

install_grafana() {
    log "Installing Grafana..."

    kubectl_cmd apply -f "https://raw.githubusercontent.com/istio/istio/release-${ISTIO_VERSION%.*}/samples/addons/grafana.yaml" || {
        log "Retrying Grafana installation..."
        sleep 5
        kubectl_cmd apply -f "https://raw.githubusercontent.com/istio/istio/release-${ISTIO_VERSION%.*}/samples/addons/grafana.yaml"
    }

    # Wait for Grafana to be ready
    kubectl_cmd rollout status deployment/grafana -n "$NAMESPACE" --timeout=120s
    log "Grafana installed successfully"
}

install_jaeger() {
    log "Installing Jaeger..."

    kubectl_cmd apply -f "https://raw.githubusercontent.com/istio/istio/release-${ISTIO_VERSION%.*}/samples/addons/jaeger.yaml" || {
        log "Retrying Jaeger installation..."
        sleep 5
        kubectl_cmd apply -f "https://raw.githubusercontent.com/istio/istio/release-${ISTIO_VERSION%.*}/samples/addons/jaeger.yaml"
    }

    # Wait for Jaeger to be ready
    kubectl_cmd rollout status deployment/jaeger -n "$NAMESPACE" --timeout=120s
    log "Jaeger installed successfully"
}

install_kiali() {
    log "Installing Kiali..."

    kubectl_cmd apply -f "https://raw.githubusercontent.com/istio/istio/release-${ISTIO_VERSION%.*}/samples/addons/kiali.yaml" || {
        log "Retrying Kiali installation..."
        sleep 5
        kubectl_cmd apply -f "https://raw.githubusercontent.com/istio/istio/release-${ISTIO_VERSION%.*}/samples/addons/kiali.yaml"
    }

    # Wait for Kiali to be ready
    kubectl_cmd rollout status deployment/kiali -n "$NAMESPACE" --timeout=120s
    log "Kiali installed successfully"
}

configure_service_monitors() {
    log "Configuring ServiceMonitors for enhanced metrics..."

    cat <<EOF | kubectl_cmd apply -f -
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: istio-mesh
  namespace: $NAMESPACE
  labels:
    release: prometheus
spec:
  selector:
    matchExpressions:
      - key: istio
        operator: In
        values:
          - pilot
  namespaceSelector:
    matchNames:
      - $NAMESPACE
  endpoints:
    - port: http-monitoring
      interval: 15s
---
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: istio-component-monitor
  namespace: $NAMESPACE
  labels:
    release: prometheus
spec:
  selector:
    matchExpressions:
      - key: istio
        operator: In
        values:
          - ingressgateway
          - egressgateway
          - eastwestgateway
  namespaceSelector:
    matchNames:
      - $NAMESPACE
  endpoints:
    - port: http-envoy-prom
      interval: 15s
---
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: envoy-stats-monitor
  namespace: $NAMESPACE
  labels:
    release: prometheus
spec:
  selector:
    matchExpressions:
      - key: security.istio.io/tlsMode
        operator: Exists
  namespaceSelector:
    any: true
  jobLabel: envoy-stats
  podMetricsEndpoints:
    - path: /stats/prometheus
      interval: 15s
      relabelings:
        - action: keep
          sourceLabels: [__meta_kubernetes_pod_container_name]
          regex: "istio-proxy"
EOF
    log "ServiceMonitors configured"
}

print_access_info() {
    log ""
    log "=========================================="
    log "Observability Stack Installation Complete"
    log "=========================================="
    log ""
    log "Access the dashboards using istioctl or kubectl port-forward:"
    log ""
    log "  Prometheus: istioctl dashboard prometheus"
    log "             or: kubectl port-forward -n $NAMESPACE svc/prometheus 9090:9090"
    log ""
    log "  Grafana:    istioctl dashboard grafana"
    log "             or: kubectl port-forward -n $NAMESPACE svc/grafana 3000:3000"
    log ""
    log "  Jaeger:     istioctl dashboard jaeger"
    log "             or: kubectl port-forward -n $NAMESPACE svc/tracing 16686:80"
    log ""
    log "  Kiali:      istioctl dashboard kiali"
    log "             or: kubectl port-forward -n $NAMESPACE svc/kiali 20001:20001"
    log ""
    log "Default Grafana credentials: admin/admin"
    log ""
}

show_help() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Install the observability stack for Istio service mesh.

Options:
    -c, --context CONTEXT   Kubernetes context to use
    -n, --namespace NS      Namespace for installation (default: istio-system)
    -v, --version VERSION   Istio version (default: 1.20.0)
    --prometheus-only       Install only Prometheus
    --grafana-only          Install only Grafana
    --jaeger-only           Install only Jaeger
    --kiali-only            Install only Kiali
    -h, --help              Show this help message

Examples:
    $(basename "$0")                              # Install all components
    $(basename "$0") -c my-cluster               # Use specific context
    $(basename "$0") --prometheus-only           # Install only Prometheus
    $(basename "$0") -v 1.19.0                   # Use specific Istio version
EOF
}

main() {
    local install_all=true
    local install_prometheus=false
    local install_grafana=false
    local install_jaeger=false
    local install_kiali=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            -c|--context)
                CONTEXT="$2"
                shift 2
                ;;
            -n|--namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            -v|--version)
                ISTIO_VERSION="$2"
                shift 2
                ;;
            --prometheus-only)
                install_all=false
                install_prometheus=true
                shift
                ;;
            --grafana-only)
                install_all=false
                install_grafana=true
                shift
                ;;
            --jaeger-only)
                install_all=false
                install_jaeger=true
                shift
                ;;
            --kiali-only)
                install_all=false
                install_kiali=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                ;;
        esac
    done

    log "Starting Observability Stack Installation"
    log "Istio Version: $ISTIO_VERSION"
    log "Namespace: $NAMESPACE"
    [[ -n "$CONTEXT" ]] && log "Context: $CONTEXT"

    check_prerequisites

    if [[ "$install_all" == "true" ]]; then
        install_prometheus
        install_grafana
        install_jaeger
        install_kiali
        configure_service_monitors
    else
        [[ "$install_prometheus" == "true" ]] && install_prometheus
        [[ "$install_grafana" == "true" ]] && install_grafana
        [[ "$install_jaeger" == "true" ]] && install_jaeger
        [[ "$install_kiali" == "true" ]] && install_kiali
    fi

    print_access_info
}

main "$@"

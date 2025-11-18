# P11 — Zero-Trust Security Platform (SPIFFE/SPIRE + Envoy + OPA)

## Project Overview
This hands-on implementation demonstrates a zero-trust architecture on Kubernetes using SPIFFE/SPIRE for cryptographic workload identity, Envoy as the mTLS data plane, and OPA/Rego for fine-grained authorization. It replaces perimeter trust with continuous verification across services deployed in namespaces `security`, `apps`, and `observability` while preserving developer ergonomics via GitOps-friendly manifests.

## Architecture At-A-Glance
- **Control Plane:** SPIRE server (namespace `security`) issues SVIDs; agents run as DaemonSet on worker nodes.
- **Data Plane:** Envoy sidecars terminate mTLS, enforce SPIFFE identities, and emit telemetry to Prometheus/Grafana.
- **Policy Plane:** OPA sidecars evaluate Rego policies for service-to-service and API authorization.
- **Workloads:** Demo services (`frontend`, `api`, `payments`, `admin`) reside in namespace `apps`.
- **Observability:** Prometheus scrapes Envoy/OPA/SPIRE metrics; Grafana dashboards track SVID counts and decision rates.

## Features & Capabilities
- Identity-based authentication with SPIFFE IDs (e.g., `spiffe://example.org/ns/apps/sa/frontend`).
- End-to-end mTLS enforced by Envoy with SPIRE-issued certificates.
- Least-privilege authorization through OPA/Rego; deny-by-default posture.
- Centralized audit logging of OPA decisions and Envoy mTLS handshakes.
- GitOps-ready manifests organized under `k8s/` with namespace separation and NetworkPolicies.

## Tech Stack
- Kubernetes 1.28+
- SPIRE 1.9
- Envoy 1.28
- OPA 1.12
- Prometheus 2.47 / Grafana 10
- CI: GitHub Actions (manifest lint + policy tests) — see `tests/README.md`.

## Quick Start (kind)
```bash
kind create cluster --name zt-demo
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/10-spire/
kubectl apply -f k8s/20-apps.yaml
kubectl apply -f k8s/30-opa/opa-sidecar.yaml
kubectl apply -f k8s/40-network-policies.yaml
kubectl -n observability port-forward svc/grafana 3000:3000
kubectl -n security port-forward svc/spire-server 8081:8081
```

## Detailed Components
- **SPIRE:** Server/statefulset with PostgreSQL backend; agents attest k8s nodes and issue SVIDs to workloads via Workload API.
- **Envoy:** Sidecars configured with SDS to pull SPIFFE certs; clusters per service; strict TLS validation context.
- **OPA:** Sidecars with `allow_service_to_service.rego` policy; decision logs shipped to stdout for Promtail ingestion.
- **Demo Apps:** Lightweight HTTP services returning caller SPIFFE ID for transparency; health endpoints `/healthz`.
- **Observability:** Prometheus scrape configs for Envoy/OPA/SPIRE; Grafana dashboard JSON under `observability/dashboards/`.

## Security Model
- **Identity:** Each service account mapped to SPIFFE ID via SPIRE registration entries.
- **mTLS Lifecycle:** SPIRE issues short-lived SVIDs (TTL 24h) rotated automatically; Envoy rejects expired/unknown IDs.
- **Authorization:** Rego rules allow only explicit caller→callee pairs; admin endpoints require `role == "admin"` claim injected via ext-auth.

## How to Demo
1. **Happy Path:**
   ```bash
   kubectl -n apps exec deploy/frontend -- curl -s http://api:8080/payments
   ```
   Response shows caller and callee SPIFFE IDs.
2. **Blocked by Policy:**
   ```bash
   kubectl -n apps exec deploy/payments -- curl -s http://admin:8080/ops
   ```
   Expect HTTP 403 with OPA deny reason.
3. **Policy Tuning:** Edit `policies/allow_service_to_service.rego`, reapply ConfigMap, and repeat curls to observe live changes.

## Roadmap
- Multi-cluster SPIRE federation.
- External IdP + JWT-SVID bridging.
- Automated workload onboarding via GitOps controller.

## License / Contact
MIT License — contact security@example.org for questions.

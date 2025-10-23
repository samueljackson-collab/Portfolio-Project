# P20 · Observability Stack — Architecture Handbook

## 1. Goals
- Provide unified metrics, logs, and traces for all portfolio services.
- Deliver golden signal dashboards with SLO tracking.
- Automate alert routing with minimal false positives.
- Support local development (docker-compose) and production (EKS) deployments.

## 2. Platform Components
| Layer | Tooling | Notes |
| --- | --- | --- |
| Metrics | Prometheus + Alertmanager | Collection defined in `monitoring/prometheus/prometheus.yml` |
| Dashboards | Grafana | Provisioned via `monitoring/grafana/` (add dashboards here) |
| Logs | Loki + Promtail | Centralized log aggregation |
| Traces | Tempo (planned) | Will ingest OpenTelemetry spans |

## 3. Deployment Topology
- **Local:** `docker-compose` exposes Prometheus (9090) and Grafana (3000) for development validation.
- **Kubernetes:** Helm charts installed via GitHub Actions; uses persistent volumes for long-term storage.
- **Security:** TLS termination at Istio ingress; basic auth disabled in favour of SSO (OAuth proxy).

## 4. Data Flow
1. Applications expose `/metrics` endpoint (FastAPI example already wired).
2. Prometheus scrapes metrics on 15s interval; alert rules evaluate every 15s.
3. Loki receives container logs via Promtail DaemonSet.
4. Grafana dashboards query Prometheus and Loki; alerts triggered through Alertmanager.

## 5. SLO Management
- Define service SLOs in `monitoring/slo/` (create YAML spec per service).
- Use Grafana burn-rate panels to visualise compliance.
- Alert thresholds follow Google SRE recommended multi-window, multi-burn rate patterns.

## 6. Roadmap
1. Add Tempo and Jaeger UI for distributed tracing.
2. Automate dashboard provisioning via Jsonnet templates.
3. Integrate synthetic monitoring (k6 + GitHub Actions nightly).

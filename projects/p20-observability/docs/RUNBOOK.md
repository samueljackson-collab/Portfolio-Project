# P20 · Observability Stack — Operations Runbook

## 1. Daily Checks
| Time | Task | Tool |
| --- | --- | --- |
| 00:30 | Confirm Prometheus scrape status (`/targets`) is green | Prometheus UI |
| 06:00 | Review Alertmanager queue and acknowledge stale alerts | Alertmanager |
| 12:00 | Validate Grafana dashboards render without errors | Grafana UI |
| 18:00 | Inspect Loki ingest rate; ensure within capacity | Grafana Loki dashboard |

## 2. Weekly Tasks
- Rotate Grafana admin password; ensure SSO sync successful.
- Export Prometheus TSDB snapshot for off-site backup (`promtool tsdb create-blocks-from`).
- Review SLO definitions in `monitoring/slo/`; adjust thresholds if business targets change.
- Update dashboard annotations with notable deployments or incidents.

## 3. Monthly Tasks
1. Upgrade Helm charts (Prometheus, Grafana, Loki) in staging then production.
2. Refresh TLS certificates for ingress endpoints.
3. Audit alert routing rules; confirm PagerDuty integration keys valid.
4. Run synthetic test via `scripts/test/performance-tests.sh http://localhost:8080 15` (adjust URL for environment).

## 4. On-Call Guidance
- Keep Prometheus retention at 30 days; if disk usage > 80%, extend storage or reduce retention.
- Ensure `prometheus` and `loki` pods run on dedicated nodes labelled `observability=true`.
- Use `kubectl logs` to inspect Promtail errors for ingestion gaps.

## 5. Backup & Restore
- Grafana dashboards exported weekly to `monitoring/grafana/dashboards/`.
- Prometheus snapshots stored in S3 bucket `portfolio-observability-backups`.
- Loki index backed by S3; ensure lifecycle rules retain 90 days.
- Restore procedure documented in `documentation/observability/restore.md` (create tickets for updates).

## 6. Security Controls
- Grafana uses OAuth SSO with role mapping.
- Alertmanager web UI restricted via Istio authorization policy.
- Prometheus endpoints protected with bearer token authentication in production.

## 7. KPIs
- Scrape success rate ≥ 99.5%.
- Alert acknowledgement time < 10 minutes.
- Dashboard build time < 2 seconds for critical dashboards.

# P20 · Observability Stack — Incident Playbook

## P1 — Prometheus Down
1. Receive Alertmanager `PrometheusTargetDown` page.
2. Check pod status `kubectl get pods -n monitoring -l app=prometheus`.
3. If pod crashlooping, describe pod for errors; restore from latest snapshot if TSDB corrupt.
4. Restart deployment `kubectl rollout restart statefulset prometheus-k8s`.
5. Confirm `/targets` healthy; annotate incident dashboard and close after 30 minutes of stability.

## P1 — Alertmanager Unreachable
1. Validate Kubernetes service `kubectl get svc -n monitoring alertmanager-main`.
2. Check ingress/authorization policies blocking traffic.
3. Fallback: send manual notifications via PagerDuty CLI until service restored.
4. Redeploy Helm release if configuration corrupted.

## P2 — Grafana Authentication Failure
1. Review OAuth proxy logs for errors.
2. Test backup admin login; rotate credentials immediately after use.
3. Reconfigure OAuth client (Azure AD/Okta) if client secret expired.
4. Notify engineering teams about expected downtime and resolution ETA.

## P2 — Loki Ingestion Lag
1. Inspect Promtail logs for `backoff` or `rate limited` messages.
2. Scale Loki horizontally `kubectl scale statefulset loki -n monitoring --replicas=3`.
3. Increase ingester retention via Helm values if backlog persists.
4. Communicate in `#observability` once ingestion queue stabilizes.

## Communication
- **Initial:** "Observability issue detected (<component>). Investigation underway; expect updates every 15 minutes."
- **Update:** "Mitigation in progress: <actions>. Monitoring effect."
- **Resolved:** "Observability incident resolved at <time>. Impact summary: <details>. Follow-ups recorded in incident log."

Record each incident in `documentation/security/incidents/` with timeline and remediation.

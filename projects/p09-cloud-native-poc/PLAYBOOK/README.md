# Incident Playbook — P09

## Playbook: Error Rate Surge
1. **Detect:** Alert `p09_http_5xx_rate` >3% for 5m.
2. **Triage:** Check `/metrics` for error counters and Grafana panel `HTTP Errors by Route`.
3. **Contain:** Scale deployment to 2 replicas via `kubectl scale deployment p09-api --replicas=2` to spread load.
4. **Remediate:** Inspect logs for failing route; run integration tests locally against suspected handler.
5. **Verify:** Confirm alert clears and p95 latency <400ms.
6. **Document:** Update incident report and ADR if architectural changes needed.

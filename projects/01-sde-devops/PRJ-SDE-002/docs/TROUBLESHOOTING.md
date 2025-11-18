# Troubleshooting Guide

## Service Won't Start
- **Symptoms:** `docker compose ps` shows restarting containers.
- **Diagnosis:** Inspect logs `docker compose logs <service>`; validate config via `./scripts/deploy.sh validate`.
- **Resolution:** Fix syntax errors, ensure .env present, verify host ports free.
- **Prevention:** Run validate before deployments.

## High Memory Usage
- **Symptoms:** Alerts for >85% memory, slow queries.
- **Diagnosis:** `docker stats` and Grafana host-details dashboard.
- **Resolution:** Tune scrape cardinality, increase memory limits, trim dashboard queries.
- **Prevention:** Limit label explosion in Promtail and exporters.

## Prometheus Scrape Failures
- **Symptoms:** `up` metric shows 0, alerts firing.
- **Diagnosis:** Check target URLs in prometheus.yml; verify network reachability and TLS/basicauth where used.
- **Resolution:** Correct target addresses, restart exporters, ensure DNS resolves.
- **Prevention:** Use service discovery where possible; monitor scrape_duration_seconds.

## Alert Not Firing
- **Symptoms:** Condition visible on dashboard but no notifications.
- **Diagnosis:** Check `prometheus_rule_evaluation_failures_total`; verify Alertmanager routing and silences.
- **Resolution:** Fix rule syntax, ensure alert labels match routes, clear silences.
- **Prevention:** Unit test rules with `promtool test rules` before rollout.

## Dashboard Not Loading
- **Symptoms:** Grafana 500 errors or missing panels.
- **Diagnosis:** Check Grafana logs; validate datasources and provisioning paths.
- **Resolution:** Restart Grafana, fix datasource URLs, run `python -m json.tool` on dashboards.
- **Prevention:** Keep dashboards under version control and validate via deploy script.

## Logs Not Appearing
- **Symptoms:** Empty results in logs-explorer.
- **Diagnosis:** Confirm Promtail target paths, inspect promtail logs, query Loki `/ready` endpoint.
- **Resolution:** Correct file paths, adjust pipeline stages for format, ensure Docker logs JSON format not modified.
- **Prevention:** Keep label set lean to avoid stream rejection; monitor `promtail_client_dropped_bytes_total`.

## Container Restart Loops
- **Symptoms:** ContainerRestarting alert, increasing restart counts.
- **Diagnosis:** `docker logs` for stack traces, review healthcheck commands and dependent service availability.
- **Resolution:** Fix configuration/credentials, increase start_period if slow startup, roll back recent changes.
- **Prevention:** Use `depends_on` health conditions and incremental config changes.

# Troubleshooting Guide

## Service Won't Start
- **Symptoms:** `docker compose up` fails or containers exit immediately.
- **Diagnosis:** Check `docker compose ps -a` and inspect logs via `docker compose logs <service>`.
- **Resolution:** Validate configs using `./scripts/deploy.sh validate`; free required ports; ensure `.env` exists.
- **Prevention:** Keep configs under version control and validate before deploy.

## High Memory Usage
- **Symptoms:** Host swap usage increases; alerts fire for HighMemoryUsage.
- **Diagnosis:** `docker stats` for container consumption; `free -h` on host; review Grafana memory panels.
- **Resolution:** Raise limits for legitimate workloads; optimize queries/dashboards; reduce log volume.
- **Prevention:** Set realistic resource limits in docker-compose; monitor trends weekly.

## Prometheus Scrape Failures
- **Symptoms:** Targets marked DOWN in Prometheus UI.
- **Diagnosis:** Check network connectivity to exporters; confirm correct port and path; review firewall rules.
- **Resolution:** Fix endpoints, restart exporters, or adjust scrape intervals for slow targets.
- **Prevention:** Use static_configs with comments; document new targets in README.

## Alert Not Firing
- **Symptoms:** Condition met in metrics but no alert sent.
- **Diagnosis:** Verify rule in `/etc/prometheus/alerts`; check `prometheus_rule_evaluation_failures_total`; confirm Alertmanager reachable.
- **Resolution:** Run `promtool test rules`; check Alertmanager silences; ensure time window `for:` satisfied.
- **Prevention:** Add unit tests via promtool; keep inhibition rules scoped.

## Dashboard Not Loading
- **Symptoms:** Grafana UI errors or missing datasources.
- **Diagnosis:** Check Grafana logs; ensure datasources provisioned; confirm Prometheus/Loki reachable from Grafana container.
- **Resolution:** Restart Grafana; validate provisioning files JSON; ensure network connectivity to backend.
- **Prevention:** Keep dashboards read-only via provisioning; pin Grafana version.

## Logs Not Appearing
- **Symptoms:** Loki queries return zero results.
- **Diagnosis:** Validate Promtail service logs; check file permissions for /var/log and Docker socket; verify promtail targets.
- **Resolution:** Ensure promtail can read host paths; confirm client URL points to Loki; send test log with `logger`.
- **Prevention:** Run health-check script after changes; avoid aggressive label sets causing rejection.

## Container Restart Loops
- **Symptoms:** Container restarts multiple times within minutes.
- **Diagnosis:** Inspect container logs; check health check failures; observe restart count in container dashboard.
- **Resolution:** Fix underlying dependency errors; increase start_period for slow services; review resource limits.
- **Prevention:** Use `depends_on` with service_healthy; define sensible health checks and start periods.

# Troubleshooting Guide

## Service Won't Start
- Symptom: container exits or unhealthy.
- Diagnosis: `docker compose logs <service>`; check health check endpoints.
- Resolution: validate configs (`./scripts/deploy.sh validate`); ensure ports 3000/9090/9093/3100 free.
- Prevention: pin versions and run validation before deploys.

## High Memory Usage
- Symptom: host memory near 100%.
- Diagnosis: Grafana panel "Top memory hosts" or `docker stats`.
- Resolution: increase Prometheus memory limit, reduce retention, tune scrape_interval.
- Prevention: monitor memory alerts; right-size resource limits.

## Prometheus Scrape Failures
- Symptom: `up` metric zero for target.
- Diagnosis: check target reachability (`curl <target>`), review firewall rules, validate DNS.
- Resolution: fix network path, adjust scrape_interval if target overloaded.
- Prevention: keep exporters on backend network; avoid high-cardinality labels.

## Alert Not Firing
- Symptom: expected alert missing.
- Diagnosis: confirm rule loaded in UI, check `prometheus_rule_evaluation_failures_total`.
- Resolution: correct rule expression, reload config (`/-/reload`), verify label selectors.
- Prevention: use `promtool test rules` pattern via validation step.

## Dashboard Not Loading
- Symptom: Grafana errors or blank panels.
- Diagnosis: confirm datasource health, check Grafana logs.
- Resolution: re-run provisioning by restarting Grafana; ensure Prometheus/Loki reachable.
- Prevention: keep provisioning files under version control; avoid UI edits when editable=false.

## Logs Not Appearing
- Symptom: Loki queries empty.
- Diagnosis: check Promtail positions file, ensure `/var/lib/docker/containers` mounted and readable.
- Resolution: restart Promtail, verify `loki:3100/ready`, confirm label filters in queries.
- Prevention: maintain label hygiene; avoid excessive label cardinality.

## Container Restart Loops
- Symptom: container restarting frequently.
- Diagnosis: `docker compose ps` restart count; check `ContainerRestarting` alert.
- Resolution: inspect logs for crash cause; fix config/health checks; increase resources if constrained.
- Prevention: rolling deploys with validation; monitor restart metrics in dashboards.

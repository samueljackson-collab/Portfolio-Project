# Troubleshooting Guide

## Service Won't Start
- Check docker compose logs: `docker compose -f docker-compose.yml logs <service>`.
- Validate configuration syntax with `./scripts/deploy.sh validate`.
- Ensure required ports (9090, 3000, 3100, 9093) are free or adjust mappings.

## High Memory Usage
- Review `HighMemoryUsage` alerts and `host-details` dashboard.
- Inspect top containers via `docker stats`; enforce limits in compose file if missing.
- Consider increasing Prometheus retention prudently or enabling recording rules to reduce query pressure.

## Prometheus Scrape Failures
- Check target status in Prometheus UI `/targets`.
- Confirm exporters reachable on backend network; inspect firewall rules when scraping remote Proxmox hosts.
- Validate certificates if switching to HTTPS endpoints.

## Alert Not Firing
- Ensure Alertmanager is reachable; check `/status` for silences.
- Confirm rule expression using Prometheus expression browser.
- Verify alert severity labels match Alertmanager route expectations.

## Dashboard Not Loading
- Confirm Grafana container health; restart if SQLite/bolt DB locked.
- Validate datasources provisioning in `datasources.yml` and connectivity to Prometheus/Loki.
- Clear browser cache or rotate admin password to re-authenticate.

## Logs Not Appearing
- Verify Promtail is reading correct paths and `positions.yaml` is writable.
- Inspect Loki ingester metrics for rejection due to old timestamps or label cardinality.
- Run sample query `count_over_time({job="varlogs"}[5m])` to ensure streams arrive.

## Container Restart Loops
- `docker inspect` health checks for failing commands.
- Review cAdvisor metrics for CPU/memory pressure causing OOM kills.
- Roll back to previous image or disable strict health check temporarily while debugging.

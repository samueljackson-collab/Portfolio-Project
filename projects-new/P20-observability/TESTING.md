# Testing

Automated commands:
- `make lint-config`
- `make test-rules`
- `python scripts/check_dashboards.py`

Manual validation:
- Verify dashboard queries return expected data from Prometheus
- Check alert rules are properly loaded in Alertmanager
- Confirm Loki is ingesting logs from Promtail
- Validate Grafana datasource connections are healthy
- Test alert notification delivery to configured channels

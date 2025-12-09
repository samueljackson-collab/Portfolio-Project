# Runbooks

- Alert storm: check Alertmanager silences, dedupe noisy rules, adjust thresholds
- Grafana outage: restore from backup via scripts/restore_grafana.py, verify datasource health
- Loki ingestion lag: scale Promtail, tune retention, compact chunks

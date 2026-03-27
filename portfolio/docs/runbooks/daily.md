# Daily Operational Tasks

1. Check Grafana dashboards for error rates and latency anomalies.
2. Review Prometheus alerts or Alertmanager notifications.
3. Verify nightly backup job completion via logs stored in `data/backups`.
4. Run `make test` on the latest `main` branch to catch regressions early.
5. Review CI pipeline runs for failed scans (Bandit, Trivy, tfsec).


# Architecture

Stack: Athena queries, Python reporting, and Grafana dashboards fed by cost-explorer exports.

Data/Control flow: Ingest CUR into S3, run Athena queries to aggregate by tag/account, surface anomalies via dashboards and Slack alerts.

Dependencies:
- Athena queries, Python reporting, and Grafana dashboards fed by cost-explorer exports.
- Env/config: see README for required secrets and endpoints.

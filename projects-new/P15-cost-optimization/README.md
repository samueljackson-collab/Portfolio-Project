# P15 – Cloud Cost Optimization

FinOps toolkit for analyzing CUR data, tagging compliance, and automated recommendations.

## Quick start
- Stack: Athena queries, Python reporting, and Grafana dashboards fed by cost-explorer exports.
- Flow: Ingest CUR into S3, run Athena queries to aggregate by tag/account, surface anomalies via dashboards and Slack alerts.
- Run: make lint then pytest tests/test_queries.py
- Operate: Refresh CUR partitions daily, enforce tag policies with `scripts/tag_audit.py`, and review savings plan coverage weekly.

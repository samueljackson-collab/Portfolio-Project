# Runbooks

- Anomaly alert: confirm spike in Grafana, run scripts/diff_cost_centers.py, notify owner, apply stop controls if needed
- Tag drift: execute scripts/tag_audit.py --fix --dry-run then apply, re-run dashboards
- Athena failure: check data partitions, repair table, clear failed query cache

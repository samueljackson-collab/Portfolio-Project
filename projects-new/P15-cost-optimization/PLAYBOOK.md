# Operations Playbook

- Routine tasks: Refresh CUR partitions daily, enforce tag policies with `scripts/tag_audit.py`, and review savings plan coverage weekly.
- Deployment/rollout: follow CI pipeline then environment-specific promotion steps.
- Validation: ensure flow 'Ingest CUR into S3, run Athena queries to aggregate by tag/account, surface anomalies via dashboards and Slack alerts.' completes in target environment.

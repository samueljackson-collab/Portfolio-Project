# Operations Playbook

- Routine tasks: Refresh scrape targets weekly, rotate Alertmanager receivers tokens, and backup Grafana via API.
- Deployment/rollout: follow CI pipeline then environment-specific promotion steps.
- Validation: ensure flow 'Promtail ships logs, Prometheus scrapes app/infra metrics, dashboards visualize SLOs, Alertmanager routes incidents.' completes in target environment.

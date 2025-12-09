# Operations Playbook

- Routine tasks: Rotate API tokens, schedule canaries hourly, and refresh dashboards with new SLOs each quarter.
- Deployment/rollout: follow CI pipeline then environment-specific promotion steps.
- Validation: ensure flow 'k6 probes hit endpoints, collectors correlate traces/metrics/logs, dashboards show burn rates per region.' completes in target environment.

# Operations Playbook

- Routine tasks: Update control baselines monthly, rotate webhook secrets, and monitor remediation success metrics.
- Deployment/rollout: follow CI pipeline then environment-specific promotion steps.
- Validation: ensure flow 'Scheduler runs scans, pushes findings to Security Hub, and triggers remediation lambdas or SSM automations.' completes in target environment.

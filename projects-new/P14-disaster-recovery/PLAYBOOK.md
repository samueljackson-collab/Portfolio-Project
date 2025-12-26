# Operations Playbook

- Routine tasks: Rotate encryption keys monthly, verify backup completion dashboards, and track RPO/RTO in status sheet.
- Deployment/rollout: follow CI pipeline then environment-specific promotion steps.
- Validation: Run scripts/dr_drill.py --env <target_env> to trigger a disaster recovery drill and validate the restore process.

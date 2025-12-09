# Operations Playbook

- Routine tasks: Rotate encryption keys monthly, verify backup completion dashboards, and track RPO/RTO in status sheet.
- Deployment/rollout: follow CI pipeline then environment-specific promotion steps.
- Validation: ensure flow 'Nightly backups captured, integrity verified, copied to offsite bucket, and periodic drills restore to sandbox and validate checksums.' completes in target environment.

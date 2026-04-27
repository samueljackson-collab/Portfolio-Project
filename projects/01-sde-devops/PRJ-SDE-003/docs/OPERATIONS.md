# Day 2 Operations

- **Patching**: Use SSM Patch Manager and Maintenance Windows bound to the app ASGs.
- **Backups**: RDS automated backups and snapshots; replicate to secondary region per DR plan.
- **Monitoring**: CloudWatch dashboards and alarms for ALB, ASG, RDS, NAT, and WAF metrics.
- **Access**: Prefer SSM Session Manager; bastion SG optional for break-glass scenarios.
- **Change management**: Pull-request reviews and `terraform plan` outputs stored in CI/CD pipeline artifacts.

# Disaster Recovery Plan

## Objectives
- **RPO:** <= 15 minutes using RDS automated backups and binlog replication.
- **RTO:** <= 60 minutes through Terraform-driven redeployments and AMI golden images.

## Strategy
1. **Data Tier**
   - RDS Multi-AZ handles AZ outages automatically.
   - Daily snapshots copied to a secondary region via cross-region snapshot copy policy (configure in AWS console).
2. **Application Tier**
   - Auto Scaling Group spans multiple AZs to survive AZ failures.
   - Store AMIs and user-data templates in version control for quick recreation.
3. **Networking**
   - Terraform state stored in S3 with versioning for infrastructure rehydrate.
   - Route53 failover records (future enhancement) to redirect to DR region.

## Runbook
1. Confirm incident scope and trigger DR bridge.
2. Restore latest RDS snapshot or promote standby if region-wide outage.
3. Execute `deploy.sh` pointing to DR region variables; override `aws_region` and AZ list.
4. Update Route53 weights to direct traffic to DR ALB.
5. Validate application smoke tests and inform stakeholders.

## Testing
- Schedule semi-annual game days to rehearse cross-region restoration.
- Document lessons learned and feed improvements back into Terraform modules.

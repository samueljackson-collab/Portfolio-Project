# Disaster Recovery

- **Backups**: Automated RDS snapshots with cross-region copy; S3 versioning and replication for static assets.
- **Infrastructure**: Terraform code is region-agnostic; set the desired region in environment variables and re-run apply in the DR region.
- **Database**: Promote a read replica or restore from snapshot; update Route53 records after failover.
- **Verification**: Run periodic game days validating restore time objectives and DNS failover.

# Standard Operating Procedures — P10

## Daily Tasks
- Check Route 53 health check status for both regions.
- Validate replication lag metrics <10s.
- Confirm backup jobs succeeded in both regions.

## Change Management
- All Terraform changes require plans for primary and secondary with peer review.
- DNS changes must be accompanied by rollback plan and communication template.

## Data Protection
- KMS keys rotated annually per region.
- Ensure S3 buckets enforce TLS and block public access.

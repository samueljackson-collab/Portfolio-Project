# Code Prompts

## Terraform Module Enhancements
- Add Config/GuardDuty outputs and wiring for existing `infra/vpc-rds.yaml` stack.
- Introduce Terraform module variables for ALB access logs bucket, WAF ACL ID, and RDS performance insights toggle.
- Ensure state backend references `terraform/backend.hcl` with DynamoDB table for locking.

### Prompt
"""
Update Terraform modules to expose outputs for AWS Config recorder ARN, GuardDuty detector ID, and S3 access logs bucket. Wire outputs into CloudFormation stack parameters for VPC/RDS. Enforce state backend stored in S3 with DynamoDB locking and add pre-commit hooks for `terraform fmt` and `terraform validate`.
"""

## CloudFormation Adjustments
- Parameterize subnet CIDRs and DB instance class for DR drill flexibility.
- Add SNS notification topics for backup failures and DR drill status.

### Prompt
"""
Modify `infra/vpc-rds.yaml` to accept CIDR and DB instance class parameters, create SNS topics for backup failures and DR drill status, and publish stack outputs for topic ARNs. Ensure resources are tagged with `Project=P01` and `Environment` variables.
"""

## Automation Scripts
- Extend `scripts/dr-drill.sh` to capture Route53 failover metrics and upload to S3 evidence bucket.

### Prompt
"""
Enhance `scripts/dr-drill.sh` to run Route53 health checks pre/post failover, record latency metrics, push JSON results to `evidence/` in S3, and exit non-zero on threshold breaches.
"""

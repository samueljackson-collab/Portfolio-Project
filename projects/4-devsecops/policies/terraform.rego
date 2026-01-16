# Terraform Security Policies
#
# This Rego policy file defines security rules for Terraform configurations.
# It enforces cloud security best practices for AWS, GCP, and Azure resources.
#
# Usage:
#   opa eval --data policies/terraform.rego --input plan.json "data.terraform"
#   conftest test --policy policies/ tfplan.json
#
# Policy Categories:
#   1. Encryption at Rest - S3, RDS, EBS, etc.
#   2. Encryption in Transit - HTTPS, TLS
#   3. Network Security - Security groups, NACLs
#   4. IAM Security - Policies, roles, users
#   5. Logging and Monitoring - CloudTrail, CloudWatch
#   6. Storage Security - Public access, versioning

package terraform

import future.keywords.in
import future.keywords.contains
import future.keywords.if

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# Get resources from Terraform plan
resources := input.resource_changes

# Get planned values for a resource
get_planned_values(resource) := resource.change.after

# Check resource type
is_resource_type(resource, type) {
    resource.type == type
}

# ============================================================================
# AWS S3 BUCKET SECURITY
# ============================================================================

# RULE: S3 Buckets must have encryption enabled
deny contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_s3_bucket")
    values := get_planned_values(resource)
    not values.server_side_encryption_configuration
    msg := sprintf("CRITICAL: S3 bucket '%s' must have server-side encryption enabled. Add server_side_encryption_configuration block.", [resource.address])
}

# RULE: S3 Buckets must block public access
deny contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_s3_bucket_public_access_block")
    values := get_planned_values(resource)
    values.block_public_acls != true
    msg := sprintf("CRITICAL: S3 bucket '%s' must block public ACLs. Set block_public_acls = true.", [resource.address])
}

deny contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_s3_bucket_public_access_block")
    values := get_planned_values(resource)
    values.block_public_policy != true
    msg := sprintf("CRITICAL: S3 bucket '%s' must block public policies. Set block_public_policy = true.", [resource.address])
}

deny contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_s3_bucket_public_access_block")
    values := get_planned_values(resource)
    values.ignore_public_acls != true
    msg := sprintf("HIGH: S3 bucket '%s' should ignore public ACLs. Set ignore_public_acls = true.", [resource.address])
}

deny contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_s3_bucket_public_access_block")
    values := get_planned_values(resource)
    values.restrict_public_buckets != true
    msg := sprintf("HIGH: S3 bucket '%s' should restrict public buckets. Set restrict_public_buckets = true.", [resource.address])
}

# RULE: S3 Buckets should have versioning enabled
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_s3_bucket_versioning")
    values := get_planned_values(resource)
    values.versioning_configuration.status != "Enabled"
    msg := sprintf("MEDIUM: S3 bucket '%s' should have versioning enabled for data protection.", [resource.address])
}

# RULE: S3 Buckets should have logging enabled
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_s3_bucket")
    values := get_planned_values(resource)
    not values.logging
    msg := sprintf("MEDIUM: S3 bucket '%s' should have access logging enabled.", [resource.address])
}

# ============================================================================
# AWS RDS SECURITY
# ============================================================================

# RULE: RDS instances must have encryption enabled
deny contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_db_instance")
    values := get_planned_values(resource)
    values.storage_encrypted != true
    msg := sprintf("CRITICAL: RDS instance '%s' must have storage encryption enabled. Set storage_encrypted = true.", [resource.address])
}

# RULE: RDS instances must not be publicly accessible
deny contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_db_instance")
    values := get_planned_values(resource)
    values.publicly_accessible == true
    msg := sprintf("CRITICAL: RDS instance '%s' must not be publicly accessible. Set publicly_accessible = false.", [resource.address])
}

# RULE: RDS instances should have backup retention
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_db_instance")
    values := get_planned_values(resource)
    values.backup_retention_period < 7
    msg := sprintf("MEDIUM: RDS instance '%s' should have backup retention of at least 7 days. Current: %d days.", [resource.address, values.backup_retention_period])
}

# RULE: RDS instances should have deletion protection
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_db_instance")
    values := get_planned_values(resource)
    values.deletion_protection != true
    msg := sprintf("MEDIUM: RDS instance '%s' should have deletion protection enabled.", [resource.address])
}

# RULE: RDS instances should have multi-AZ for production
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_db_instance")
    values := get_planned_values(resource)
    values.multi_az != true
    msg := sprintf("LOW: RDS instance '%s' should consider multi-AZ deployment for high availability.", [resource.address])
}

# RULE: RDS instances should use latest engine versions
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_db_instance")
    values := get_planned_values(resource)
    contains(values.engine, "mysql")
    not startswith(values.engine_version, "8.")
    msg := sprintf("LOW: RDS instance '%s' should use MySQL 8.x for security updates.", [resource.address])
}

# ============================================================================
# AWS EC2/EBS SECURITY
# ============================================================================

# RULE: EBS volumes must be encrypted
deny contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_ebs_volume")
    values := get_planned_values(resource)
    values.encrypted != true
    msg := sprintf("CRITICAL: EBS volume '%s' must be encrypted. Set encrypted = true.", [resource.address])
}

# RULE: EC2 instances should use IMDSv2
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_instance")
    values := get_planned_values(resource)
    not values.metadata_options
    msg := sprintf("HIGH: EC2 instance '%s' should configure metadata_options to require IMDSv2.", [resource.address])
}

warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_instance")
    values := get_planned_values(resource)
    values.metadata_options.http_tokens != "required"
    msg := sprintf("HIGH: EC2 instance '%s' should require IMDSv2. Set http_tokens = \"required\".", [resource.address])
}

# RULE: EC2 instances should not have public IPs in private subnets
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_instance")
    values := get_planned_values(resource)
    values.associate_public_ip_address == true
    msg := sprintf("MEDIUM: EC2 instance '%s' has public IP. Ensure this is intentional and properly secured.", [resource.address])
}

# ============================================================================
# AWS SECURITY GROUPS
# ============================================================================

# RULE: Security groups must not allow unrestricted ingress (0.0.0.0/0)
deny contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_security_group_rule")
    values := get_planned_values(resource)
    values.type == "ingress"
    values.cidr_blocks[_] == "0.0.0.0/0"
    values.from_port == 22
    msg := sprintf("CRITICAL: Security group rule '%s' allows SSH (22) from 0.0.0.0/0. Restrict to specific IPs.", [resource.address])
}

deny contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_security_group_rule")
    values := get_planned_values(resource)
    values.type == "ingress"
    values.cidr_blocks[_] == "0.0.0.0/0"
    values.from_port == 3389
    msg := sprintf("CRITICAL: Security group rule '%s' allows RDP (3389) from 0.0.0.0/0. Restrict to specific IPs.", [resource.address])
}

deny contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_security_group_rule")
    values := get_planned_values(resource)
    values.type == "ingress"
    values.cidr_blocks[_] == "0.0.0.0/0"
    values.from_port == 0
    values.to_port == 65535
    msg := sprintf("CRITICAL: Security group rule '%s' allows all ports from 0.0.0.0/0. This is extremely dangerous.", [resource.address])
}

# RULE: Security groups should have descriptions
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_security_group")
    values := get_planned_values(resource)
    values.description == ""
    msg := sprintf("LOW: Security group '%s' should have a description.", [resource.address])
}

warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_security_group")
    values := get_planned_values(resource)
    values.description == "Managed by Terraform"
    msg := sprintf("LOW: Security group '%s' should have a meaningful description.", [resource.address])
}

# ============================================================================
# AWS IAM SECURITY
# ============================================================================

# RULE: IAM policies should not use wildcard actions
deny contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_iam_policy")
    values := get_planned_values(resource)
    contains(values.policy, "\"Action\": \"*\"")
    msg := sprintf("CRITICAL: IAM policy '%s' uses wildcard (*) actions. Follow least privilege principle.", [resource.address])
}

deny contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_iam_role_policy")
    values := get_planned_values(resource)
    contains(values.policy, "\"Action\": \"*\"")
    msg := sprintf("CRITICAL: IAM role policy '%s' uses wildcard (*) actions. Follow least privilege principle.", [resource.address])
}

# RULE: IAM policies should not use wildcard resources
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_iam_policy")
    values := get_planned_values(resource)
    contains(values.policy, "\"Resource\": \"*\"")
    msg := sprintf("HIGH: IAM policy '%s' uses wildcard (*) resources. Scope down to specific resources.", [resource.address])
}

# RULE: IAM users should not have inline policies
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_iam_user_policy")
    msg := sprintf("MEDIUM: IAM user policy '%s' uses inline policy. Prefer managed policies attached to groups.", [resource.address])
}

# RULE: IAM users should not have direct policy attachments
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_iam_user_policy_attachment")
    msg := sprintf("MEDIUM: IAM user '%s' has direct policy attachment. Prefer attaching policies to groups.", [resource.address])
}

# ============================================================================
# AWS CLOUDTRAIL AND LOGGING
# ============================================================================

# RULE: CloudTrail should be enabled
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_cloudtrail")
    values := get_planned_values(resource)
    values.enable_logging != true
    msg := sprintf("HIGH: CloudTrail '%s' should have logging enabled.", [resource.address])
}

# RULE: CloudTrail should have log file validation
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_cloudtrail")
    values := get_planned_values(resource)
    values.enable_log_file_validation != true
    msg := sprintf("MEDIUM: CloudTrail '%s' should enable log file validation for integrity.", [resource.address])
}

# RULE: CloudTrail should be multi-region
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_cloudtrail")
    values := get_planned_values(resource)
    values.is_multi_region_trail != true
    msg := sprintf("MEDIUM: CloudTrail '%s' should be multi-region for complete coverage.", [resource.address])
}

# RULE: CloudTrail logs should be encrypted
deny contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_cloudtrail")
    values := get_planned_values(resource)
    not values.kms_key_id
    msg := sprintf("HIGH: CloudTrail '%s' should encrypt logs with KMS.", [resource.address])
}

# ============================================================================
# AWS KMS SECURITY
# ============================================================================

# RULE: KMS keys should have rotation enabled
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_kms_key")
    values := get_planned_values(resource)
    values.enable_key_rotation != true
    msg := sprintf("MEDIUM: KMS key '%s' should have automatic key rotation enabled.", [resource.address])
}

# RULE: KMS keys should have deletion window
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_kms_key")
    values := get_planned_values(resource)
    values.deletion_window_in_days < 7
    msg := sprintf("LOW: KMS key '%s' deletion window should be at least 7 days.", [resource.address])
}

# ============================================================================
# AWS LAMBDA SECURITY
# ============================================================================

# RULE: Lambda functions should have tracing enabled
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_lambda_function")
    values := get_planned_values(resource)
    not values.tracing_config
    msg := sprintf("LOW: Lambda function '%s' should have X-Ray tracing enabled.", [resource.address])
}

# RULE: Lambda functions should use VPC when accessing private resources
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_lambda_function")
    values := get_planned_values(resource)
    not values.vpc_config
    msg := sprintf("LOW: Lambda function '%s' should consider VPC configuration if accessing private resources.", [resource.address])
}

# ============================================================================
# AWS ELASTICACHE SECURITY
# ============================================================================

# RULE: ElastiCache should have encryption at rest
deny contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_elasticache_replication_group")
    values := get_planned_values(resource)
    values.at_rest_encryption_enabled != true
    msg := sprintf("HIGH: ElastiCache '%s' should have encryption at rest enabled.", [resource.address])
}

# RULE: ElastiCache should have encryption in transit
deny contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_elasticache_replication_group")
    values := get_planned_values(resource)
    values.transit_encryption_enabled != true
    msg := sprintf("HIGH: ElastiCache '%s' should have encryption in transit enabled.", [resource.address])
}

# ============================================================================
# AWS ALB/ELB SECURITY
# ============================================================================

# RULE: Load balancers should drop invalid headers
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_lb")
    values := get_planned_values(resource)
    values.drop_invalid_header_fields != true
    msg := sprintf("MEDIUM: ALB '%s' should drop invalid header fields.", [resource.address])
}

# RULE: Load balancers should have access logs enabled
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_lb")
    values := get_planned_values(resource)
    not values.access_logs
    msg := sprintf("MEDIUM: ALB '%s' should have access logging enabled.", [resource.address])
}

# RULE: HTTPS listeners should use TLS 1.2+
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_lb_listener")
    values := get_planned_values(resource)
    values.protocol == "HTTPS"
    not contains(values.ssl_policy, "TLS12")
    not contains(values.ssl_policy, "TLS13")
    msg := sprintf("HIGH: ALB listener '%s' should use TLS 1.2 or higher.", [resource.address])
}

# ============================================================================
# AWS SNS SECURITY
# ============================================================================

# RULE: SNS topics should be encrypted
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_sns_topic")
    values := get_planned_values(resource)
    not values.kms_master_key_id
    msg := sprintf("MEDIUM: SNS topic '%s' should be encrypted with KMS.", [resource.address])
}

# ============================================================================
# AWS SQS SECURITY
# ============================================================================

# RULE: SQS queues should be encrypted
warn contains msg if {
    some resource in resources
    is_resource_type(resource, "aws_sqs_queue")
    values := get_planned_values(resource)
    not values.kms_master_key_id
    msg := sprintf("MEDIUM: SQS queue '%s' should be encrypted with KMS.", [resource.address])
}

# ============================================================================
# GENERAL TERRAFORM SECURITY
# ============================================================================

# RULE: Resources should have tags
warn contains msg if {
    some resource in resources
    values := get_planned_values(resource)
    not values.tags
    resource.type in {"aws_instance", "aws_db_instance", "aws_s3_bucket", "aws_lb"}
    msg := sprintf("LOW: Resource '%s' should have tags for organization and cost tracking.", [resource.address])
}

# RULE: Check for hardcoded secrets in variables
deny contains msg if {
    some resource in resources
    values := get_planned_values(resource)
    some key, value in values
    contains(lower(key), "password")
    value != null
    not contains(value, "var.")
    not contains(value, "data.")
    msg := sprintf("CRITICAL: Resource '%s' may have hardcoded password in '%s'. Use variables or secrets manager.", [resource.address, key])
}

# ============================================================================
# SUMMARY
# ============================================================================

critical_count := count([msg | some msg in deny; contains(msg, "CRITICAL")])
high_count := count([msg | some msg in deny; contains(msg, "HIGH")])
medium_count := count([msg | some msg in warn; contains(msg, "MEDIUM")])
low_count := count([msg | some msg in warn; contains(msg, "LOW")])

passed := count(deny) == 0

# Terraform Security Policies using Open Policy Agent (OPA)
# These policies enforce security best practices for AWS infrastructure

package terraform.security

import future.keywords.in

# ============================================
# S3 Bucket Security
# ============================================

# Deny S3 buckets without encryption
deny[msg] {
    resource := input.resource.aws_s3_bucket[name]
    not has_encryption(name)
    msg := sprintf("S3 bucket '%v' must have server-side encryption enabled", [name])
}

has_encryption(bucket_name) {
    input.resource.aws_s3_bucket_server_side_encryption_configuration[_].bucket == bucket_name
}

has_encryption(bucket_name) {
    enc := input.resource.aws_s3_bucket[bucket_name].server_side_encryption_configuration
    enc != null
}

# Deny S3 buckets without versioning
deny[msg] {
    resource := input.resource.aws_s3_bucket[name]
    not has_versioning(name)
    msg := sprintf("S3 bucket '%v' must have versioning enabled", [name])
}

has_versioning(bucket_name) {
    ver := input.resource.aws_s3_bucket_versioning[_]
    ver.bucket == bucket_name
    ver.versioning_configuration.status == "Enabled"
}

# Deny public S3 buckets
deny[msg] {
    resource := input.resource.aws_s3_bucket[name]
    not has_public_access_block(name)
    msg := sprintf("S3 bucket '%v' must have public access block enabled", [name])
}

has_public_access_block(bucket_name) {
    block := input.resource.aws_s3_bucket_public_access_block[_]
    block.bucket == bucket_name
    block.block_public_acls == true
    block.block_public_policy == true
    block.ignore_public_acls == true
    block.restrict_public_buckets == true
}

# ============================================
# RDS Security
# ============================================

# Deny RDS without encryption
deny[msg] {
    resource := input.resource.aws_db_instance[name]
    not resource.storage_encrypted
    msg := sprintf("RDS instance '%v' must have storage encryption enabled", [name])
}

# Deny publicly accessible RDS
deny[msg] {
    resource := input.resource.aws_db_instance[name]
    resource.publicly_accessible
    msg := sprintf("RDS instance '%v' must not be publicly accessible", [name])
}

# Deny RDS without deletion protection in production
deny[msg] {
    resource := input.resource.aws_db_instance[name]
    contains(name, "prod")
    not resource.deletion_protection
    msg := sprintf("Production RDS instance '%v' must have deletion protection enabled", [name])
}

# Deny RDS without backup retention
deny[msg] {
    resource := input.resource.aws_db_instance[name]
    resource.backup_retention_period < 7
    msg := sprintf("RDS instance '%v' must have backup retention of at least 7 days", [name])
}

# ============================================
# Security Group Rules
# ============================================

# Deny security groups with unrestricted SSH access
deny[msg] {
    resource := input.resource.aws_security_group[name]
    ingress := resource.ingress[_]
    ingress.from_port <= 22
    ingress.to_port >= 22
    cidr := ingress.cidr_blocks[_]
    cidr == "0.0.0.0/0"
    msg := sprintf("Security group '%v' must not allow SSH (port 22) from 0.0.0.0/0", [name])
}

# Deny security groups with unrestricted RDP access
deny[msg] {
    resource := input.resource.aws_security_group[name]
    ingress := resource.ingress[_]
    ingress.from_port <= 3389
    ingress.to_port >= 3389
    cidr := ingress.cidr_blocks[_]
    cidr == "0.0.0.0/0"
    msg := sprintf("Security group '%v' must not allow RDP (port 3389) from 0.0.0.0/0", [name])
}

# Deny overly permissive security group rules
deny[msg] {
    resource := input.resource.aws_security_group[name]
    ingress := resource.ingress[_]
    ingress.from_port == 0
    ingress.to_port == 65535
    cidr := ingress.cidr_blocks[_]
    cidr == "0.0.0.0/0"
    msg := sprintf("Security group '%v' must not allow all ports from 0.0.0.0/0", [name])
}

# ============================================
# EKS Security
# ============================================

# Deny EKS clusters without encryption
deny[msg] {
    resource := input.resource.aws_eks_cluster[name]
    not resource.encryption_config
    msg := sprintf("EKS cluster '%v' must have encryption enabled for secrets", [name])
}

# Deny EKS clusters with public endpoint access
deny[msg] {
    resource := input.resource.aws_eks_cluster[name]
    resource.vpc_config.endpoint_public_access
    not resource.vpc_config.public_access_cidrs
    msg := sprintf("EKS cluster '%v' with public endpoint must restrict access via CIDRs", [name])
}

# ============================================
# IAM Security
# ============================================

# Deny IAM policies with * actions
deny[msg] {
    resource := input.resource.aws_iam_policy[name]
    policy := json.unmarshal(resource.policy)
    statement := policy.Statement[_]
    statement.Effect == "Allow"
    statement.Action[_] == "*"
    msg := sprintf("IAM policy '%v' must not allow Action: '*'", [name])
}

# Deny IAM policies with * resources
deny[msg] {
    resource := input.resource.aws_iam_policy[name]
    policy := json.unmarshal(resource.policy)
    statement := policy.Statement[_]
    statement.Effect == "Allow"
    statement.Resource == "*"
    msg := sprintf("IAM policy '%v' must not allow Resource: '*' for all actions", [name])
}

# ============================================
# EC2 Security
# ============================================

# Deny EC2 instances without IMDSv2
deny[msg] {
    resource := input.resource.aws_instance[name]
    not resource.metadata_options.http_tokens == "required"
    msg := sprintf("EC2 instance '%v' must require IMDSv2 (http_tokens = required)", [name])
}

# Deny unencrypted EBS volumes
deny[msg] {
    resource := input.resource.aws_ebs_volume[name]
    not resource.encrypted
    msg := sprintf("EBS volume '%v' must be encrypted", [name])
}

# ============================================
# CloudTrail
# ============================================

# Deny CloudTrail without encryption
deny[msg] {
    resource := input.resource.aws_cloudtrail[name]
    not resource.kms_key_id
    msg := sprintf("CloudTrail '%v' must be encrypted with KMS", [name])
}

# Deny CloudTrail without log validation
deny[msg] {
    resource := input.resource.aws_cloudtrail[name]
    not resource.enable_log_file_validation
    msg := sprintf("CloudTrail '%v' must have log file validation enabled", [name])
}

# ============================================
# VPC
# ============================================

# Deny VPCs without flow logs
deny[msg] {
    resource := input.resource.aws_vpc[name]
    not has_flow_logs(name)
    msg := sprintf("VPC '%v' must have flow logs enabled", [name])
}

has_flow_logs(vpc_name) {
    flow_log := input.resource.aws_flow_log[_]
    flow_log.vpc_id == vpc_name
}

# ============================================
# Tags
# ============================================

required_tags := ["Environment", "Owner", "Project"]

# Require standard tags on all resources
deny[msg] {
    resource_type := ["aws_instance", "aws_s3_bucket", "aws_db_instance", "aws_eks_cluster"][_]
    resource := input.resource[resource_type][name]
    tag := required_tags[_]
    not resource.tags[tag]
    msg := sprintf("%v '%v' must have tag '%v'", [resource_type, name, tag])
}

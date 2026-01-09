# Security Module

## Overview

This module creates security resources including IAM roles and policies, KMS keys for encryption, WAF Web ACL for application protection, Secrets Manager integration, and security groups.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Security Resources                                │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         IAM Roles                                     │  │
│  │                                                                       │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐          │  │
│  │  │  CI/CD Role    │  │  Application   │  │  Monitoring    │          │  │
│  │  │  (GitHub OIDC) │  │  Instance Role │  │  Role          │          │  │
│  │  └───────┬────────┘  └───────┬────────┘  └────────────────┘          │  │
│  │          │                   │                                        │  │
│  │          ▼                   ▼                                        │  │
│  │  ┌────────────────────────────────────────┐                          │  │
│  │  │ Policies: S3, RDS, EC2, CloudWatch,    │                          │  │
│  │  │           SSM, Secrets Manager          │                          │  │
│  │  └────────────────────────────────────────┘                          │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         Encryption                                    │  │
│  │                                                                       │  │
│  │  ┌────────────────┐     ┌────────────────┐                           │  │
│  │  │  KMS Key       │────►│  Key Policy    │                           │  │
│  │  │  (Multi-region)│     │  (CloudWatch,  │                           │  │
│  │  └────────────────┘     │   SNS, S3)     │                           │  │
│  │                         └────────────────┘                           │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         WAF Web ACL                                   │  │
│  │                                                                       │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐          │  │
│  │  │ Common Rules   │  │ SQLi Rules     │  │ Rate Limiting  │          │  │
│  │  │ (OWASP)        │  │                │  │ (2000/5min)    │          │  │
│  │  └────────────────┘  └────────────────┘  └────────────────┘          │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      Secrets Manager                                  │  │
│  │                                                                       │  │
│  │  ┌────────────────────────────────────────────────────────┐          │  │
│  │  │ Database Credentials (username, password, host, port)  │          │  │
│  │  └────────────────────────────────────────────────────────┘          │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Features

- **KMS Keys**: Customer-managed keys with automatic rotation
- **IAM Roles**: Least-privilege roles for CI/CD and applications
- **GitHub OIDC**: Secure CI/CD authentication without long-lived credentials
- **WAF Web ACL**: AWS Managed Rules for OWASP Top 10 protection
- **Secrets Manager**: Secure storage for database credentials
- **Security Groups**: Network-level access controls

## Input Variables

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| `name_prefix` | Prefix for resource names | `string` | - | Yes |
| `vpc_id` | ID of the VPC for security groups | `string` | `""` | No |
| `create_kms_key` | Create a KMS key | `bool` | `true` | No |
| `kms_deletion_window_days` | KMS key deletion window | `number` | `7` | No |
| `kms_multi_region` | Create multi-region KMS key | `bool` | `false` | No |
| `create_cicd_role` | Create CI/CD IAM role | `bool` | `false` | No |
| `oidc_provider_arn` | GitHub OIDC provider ARN | `string` | `""` | No |
| `github_repo_pattern` | GitHub repo pattern for OIDC | `string` | `"repo:*/*:*"` | No |
| `terraform_state_bucket` | S3 bucket for Terraform state | `string` | `""` | No |
| `terraform_lock_table` | DynamoDB table for state locking | `string` | `""` | No |
| `create_application_role` | Create application IAM role | `bool` | `true` | No |
| `secrets_arns` | Secrets Manager ARNs for app access | `list(string)` | `[]` | No |
| `create_db_secret` | Create database credentials secret | `bool` | `false` | No |
| `create_waf_acl` | Create WAF Web ACL | `bool` | `false` | No |
| `waf_scope` | WAF scope (REGIONAL/CLOUDFRONT) | `string` | `"REGIONAL"` | No |
| `waf_rate_limit` | Rate limit per 5 minutes | `number` | `2000` | No |
| `tags` | Tags to apply to resources | `map(string)` | `{}` | No |

## Outputs

| Name | Description |
|------|-------------|
| `kms_key_id` | The ID of the KMS key |
| `kms_key_arn` | The ARN of the KMS key |
| `cicd_role_arn` | The ARN of the CI/CD IAM role |
| `application_role_arn` | The ARN of the application IAM role |
| `application_instance_profile_arn` | The ARN of the instance profile |
| `db_secret_arn` | The ARN of the database secret |
| `waf_acl_id` | The ID of the WAF Web ACL |
| `waf_acl_arn` | The ARN of the WAF Web ACL |
| `bastion_security_group_id` | The ID of the bastion security group |

## Example Usage

### Basic Security Resources

```hcl
module "security" {
  source = "./modules/security"

  name_prefix = "myapp-dev"

  create_kms_key          = true
  create_application_role = true

  tags = {
    Environment = "dev"
    Project     = "myapp"
  }
}
```

### CI/CD with GitHub Actions

```hcl
# First, create the OIDC provider
resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

module "security" {
  source = "./modules/security"

  name_prefix = "myapp-prod"

  create_cicd_role       = true
  oidc_provider_arn      = aws_iam_openid_connect_provider.github.arn
  github_repo_pattern    = "repo:myorg/myrepo:*"
  terraform_state_bucket = "myapp-terraform-state"
  terraform_lock_table   = "myapp-terraform-locks"

  tags = {
    Environment = "production"
  }
}
```

### Database Credentials in Secrets Manager

```hcl
module "security" {
  source = "./modules/security"

  name_prefix = "myapp-prod"

  create_db_secret = true
  db_username      = "admin"
  db_password      = var.db_password  # From tfvars or secrets
  db_host          = module.database.db_instance_address
  db_port          = 5432
  db_name          = "myapp"

  tags = {
    Environment = "production"
  }
}
```

### WAF Protection

```hcl
module "security" {
  source = "./modules/security"

  name_prefix = "myapp-prod"

  create_waf_acl  = true
  waf_scope       = "REGIONAL"  # For ALB
  waf_rate_limit  = 1000

  tags = {
    Environment = "production"
  }
}

# Associate WAF with ALB
resource "aws_wafv2_web_acl_association" "alb" {
  resource_arn = module.compute.alb_arn
  web_acl_arn  = module.security.waf_acl_arn
}
```

### Complete Production Setup

```hcl
module "security" {
  source = "./modules/security"

  name_prefix = "myapp-prod"
  vpc_id      = module.networking.vpc_id

  # KMS
  create_kms_key     = true
  kms_multi_region   = true

  # CI/CD
  create_cicd_role       = true
  oidc_provider_arn      = aws_iam_openid_connect_provider.github.arn
  github_repo_pattern    = "repo:myorg/myrepo:ref:refs/heads/main"
  terraform_state_bucket = "myapp-terraform-state"
  terraform_lock_table   = "myapp-terraform-locks"

  # Application
  create_application_role = true
  secrets_arns = [
    module.security.db_secret_arn,
    "arn:aws:secretsmanager:us-west-2:123456789012:secret:api-keys-*"
  ]

  # Database credentials
  create_db_secret = true
  db_username      = "admin"
  db_password      = var.db_password
  db_host          = module.database.db_instance_address
  db_port          = 5432
  db_name          = "myapp"

  # WAF
  create_waf_acl = true
  waf_scope      = "REGIONAL"
  waf_rate_limit = 2000

  # Bastion
  create_bastion_sg     = true
  bastion_allowed_cidrs = ["10.0.0.0/8"]

  tags = {
    Environment = "production"
  }
}
```

## WAF Managed Rules

The WAF Web ACL includes these AWS Managed Rule Groups:

| Rule Group | Description |
|------------|-------------|
| AWSManagedRulesCommonRuleSet | OWASP Top 10 vulnerabilities |
| AWSManagedRulesKnownBadInputsRuleSet | Known bad inputs and patterns |
| AWSManagedRulesSQLiRuleSet | SQL injection protection |
| Rate-based rule | IP-based rate limiting |

## Important Notes

1. **KMS Key Rotation**: Automatic key rotation is enabled by default.

2. **GitHub OIDC**: More secure than long-lived access keys. Limit `github_repo_pattern` to specific repos/branches.

3. **WAF Scope**: Use `REGIONAL` for ALB/API Gateway, `CLOUDFRONT` for CloudFront distributions.

4. **Secrets Rotation**: Consider implementing automatic rotation for database credentials.

5. **Instance Profiles**: Application role includes SSM access for Session Manager.

## Security Best Practices

- Use separate KMS keys for different data classifications
- Implement least-privilege IAM policies
- Enable CloudTrail for API auditing
- Regularly rotate credentials in Secrets Manager
- Review WAF rules and adjust rate limits based on traffic patterns
- Use VPC endpoints to avoid internet traffic for AWS services

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.4 |
| aws | ~> 5.0 |

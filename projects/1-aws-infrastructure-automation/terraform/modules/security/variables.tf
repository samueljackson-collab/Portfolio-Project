###############################################################################
# Security Module - Input Variables
###############################################################################

variable "name_prefix" {
  description = "Prefix for resource names (e.g., 'portfolio-dev')."
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC for security groups."
  type        = string
  default     = ""
}

#------------------------------------------------------------------------------
# KMS Configuration
#------------------------------------------------------------------------------

variable "create_kms_key" {
  description = "Create a KMS key for encryption."
  type        = bool
  default     = true
}

variable "kms_deletion_window_days" {
  description = "Days before KMS key deletion."
  type        = number
  default     = 7
}

variable "kms_multi_region" {
  description = "Create a multi-region KMS key."
  type        = bool
  default     = false
}

variable "kms_key_arn" {
  description = "Existing KMS key ARN (if not creating new)."
  type        = string
  default     = ""
}

#------------------------------------------------------------------------------
# CI/CD Role Configuration
#------------------------------------------------------------------------------

variable "create_cicd_role" {
  description = "Create an IAM role for CI/CD pipelines."
  type        = bool
  default     = false
}

variable "oidc_provider_arn" {
  description = "ARN of the OIDC provider for GitHub Actions."
  type        = string
  default     = ""
}

variable "oidc_provider_url" {
  description = "URL of the OIDC provider (without https://)."
  type        = string
  default     = "token.actions.githubusercontent.com"
}

variable "github_repo_pattern" {
  description = "GitHub repository pattern for OIDC trust."
  type        = string
  default     = "repo:*/*:*"
}

variable "terraform_state_bucket" {
  description = "S3 bucket name for Terraform state."
  type        = string
  default     = ""
}

variable "terraform_lock_table" {
  description = "DynamoDB table name for Terraform locks."
  type        = string
  default     = ""
}

#------------------------------------------------------------------------------
# Application Role Configuration
#------------------------------------------------------------------------------

variable "create_application_role" {
  description = "Create an IAM role for application instances."
  type        = bool
  default     = true
}

variable "secrets_arns" {
  description = "List of Secrets Manager ARNs the application can access."
  type        = list(string)
  default     = []
}

#------------------------------------------------------------------------------
# Secrets Manager Configuration
#------------------------------------------------------------------------------

variable "create_db_secret" {
  description = "Create a Secrets Manager secret for database credentials."
  type        = bool
  default     = false
}

variable "db_username" {
  description = "Database username for the secret."
  type        = string
  default     = ""
}

variable "db_password" {
  description = "Database password for the secret."
  type        = string
  default     = ""
  sensitive   = true
}

variable "db_host" {
  description = "Database host for the secret."
  type        = string
  default     = ""
}

variable "db_port" {
  description = "Database port for the secret."
  type        = number
  default     = 5432
}

variable "db_name" {
  description = "Database name for the secret."
  type        = string
  default     = ""
}

#------------------------------------------------------------------------------
# WAF Configuration
#------------------------------------------------------------------------------

variable "create_waf_acl" {
  description = "Create a WAF Web ACL."
  type        = bool
  default     = false
}

variable "waf_scope" {
  description = "WAF scope (REGIONAL for ALB, CLOUDFRONT for CloudFront)."
  type        = string
  default     = "REGIONAL"
}

variable "waf_rate_limit" {
  description = "Rate limit for WAF rate-based rule (requests per 5 min)."
  type        = number
  default     = 2000
}

#------------------------------------------------------------------------------
# Bastion Security Group
#------------------------------------------------------------------------------

variable "create_bastion_sg" {
  description = "Create a security group for bastion hosts."
  type        = bool
  default     = false
}

variable "bastion_allowed_cidrs" {
  description = "CIDR blocks allowed to SSH to bastion."
  type        = list(string)
  default     = []
}

#------------------------------------------------------------------------------
# Tags
#------------------------------------------------------------------------------

variable "tags" {
  description = "Tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "aws_region" {
  description = "AWS region for the SSO/Identity Center provider"
  type        = string
  default     = "us-east-1"
}

variable "management_account_id" {
  description = "AWS account ID of the management (root) account"
  type        = string
}

variable "security_audit_account_id" {
  description = "AWS account ID of the security-audit account"
  type        = string
}

variable "log_archive_account_id" {
  description = "AWS account ID of the log-archive account"
  type        = string
}

variable "shared_services_account_id" {
  description = "AWS account ID of the shared-services account"
  type        = string
}

variable "sandbox_dev_account_id" {
  description = "AWS account ID of the sandbox-dev account"
  type        = string
}

variable "platform_team_group_id" {
  description = "Identity Center group ID for the platform/cloud engineering team"
  type        = string
}

variable "devops_team_group_id" {
  description = "Identity Center group ID for the DevOps/application team"
  type        = string
}

variable "security_team_group_id" {
  description = "Identity Center group ID for the security team"
  type        = string
}

variable "auditor_group_id" {
  description = "Identity Center group ID for external auditors (read-only)"
  type        = string
}

variable "aws_region" {
  description = "AWS region for the management account provider"
  type        = string
  default     = "us-east-1"
}

variable "email_domain" {
  description = "Email domain used to generate member account email addresses"
  type        = string
  default     = "example.com"
}

variable "account_names" {
  description = "Display names for each member account"
  type = object({
    security_audit  = string
    log_archive     = string
    shared_services = string
    sandbox_dev     = string
  })
  default = {
    security_audit  = "security-audit"
    log_archive     = "log-archive"
    shared_services = "shared-services"
    sandbox_dev     = "sandbox-dev"
  }
}

variable "organization_name" {
  description = "Human-readable name for this AWS Organization (used in tags/docs)"
  type        = string
  default     = "MyOrg Landing Zone"
}

variable "enable_all_features" {
  description = "Enable all AWS Organizations features (required for SCPs)"
  type        = bool
  default     = true
}

variable "trusted_services" {
  description = "AWS services granted access to the organization"
  type        = list(string)
  default = [
    "cloudtrail.amazonaws.com",
    "config.amazonaws.com",
    "sso.amazonaws.com",
    "securityhub.amazonaws.com",
    "guardduty.amazonaws.com",
    "access-analyzer.amazonaws.com",
    "account.amazonaws.com",
  ]
}

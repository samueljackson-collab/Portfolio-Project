terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.30"
    }
  }
  required_version = ">= 1.5"
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      ManagedBy   = "terraform"
      Project     = "aws-landing-zone"
      Environment = "management"
    }
  }
}

# =============================================================================
# AWS Organization
# =============================================================================

resource "aws_organizations_organization" "main" {
  aws_service_access_principals = [
    "cloudtrail.amazonaws.com",
    "config.amazonaws.com",
    "sso.amazonaws.com",
    "securityhub.amazonaws.com",
    "guardduty.amazonaws.com",
    "access-analyzer.amazonaws.com",
    "account.amazonaws.com",
  ]

  feature_set          = "ALL"
  enabled_policy_types = ["SERVICE_CONTROL_POLICY", "TAG_POLICY"]
}

# =============================================================================
# Organizational Units
# =============================================================================

resource "aws_organizations_organizational_unit" "security" {
  name      = "Security"
  parent_id = aws_organizations_organization.main.roots[0].id

  tags = {
    Purpose = "Security tooling accounts (audit, logging)"
  }
}

resource "aws_organizations_organizational_unit" "infrastructure" {
  name      = "Infrastructure"
  parent_id = aws_organizations_organization.main.roots[0].id

  tags = {
    Purpose = "Shared infrastructure and platform services"
  }
}

resource "aws_organizations_organizational_unit" "workloads" {
  name      = "Workloads"
  parent_id = aws_organizations_organization.main.roots[0].id

  tags = {
    Purpose = "Application workload accounts"
  }
}

resource "aws_organizations_organizational_unit" "workloads_prod" {
  name      = "Production"
  parent_id = aws_organizations_organizational_unit.workloads.id

  tags = {
    Purpose = "Production application accounts"
  }
}

resource "aws_organizations_organizational_unit" "workloads_nonprod" {
  name      = "Non-Production"
  parent_id = aws_organizations_organizational_unit.workloads.id

  tags = {
    Purpose = "Non-production application accounts (dev, staging)"
  }
}

resource "aws_organizations_organizational_unit" "sandbox" {
  name      = "Sandbox"
  parent_id = aws_organizations_organization.main.roots[0].id

  tags = {
    Purpose = "Experimental and developer sandbox accounts"
  }
}

# =============================================================================
# Member Accounts
# =============================================================================

resource "aws_organizations_account" "security_audit" {
  name      = var.account_names.security_audit
  email     = "aws+security-audit@${var.email_domain}"
  parent_id = aws_organizations_organizational_unit.security.id

  iam_user_access_to_billing = "DENY"
  role_name                  = "OrganizationAccountAccessRole"

  tags = {
    AccountType = "security"
    Purpose     = "Security tooling, GuardDuty master, SecurityHub aggregator"
  }

  lifecycle {
    ignore_changes = [email, name]
  }
}

resource "aws_organizations_account" "log_archive" {
  name      = var.account_names.log_archive
  email     = "aws+log-archive@${var.email_domain}"
  parent_id = aws_organizations_organizational_unit.security.id

  iam_user_access_to_billing = "DENY"
  role_name                  = "OrganizationAccountAccessRole"

  tags = {
    AccountType = "security"
    Purpose     = "Centralized CloudTrail and Config log archive"
  }

  lifecycle {
    ignore_changes = [email, name]
  }
}

resource "aws_organizations_account" "shared_services" {
  name      = var.account_names.shared_services
  email     = "aws+shared-services@${var.email_domain}"
  parent_id = aws_organizations_organizational_unit.infrastructure.id

  iam_user_access_to_billing = "DENY"
  role_name                  = "OrganizationAccountAccessRole"

  tags = {
    AccountType = "infrastructure"
    Purpose     = "Shared VPC, Transit Gateway, DNS, CI/CD pipelines"
  }

  lifecycle {
    ignore_changes = [email, name]
  }
}

resource "aws_organizations_account" "sandbox_dev" {
  name      = var.account_names.sandbox_dev
  email     = "aws+sandbox-dev@${var.email_domain}"
  parent_id = aws_organizations_organizational_unit.sandbox.id

  iam_user_access_to_billing = "ALLOW"
  role_name                  = "OrganizationAccountAccessRole"

  tags = {
    AccountType = "sandbox"
    Purpose     = "Developer experimentation — auto-cleanup after 7 days"
  }

  lifecycle {
    ignore_changes = [email, name]
  }
}

# =============================================================================
# Service Control Policies — attachments
# Actual policy JSON content lives in terraform/scp/
# =============================================================================

resource "aws_organizations_policy" "deny_root_actions" {
  name        = "DenyRootActions"
  description = "Prevents root account actions across all accounts"
  type        = "SERVICE_CONTROL_POLICY"
  content     = file("${path.module}/../../scp/policies/deny-root-actions.json")

  tags = {
    PolicyType = "security-baseline"
  }
}

resource "aws_organizations_policy_attachment" "deny_root_actions_root" {
  policy_id = aws_organizations_policy.deny_root_actions.id
  target_id = aws_organizations_organization.main.roots[0].id
}

resource "aws_organizations_policy" "require_mfa" {
  name        = "RequireMFA"
  description = "Requires MFA for sensitive IAM and billing actions"
  type        = "SERVICE_CONTROL_POLICY"
  content     = file("${path.module}/../../scp/policies/require-mfa.json")

  tags = {
    PolicyType = "security-baseline"
  }
}

resource "aws_organizations_policy_attachment" "require_mfa_root" {
  policy_id = aws_organizations_policy.require_mfa.id
  target_id = aws_organizations_organization.main.roots[0].id
}

resource "aws_organizations_policy" "restrict_regions" {
  name        = "RestrictRegions"
  description = "Restricts workload deployments to approved AWS regions"
  type        = "SERVICE_CONTROL_POLICY"
  content     = file("${path.module}/../../scp/policies/restrict-regions.json")

  tags = {
    PolicyType = "compliance"
  }
}

resource "aws_organizations_policy_attachment" "restrict_regions_workloads" {
  policy_id = aws_organizations_policy.restrict_regions.id
  target_id = aws_organizations_organizational_unit.workloads.id
}

resource "aws_organizations_policy" "deny_internet_gateways" {
  name        = "DenyInternetGateways"
  description = "Prevents creation of Internet Gateways in the Security OU"
  type        = "SERVICE_CONTROL_POLICY"
  content     = file("${path.module}/../../scp/policies/deny-internet-gateways.json")

  tags = {
    PolicyType = "network-security"
  }
}

resource "aws_organizations_policy_attachment" "deny_igw_security" {
  policy_id = aws_organizations_policy.deny_internet_gateways.id
  target_id = aws_organizations_organizational_unit.security.id
}

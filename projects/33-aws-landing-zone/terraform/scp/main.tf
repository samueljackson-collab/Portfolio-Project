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
}

# ---------------------------------------------------------------------------
# Data sources — read OU/root IDs from the organizations module state
# ---------------------------------------------------------------------------

data "aws_organizations_organization" "main" {}

locals {
  root_id = data.aws_organizations_organization.main.roots[0].id
}

# ---------------------------------------------------------------------------
# SCP Policy resources — content loaded from JSON files
# ---------------------------------------------------------------------------

resource "aws_organizations_policy" "deny_root_actions" {
  name        = "DenyRootActions"
  description = "Denies root account actions across all member accounts"
  type        = "SERVICE_CONTROL_POLICY"
  content     = file("${path.module}/policies/deny-root-actions.json")

  tags = {
    PolicyFamily = "security-baseline"
    ManagedBy    = "terraform"
  }
}

resource "aws_organizations_policy" "require_mfa" {
  name        = "RequireMFA"
  description = "Requires MFA for sensitive IAM and billing operations"
  type        = "SERVICE_CONTROL_POLICY"
  content     = file("${path.module}/policies/require-mfa.json")

  tags = {
    PolicyFamily = "security-baseline"
    ManagedBy    = "terraform"
  }
}

resource "aws_organizations_policy" "restrict_regions" {
  name        = "RestrictRegions"
  description = "Restricts deployments to approved AWS regions only"
  type        = "SERVICE_CONTROL_POLICY"
  content     = file("${path.module}/policies/restrict-regions.json")

  tags = {
    PolicyFamily = "compliance"
    ManagedBy    = "terraform"
  }
}

resource "aws_organizations_policy" "deny_internet_gateways" {
  name        = "DenyInternetGateways"
  description = "Prevents creation of Internet Gateways in the Security OU"
  type        = "SERVICE_CONTROL_POLICY"
  content     = file("${path.module}/policies/deny-internet-gateways.json")

  tags = {
    PolicyFamily = "network-security"
    ManagedBy    = "terraform"
  }
}

# ---------------------------------------------------------------------------
# Policy attachments
# ---------------------------------------------------------------------------

# deny-root-actions → attached to organization root (all accounts)
resource "aws_organizations_policy_attachment" "deny_root_actions_root" {
  policy_id = aws_organizations_policy.deny_root_actions.id
  target_id = local.root_id
}

# require-mfa → attached to organization root (all accounts)
resource "aws_organizations_policy_attachment" "require_mfa_root" {
  policy_id = aws_organizations_policy.require_mfa.id
  target_id = local.root_id
}

# restrict-regions → attached to the Workloads OU
resource "aws_organizations_policy_attachment" "restrict_regions_workloads" {
  policy_id = aws_organizations_policy.restrict_regions.id
  target_id = var.workloads_ou_id
}

# deny-internet-gateways → attached to the Security OU
resource "aws_organizations_policy_attachment" "deny_igw_security" {
  policy_id = aws_organizations_policy.deny_internet_gateways.id
  target_id = var.security_ou_id
}

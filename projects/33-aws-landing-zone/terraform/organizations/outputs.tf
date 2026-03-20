output "organization_id" {
  description = "AWS Organizations organization ID"
  value       = aws_organizations_organization.main.id
}

output "organization_arn" {
  description = "AWS Organizations organization ARN"
  value       = aws_organizations_organization.main.arn
}

output "root_id" {
  description = "Root ID of the AWS Organization"
  value       = aws_organizations_organization.main.roots[0].id
}

# ---------------------------------------------------------------------------
# OU IDs
# ---------------------------------------------------------------------------

output "security_ou_id" {
  description = "ID of the Security organizational unit"
  value       = aws_organizations_organizational_unit.security.id
}

output "infrastructure_ou_id" {
  description = "ID of the Infrastructure organizational unit"
  value       = aws_organizations_organizational_unit.infrastructure.id
}

output "workloads_ou_id" {
  description = "ID of the Workloads organizational unit"
  value       = aws_organizations_organizational_unit.workloads.id
}

output "workloads_prod_ou_id" {
  description = "ID of the Workloads/Production organizational unit"
  value       = aws_organizations_organizational_unit.workloads_prod.id
}

output "workloads_nonprod_ou_id" {
  description = "ID of the Workloads/Non-Production organizational unit"
  value       = aws_organizations_organizational_unit.workloads_nonprod.id
}

output "sandbox_ou_id" {
  description = "ID of the Sandbox organizational unit"
  value       = aws_organizations_organizational_unit.sandbox.id
}

# ---------------------------------------------------------------------------
# Account IDs
# ---------------------------------------------------------------------------

output "security_audit_account_id" {
  description = "AWS account ID of the security-audit account"
  value       = aws_organizations_account.security_audit.id
}

output "log_archive_account_id" {
  description = "AWS account ID of the log-archive account"
  value       = aws_organizations_account.log_archive.id
}

output "shared_services_account_id" {
  description = "AWS account ID of the shared-services account"
  value       = aws_organizations_account.shared_services.id
}

output "sandbox_dev_account_id" {
  description = "AWS account ID of the sandbox-dev account"
  value       = aws_organizations_account.sandbox_dev.id
}

output "all_account_ids" {
  description = "Map of account name to account ID for all managed accounts"
  value = {
    security_audit  = aws_organizations_account.security_audit.id
    log_archive     = aws_organizations_account.log_archive.id
    shared_services = aws_organizations_account.shared_services.id
    sandbox_dev     = aws_organizations_account.sandbox_dev.id
  }
}

# ---------------------------------------------------------------------------
# SCP Policy IDs
# ---------------------------------------------------------------------------

output "scp_deny_root_actions_id" {
  description = "ID of the DenyRootActions SCP"
  value       = aws_organizations_policy.deny_root_actions.id
}

output "scp_require_mfa_id" {
  description = "ID of the RequireMFA SCP"
  value       = aws_organizations_policy.require_mfa.id
}

output "scp_restrict_regions_id" {
  description = "ID of the RestrictRegions SCP"
  value       = aws_organizations_policy.restrict_regions.id
}

output "scp_deny_internet_gateways_id" {
  description = "ID of the DenyInternetGateways SCP"
  value       = aws_organizations_policy.deny_internet_gateways.id
}

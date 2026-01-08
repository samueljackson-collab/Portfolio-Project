###############################################################################
# Security Module - Outputs
###############################################################################

#------------------------------------------------------------------------------
# KMS Key Outputs
#------------------------------------------------------------------------------

output "kms_key_id" {
  description = "The ID of the KMS key."
  value       = var.create_kms_key ? aws_kms_key.main[0].key_id : null
}

output "kms_key_arn" {
  description = "The ARN of the KMS key."
  value       = var.create_kms_key ? aws_kms_key.main[0].arn : var.kms_key_arn
}

output "kms_alias_arn" {
  description = "The ARN of the KMS key alias."
  value       = var.create_kms_key ? aws_kms_alias.main[0].arn : null
}

#------------------------------------------------------------------------------
# CI/CD Role Outputs
#------------------------------------------------------------------------------

output "cicd_role_arn" {
  description = "The ARN of the CI/CD IAM role."
  value       = var.create_cicd_role ? aws_iam_role.cicd[0].arn : null
}

output "cicd_role_name" {
  description = "The name of the CI/CD IAM role."
  value       = var.create_cicd_role ? aws_iam_role.cicd[0].name : null
}

#------------------------------------------------------------------------------
# Application Role Outputs
#------------------------------------------------------------------------------

output "application_role_arn" {
  description = "The ARN of the application IAM role."
  value       = var.create_application_role ? aws_iam_role.application[0].arn : null
}

output "application_role_name" {
  description = "The name of the application IAM role."
  value       = var.create_application_role ? aws_iam_role.application[0].name : null
}

output "application_instance_profile_arn" {
  description = "The ARN of the application instance profile."
  value       = var.create_application_role ? aws_iam_instance_profile.application[0].arn : null
}

output "application_instance_profile_name" {
  description = "The name of the application instance profile."
  value       = var.create_application_role ? aws_iam_instance_profile.application[0].name : null
}

#------------------------------------------------------------------------------
# Secrets Manager Outputs
#------------------------------------------------------------------------------

output "db_secret_arn" {
  description = "The ARN of the database credentials secret."
  value       = var.create_db_secret ? aws_secretsmanager_secret.db_credentials[0].arn : null
}

output "db_secret_name" {
  description = "The name of the database credentials secret."
  value       = var.create_db_secret ? aws_secretsmanager_secret.db_credentials[0].name : null
}

#------------------------------------------------------------------------------
# WAF Outputs
#------------------------------------------------------------------------------

output "waf_acl_id" {
  description = "The ID of the WAF Web ACL."
  value       = var.create_waf_acl ? aws_wafv2_web_acl.main[0].id : null
}

output "waf_acl_arn" {
  description = "The ARN of the WAF Web ACL."
  value       = var.create_waf_acl ? aws_wafv2_web_acl.main[0].arn : null
}

output "waf_acl_capacity" {
  description = "The capacity units used by the WAF Web ACL."
  value       = var.create_waf_acl ? aws_wafv2_web_acl.main[0].capacity : null
}

#------------------------------------------------------------------------------
# Security Group Outputs
#------------------------------------------------------------------------------

output "bastion_security_group_id" {
  description = "The ID of the bastion security group."
  value       = var.create_bastion_sg ? aws_security_group.bastion[0].id : null
}

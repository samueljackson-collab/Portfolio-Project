output "backup_vault_name" {
  description = "Name of the AWS Backup vault."
  value       = aws_backup_vault.this.name
}

output "backup_plan_id" {
  description = "Identifier of the AWS Backup plan."
  value       = aws_backup_plan.this.id
}

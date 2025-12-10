output "vpc_id" {
  description = "ID of the provisioned VPC"
  value       = module.network.vpc_id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = module.network.public_subnet_ids
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = module.network.private_subnet_ids
}

output "state_bucket" {
  description = "Name of the Terraform state bucket"
  value       = module.state.bucket_name
  sensitive   = false
}

output "state_lock_table" {
  description = "Name of the DynamoDB state lock table"
  value       = module.state.dynamodb_table_name
  sensitive   = false
}

output "vpc_id" {
  value       = module.network.vpc_id
  description = "ID of the provisioned VPC"
}

output "public_subnet_ids" {
  value       = module.network.public_subnet_ids
  description = "Public subnet IDs"
}

output "private_subnet_ids" {
  value       = module.network.private_subnet_ids
  description = "Private subnet IDs"
}

output "vpc_id" {
  description = "VPC identifier for the environment."
  value       = module.vpc.vpc_id
}

output "public_subnets" {
  description = "Public subnet IDs for ALB/NAT placement."
  value       = module.vpc.public_subnet_ids
}

output "private_app_subnets" {
  description = "Private application subnet IDs."
  value       = module.vpc.private_app_subnet_ids
}

output "private_db_subnets" {
  description = "Private database subnet IDs."
  value       = module.vpc.private_db_subnet_ids
}

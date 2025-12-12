output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = module.vpc.vpc_cidr
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = module.vpc.private_subnet_ids
}

output "nat_gateway_ids" {
  description = "IDs of NAT Gateways"
  value       = module.vpc.nat_gateway_ids
}

output "db_instance_identifier" {
  description = "RDS instance identifier"
  value       = module.rds.db_instance_identifier
}

output "db_instance_endpoint" {
  description = "RDS instance endpoint"
  value       = module.rds.db_instance_endpoint
  sensitive   = true
}

output "db_instance_arn" {
  description = "ARN of the RDS instance"
  value       = module.rds.db_instance_arn
}

output "db_subnet_group_name" {
  description = "Name of the DB subnet group"
  value       = module.rds.db_subnet_group_name
}

output "db_security_group_id" {
  description = "ID of the database security group"
  value       = module.rds.db_security_group_id
}

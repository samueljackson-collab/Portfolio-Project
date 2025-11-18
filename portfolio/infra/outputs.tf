output "vpc_id" {
  value       = module.network.vpc_id
  description = "ID of the created VPC"
}

output "public_subnets" {
  value = module.network.public_subnet_ids
}

output "private_subnets" {
  value = module.network.private_subnet_ids
}

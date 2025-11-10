output "vpc_id" {
  description = "Identifier of the created VPC."
  value       = module.vpc.vpc_id
}

output "private_subnets" {
  description = "Private subnet IDs for workloads."
  value       = module.vpc.private_subnets
}

output "eks_cluster_name" {
  description = "Name of the EKS cluster."
  value       = module.eks.cluster_name
}

output "rds_endpoint" {
  description = "DNS endpoint for the PostgreSQL database."
  value       = module.rds.db_instance_address
}

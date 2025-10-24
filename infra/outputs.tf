output "vpc_id" {
  value = module.network.vpc_id
}

output "alb_dns_name" {
  value = module.compute.alb_dns_name
}

output "rds_endpoint" {
  value = module.storage.db_endpoint
}

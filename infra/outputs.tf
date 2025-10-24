output "vpc_id" {
  value = module.network.vpc_id
}

output "alb_dns_name" {
  value = module.compute.alb_dns_name
}

output "db_endpoint" {
  value = module.storage.db_endpoint
}

output "static_bucket" {
  value = module.storage.static_bucket
}

project_name   = "portfolio"
environment    = "staging"
aws_region     = "us-east-1"
vpc_cidr       = "10.30.16.0/20"
az_count       = 2
single_nat_gateway = false
enable_nat_gateway = true

container_image = "ghcr.io/example/portfolio-api:staging"
container_port  = 8000
task_cpu        = "1024"
task_memory     = "2048"
desired_count   = 2

db_username = "portfolio"
db_password = "CHANGEME_STAGING"
db_instance_class = "db.t4g.small"
db_allocated_storage = 50
db_max_allocated_storage = 200
db_multi_az = true
db_backup_retention = 7

otel_exporter_endpoint = "http://otel-collector.monitoring:4317"

extra_tags = {
  Owner = "platform-team"
  CostCenter = "eng"
}

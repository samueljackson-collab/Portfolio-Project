project_name   = "portfolio"
environment    = "prod"
aws_region     = "us-east-1"
vpc_cidr       = "10.30.32.0/20"
az_count       = 3
single_nat_gateway = false
enable_nat_gateway = true

container_image = "ghcr.io/example/portfolio-api:main"
container_port  = 8000
task_cpu        = "2048"
task_memory     = "4096"
desired_count   = 3

db_username = "portfolio"
db_password = "CHANGEME_PROD"
db_instance_class = "db.m6g.large"
db_allocated_storage = 100
db_max_allocated_storage = 500
db_multi_az = true
db_backup_retention = 30

otel_exporter_endpoint = "https://otel-gateway.company:4317"

extra_tags = {
  Owner      = "platform-team"
  CostCenter = "production"
  DataClass  = "confidential"
}

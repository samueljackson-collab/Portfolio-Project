project_name   = "portfolio"
environment    = "dev"
aws_region     = "us-east-1"
vpc_cidr       = "10.30.0.0/20"
az_count       = 2
single_nat_gateway = true
enable_nat_gateway = true

container_image = "ghcr.io/example/portfolio-api:dev"
container_port  = 8000
task_cpu        = "512"
task_memory     = "1024"
desired_count   = 1

db_username = "portfolio"
db_password = "CHANGEME_DEV"
db_instance_class = "db.t4g.micro"
db_allocated_storage = 20
db_max_allocated_storage = 40
db_multi_az = false
db_backup_retention = 3

otel_exporter_endpoint = "http://otel-collector.monitoring:4317"

extra_tags = {
  Owner = "platform-team"
  CostCenter = "rnd"
}

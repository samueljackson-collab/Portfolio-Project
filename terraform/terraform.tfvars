# terraform/terraform.tfvars
#
# This file contains actual values for variables.
# IMPORTANT: Do NOT commit this file to Git if it contains sensitive data!

# General configuration
project_name = "portfolio-aws-infra"
environment  = "prod"
aws_region   = "us-east-1"

# Network configuration
vpc_cidr              = "10.0.0.0/16"
public_subnet_cidrs   = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs  = ["10.0.10.0/24", "10.0.11.0/24"]
database_subnet_cidrs = ["10.0.20.0/24", "10.0.21.0/24"]
availability_zones    = ["us-east-1a", "us-east-1b"]

# Compute configuration
instance_type               = "t3.micro"
app_server_desired_capacity = 2
app_server_min_size         = 2
app_server_max_size         = 6

# Database configuration
db_engine                = "postgres"
db_engine_version        = "15.3"
db_instance_class        = "db.t3.micro"
db_allocated_storage     = 20
db_max_allocated_storage = 100
db_name                  = "appdb"
db_username              = "dbadmin"
db_multi_az              = true  # Set to false for dev to save money

# Load balancer configuration
alb_health_check_path     = "/health"
alb_health_check_interval = 30
alb_deregistration_delay  = 30

# Security configuration
allowed_cidr_blocks        = ["0.0.0.0/0"]  # Allow from internet
enable_deletion_protection = false  # Set to true for production

# Monitoring configuration
enable_cloudwatch_logs = true
log_retention_days     = 7

# Tags
tags = {
  Project     = "Portfolio Infrastructure"
  ManagedBy   = "Terraform"
  Environment = "Production"
  Owner       = "Your Name"
  CostCenter  = "Portfolio"
}


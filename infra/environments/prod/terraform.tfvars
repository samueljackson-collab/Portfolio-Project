# ============================================================================
# File: infra/environments/prod/terraform.tfvars
# ============================================================================

# Project Configuration
project_name = "portfolio"
environment  = "prod"
owner        = "samuel.jackson@example.com"

# AWS Configuration
aws_region         = "us-west-2"
availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]

# Network Configuration
vpc_cidr = "10.0.0.0/16"

# Compute Configuration
instance_type        = "t3.medium"
asg_min_size         = 2
asg_max_size         = 10
asg_desired_capacity = 2

# Database Configuration
db_instance_class    = "db.t3.medium"
db_name              = "portfolio"
db_username          = "portfolio_admin"
db_allocated_storage = 100
db_backup_retention  = 30
multi_az             = true

# CloudFront Configuration
enable_cloudfront = true

# Monitoring Configuration
alert_email = "alerts@example.com"

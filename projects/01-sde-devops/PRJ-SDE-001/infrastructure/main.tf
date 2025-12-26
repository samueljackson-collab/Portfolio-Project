# Root Terraform Configuration for Full-Stack Database Infrastructure
# This configuration deploys a complete production-ready stack:
# - VPC with public/private/database subnets
# - PostgreSQL RDS database with security hardening
# - ECS Fargate application with load balancer
# - CloudWatch monitoring and alarms

terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Backend configuration for remote state storage
  # Uncomment and configure for production use
  # backend "s3" {
  #   bucket         = "my-terraform-state-bucket"
  #   key            = "full-stack-app/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "terraform-state-lock"
  #   encrypt        = true
  # }
}

# AWS Provider Configuration
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      ManagedBy   = "Terraform"
      Repository  = "Portfolio-Project"
      Project     = var.project_name
      Environment = var.environment
    }
  }
}

#------------------------------------------------------------------------------
# VPC Module - Production Networking Infrastructure
#------------------------------------------------------------------------------

module "vpc" {
  source = "../../../../infrastructure/terraform/modules/vpc"

  project_name = var.project_name
  environment  = var.environment

  # Network configuration
  vpc_cidr               = var.vpc_cidr
  az_count               = var.az_count
  enable_nat_gateway     = var.enable_nat_gateway
  single_nat_gateway     = var.single_nat_gateway
  enable_dns_hostnames   = true
  enable_dns_support     = true
  map_public_ip_on_launch = true

  # Security and monitoring
  enable_flow_logs           = var.enable_flow_logs
  flow_logs_retention_days   = var.flow_logs_retention_days
  enable_s3_endpoint         = var.enable_s3_endpoint

  tags = {
    Component = "Networking"
  }
}

#------------------------------------------------------------------------------
# Database Module - Production PostgreSQL RDS Instance
#------------------------------------------------------------------------------

module "database" {
  source = "../../../../infrastructure/terraform/modules/database"

  # Required variables
  project_name = var.project_name
  environment  = var.environment
  vpc_id       = module.vpc.vpc_id
  subnet_ids   = module.vpc.database_subnet_ids
  db_username  = var.db_username
  db_password  = var.db_password

  # Security - Allow access from application
  allowed_security_group_ids = var.deploy_application ? [module.application[0].ecs_tasks_security_group_id] : []

  # Instance configuration
  instance_class        = var.db_instance_class
  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  engine_version        = var.db_engine_version

  # High Availability
  multi_az = var.db_multi_az

  # Backup configuration
  backup_retention_period = var.db_backup_retention_days

  # Safety controls
  deletion_protection = var.db_deletion_protection
  skip_final_snapshot = var.db_skip_final_snapshot
  apply_immediately   = var.db_apply_immediately

  # Tags
  tags = {
    Component = "Database"
    Backup    = "Required"
  }
}

#------------------------------------------------------------------------------
# ECS Application Module - Containerized Application (Optional)
#------------------------------------------------------------------------------

module "application" {
  count  = var.deploy_application ? 1 : 0
  source = "../../../../infrastructure/terraform/modules/ecs-application"

  project_name = var.project_name
  environment  = var.environment

  # Network configuration
  vpc_id             = module.vpc.vpc_id
  public_subnet_ids  = module.vpc.public_subnet_ids
  private_subnet_ids = module.vpc.private_subnet_ids

  # Container configuration
  container_name  = var.app_container_name
  container_image = var.app_container_image
  container_port  = var.app_container_port

  # Pass database connection as environment variable
  environment_variables = [
    {
      name  = "DATABASE_HOST"
      value = module.database.db_endpoint
    },
    {
      name  = "DATABASE_PORT"
      value = "5432"
    },
    {
      name  = "DATABASE_NAME"
      value = "postgres"
    },
    {
      name  = "DATABASE_USER"
      value = var.db_username
    }
    # Note: In production, use AWS Secrets Manager for DB_PASSWORD
  ]

  # ECS Task configuration
  task_cpu       = var.app_task_cpu
  task_memory    = var.app_task_memory
  desired_count  = var.app_desired_count

  # Auto-scaling
  enable_autoscaling   = var.app_enable_autoscaling
  min_capacity         = var.app_min_capacity
  max_capacity         = var.app_max_capacity
  cpu_target_value     = var.app_cpu_target
  memory_target_value  = var.app_memory_target

  # Health checks
  health_check_path               = var.app_health_check_path
  health_check_healthy_threshold  = 2
  health_check_unhealthy_threshold = 3
  health_check_timeout            = 5
  health_check_interval           = 30

  # Load balancer
  internal_alb            = false
  enable_deletion_protection = var.enable_deletion_protection

  # Monitoring
  enable_container_insights = true
  log_retention_days        = var.log_retention_days

  # Database access
  database_security_group_id = module.database.db_security_group_id

  tags = {
    Component = "Application"
  }

  depends_on = [module.database]
}

# Optional: CloudWatch alarms for database monitoring
resource "aws_cloudwatch_metric_alarm" "database_cpu" {
  alarm_name          = "${var.project_name}-${var.environment}-db-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "This metric monitors database CPU utilization"
  alarm_actions       = [] # Add SNS topic ARN for notifications

  dimensions = {
    DBInstanceIdentifier = module.database.db_instance_identifier
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-db-cpu-alarm"
  }
}

resource "aws_cloudwatch_metric_alarm" "database_storage" {
  alarm_name          = "${var.project_name}-${var.environment}-db-storage-space"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 2147483648 # 2 GB in bytes
  alarm_description   = "This metric monitors database free storage space"
  alarm_actions       = [] # Add SNS topic ARN for notifications

  dimensions = {
    DBInstanceIdentifier = module.database.db_instance_identifier
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-db-storage-alarm"
  }
}

resource "aws_cloudwatch_metric_alarm" "database_connections" {
  alarm_name          = "${var.project_name}-${var.environment}-db-connections"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "This metric monitors database connections"
  alarm_actions       = [] # Add SNS topic ARN for notifications

  dimensions = {
    DBInstanceIdentifier = module.database.db_instance_identifier
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-db-connections-alarm"
  }
}

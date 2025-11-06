# Root Terraform Configuration for Database Infrastructure
# This configuration uses the database module to provision a PostgreSQL RDS instance

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
  #   key            = "database/terraform.tfstate"
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

# Data source to get available AZs
data "aws_availability_zones" "available" {
  state = "available"
}

# Data source to get default VPC (for demo/testing)
# In production, you'd create a custom VPC or reference an existing one
data "aws_vpc" "default" {
  default = true
}

# Data source to get default subnets
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Security group for application servers that will access the database
resource "aws_security_group" "app_servers" {
  name        = "${var.project_name}-${var.environment}-app-sg"
  description = "Security group for application servers"
  vpc_id      = data.aws_vpc.default.id

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-app-sg"
  }
}

# Database Module - Production PostgreSQL RDS Instance
module "database" {
  source = "../../../../infrastructure/terraform/modules/database"

  # Required variables
  project_name = var.project_name
  environment  = var.environment
  vpc_id       = data.aws_vpc.default.id
  subnet_ids   = data.aws_subnets.default.ids
  db_username  = var.db_username
  db_password  = var.db_password

  # Security - Allow access from application security group
  allowed_security_group_ids = [aws_security_group.app_servers.id]

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

# NOTE: CloudWatch alarms below are configured with empty alarm_actions.
# To receive notifications, create an SNS topic and add its ARN to alarm_actions:
#
# resource "aws_sns_topic" "database_alerts" {
#   name = "${var.project_name}-${var.environment}-db-alerts"
# }
#
# resource "aws_sns_topic_subscription" "database_alerts_email" {
#   topic_arn = aws_sns_topic.database_alerts.arn
#   protocol  = "email"
#   endpoint  = "your-email@example.com"
# }
#
# Then update alarm_actions = [aws_sns_topic.database_alerts.arn]

# CloudWatch alarm for database CPU utilization
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

# CloudWatch alarm for database storage space
resource "aws_cloudwatch_metric_alarm" "database_storage" {
  alarm_name          = "${var.project_name}-${var.environment}-db-storage-space"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 2 * 1024 * 1024 * 1024 # 2 GB in bytes
  alarm_description   = "This metric monitors database free storage space"
  alarm_actions       = [] # Add SNS topic ARN for notifications

  dimensions = {
    DBInstanceIdentifier = module.database.db_instance_identifier
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-db-storage-alarm"
  }
}

# CloudWatch alarm for database connections
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

# Root Terraform Variables
# Configure these values in terraform.tfvars or via environment variables

#------------------------------------------------------------------------------
# General Configuration
#------------------------------------------------------------------------------

variable "aws_region" {
  type        = string
  description = "AWS region for resources"
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Project identifier used for resource naming"
}

variable "environment" {
  type        = string
  description = "Environment name (dev, staging, prod)"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod"
  }
}

#------------------------------------------------------------------------------
# VPC Configuration
#------------------------------------------------------------------------------

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC"
  default     = "10.0.0.0/16"
}

variable "az_count" {
  type        = number
  description = "Number of availability zones to use"
  default     = 2

  validation {
    condition     = var.az_count >= 1 && var.az_count <= 3
    error_message = "AZ count must be between 1 and 3"
  }
}

variable "enable_nat_gateway" {
  type        = bool
  description = "Enable NAT Gateway for private subnet internet access"
  default     = true
}

variable "single_nat_gateway" {
  type        = bool
  description = "Use single NAT Gateway (cost savings) vs one per AZ (HA)"
  default     = true # Set to false for production HA
}

variable "enable_flow_logs" {
  type        = bool
  description = "Enable VPC Flow Logs for network monitoring"
  default     = true
}

variable "flow_logs_retention_days" {
  type        = number
  description = "CloudWatch log retention for VPC Flow Logs"
  default     = 7
}

variable "enable_s3_endpoint" {
  type        = bool
  description = "Enable S3 VPC Endpoint for private S3 access"
  default     = true
}

# Database Configuration
variable "db_username" {
  type        = string
  description = "Master username for the database"
  sensitive   = true
}

variable "db_password" {
  type        = string
  description = "Master password for the database (min 8 characters)"
  sensitive   = true

  validation {
    condition     = length(var.db_password) >= 8
    error_message = "Database password must be at least 8 characters"
  }
}

variable "db_instance_class" {
  type        = string
  description = "RDS instance class (e.g., db.t3.small, db.t3.medium)"
  default     = "db.t3.small"
}

variable "db_allocated_storage" {
  type        = number
  description = "Initial allocated storage in GB"
  default     = 20

  validation {
    condition     = var.db_allocated_storage >= 20 && var.db_allocated_storage <= 65536
    error_message = "Allocated storage must be between 20 and 65536 GB"
  }
}

variable "db_max_allocated_storage" {
  type        = number
  description = "Maximum storage for autoscaling in GB"
  default     = 100

  validation {
    condition     = var.db_max_allocated_storage >= 20 && var.db_max_allocated_storage <= 65536
    error_message = "Max allocated storage must be between 20 and 65536 GB"
  }
}

variable "db_engine_version" {
  type        = string
  description = "PostgreSQL engine version"
  default     = "15.4"
}

variable "db_multi_az" {
  type        = bool
  description = "Enable Multi-AZ deployment for high availability"
  default     = false # Set to true for production
}

variable "db_backup_retention_days" {
  type        = number
  description = "Number of days to retain automated backups"
  default     = 7

  validation {
    condition     = var.db_backup_retention_days >= 0 && var.db_backup_retention_days <= 35
    error_message = "Backup retention must be between 0 and 35 days"
  }
}

variable "db_deletion_protection" {
  type        = bool
  description = "Enable deletion protection (recommended for production)"
  default     = false # Set to true for production
}

variable "db_skip_final_snapshot" {
  type        = bool
  description = "Skip final snapshot when destroying (NOT recommended for production)"
  default     = false # Keep false to protect data
}

variable "db_apply_immediately" {
  type        = bool
  description = "Apply changes immediately vs. during maintenance window"
  default     = false # Set to false for production to use maintenance window
}

#------------------------------------------------------------------------------
# Application Configuration (ECS)
#------------------------------------------------------------------------------

variable "deploy_application" {
  type        = bool
  description = "Deploy ECS application alongside database"
  default     = false # Set to true to deploy full stack
}

variable "app_container_name" {
  type        = string
  description = "Name of the application container"
  default     = "app"
}

variable "app_container_image" {
  type        = string
  description = "Docker image for application (e.g., nginx:latest or your ECR URI)"
  default     = "nginx:latest" # Replace with your application image
}

variable "app_container_port" {
  type        = number
  description = "Port the application listens on"
  default     = 80
}

variable "app_task_cpu" {
  type        = string
  description = "CPU units for ECS task"
  default     = "256"
}

variable "app_task_memory" {
  type        = string
  description = "Memory for ECS task in MB"
  default     = "512"
}

variable "app_desired_count" {
  type        = number
  description = "Desired number of application tasks"
  default     = 2
}

variable "app_enable_autoscaling" {
  type        = bool
  description = "Enable auto-scaling for application"
  default     = true
}

variable "app_min_capacity" {
  type        = number
  description = "Minimum number of tasks"
  default     = 1
}

variable "app_max_capacity" {
  type        = number
  description = "Maximum number of tasks"
  default     = 10
}

variable "app_cpu_target" {
  type        = number
  description = "Target CPU utilization for auto-scaling"
  default     = 70
}

variable "app_memory_target" {
  type        = number
  description = "Target memory utilization for auto-scaling"
  default     = 80
}

variable "app_health_check_path" {
  type        = string
  description = "Health check path for application"
  default     = "/"
}

#------------------------------------------------------------------------------
# Shared Configuration
#------------------------------------------------------------------------------

variable "enable_deletion_protection" {
  type        = bool
  description = "Enable deletion protection on ALB and RDS"
  default     = false # Set to true for production
}

variable "log_retention_days" {
  type        = number
  description = "CloudWatch log retention in days"
  default     = 7

  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.log_retention_days)
    error_message = "Log retention must be a valid CloudWatch retention period"
  }
}

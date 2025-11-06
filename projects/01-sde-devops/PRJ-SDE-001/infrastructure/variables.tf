# Root Terraform Variables
# Configure these values in terraform.tfvars or via environment variables

# General Configuration
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

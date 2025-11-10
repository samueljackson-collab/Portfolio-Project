/**
 * Root module input definitions with validation to guard against misconfiguration.
 */
variable "project_name" {
  description = "Human-readable project identifier used in tagging and resource naming."
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z0-9-]+$", var.project_name))
    error_message = "project_name may only contain alphanumeric characters and dashes."
  }
}

variable "environment" {
  description = "Deployment stage for the stack (dev, staging, prod)."
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of dev, staging, prod."
  }
}

variable "aws_region" {
  description = "AWS region where resources will be created."
  type        = string
  default     = "us-west-2"
}

variable "deployment_role_arn" {
  description = "Optional IAM role ARN assumed by Terraform during operations. Leave blank for default credentials."
  type        = string
  default     = ""
}

variable "state_bucket_name" {
  description = "Name of the S3 bucket hosting remote Terraform state."
  type        = string
}

variable "state_lock_table" {
  description = "Name of the DynamoDB table used for state locking."
  type        = string
}

variable "vpc_id" {
  description = "Target VPC identifier where the database resources are provisioned."
  type        = string
}

variable "subnet_ids" {
  description = "List of private subnet IDs across at least two availability zones."
  type        = list(string)

  validation {
    condition     = length(var.subnet_ids) >= 2
    error_message = "Provide at least two subnet IDs for Multi-AZ support."
  }
}

variable "allowed_security_group_ids" {
  description = "Security groups permitted ingress on port 5432 to the database."
  type        = list(string)
  default     = []
}

variable "db_username" {
  description = "Master database username stored securely via secrets manager."
  type        = string
}

variable "db_password" {
  description = "Master database password supplied through TF_VAR_db_password or CI secret store."
  type        = string
  sensitive   = true
}

variable "instance_class" {
  description = "AWS RDS instance class sizing the compute and memory footprint."
  type        = string
  default     = "db.t3.small"
}

variable "allocated_storage" {
  description = "Initial storage allocation in GiB for the RDS instance."
  type        = number
  default     = 20
}

variable "max_allocated_storage" {
  description = "Maximum storage (GiB) the instance can autoscale to using storage autoscaling."
  type        = number
  default     = 100
}

variable "engine_version" {
  description = "PostgreSQL engine version for the RDS instance."
  type        = string
  default     = "15.4"
}

variable "multi_az" {
  description = "Whether to deploy Multi-AZ replication for high availability."
  type        = bool
  default     = true
}

variable "backup_retention_period" {
  description = "Number of days automated backups are retained."
  type        = number
  default     = 7

  validation {
    condition     = var.backup_retention_period >= 1 && var.backup_retention_period <= 35
    error_message = "backup_retention_period must be between 1 and 35 days."
  }
}

variable "deletion_protection" {
  description = "Prevent accidental deletion of production databases."
  type        = bool
  default     = false
}

variable "skip_final_snapshot" {
  description = "Skip creation of a final snapshot during destroy. Always false for production."
  type        = bool
  default     = false
}

variable "apply_immediately" {
  description = "Apply modifications immediately (true) or during maintenance window (false)."
  type        = bool
  default     = true
}

variable "performance_insights_enabled" {
  description = "Enable Amazon RDS Performance Insights for performance tuning."
  type        = bool
  default     = true
}

variable "performance_insights_retention_period" {
  description = "Retention period in days for Performance Insights (7 or 731)."
  type        = number
  default     = 7

  validation {
    condition     = contains([7, 731], var.performance_insights_retention_period)
    error_message = "performance_insights_retention_period must be either 7 or 731 days."
  }
}

variable "tags" {
  description = "Additional metadata tags applied to every resource."
  type        = map(string)
  default     = {}
}

variable "project_name" {
  type        = string
  description = "Project identifier for tagging and resource names"
}

variable "environment" {
  type        = string
  description = "Deployment environment (dev, staging, production)"
}

variable "aws_region" {
  type        = string
  description = "AWS region for resource deployment"
  default     = "us-east-1"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the platform VPC"
  default     = "10.20.0.0/16"
}

variable "az_count" {
  type        = number
  description = "Number of availability zones to target"
  default     = 2
}

variable "db_username" {
  type        = string
  description = "Database admin username"
}

variable "db_password" {
  type        = string
  description = "Database admin password"
  sensitive   = true
}

variable "db_instance_class" {
  type        = string
  description = "Instance size for the PostgreSQL database"
  default     = "db.t3.small"
}

variable "db_allocated_storage" {
  type        = number
  description = "Initial allocated storage for the database"
  default     = 20
}

variable "db_max_allocated_storage" {
  type        = number
  description = "Maximum autoscaling storage for the database"
  default     = 100
}

variable "db_engine_version" {
  type        = string
  description = "PostgreSQL engine version"
  default     = "15.4"
}

variable "db_backup_retention" {
  type        = number
  description = "Backup retention period in days"
  default     = 7
}

variable "container_image" {
  type        = string
  description = "Container image for the ECS service"
}

variable "tags" {
  type        = map(string)
  description = "Additional tags applied to all resources"
  default     = {}
}

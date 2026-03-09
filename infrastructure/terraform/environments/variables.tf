variable "project_name" {
  description = "Project identifier used for naming resources"
  type        = string
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
}

variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for the environment VPC"
  type        = string
  default     = "10.30.0.0/16"
}

variable "az_count" {
  description = "Number of AZs to spread across"
  type        = number
  default     = 2
}

variable "enable_nat_gateway" {
  description = "Whether to provision NAT gateways for private egress"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Share a single NAT gateway (cost saver for non-prod)"
  type        = bool
  default     = false
}

variable "db_username" {
  description = "Master database username"
  type        = string
}

variable "db_password" {
  description = "Master database password"
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "Instance size for RDS"
  type        = string
  default     = "db.t4g.small"
}

variable "db_allocated_storage" {
  description = "Initial database storage"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Maximum storage for autoscaling"
  type        = number
  default     = 200
}

variable "db_multi_az" {
  description = "Enable Multi-AZ for RDS"
  type        = bool
  default     = false
}

variable "db_backup_retention" {
  description = "Backup retention in days"
  type        = number
  default     = 7
}

variable "container_image" {
  description = "Container image URI for the portfolio API"
  type        = string
}

variable "container_port" {
  description = "Application listening port"
  type        = number
  default     = 8000
}

variable "task_cpu" {
  description = "ECS task CPU units"
  type        = string
  default     = "512"
}

variable "task_memory" {
  description = "ECS task memory"
  type        = string
  default     = "1024"
}

variable "desired_count" {
  description = "Number of ECS tasks to run"
  type        = number
  default     = 2
}

variable "otel_exporter_endpoint" {
  description = "OTel exporter endpoint used by services"
  type        = string
  default     = "http://otel-collector.monitoring:4317"
}

variable "extra_tags" {
  description = "Optional additional tags applied to all resources"
  type        = map(string)
  default     = {}
}

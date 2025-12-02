variable "project_name" {
  type        = string
  description = "Project identifier for tagging and names"
  default     = "portfolio-platform"
}

variable "environment" {
  type        = string
  description = "Environment name"
  default     = "staging"
}

variable "region" {
  type        = string
  description = "AWS region for the environment"
  default     = "us-east-1"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC"
  default     = "10.10.0.0/16"
}

variable "az_count" {
  type        = number
  description = "Number of AZs to span"
  default     = 2
}

variable "db_username" {
  type        = string
  description = "Database master username"
  default     = "app_user"
}

variable "db_password" {
  type        = string
  description = "Database master password (override via tfvars or environment)"
  sensitive   = true
  default     = "change_me_staging"
}

variable "container_image" {
  type        = string
  description = "Container image for the orchestrator API"
  default     = "ghcr.io/samueljackson-collab/portfolio-api:staging"
}

variable "desired_count" {
  type        = number
  description = "Desired ECS task count"
  default     = 2
}

variable "min_capacity" {
  type        = number
  description = "Minimum tasks for autoscaling"
  default     = 2
}

variable "max_capacity" {
  type        = number
  description = "Maximum tasks for autoscaling"
  default     = 6
}

variable "tags" {
  type        = map(string)
  description = "Common tags applied to all resources"
  default = {
    Owner      = "platform-team"
    CostCenter = "portfolio-staging"
    ManagedBy  = "terraform"
  }
}

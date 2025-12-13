variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID for application resources"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR for security group rules"
  type        = string
}

variable "public_subnet_ids" {
  description = "Public subnet IDs"
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "Private subnet IDs"
  type        = list(string)
}

variable "create_rds" {
  description = "Create PostgreSQL RDS instance"
  type        = bool
  default     = true
}

variable "db_name" {
  description = "Database name"
  type        = string
}

variable "db_username" {
  description = "Database admin username"
  type        = string
}

variable "db_password" {
  description = "Database admin password"
  type        = string
  default     = ""
  sensitive   = true
}

variable "db_allocated_storage" {
  description = "Allocated storage for RDS"
  type        = number
}

variable "db_instance_class" {
  description = "Instance class for RDS"
  type        = string
}

variable "db_engine_version" {
  description = "Engine version"
  type        = string
}

variable "allowed_cidrs" {
  description = "CIDR blocks allowed to access app resources"
  type        = list(string)
  default     = []
}

variable "app_bucket_force_destroy" {
  description = "Force destroy app buckets"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags to apply"
  type        = map(string)
  default     = {}
}

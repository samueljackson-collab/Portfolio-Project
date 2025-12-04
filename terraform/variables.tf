variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]{1}$", var.aws_region))
    error_message = "Must be a valid AWS region format (e.g., us-east-1)"
  }
}

variable "project_tag" {
  description = "Project tag applied to all resources"
  type        = string
  default     = "twisted-monk"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "List of CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "List of CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}

variable "enable_nat_gateway" {
  description = "Deploy a single shared NAT Gateway for private egress"
  type        = bool
  default     = true
}

variable "enable_flow_logs" {
  description = "Enable VPC Flow Logs to CloudWatch"
  type        = bool
  default     = true
}

variable "create_rds" {
  description = "Create a PostgreSQL RDS instance for the application"
  type        = bool
  default     = true
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "twisted_monk_db"
}

variable "db_username" {
  description = "Database admin username"
  type        = string
  default     = "tm_admin"
}

variable "db_password" {
  description = "Database admin password (leave empty to generate)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "db_allocated_storage" {
  description = "RDS allocated storage (GB)"
  type        = number
  default     = 20
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "15.5"
}

variable "db_backup_retention" {
  description = "Backup retention period in days"
  type        = number
  default     = 7
}

variable "assets_bucket_name" {
  description = "Optional override for the application assets bucket name"
  type        = string
  default     = ""
}

variable "monitoring_alarm_emails" {
  description = "Email addresses subscribed to alert notifications"
  type        = list(string)
  default     = []
}

variable "monitoring_enable_rds_alarm" {
  description = "Enable RDS performance alarms"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "Retention in days for CloudWatch Log Groups created by modules"
  type        = number
  default     = 30
}

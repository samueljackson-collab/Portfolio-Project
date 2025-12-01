variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for tagging and resource naming"
  type        = string
  default     = "twisted-monk"
}

variable "environment" {
  description = "Deployment environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnets" {
  description = "Public subnets with CIDR and AZ configuration"
  type = list(object({
    cidr = string
    az   = string
  }))
  default = [
    {
      cidr = "10.0.1.0/24"
      az   = "us-east-1a"
    },
    {
      cidr = "10.0.2.0/24"
      az   = "us-east-1b"
    }
  ]
}

variable "private_subnets" {
  description = "Private subnets with CIDR and AZ configuration"
  type = list(object({
    cidr = string
    az   = string
  }))
  default = [
    {
      cidr = "10.0.11.0/24"
      az   = "us-east-1a"
    },
    {
      cidr = "10.0.12.0/24"
      az   = "us-east-1b"
    }
  ]
}

variable "enable_nat_gateway" {
  description = "Create a NAT gateway for private subnet egress"
  type        = bool
  default     = true
}

variable "create_rds" {
  description = "Whether to create a PostgreSQL RDS instance"
  type        = bool
  default     = true
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "portfolio_db"
}

variable "db_username" {
  description = "Database admin username"
  type        = string
  default     = "portfolio_admin"
}

variable "db_password" {
  description = "Optional database admin password (leave blank to autogenerate)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
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

variable "app_bucket_force_destroy" {
  description = "Force destroy S3 buckets when destroying the stack"
  type        = bool
  default     = false
}

variable "enable_flow_logs" {
  description = "Enable VPC Flow Logs to CloudWatch"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "Retention period for CloudWatch log groups"
  type        = number
  default     = 30
}

variable "alert_email_addresses" {
  description = "Optional list of email addresses subscribed to the monitoring topic"
  type        = list(string)
  default     = []
}

variable "allowed_cidrs" {
  description = "CIDR blocks allowed to reach application resources (e.g., bastion)"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}

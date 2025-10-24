# terraform/variables.tf
#
# Centralized variable definitions for the AWS multi-tier architecture.
# Defaults are production-ready but can be overridden per-environment via
# terraform.tfvars files.

# ========================================
# General Configuration
# ========================================

variable "project_name" {
  description = "Project name used for resource naming and tagging"
  type        = string
  default     = "portfolio-aws-infra"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "tags" {
  description = "Additional tags applied to all resources"
  type        = map(string)
  default     = {
    Project     = "Portfolio Infrastructure"
    ManagedBy   = "Terraform"
    Environment = "Production"
  }
}

# ========================================
# Network Configuration
# ========================================

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "database_subnet_cidrs" {
  description = "CIDR blocks for database subnets"
  type        = list(string)
  default     = ["10.0.20.0/24", "10.0.21.0/24"]
}

variable "availability_zones" {
  description = "Availability Zones to distribute resources across"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# ========================================
# Compute Configuration
# ========================================

variable "instance_type" {
  description = "EC2 instance type for application servers"
  type        = string
  default     = "t3.micro"
}

variable "app_server_desired_capacity" {
  description = "Desired number of EC2 instances in the Auto Scaling Group"
  type        = number
  default     = 2
}

variable "app_server_min_size" {
  description = "Minimum number of EC2 instances in the Auto Scaling Group"
  type        = number
  default     = 2
}

variable "app_server_max_size" {
  description = "Maximum number of EC2 instances in the Auto Scaling Group"
  type        = number
  default     = 6
}

# ========================================
# Database Configuration
# ========================================

variable "db_engine" {
  description = "Database engine (postgres, mysql, etc.)"
  type        = string
  default     = "postgres"
}

variable "db_engine_version" {
  description = "Database engine version"
  type        = string
  default     = "15.3"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Initial allocated storage for RDS (GB)"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Maximum storage for RDS autoscaling (GB)"
  type        = number
  default     = 100
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "appdb"
}

variable "db_username" {
  description = "Master database username"
  type        = string
  default     = "dbadmin"
}

variable "db_multi_az" {
  description = "Deploy RDS in Multi-AZ mode"
  type        = bool
  default     = true
}

# ========================================
# Load Balancer Configuration
# ========================================

variable "alb_health_check_path" {
  description = "Health check path for the Application Load Balancer"
  type        = string
  default     = "/health"
}

variable "alb_health_check_interval" {
  description = "Health check interval in seconds"
  type        = number
  default     = 30
}

variable "alb_deregistration_delay" {
  description = "Connection draining delay for ALB target group"
  type        = number
  default     = 30
}

# ========================================
# Security Configuration
# ========================================

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to reach the load balancer"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection on critical resources"
  type        = bool
  default     = false
}

# ========================================
# Monitoring Configuration
# ========================================

variable "enable_cloudwatch_logs" {
  description = "Create CloudWatch log group for application logs"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "Retention period for CloudWatch log groups"
  type        = number
  default     = 7
}

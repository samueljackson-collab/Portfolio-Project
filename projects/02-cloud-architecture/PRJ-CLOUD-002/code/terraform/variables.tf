/**
 * variables.tf
 *
 * Centralized variable declarations for the multi-tier AWS environment.
 * Defaults reflect a production-ready but budget-conscious deployment.
 * Every variable includes context so future maintainers understand
 * the business or security reason behind the chosen value.
 */

variable "project_name" {
  description = "Project slug used for tagging and resource names"
  type        = string
  default     = "aws-multi-tier"
}

variable "environment" {
  description = "Environment identifier (dev|staging|prod)"
  type        = string
  default     = "prod"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of dev, staging, or prod."
  }
}

variable "aws_region" {
  description = "AWS region for resource deployment"
  type        = string
  default     = "us-east-1"
}

variable "tags" {
  description = "Common tags applied to every resource"
  type        = map(string)
  default = {
    ManagedBy = "Terraform"
    Owner     = "Sam Jackson"
  }
}

variable "vpc_cidr" {
  description = "Primary CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Ordered list of availability zones to use"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for application subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "database_subnet_cidrs" {
  description = "CIDR blocks reserved for the data tier"
  type        = list(string)
  default     = ["10.0.20.0/24", "10.0.21.0/24"]
}

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
  description = "Minimum number of EC2 instances"
  type        = number
  default     = 2
}

variable "app_server_max_size" {
  description = "Maximum number of EC2 instances"
  type        = number
  default     = 6
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks permitted to reach the load balancer"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "alb_health_check_path" {
  description = "HTTP path used by the ALB to test instance health"
  type        = string
  default     = "/health"
}

variable "alb_health_check_interval" {
  description = "Seconds between ALB health checks"
  type        = number
  default     = 30
}

variable "alb_deregistration_delay" {
  description = "Seconds the ALB waits before removing an instance"
  type        = number
  default     = 30
}

variable "db_engine" {
  description = "Database engine for RDS"
  type        = string
  default     = "postgres"
}

variable "db_engine_version" {
  description = "Database engine version"
  type        = string
  default     = "15.3"
}

variable "db_instance_class" {
  description = "RDS instance size"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Initial RDS storage allocation in GB"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Upper limit for storage autoscaling"
  type        = number
  default     = 100
}

variable "db_name" {
  description = "Initial database name"
  type        = string
  default     = "appdb"
}

variable "db_username" {
  description = "Master database username"
  type        = string
  default     = "dbadmin"
}

variable "db_password" {
  description = "Master database password"
  type        = string
  sensitive   = true
}

variable "db_multi_az" {
  description = "Controls whether RDS deploys a synchronous standby"
  type        = bool
  default     = true
}

variable "enable_deletion_protection" {
  description = "Protect critical resources from accidental deletion"
  type        = bool
  default     = false
}

variable "enable_cloudwatch_logs" {
  description = "Toggle creation of CloudWatch log groups for EC2 and ALB"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "Retention period for CloudWatch logs"
  type        = number
  default     = 7
}


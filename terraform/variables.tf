variable "project_tag" {
  description = "Project name tag applied to all resources"
  type        = string
  default     = "twisted-monk"
}

variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]{1}$", var.aws_region))
    error_message = "Must be a valid AWS region format (e.g., us-east-1)"
  }
}

variable "environment" {
  description = "Friendly environment name. Defaults to the Terraform workspace if unset."
  type        = string
  default     = null
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "List of public subnet CIDRs"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "List of private subnet CIDRs"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}

variable "enable_nat_gateway" {
  description = "Create a single NAT Gateway for private subnet egress"
  type        = bool
  default     = true
}

variable "asset_bucket_prefix" {
  description = "Prefix for the application asset bucket"
  type        = string
  default     = "twisted-monk-assets"
}

variable "create_rds" {
  description = "Whether to create an RDS instance"
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
  description = "DB engine version"
  type        = string
  default     = "15.3"
}

variable "skip_final_snapshot" {
  description = "Skip final snapshot on RDS deletion"
  type        = bool
  default     = true
}

variable "enable_eks" {
  description = "Whether to create a control-plane-only EKS cluster"
  type        = bool
  default     = false
}

variable "eks_cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "twisted-monk-eks"
}

variable "eks_version" {
  description = "EKS Kubernetes version"
  type        = string
  default     = "1.29"
}

variable "enable_flow_logs" {
  description = "Enable VPC flow logs to CloudWatch"
  type        = bool
  default     = true
}

variable "flow_log_retention_days" {
  description = "Retention in days for flow log CloudWatch log group"
  type        = number
  default     = 30
}

variable "vpc_flow_log_traffic_type" {
  description = "Traffic type to capture in flow logs (ACCEPT, REJECT, or ALL)"
  type        = string
  default     = "ALL"
}

variable "enable_rds_alarms" {
  description = "Enable CloudWatch alarms for the RDS instance"
  type        = bool
  default     = true
}

variable "alarm_email" {
  description = "Optional email address for alarm notifications"
  type        = string
  default     = ""
}

variable "rds_cpu_threshold" {
  description = "CPU utilization percentage that triggers the RDS alarm"
  type        = number
  default     = 75
}

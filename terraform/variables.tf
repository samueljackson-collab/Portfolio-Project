variable "terraform_backend_bucket" {
  description = "Optional override for the remote state S3 bucket"
  type        = string
  default     = ""
}

variable "terraform_backend_key" {
  description = "Optional override for the remote state object key"
  type        = string
  default     = ""
}

variable "terraform_backend_dynamodb_table" {
  description = "Optional override for the DynamoDB state lock table"
  type        = string
  default     = ""
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

variable "project_tag" {
  description = "Project name tag applied to all resources"
  type        = string
  default     = "twisted-monk"

  validation {
    condition     = length(var.project_tag) > 0
    error_message = "Project tag cannot be empty"
  }
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "List of public subnet CIDRs"
  type        = list(string)
  default     = ["10.0.1.0/24"]
}

variable "private_subnet_cidrs" {
  description = "List of private subnet CIDRs"
  type        = list(string)
  default     = ["10.0.101.0/24"]
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

variable "create_eks" {
  description = "Whether to create an EKS cluster"
  type        = bool
  default     = false
}

variable "eks_cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "twisted-monk-eks"
}
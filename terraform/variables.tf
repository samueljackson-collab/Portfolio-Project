variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]{1}$", var.aws_region))
    error_message = "Must be a valid AWS region format (e.g., us-east-1)"
  }
}

variable "tfstate_bucket_name" {
  description = "Name of the remote state S3 bucket (from bootstrap script)"
  type        = string
  default     = "REPLACE_TFSTATE_BUCKET_NAME"
}

variable "tfstate_region" {
  description = "AWS region where the remote state bucket lives"
  type        = string
  default     = "us-east-1"
}

variable "tfstate_lock_table" {
  description = "DynamoDB table used for Terraform state locking"
  type        = string
  default     = "REPLACE_TFSTATE_LOCK_TABLE"
}

variable "tfstate_key" {
  description = "Path/key inside the state bucket for this workspace"
  type        = string
  default     = "twisted-monk/terraform.tfstate"
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
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "staging"
}

variable "owner" {
  description = "Resource owner tag"
  type        = string
  default     = "platform-team"
}

variable "tf_backend_bucket" {
  description = "S3 bucket for Terraform state"
  type        = string
  default     = "replace-me-state"
}

variable "tf_backend_lock_table" {
  description = "DynamoDB table for state locking"
  type        = string
  default     = "replace-me-lock"
}

variable "vpc_cidr_block" {
  description = "CIDR block for VPC"
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
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}

variable "region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "Project tag"
  type        = string
  default     = "portfolio"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnets" {
  description = "Public subnet CIDRs"
  type        = list(string)
}

variable "private_subnets" {
  description = "Private subnet CIDRs"
  type        = list(string)
}

variable "data_subnets" {
  description = "Data subnet CIDRs"
  type        = list(string)
}

variable "instance_type" {
  description = "EC2 instance type for backend"
  type        = string
  default     = "t3.small"
}

variable "min_size" {
  description = "Minimum instances in Auto Scaling Group"
  type        = number
  default     = 1
}

variable "max_size" {
  description = "Maximum instances in Auto Scaling Group"
  type        = number
  default     = 3
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.small"
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "portfolio"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "portfolio"
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

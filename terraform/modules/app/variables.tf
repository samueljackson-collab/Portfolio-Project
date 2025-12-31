variable "project_tag" {
  description = "Project tag for naming"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "Target VPC ID"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR for the VPC"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for database/EKS"
  type        = list(string)
}

variable "asset_bucket_prefix" {
  description = "Prefix for application asset bucket"
  type        = string
}

variable "create_rds" {
  description = "Whether to create an RDS instance"
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
  description = "Database admin password (leave empty to generate)"
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
  description = "PostgreSQL engine version"
  type        = string
}

variable "skip_final_snapshot" {
  description = "Skip final snapshot on DB deletion"
  type        = bool
  default     = true
}

variable "enable_eks" {
  description = "Whether to create an EKS control plane"
  type        = bool
  default     = false
}

variable "eks_cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "twisted-monk-eks"
}

variable "eks_version" {
  description = "Kubernetes version for EKS"
  type        = string
  default     = "1.29"
}

variable "tags" {
  description = "Common tags to apply"
  type        = map(string)
  default     = {}
}

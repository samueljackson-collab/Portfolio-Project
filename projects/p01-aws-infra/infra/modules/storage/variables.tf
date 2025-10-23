variable "name" {
  description = "Resource name prefix"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "database_subnet_ids" {
  description = "IDs of database subnets"
  type        = list(string)
}

variable "database_security_group_id" {
  description = "Security group ID for database"
  type        = string
}

variable "engine" {
  description = "Database engine"
  type        = string
  default     = "postgres"
}

variable "engine_version" {
  description = "Database engine version"
  type        = string
  default     = "15.4"
}

variable "instance_class" {
  description = "Database instance class"
  type        = string
  default     = "db.m6g.large"
}

variable "allocated_storage" {
  description = "Initial allocated storage"
  type        = number
  default     = 100
}

variable "max_allocated_storage" {
  description = "Maximum storage for autoscaling"
  type        = number
  default     = 500
}

variable "backup_retention_period" {
  description = "Backup retention in days"
  type        = number
  default     = 35
}

variable "username" {
  description = "Master username for database"
  type        = string
}

variable "password" {
  description = "Master password for database"
  type        = string
  sensitive   = true
}

variable "kms_key_arn" {
  description = "KMS key ARN for encryption"
  type        = string
}

variable "enhanced_monitoring_role_arn" {
  description = "IAM role ARN for RDS enhanced monitoring"
  type        = string
}

variable "cdn_certificate_arn" {
  description = "ACM certificate ARN for CloudFront"
  type        = string
}

variable "cdn_price_class" {
  description = "CloudFront price class"
  type        = string
  default     = "PriceClass_100"
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
  default     = {}
}


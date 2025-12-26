variable "project_name" {
  description = "Name prefix for resources."
  type        = string
}

variable "environment" {
  description = "Environment name used for tagging."
  type        = string
}

variable "vpc_id" {
  description = "VPC ID for the RDS security group."
  type        = string
}

variable "db_subnet_ids" {
  description = "Subnet IDs for the DB subnet group."
  type        = list(string)
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access the database."
  type        = list(string)
  default     = []
}

variable "engine" {
  description = "Database engine (postgres or mysql)."
  type        = string
  default     = "postgres"

  validation {
    condition     = contains(["postgres", "mysql"], var.engine)
    error_message = "Engine must be postgres or mysql."
  }
}

variable "engine_version" {
  description = "Engine version."
  type        = string
  default     = "15.5"
}

variable "instance_class" {
  description = "Primary instance class."
  type        = string
  default     = "db.t3.medium"
}

variable "replica_instance_class" {
  description = "Read replica instance class."
  type        = string
  default     = "db.t3.medium"
}

variable "allocated_storage" {
  description = "Allocated storage in GB."
  type        = number
  default     = 20
}

variable "max_allocated_storage" {
  description = "Max autoscaled storage in GB."
  type        = number
  default     = 100
}

variable "db_name" {
  description = "Database name."
  type        = string
  default     = "app"
}

variable "username" {
  description = "Master username."
  type        = string
  default     = "appuser"
}

variable "port" {
  description = "Database port."
  type        = number
  default     = 5432
}

variable "multi_az" {
  description = "Enable Multi-AZ deployment."
  type        = bool
  default     = true
}

variable "read_replica_count" {
  description = "Number of read replicas to create."
  type        = number
  default     = 0
}

variable "backup_retention_period" {
  description = "Backup retention days."
  type        = number
  default     = 7
}

variable "backup_window" {
  description = "Preferred backup window."
  type        = string
  default     = "03:00-05:00"
}

variable "maintenance_window" {
  description = "Preferred maintenance window."
  type        = string
  default     = "Mon:05:00-Mon:06:00"
}

variable "parameter_group_family" {
  description = "Parameter group family."
  type        = string
  default     = "postgres15"
}

variable "parameters" {
  description = "List of parameters to apply."
  type        = list(object({
    name  = string
    value = string
  }))
  default = []
}

variable "storage_encrypted" {
  description = "Enable storage encryption."
  type        = bool
  default     = true
}

variable "kms_key_id" {
  description = "KMS key ID for storage encryption."
  type        = string
  default     = null
}

variable "secrets_manager_kms_key_id" {
  description = "KMS key ID for Secrets Manager."
  type        = string
  default     = null
}

variable "deletion_protection" {
  description = "Enable deletion protection."
  type        = bool
  default     = true
}

variable "skip_final_snapshot" {
  description = "Skip final snapshot on destroy."
  type        = bool
  default     = false
}

variable "final_snapshot_identifier" {
  description = "Final snapshot identifier when skip_final_snapshot is false."
  type        = string
  default     = "final-snapshot"
}

variable "apply_immediately" {
  description = "Apply changes immediately."
  type        = bool
  default     = false
}

variable "tags" {
  description = "Additional tags to apply."
  type        = map(string)
  default     = {}
}

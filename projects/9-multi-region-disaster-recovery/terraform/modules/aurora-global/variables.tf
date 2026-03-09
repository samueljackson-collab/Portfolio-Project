# Aurora Global Database Module Variables

variable "cluster_identifier" {
  description = "Identifier for the Aurora cluster"
  type        = string
}

variable "global_cluster_identifier" {
  description = "Identifier for the global cluster"
  type        = string
  default     = null
}

variable "is_primary" {
  description = "Whether this is the primary cluster"
  type        = bool
  default     = true
}

variable "enable_global_cluster" {
  description = "Whether to enable global cluster for multi-region DR"
  type        = bool
  default     = true
}

variable "engine_version" {
  description = "Aurora PostgreSQL engine version"
  type        = string
  default     = "15.4"
}

variable "database_name" {
  description = "Name of the default database"
  type        = string
  default     = "appdb"
}

variable "master_username" {
  description = "Master username for the database"
  type        = string
  default     = "admin"
}

variable "port" {
  description = "Database port"
  type        = number
  default     = 5432
}

variable "vpc_id" {
  description = "VPC ID where the cluster will be created"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for the DB subnet group"
  type        = list(string)
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to connect to the database"
  type        = list(string)
  default     = []
}

variable "allowed_security_groups" {
  description = "Security groups allowed to connect to the database"
  type        = list(string)
  default     = []
}

variable "cross_region_cidr_blocks" {
  description = "CIDR blocks from other regions for cross-region replication"
  type = list(object({
    region = string
    cidr   = string
  }))
  default = []
}

variable "instance_class" {
  description = "Instance class for Aurora instances"
  type        = string
  default     = "db.serverless"
}

variable "instance_count" {
  description = "Number of Aurora instances"
  type        = number
  default     = 2
}

variable "serverless_min_capacity" {
  description = "Minimum ACU capacity for serverless v2"
  type        = number
  default     = 0.5
}

variable "serverless_max_capacity" {
  description = "Maximum ACU capacity for serverless v2"
  type        = number
  default     = 16
}

variable "backup_retention_period" {
  description = "Number of days to retain backups"
  type        = number
  default     = 7
}

variable "preferred_backup_window" {
  description = "Daily time range for automated backups"
  type        = string
  default     = "03:00-04:00"
}

variable "preferred_maintenance_window" {
  description = "Weekly time range for maintenance"
  type        = string
  default     = "sun:04:00-sun:05:00"
}

variable "deletion_protection" {
  description = "Enable deletion protection"
  type        = bool
  default     = true
}

variable "skip_final_snapshot" {
  description = "Skip final snapshot when deleting"
  type        = bool
  default     = false
}

variable "auto_minor_version_upgrade" {
  description = "Enable auto minor version upgrade"
  type        = bool
  default     = true
}

variable "performance_insights_enabled" {
  description = "Enable Performance Insights"
  type        = bool
  default     = true
}

variable "enhanced_monitoring_interval" {
  description = "Enhanced monitoring interval (0 to disable)"
  type        = number
  default     = 60
}

variable "additional_cluster_parameters" {
  description = "Additional cluster parameter group parameters"
  type = list(object({
    name         = string
    value        = string
    apply_method = optional(string)
  }))
  default = []
}

variable "additional_db_parameters" {
  description = "Additional DB parameter group parameters"
  type = list(object({
    name         = string
    value        = string
    apply_method = optional(string)
  }))
  default = []
}

variable "alarm_actions" {
  description = "List of ARNs to notify when alarms trigger"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}

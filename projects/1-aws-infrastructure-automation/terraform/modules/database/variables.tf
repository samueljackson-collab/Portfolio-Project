###############################################################################
# Database Module - Input Variables
###############################################################################

variable "name_prefix" {
  description = "Prefix for resource names (e.g., 'portfolio-dev')."
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC where the RDS instance will be created."
  type        = string
}

variable "db_subnet_group_name" {
  description = "Name of the database subnet group."
  type        = string
}

#------------------------------------------------------------------------------
# Engine Configuration
#------------------------------------------------------------------------------

variable "engine" {
  description = "Database engine (postgres, mysql, mariadb)."
  type        = string
  default     = "postgres"
}

variable "engine_version" {
  description = "Database engine version."
  type        = string
  default     = "15.4"
}

variable "major_engine_version" {
  description = "Major engine version for option group."
  type        = string
  default     = "15"
}

variable "parameter_group_family" {
  description = "Parameter group family (e.g., postgres15)."
  type        = string
  default     = "postgres15"
}

variable "instance_class" {
  description = "RDS instance class."
  type        = string
  default     = "db.t3.medium"
}

#------------------------------------------------------------------------------
# Storage Configuration
#------------------------------------------------------------------------------

variable "allocated_storage" {
  description = "Initial allocated storage in GB."
  type        = number
  default     = 20
}

variable "max_allocated_storage" {
  description = "Maximum storage for autoscaling in GB."
  type        = number
  default     = 100
}

variable "storage_type" {
  description = "Storage type (gp3, gp2, io1)."
  type        = string
  default     = "gp3"
}

#------------------------------------------------------------------------------
# Database Configuration
#------------------------------------------------------------------------------

variable "database_name" {
  description = "Name of the database to create."
  type        = string
  default     = "portfolio"
}

variable "master_username" {
  description = "Master username for the database."
  type        = string
}

variable "master_password" {
  description = "Master password for the database."
  type        = string
  sensitive   = true
}

variable "port" {
  description = "Database port."
  type        = number
  default     = 5432
}

#------------------------------------------------------------------------------
# High Availability
#------------------------------------------------------------------------------

variable "multi_az" {
  description = "Enable Multi-AZ deployment."
  type        = bool
  default     = true
}

variable "create_read_replica" {
  description = "Create a read replica."
  type        = bool
  default     = false
}

variable "replica_instance_class" {
  description = "Instance class for the read replica."
  type        = string
  default     = "db.t3.medium"
}

#------------------------------------------------------------------------------
# Backup Configuration
#------------------------------------------------------------------------------

variable "backup_retention_period" {
  description = "Number of days to retain backups."
  type        = number
  default     = 7
}

variable "backup_window" {
  description = "Preferred backup window (UTC)."
  type        = string
  default     = "03:00-04:00"
}

variable "maintenance_window" {
  description = "Preferred maintenance window (UTC)."
  type        = string
  default     = "Mon:04:00-Mon:05:00"
}

#------------------------------------------------------------------------------
# Security Configuration
#------------------------------------------------------------------------------

variable "allowed_security_groups" {
  description = "List of security group IDs allowed to connect."
  type        = list(string)
  default     = []
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to connect (use with caution)."
  type        = list(string)
  default     = []
}

variable "create_kms_key" {
  description = "Create a new KMS key for encryption."
  type        = bool
  default     = true
}

variable "kms_key_id" {
  description = "Existing KMS key ID for encryption (if not creating new)."
  type        = string
  default     = null
}

variable "deletion_protection" {
  description = "Enable deletion protection."
  type        = bool
  default     = false
}

variable "skip_final_snapshot" {
  description = "Skip final snapshot when destroying."
  type        = bool
  default     = false
}

#------------------------------------------------------------------------------
# Performance and Monitoring
#------------------------------------------------------------------------------

variable "performance_insights_enabled" {
  description = "Enable Performance Insights."
  type        = bool
  default     = true
}

variable "performance_insights_retention_period" {
  description = "Performance Insights retention period in days."
  type        = number
  default     = 7
}

variable "monitoring_interval" {
  description = "Enhanced monitoring interval in seconds (0 to disable)."
  type        = number
  default     = 60
}

variable "enabled_cloudwatch_logs_exports" {
  description = "List of log types to export to CloudWatch."
  type        = list(string)
  default     = ["postgresql", "upgrade"]
}

variable "auto_minor_version_upgrade" {
  description = "Enable automatic minor version upgrades."
  type        = bool
  default     = true
}

variable "apply_immediately" {
  description = "Apply changes immediately (vs. during maintenance window)."
  type        = bool
  default     = false
}

#------------------------------------------------------------------------------
# Parameter Group Settings
#------------------------------------------------------------------------------

variable "log_min_duration_statement" {
  description = "Minimum duration (ms) for statement logging (-1 to disable)."
  type        = string
  default     = "1000"
}

variable "max_connections" {
  description = "Maximum database connections."
  type        = string
  default     = "100"
}

variable "work_mem" {
  description = "Work memory per operation (KB)."
  type        = string
  default     = "4096"
}

variable "maintenance_work_mem" {
  description = "Maintenance work memory (KB)."
  type        = string
  default     = "65536"
}

variable "log_statement" {
  description = "Statement logging level (none, ddl, mod, all)."
  type        = string
  default     = "ddl"
}

#------------------------------------------------------------------------------
# CloudWatch Alarms
#------------------------------------------------------------------------------

variable "create_cloudwatch_alarms" {
  description = "Create CloudWatch alarms for the RDS instance."
  type        = bool
  default     = true
}

variable "alarm_actions" {
  description = "List of ARNs to notify when alarms trigger."
  type        = list(string)
  default     = []
}

variable "cpu_utilization_threshold" {
  description = "CPU utilization alarm threshold (percentage)."
  type        = number
  default     = 80
}

variable "free_storage_threshold" {
  description = "Free storage alarm threshold (bytes)."
  type        = number
  default     = 5368709120  # 5 GB
}

variable "database_connections_threshold" {
  description = "Database connections alarm threshold."
  type        = number
  default     = 80
}

variable "freeable_memory_threshold" {
  description = "Freeable memory alarm threshold (bytes)."
  type        = number
  default     = 268435456  # 256 MB
}

#------------------------------------------------------------------------------
# Tags
#------------------------------------------------------------------------------

variable "tags" {
  description = "Tags to apply to all resources."
  type        = map(string)
  default     = {}
}

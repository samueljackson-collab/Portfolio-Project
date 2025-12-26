variable "aws_region" {
  type        = string
  description = "AWS region for simulator deployments"
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Project label for tagging"
  default     = "security-simulators"
}

variable "environment" {
  type        = string
  description = "Deployment environment"
  default     = "dev"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR for the shared VPC"
  default     = "10.90.0.0/16"
}

variable "db_username" {
  type        = string
  description = "Database admin username"
  default     = "sim_user"
}

variable "db_password" {
  type        = string
  description = "Database admin password"
  default     = "ChangeMe123!"
  sensitive   = true
}

variable "db_instance_class" {
  type        = string
  description = "RDS instance class"
  default     = "db.t3.small"
}

variable "db_allocated_storage" {
  type        = number
  description = "Allocated storage in GiB"
  default     = 20
}

variable "db_max_allocated_storage" {
  type        = number
  description = "Max autoscaled storage in GiB"
  default     = 100
}

variable "container_images" {
  type        = map(string)
  description = "Optional override for container images per simulator"
  default     = {}
}

variable "enable_red_team_alarm" {
  type        = bool
  description = "Enable CloudWatch alarm for red team detections"
  default     = true
}

variable "enable_backup_vault" {
  type        = bool
  description = "Deploy AWS Backup vault for ransomware drills"
  default     = true
}

variable "enable_hunting_athena" {
  type        = bool
  description = "Toggle Athena workgroup for hunt result storage"
  default     = false
}

variable "enable_opensearch" {
  type        = bool
  description = "Toggle OpenSearch domain for SOC analytics"
  default     = false
}

variable "enable_hunt_notifications" {
  type        = bool
  description = "Enable SNS topic for hunt notifications"
  default     = false
}

variable "extra_tags" {
  type        = map(string)
  description = "Additional tags to apply to resources"
  default     = {}
}

# OpenSearch Module Variables

variable "project_name" {
  type        = string
  description = "Project identifier for resource naming"
}

variable "environment" {
  type        = string
  description = "Environment name (dev, staging, prod)"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID where OpenSearch will be deployed"
}

variable "vpc_cidr" {
  type        = string
  description = "VPC CIDR block for security group rules"
}

variable "subnet_ids" {
  type        = list(string)
  description = "Subnet IDs for OpenSearch domain (private subnets recommended)"
}

#------------------------------------------------------------------------------
# OpenSearch Configuration
#------------------------------------------------------------------------------

variable "engine_version" {
  type        = string
  description = "OpenSearch engine version"
  default     = "OpenSearch_2.11"
}

variable "instance_type" {
  type        = string
  description = "Instance type for data nodes"
  default     = "t3.small.search"
}

variable "instance_count" {
  type        = number
  description = "Number of instances in the cluster"
  default     = 3

  validation {
    condition     = var.instance_count >= 1
    error_message = "Instance count must be at least 1"
  }
}

variable "dedicated_master_enabled" {
  type        = bool
  description = "Enable dedicated master nodes"
  default     = false
}

variable "dedicated_master_type" {
  type        = string
  description = "Instance type for dedicated master nodes"
  default     = "t3.small.search"
}

variable "dedicated_master_count" {
  type        = number
  description = "Number of dedicated master nodes"
  default     = 3

  validation {
    condition     = var.dedicated_master_count == 3 || var.dedicated_master_count == 5
    error_message = "Dedicated master count must be 3 or 5"
  }
}

variable "zone_awareness_enabled" {
  type        = bool
  description = "Enable zone awareness (multi-AZ)"
  default     = true
}

variable "availability_zone_count" {
  type        = number
  description = "Number of availability zones"
  default     = 3

  validation {
    condition     = contains([2, 3], var.availability_zone_count)
    error_message = "Availability zone count must be 2 or 3"
  }
}

#------------------------------------------------------------------------------
# EBS Configuration
#------------------------------------------------------------------------------

variable "ebs_volume_type" {
  type        = string
  description = "EBS volume type (gp2, gp3, io1)"
  default     = "gp3"

  validation {
    condition     = contains(["gp2", "gp3", "io1"], var.ebs_volume_type)
    error_message = "EBS volume type must be gp2, gp3, or io1"
  }
}

variable "ebs_volume_size" {
  type        = number
  description = "EBS volume size in GB"
  default     = 20

  validation {
    condition     = var.ebs_volume_size >= 10 && var.ebs_volume_size <= 3584
    error_message = "EBS volume size must be between 10 and 3584 GB"
  }
}

variable "ebs_iops" {
  type        = number
  description = "IOPS for EBS volume (gp3 or io1)"
  default     = 3000
}

variable "ebs_throughput" {
  type        = number
  description = "Throughput for gp3 volumes in MB/s"
  default     = 125
}

#------------------------------------------------------------------------------
# Security Configuration
#------------------------------------------------------------------------------

variable "kms_key_id" {
  type        = string
  description = "KMS key ID for encryption at rest (leave empty to use AWS managed key)"
  default     = ""
}

variable "advanced_security_enabled" {
  type        = bool
  description = "Enable fine-grained access control"
  default     = true
}

variable "internal_user_database_enabled" {
  type        = bool
  description = "Enable internal user database for authentication"
  default     = true
}

variable "master_user_name" {
  type        = string
  description = "Master username for OpenSearch"
  default     = "admin"
  sensitive   = true
}

variable "master_user_password" {
  type        = string
  description = "Master password for OpenSearch (min 8 characters)"
  sensitive   = true

  validation {
    condition     = length(var.master_user_password) >= 8
    error_message = "Master user password must be at least 8 characters"
  }
}

variable "allowed_cidr_blocks" {
  type        = list(string)
  description = "CIDR blocks allowed to access OpenSearch"
  default     = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
}

#------------------------------------------------------------------------------
# Backup Configuration
#------------------------------------------------------------------------------

variable "snapshot_start_hour" {
  type        = number
  description = "Hour of day (UTC) to start automated snapshots"
  default     = 3

  validation {
    condition     = var.snapshot_start_hour >= 0 && var.snapshot_start_hour <= 23
    error_message = "Snapshot start hour must be between 0 and 23"
  }
}

#------------------------------------------------------------------------------
# Logging Configuration
#------------------------------------------------------------------------------

variable "log_retention_days" {
  type        = number
  description = "CloudWatch log retention in days"
  default     = 7

  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.log_retention_days)
    error_message = "Log retention must be a valid CloudWatch retention period"
  }
}

#------------------------------------------------------------------------------
# Monitoring Configuration
#------------------------------------------------------------------------------

variable "alarm_actions" {
  type        = list(string)
  description = "SNS topic ARNs for CloudWatch alarms"
  default     = []
}

variable "free_storage_threshold" {
  type        = number
  description = "Free storage space threshold in MB for alarm"
  default     = 2048 # 2 GB
}

variable "cpu_threshold" {
  type        = number
  description = "CPU utilization threshold percentage for alarm"
  default     = 80

  validation {
    condition     = var.cpu_threshold >= 0 && var.cpu_threshold <= 100
    error_message = "CPU threshold must be between 0 and 100"
  }
}

variable "jvm_memory_threshold" {
  type        = number
  description = "JVM memory pressure threshold percentage for alarm"
  default     = 85

  validation {
    condition     = var.jvm_memory_threshold >= 0 && var.jvm_memory_threshold <= 100
    error_message = "JVM memory threshold must be between 0 and 100"
  }
}

#------------------------------------------------------------------------------
# IAM Configuration
#------------------------------------------------------------------------------

variable "create_service_linked_role" {
  type        = bool
  description = "Create IAM service-linked role for OpenSearch"
  default     = true
}

#------------------------------------------------------------------------------
# Tags
#------------------------------------------------------------------------------

variable "tags" {
  type        = map(string)
  description = "Additional tags for all resources"
  default     = {}
}

# Root Terraform Variables for SIEM Pipeline

#------------------------------------------------------------------------------
# General Configuration
#------------------------------------------------------------------------------

variable "aws_region" {
  type        = string
  description = "AWS region for SIEM deployment"
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Project identifier for resource naming"
}

variable "environment" {
  type        = string
  description = "Environment name (dev, staging, prod)"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod"
  }
}

#------------------------------------------------------------------------------
# Network Configuration
#------------------------------------------------------------------------------

variable "create_vpc" {
  type        = bool
  description = "Create new VPC or use existing"
  default     = false
}

variable "use_default_vpc" {
  type        = bool
  description = "Use default VPC (only if create_vpc = false)"
  default     = false
}

variable "vpc_id" {
  type        = string
  description = "VPC ID (required if create_vpc = false and use_default_vpc = false)"
  default     = ""
}

variable "subnet_ids" {
  type        = list(string)
  description = "Subnet IDs for OpenSearch (private subnets recommended)"
  default     = []
}

#------------------------------------------------------------------------------
# OpenSearch Configuration
#------------------------------------------------------------------------------

variable "opensearch_engine_version" {
  type        = string
  description = "OpenSearch engine version"
  default     = "OpenSearch_2.11"
}

variable "opensearch_instance_type" {
  type        = string
  description = "Instance type for OpenSearch data nodes"
  default     = "t3.small.search"
}

variable "opensearch_instance_count" {
  type        = number
  description = "Number of instances in OpenSearch cluster"
  default     = 3
}

variable "opensearch_zone_awareness" {
  type        = bool
  description = "Enable multi-AZ deployment"
  default     = true
}

variable "opensearch_az_count" {
  type        = number
  description = "Number of availability zones"
  default     = 3

  validation {
    condition     = contains([2, 3], var.opensearch_az_count)
    error_message = "AZ count must be 2 or 3"
  }
}

variable "opensearch_dedicated_master" {
  type        = bool
  description = "Enable dedicated master nodes"
  default     = false
}

variable "opensearch_master_type" {
  type        = string
  description = "Instance type for dedicated master nodes"
  default     = "t3.small.search"
}

variable "opensearch_master_count" {
  type        = number
  description = "Number of dedicated master nodes"
  default     = 3
}

variable "opensearch_ebs_type" {
  type        = string
  description = "EBS volume type"
  default     = "gp3"
}

variable "opensearch_ebs_size" {
  type        = number
  description = "EBS volume size in GB"
  default     = 20
}

variable "opensearch_master_user" {
  type        = string
  description = "Master username for OpenSearch"
  default     = "admin"
  sensitive   = true
}

variable "opensearch_master_password" {
  type        = string
  description = "Master password for OpenSearch (min 8 characters)"
  sensitive   = true

  validation {
    condition     = length(var.opensearch_master_password) >= 8
    error_message = "Password must be at least 8 characters"
  }
}

variable "opensearch_index_name" {
  type        = string
  description = "Name of the OpenSearch index"
  default     = "security-events"
}

#------------------------------------------------------------------------------
# Log Sources Configuration
#------------------------------------------------------------------------------

variable "enable_guardduty" {
  type        = bool
  description = "Enable GuardDuty and log ingestion"
  default     = true
}

variable "enable_cloudtrail" {
  type        = bool
  description = "Enable CloudTrail and log ingestion"
  default     = true
}

#------------------------------------------------------------------------------
# Kinesis Firehose Configuration
#------------------------------------------------------------------------------

variable "lambda_zip_path" {
  type        = string
  description = "Path to Lambda function ZIP file"
  default     = "../lambda/log_transformer.zip"
}

variable "firehose_buffer_size" {
  type        = number
  description = "Firehose buffer size in MB"
  default     = 5
}

variable "firehose_buffer_interval" {
  type        = number
  description = "Firehose buffer interval in seconds"
  default     = 300
}

#------------------------------------------------------------------------------
# Alerting Configuration
#------------------------------------------------------------------------------

variable "alert_email" {
  type        = string
  description = "Email address for security alerts"
  default     = ""
}

variable "sns_kms_key_id" {
  type        = string
  description = "KMS key ID for SNS topic encryption"
  default     = ""
}

#------------------------------------------------------------------------------
# Monitoring Configuration
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

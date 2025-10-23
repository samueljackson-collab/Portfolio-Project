variable "project_name" {
  description = "Canonical project name"
  type        = string
}

variable "environment" {
  description = "Environment identifier"
  type        = string
  default     = "prod"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "owner" {
  description = "Business owner of the environment"
  type        = string
}

variable "cost_center" {
  description = "Cost center for tagging"
  type        = string
}

variable "additional_tags" {
  description = "Additional tags applied to resources"
  type        = map(string)
  default     = {}
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
}

variable "public_subnets" {
  description = "Public subnet definitions"
  type = map(object({
    cidr = string
    az   = string
  }))
}

variable "private_subnets" {
  description = "Private subnet definitions"
  type = map(object({
    cidr = string
    az   = string
  }))
}

variable "database_subnets" {
  description = "Database subnet definitions"
  type = map(object({
    cidr = string
    az   = string
  }))
}

variable "enable_nat_gateways" {
  description = "Whether NAT gateways are created"
  type        = bool
  default     = true
}

variable "ssm_prefix_list_ids" {
  description = "Prefix list IDs for SSM endpoints"
  type        = list(string)
  default     = []
}

variable "ami_id" {
  description = "AMI for compute instances"
  type        = string
}

variable "instance_type" {
  description = "Instance type for compute"
  type        = string
  default     = "t3.medium"
}

variable "root_block_device" {
  description = "Root block device configuration"
  type = object({
    device_name = string
    volume_size = number
    volume_type = string
  })
  default = {
    device_name = "/dev/xvda"
    volume_size = 30
    volume_type = "gp3"
  }
}

variable "ssm_instance_profile" {
  description = "IAM instance profile for compute"
  type        = string
}

variable "log_level" {
  description = "Application log level"
  type        = string
  default     = "info"
}

variable "app_port" {
  description = "Application port"
  type        = number
  default     = 8080
}

variable "health_check_path" {
  description = "ALB health check path"
  type        = string
  default     = "/healthz"
}

variable "acm_certificate_arn" {
  description = "ACM certificate ARN"
  type        = string
}

variable "alb_ssl_policy" {
  description = "SSL policy for ALB"
  type        = string
  default     = "ELBSecurityPolicy-TLS13-1-2-2021-06"
}

variable "min_size" {
  description = "Minimum ASG size"
  type        = number
  default     = 2
}

variable "max_size" {
  description = "Maximum ASG size"
  type        = number
  default     = 6
}

variable "desired_capacity" {
  description = "Desired ASG capacity"
  type        = number
  default     = 3
}

variable "database_engine" {
  description = "Database engine"
  type        = string
  default     = "postgres"
}

variable "database_engine_version" {
  description = "Database engine version"
  type        = string
  default     = "15.4"
}

variable "database_instance_class" {
  description = "Instance class for database"
  type        = string
  default     = "db.m6g.large"
}

variable "database_allocated_storage" {
  description = "Allocated storage for database"
  type        = number
  default     = 100
}

variable "database_max_allocated_storage" {
  description = "Max allocated storage for database"
  type        = number
  default     = 500
}

variable "database_backup_retention" {
  description = "Backup retention period"
  type        = number
  default     = 35
}

variable "database_username" {
  description = "Database master username"
  type        = string
}

variable "database_password" {
  description = "Database master password"
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
  description = "Certificate ARN for CloudFront"
  type        = string
}

variable "cdn_price_class" {
  description = "CloudFront price class"
  type        = string
  default     = "PriceClass_100"
}


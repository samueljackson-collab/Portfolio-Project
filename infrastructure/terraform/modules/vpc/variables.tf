# VPC Module Variables

variable "project_name" {
  type        = string
  description = "Project identifier for resource naming"
}

variable "environment" {
  type        = string
  description = "Environment name (dev, staging, prod)"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC"
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid IPv4 CIDR block"
  }
}

variable "az_count" {
  type        = number
  description = "Number of availability zones to use (max 3)"
  default     = 2

  validation {
    condition     = var.az_count >= 1 && var.az_count <= 3
    error_message = "AZ count must be between 1 and 3"
  }
}

variable "enable_dns_hostnames" {
  type        = bool
  description = "Enable DNS hostnames in the VPC"
  default     = true
}

variable "enable_dns_support" {
  type        = bool
  description = "Enable DNS support in the VPC"
  default     = true
}

variable "map_public_ip_on_launch" {
  type        = bool
  description = "Auto-assign public IP to instances launched in public subnets"
  default     = true
}

variable "enable_nat_gateway" {
  type        = bool
  description = "Enable NAT Gateway for private subnet internet access"
  default     = true
}

variable "single_nat_gateway" {
  type        = bool
  description = "Use single NAT Gateway for all AZs (cost savings vs high availability)"
  default     = false
}

variable "enable_flow_logs" {
  type        = bool
  description = "Enable VPC Flow Logs for network monitoring"
  default     = true
}

variable "flow_logs_retention_days" {
  type        = number
  description = "CloudWatch log retention for VPC Flow Logs"
  default     = 7

  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.flow_logs_retention_days)
    error_message = "Flow logs retention must be a valid CloudWatch retention period"
  }
}

variable "enable_s3_endpoint" {
  type        = bool
  description = "Enable S3 VPC Endpoint for private S3 access"
  default     = true
}

variable "tags" {
  type        = map(string)
  description = "Additional tags for all resources"
  default     = {}
}

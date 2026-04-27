# VPC Module Input Variables
# Purpose: Define all configurable parameters for VPC module
# Usage: Called from environment-specific configurations (dev/staging/prod)
# 
# Variable Design Philosophy:
# - Sensible defaults for rapid deployment
# - Override capability for customization
# - Type constraints for validation
# - Descriptions explaining purpose and valid values

variable "project_name" {
  description = "Project name used for resource naming and tagging. Should be short, lowercase, alphanumeric."
  type        = string
  
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "Project name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "environment" {
  description = "Environment name (dev, staging, prod). Affects resource sizing and redundancy."
  type        = string
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "vpc_cidr" {
  description = <<-EOT
    CIDR block for the VPC. Must be a valid private IPv4 range (RFC 1918).
    Recommended: /16 for production (65,536 IPs), /20 for dev (4,096 IPs).
    Examples: 10.0.0.0/16, 172.16.0.0/16, 192.168.0.0/16
  EOT
  type        = string
  default     = "10.0.0.0/16"
  
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid IPv4 CIDR block."
  }
}

variable "enable_nat_gateway" {
  description = <<-EOT
    Enable NAT Gateways for private subnet internet access.
    Production: true (high availability, one NAT per AZ, ~$100/month)
    Development: false (use single NAT or none, saves cost)
    Note: Without NAT, private instances cannot reach internet (no yum updates, no API calls)
  EOT
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = <<-EOT
    Use a single NAT Gateway instead of one per AZ.
    Cost savings: ~$66/month (vs. 3 NAT Gateways)
    Downside: Single point of failure, cross-AZ data transfer charges
    Recommended: true for dev/staging, false for production
  EOT
  type        = bool
  default     = false
}

variable "enable_flow_logs" {
  description = <<-EOT
    Enable VPC Flow Logs for network traffic monitoring.
    Use cases: Security analysis, troubleshooting, compliance
    Cost: ~$0.50 per GB ingested to CloudWatch (can be expensive)
    Recommended: true for production, false for dev to save cost
  EOT
  type        = bool
  default     = true
}

variable "flow_logs_retention_days" {
  description = "CloudWatch Logs retention period for VPC Flow Logs. Lower = less cost."
  type        = number
  default     = 7
  
  validation {
    condition = contains([
      0, 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653
    ], var.flow_logs_retention_days)
    error_message = "Retention days must be a valid CloudWatch Logs retention period."
  }
}

variable "enable_s3_endpoint" {
  description = <<-EOT
    Create VPC endpoint for S3 (Gateway type, FREE).
    Benefits: Private S3 access, no NAT costs, improved security
    Recommended: true (no cost, only benefits)
  EOT
  type        = bool
  default     = true
}

variable "enable_dynamodb_endpoint" {
  description = "Create VPC endpoint for DynamoDB (Gateway type, FREE). Enable if using DynamoDB."
  type        = bool
  default     = false
}

variable "enable_ecr_endpoints" {
  description = <<-EOT
    Create VPC endpoints for ECR (Elastic Container Registry).
    Required if: Pulling Docker images from ECR in private subnets
    Cost: ~$21.60/month (2 endpoints × 3 AZs × $3.60/month)
    Recommended: true if using ECS/EKS, false otherwise
  EOT
  type        = bool
  default     = false
}

variable "enable_ssm_endpoints" {
  description = <<-EOT
    Create VPC endpoints for Systems Manager (SSM).
    Benefits: EC2 management without SSH, no bastion needed, Session Manager access
    Cost: ~$21.60/month (3 endpoints × 3 AZs × $2.40/month)
    Recommended: true (eliminates need for bastion, improves security)
  EOT
  type        = bool
  default     = true
}

variable "common_tags" {
  description = <<-EOT
    Common tags applied to all resources.
    Best practice: Include Project, Environment, Owner, CostCenter, Terraform
    Tags enable cost allocation, resource filtering, and automation
  EOT
  type        = map(string)
  default     = {}
}

variable "azs_count" {
  description = <<-EOT
    Number of Availability Zones to use (2 or 3).
    Production: 3 AZs for maximum availability
    Development: 2 AZs to reduce cost (fewer NAT Gateways, subnets)
    Note: Some regions only have 2 AZs available
  EOT
  type        = number
  default     = 3
  
  validation {
    condition     = var.azs_count >= 2 && var.azs_count <= 3
    error_message = "AZ count must be 2 or 3."
  }
}

variable "enable_dns_hostnames" {
  description = "Enable DNS hostnames in VPC. Required for most use cases (ELB, RDS, etc.)."
  type        = bool
  default     = true
}

variable "enable_dns_support" {
  description = "Enable DNS resolution in VPC. Should always be true."
  type        = bool
  default     = true
}

# Advanced Variables for Fine-Tuning

variable "public_subnet_suffix" {
  description = "Suffix for public subnet names. Useful for multi-region deployments."
  type        = string
  default     = "public"
}

variable "private_app_subnet_suffix" {
  description = "Suffix for private application subnet names."
  type        = string
  default     = "private-app"
}

variable "private_db_subnet_suffix" {
  description = "Suffix for private database subnet names."
  type        = string
  default     = "private-db"
}

variable "map_public_ip_on_launch" {
  description = "Auto-assign public IP to instances in public subnets. Typically true for public subnets."
  type        = bool
  default     = true
}

variable "enable_nat_gateway_per_az" {
  description = <<-EOT
    Create one NAT Gateway per AZ for high availability.
    If false and enable_nat_gateway is true, creates single NAT Gateway.
    Overrides single_nat_gateway variable for explicit control.
  EOT
  type        = bool
  default     = true
}

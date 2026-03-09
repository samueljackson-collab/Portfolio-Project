###############################################################################
# Networking Module - Input Variables
###############################################################################

variable "name_prefix" {
  description = "Prefix for resource names (e.g., 'portfolio-dev')."
  type        = string
}

variable "region" {
  description = "AWS region for VPC endpoints and other regional services."
  type        = string
  default     = "us-west-2"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC (e.g., '10.0.0.0/16')."
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones for subnet distribution."
  type        = list(string)
  default     = ["us-west-2a", "us-west-2b", "us-west-2c"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets (one per AZ)."
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets (one per AZ)."
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
}

variable "database_subnet_cidrs" {
  description = "CIDR blocks for database subnets (one per AZ)."
  type        = list(string)
  default     = ["10.0.21.0/24", "10.0.22.0/24", "10.0.23.0/24"]
}

variable "enable_nat_gateway" {
  description = "Enable NAT gateway for private subnet internet access."
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use a single NAT gateway for all AZs (cost savings for non-prod)."
  type        = bool
  default     = false
}

variable "enable_flow_logs" {
  description = "Enable VPC Flow Logs for network traffic monitoring."
  type        = bool
  default     = true
}

variable "flow_logs_retention_days" {
  description = "Number of days to retain VPC Flow Logs."
  type        = number
  default     = 30
}

variable "enable_vpc_endpoints" {
  description = "Create VPC endpoints for S3 and DynamoDB."
  type        = bool
  default     = true
}

variable "create_custom_nacls" {
  description = "Create custom Network ACLs for subnets."
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags to apply to all resources."
  type        = map(string)
  default     = {}
}

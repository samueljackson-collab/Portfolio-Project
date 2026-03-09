variable "project_name" {
  description = "Name prefix for resources."
  type        = string
}

variable "environment" {
  description = "Environment name used for tagging."
  type        = string
}

variable "region" {
  description = "AWS region for endpoint service names."
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "azs" {
  description = "Optional list of availability zones to use. Defaults to all available AZs."
  type        = list(string)
  default     = []
}

variable "public_subnet_cidrs" {
  description = "List of CIDR blocks for public subnets."
  type        = list(string)

  validation {
    condition     = length(var.public_subnet_cidrs) > 0
    error_message = "At least one public subnet CIDR must be provided."
  }
  validation {
    condition     = length(var.azs) == 0 || length(var.public_subnet_cidrs) == length(var.azs)
    error_message = "Public subnet CIDR count must match the number of AZs when azs is provided."
  }
}

variable "private_subnet_cidrs" {
  description = "List of CIDR blocks for private subnets."
  type        = list(string)

  validation {
    condition     = length(var.private_subnet_cidrs) > 0
    error_message = "At least one private subnet CIDR must be provided."
  }
  validation {
    condition     = length(var.azs) == 0 || length(var.private_subnet_cidrs) == length(var.azs)
    error_message = "Private subnet CIDR count must match the number of AZs when azs is provided."
  }
}

variable "enable_nat_gateway" {
  description = "Whether to create NAT gateways for private subnet egress."
  type        = bool
  default     = true
}

variable "enable_flow_logs" {
  description = "Enable VPC flow logs to CloudWatch."
  type        = bool
  default     = true
}

variable "flow_logs_retention_in_days" {
  description = "CloudWatch log retention period for VPC flow logs."
  type        = number
  default     = 30
}

variable "enable_vpc_endpoints" {
  description = "Enable VPC endpoints for gateway and interface services."
  type        = bool
  default     = true
}

variable "gateway_endpoints" {
  description = "Gateway endpoints to create (e.g., s3, dynamodb)."
  type        = list(string)
  default     = ["s3", "dynamodb"]
}

variable "interface_endpoints" {
  description = "Interface endpoints to create (e.g., logs, ec2, ssm)."
  type        = list(string)
  default     = ["logs", "ec2", "ssm"]
}

variable "tags" {
  description = "Additional tags to apply."
  type        = map(string)
  default     = {}
}

locals {
  az_count = length(var.azs) > 0 ? length(var.azs) : length(data.aws_availability_zones.available.names)
}

variable "validate_subnet_counts" {
  description = "Internal helper to validate subnet list lengths."
  type        = bool
  default     = true

  validation {
    condition     = !var.validate_subnet_counts || length(var.public_subnet_cidrs) == length(var.private_subnet_cidrs)
    error_message = "Public and private subnet CIDR lists must be the same length."
  }
}

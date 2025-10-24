variable "project_name" {
  description = "Project name used in resource tags."
  type        = string
}

variable "environment" {
  description = "Environment name used in resource tags."
  type        = string
}

variable "cidr_block" {
  description = "CIDR block for the VPC."
  type        = string
}

variable "availability_zones" {
  description = "List of availability zones for the subnets."
  type        = list(string)
  validation {
    condition     = length(var.availability_zones) >= 2
    error_message = "Provide at least two availability zones for a multi-AZ deployment."
  }
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for the public subnets. Must align with the number of availability zones."
  type        = list(string)
}

variable "private_app_subnet_cidrs" {
  description = "CIDR blocks for the application subnets. Must align with the number of availability zones."
  type        = list(string)
}

variable "database_subnet_cidrs" {
  description = "CIDR blocks for the database subnets. Must align with the number of availability zones."
  type        = list(string)
}

variable "tags" {
  description = "Tags applied to created resources."
  type        = map(string)
  default     = {}
}

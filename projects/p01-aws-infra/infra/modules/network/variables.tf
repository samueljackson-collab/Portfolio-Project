variable "name" {
  description = "Prefix used for naming AWS resources"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
}

variable "public_subnets" {
  description = "Map of public subnet definitions"
  type = map(object({
    cidr = string
    az   = string
    tags = optional(map(string), {})
  }))
}

variable "private_subnets" {
  description = "Map of private subnet definitions"
  type = map(object({
    cidr = string
    az   = string
    tags = optional(map(string), {})
  }))
}

variable "database_subnets" {
  description = "Map of database subnet definitions"
  type = map(object({
    cidr = string
    az   = string
    tags = optional(map(string), {})
  }))
}

variable "enable_nat_gateways" {
  description = "Whether to create NAT gateways for private subnets"
  type        = bool
  default     = true
}

variable "app_port" {
  description = "Application port exposed by compute instances"
  type        = number
  default     = 8080
}

variable "database_port" {
  description = "Port used by the database tier"
  type        = number
  default     = 5432
}

variable "ssm_prefix_list_ids" {
  description = "Prefix list IDs that allow SSM connectivity"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Base tags applied to all resources"
  type        = map(string)
  default     = {}
}


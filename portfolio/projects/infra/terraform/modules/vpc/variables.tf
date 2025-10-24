variable "name" {
  type        = string
  description = "Prefix for tagging resources"
}

variable "cidr_block" {
  type        = string
  description = "CIDR block for the VPC"
}

variable "public_subnets" {
  description = "Map of public subnet definitions"
  type = map(object({
    cidr = string
    az   = string
  }))
}

variable "private_subnets" {
  description = "Map of private subnet definitions"
  type = map(object({
    cidr = string
    az   = string
  }))
}

variable "tags" {
  type        = map(string)
  description = "Additional resource tags"
  default     = {}
}

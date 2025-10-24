variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "vpc_cidr" {
  type = string
}

variable "azs" {
  description = "List of availability zones used for subnets."
  type        = list(string)
}

variable "tags" {
  description = "Map of common resource tags."
  type        = map(string)
  default     = {}
}

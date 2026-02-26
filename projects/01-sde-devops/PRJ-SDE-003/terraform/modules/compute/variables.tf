variable "project_name" {
  description = "Project identifier used for naming."
  type        = string
}

variable "environment" {
  description = "Environment name (dev/staging/prod)."
  type        = string
}

variable "vpc_id" {
  description = "VPC to attach compute resources to."
  type        = string
}

variable "public_subnet_ids" {
  description = "Public subnets for load balancers."
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "Private subnets for application instances."
  type        = list(string)
}

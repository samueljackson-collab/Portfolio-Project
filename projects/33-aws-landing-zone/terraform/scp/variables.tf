variable "aws_region" {
  description = "AWS region for the SCP module provider"
  type        = string
  default     = "us-east-1"
}

variable "workloads_ou_id" {
  description = "OU ID for the Workloads organizational unit (restrict-regions applied here)"
  type        = string
}

variable "security_ou_id" {
  description = "OU ID for the Security organizational unit (deny-igw applied here)"
  type        = string
}

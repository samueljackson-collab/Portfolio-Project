variable "project_name" {
  type        = string
  description = "Identifier for the networking blueprint"
  default     = "networking-datacenter"
}

variable "region" {
  type        = string
  description = "Region or site code"
  default     = "local"
}

variable "project_name" {
  type        = string
  description = "Short name used for tagging and resource prefixes"
  default     = "cloud-architecture"
}

variable "region" {
  type        = string
  description = "AWS region for provisioning"
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Identifier for tagging and parameter naming"
  default     = "cloud-solutions"
}

variable "region" {
  type        = string
  description = "Deployment region"
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project identifier used for naming."
  type        = string
}

variable "environment" {
  description = "Environment name (dev/staging/prod)."
  type        = string
}

variable "domain_name" {
  description = "Primary domain for CDN configuration."
  type        = string
  default     = null
}

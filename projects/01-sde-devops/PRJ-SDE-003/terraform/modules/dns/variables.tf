variable "project_name" {
  description = "Project identifier used for naming."
  type        = string
}

variable "environment" {
  description = "Environment name (dev/staging/prod)."
  type        = string
}

variable "root_domain" {
  description = "Base domain managed in Route53."
  type        = string
}

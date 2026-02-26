variable "project_name" {
  description = "Project identifier used for naming."
  type        = string
}

variable "environment" {
  description = "Environment name (dev/staging/prod)."
  type        = string
}

variable "waf_scope" {
  description = "WAF scope (REGIONAL or CLOUDFRONT)."
  type        = string
  default     = "REGIONAL"
}

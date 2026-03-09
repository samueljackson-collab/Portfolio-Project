variable "project_name" {
  description = "Name prefix for resources."
  type        = string
}

variable "environment" {
  description = "Environment name used for tagging."
  type        = string
}

variable "origin_domain_name" {
  description = "Origin domain name (ALB, S3 website, etc.)."
  type        = string
}

variable "origin_id" {
  description = "Origin identifier."
  type        = string
  default     = "origin-1"
}

variable "enabled" {
  description = "Enable the distribution."
  type        = bool
  default     = true
}

variable "default_root_object" {
  description = "Default root object."
  type        = string
  default     = "index.html"
}

variable "price_class" {
  description = "CloudFront price class."
  type        = string
  default     = "PriceClass_100"
}

variable "aliases" {
  description = "Optional alternate domain names."
  type        = list(string)
  default     = []
}

variable "viewer_certificate_arn" {
  description = "ACM certificate ARN in us-east-1."
  type        = string
}

variable "minimum_protocol_version" {
  description = "Minimum TLS version."
  type        = string
  default     = "TLSv1.2_2021"
}

variable "origin_protocol_policy" {
  description = "Origin protocol policy."
  type        = string
  default     = "https-only"
}

variable "viewer_protocol_policy" {
  description = "Viewer protocol policy."
  type        = string
  default     = "redirect-to-https"
}

variable "compress" {
  description = "Enable compression."
  type        = bool
  default     = true
}

variable "forward_query_string" {
  description = "Forward query strings to origin."
  type        = bool
  default     = true
}

variable "forward_headers" {
  description = "Headers to forward."
  type        = list(string)
  default     = []
}

variable "forward_cookies" {
  description = "Cookie forwarding behavior."
  type        = string
  default     = "none"
}

variable "min_ttl" {
  description = "Minimum TTL in seconds."
  type        = number
  default     = 0
}

variable "default_ttl" {
  description = "Default TTL in seconds."
  type        = number
  default     = 3600
}

variable "max_ttl" {
  description = "Max TTL in seconds."
  type        = number
  default     = 86400
}

variable "web_acl_id" {
  description = "WAF web ACL ID."
  type        = string
  default     = null
}

variable "logging_bucket" {
  description = "S3 bucket domain name for access logs."
  type        = string
}

variable "logging_prefix" {
  description = "Log prefix for access logs."
  type        = string
  default     = "cloudfront/"
}

variable "tags" {
  description = "Additional tags to apply."
  type        = map(string)
  default     = {}
}

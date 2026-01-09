###############################################################################
# Storage Module - Input Variables
###############################################################################

variable "name_prefix" {
  description = "Prefix for resource names (e.g., 'portfolio-dev')."
  type        = string
}

#------------------------------------------------------------------------------
# S3 Bucket Configuration
#------------------------------------------------------------------------------

variable "bucket_name" {
  description = "Custom bucket name (leave empty for auto-generated)."
  type        = string
  default     = ""
}

variable "force_destroy" {
  description = "Allow bucket to be destroyed with objects inside."
  type        = bool
  default     = false
}

variable "enable_versioning" {
  description = "Enable versioning on the S3 bucket."
  type        = bool
  default     = true
}

variable "kms_key_arn" {
  description = "KMS key ARN for encryption (leave empty for AES256)."
  type        = string
  default     = ""
}

#------------------------------------------------------------------------------
# CORS Configuration
#------------------------------------------------------------------------------

variable "cors_allowed_origins" {
  description = "List of allowed origins for CORS."
  type        = list(string)
  default     = []
}

variable "cors_allowed_headers" {
  description = "List of allowed headers for CORS."
  type        = list(string)
  default     = ["*"]
}

variable "cors_allowed_methods" {
  description = "List of allowed methods for CORS."
  type        = list(string)
  default     = ["GET", "HEAD"]
}

variable "cors_expose_headers" {
  description = "List of headers to expose in CORS responses."
  type        = list(string)
  default     = ["ETag"]
}

variable "cors_max_age_seconds" {
  description = "Max age for CORS preflight cache."
  type        = number
  default     = 3600
}

#------------------------------------------------------------------------------
# Lifecycle Rules
#------------------------------------------------------------------------------

variable "enable_lifecycle_rules" {
  description = "Enable lifecycle rules for cost optimization."
  type        = bool
  default     = true
}

variable "transition_to_ia_days" {
  description = "Days before transitioning to Infrequent Access."
  type        = number
  default     = 90
}

variable "noncurrent_version_transition_days" {
  description = "Days before transitioning non-current versions."
  type        = number
  default     = 30
}

variable "noncurrent_version_expiration_days" {
  description = "Days before expiring non-current versions."
  type        = number
  default     = 90
}

#------------------------------------------------------------------------------
# CloudFront Configuration
#------------------------------------------------------------------------------

variable "create_cloudfront_distribution" {
  description = "Create a CloudFront distribution."
  type        = bool
  default     = true
}

variable "default_root_object" {
  description = "Default root object for CloudFront."
  type        = string
  default     = "index.html"
}

variable "cloudfront_price_class" {
  description = "CloudFront price class."
  type        = string
  default     = "PriceClass_100"
}

variable "cloudfront_aliases" {
  description = "List of domain aliases for CloudFront."
  type        = list(string)
  default     = []
}

variable "acm_certificate_arn" {
  description = "ACM certificate ARN for CloudFront (us-east-1)."
  type        = string
  default     = ""
}

variable "web_acl_id" {
  description = "WAF Web ACL ID for CloudFront."
  type        = string
  default     = null
}

#------------------------------------------------------------------------------
# Cache Settings
#------------------------------------------------------------------------------

variable "cache_min_ttl" {
  description = "Minimum TTL for cached objects."
  type        = number
  default     = 0
}

variable "cache_default_ttl" {
  description = "Default TTL for cached objects."
  type        = number
  default     = 86400  # 24 hours
}

variable "cache_max_ttl" {
  description = "Maximum TTL for cached objects."
  type        = number
  default     = 31536000  # 1 year
}

#------------------------------------------------------------------------------
# ALB Origin (for API routing)
#------------------------------------------------------------------------------

variable "alb_domain_name" {
  description = "ALB domain name for API origin."
  type        = string
  default     = ""
}

variable "alb_origin_protocol_policy" {
  description = "Protocol policy for ALB origin."
  type        = string
  default     = "http-only"
}

#------------------------------------------------------------------------------
# Geo Restrictions
#------------------------------------------------------------------------------

variable "geo_restriction_type" {
  description = "Geo restriction type (none, whitelist, blacklist)."
  type        = string
  default     = "none"
}

variable "geo_restriction_locations" {
  description = "List of country codes for geo restrictions."
  type        = list(string)
  default     = []
}

#------------------------------------------------------------------------------
# Custom Error Responses
#------------------------------------------------------------------------------

variable "custom_error_responses" {
  description = "List of custom error response configurations."
  type = list(object({
    error_code            = number
    response_code         = number
    response_page_path    = string
    error_caching_min_ttl = number
  }))
  default = [
    {
      error_code            = 404
      response_code         = 404
      response_page_path    = "/404.html"
      error_caching_min_ttl = 300
    }
  ]
}

#------------------------------------------------------------------------------
# Logging
#------------------------------------------------------------------------------

variable "logging_bucket" {
  description = "S3 bucket for CloudFront access logs."
  type        = string
  default     = ""
}

variable "create_logs_bucket" {
  description = "Create a separate S3 bucket for logs."
  type        = bool
  default     = false
}

variable "logs_retention_days" {
  description = "Number of days to retain logs."
  type        = number
  default     = 365
}

#------------------------------------------------------------------------------
# Tags
#------------------------------------------------------------------------------

variable "tags" {
  description = "Tags to apply to all resources."
  type        = map(string)
  default     = {}
}

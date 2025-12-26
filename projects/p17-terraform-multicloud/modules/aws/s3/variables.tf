variable "project_name" {
  description = "Name prefix for resources."
  type        = string
}

variable "environment" {
  description = "Environment name used for tagging."
  type        = string
}

variable "bucket_name" {
  description = "Name of the S3 bucket."
  type        = string
}

variable "force_destroy" {
  description = "Whether to force destroy the bucket."
  type        = bool
  default     = false
}

variable "versioning_enabled" {
  description = "Enable versioning."
  type        = bool
  default     = true
}

variable "kms_key_id" {
  description = "KMS key ID for encryption."
  type        = string
  default     = null
}

variable "lifecycle_rules" {
  description = "Lifecycle rules to apply."
  type = list(object({
    id                       = string
    enabled                  = bool
    transition_days          = optional(number)
    transition_storage_class = optional(string)
    expiration_days          = optional(number)
  }))
  default = []
}

variable "logging" {
  description = "Access logging configuration."
  type = object({
    target_bucket = string
    target_prefix = string
  })
  default = null
}

variable "replication" {
  description = "Replication configuration."
  type = object({
    role_arn                = string
    destination_bucket_arn  = string
    storage_class           = string
  })
  default = null
}

variable "bucket_policy_json" {
  description = "Optional bucket policy JSON."
  type        = string
  default     = null
}

variable "tags" {
  description = "Additional tags to apply."
  type        = map(string)
  default     = {}
}

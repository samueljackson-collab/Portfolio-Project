variable "project_name" { type = string }
variable "environment" { type = string }
variable "common_tags" { type = map(string) default = {} }
variable "bucket_name" { type = string default = null }
variable "force_destroy" { type = bool default = false }
variable "enable_versioning" { type = bool default = true }
variable "kms_key_id" { type = string default = null }

variable "lifecycle_rules" {
  description = "Lifecycle rules for archival"
  type = list(object({
    id              = string
    enabled         = bool
    transition_days = number
    storage_class   = string
    expiration_days = number
  }))
  default = [
    {
      id              = "standard-to-glacier"
      enabled         = true
      transition_days = 30
      storage_class   = "GLACIER"
      expiration_days = 365
    }
  ]
}

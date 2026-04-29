variable "frameworks" {
  description = "Compliance frameworks enforced"
  type        = list(string)
  default     = ["CIS", "NIST"]
}

variable "enabled" {
  description = "Flag to enable security controls"
  type        = bool
  default     = true
}

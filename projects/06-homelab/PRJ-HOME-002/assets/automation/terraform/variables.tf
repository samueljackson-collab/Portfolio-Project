variable "proxmox_api_url" {
  description = "Proxmox API URL"
  type        = string
  default     = "https://192.168.40.10:8006/api2/json"
}

variable "proxmox_user" {
  description = "Proxmox API user"
  type        = string
  default     = "root@pam"
}

variable "proxmox_password" {
  description = "Proxmox API password"
  type        = string
  sensitive   = true
  # ⚠️ SECURITY: Set via environment variable TF_VAR_proxmox_password
  # or use -var="proxmox_password=..." on command line
  # Never commit passwords to version control!
  validation {
    condition     = length(var.proxmox_password) >= 12
    error_message = "Password must be at least 12 characters long."
  }
}

variable "vm_template" {
  description = "VM template name"
  type        = string
  default     = "ubuntu-22.04-cloudimg"
}

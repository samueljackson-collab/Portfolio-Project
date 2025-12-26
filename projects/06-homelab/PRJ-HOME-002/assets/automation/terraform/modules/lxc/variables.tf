variable "hostname" {
  description = "LXC hostname"
  type        = string
}

variable "target_node" {
  description = "Proxmox node to deploy on"
  type        = string
}

variable "ostemplate" {
  description = "LXC OS template"
  type        = string
}

variable "password" {
  description = "LXC root password"
  type        = string
  sensitive   = true
}

variable "cores" {
  description = "CPU cores"
  type        = number
}

variable "memory" {
  description = "Memory in MB"
  type        = number
}

variable "swap" {
  description = "Swap in MB"
  type        = number
}

variable "disk_size" {
  description = "Disk size"
  type        = string
}

variable "storage" {
  description = "Storage backend"
  type        = string
}

variable "bridge" {
  description = "Network bridge"
  type        = string
}

variable "ip" {
  description = "Static IP address with CIDR"
  type        = string
}

variable "gateway" {
  description = "Gateway"
  type        = string
}

variable "vlan_tag" {
  description = "VLAN tag"
  type        = number
}

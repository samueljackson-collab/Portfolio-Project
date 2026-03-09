variable "name" {
  description = "VM name"
  type        = string
}

variable "target_node" {
  description = "Proxmox node to deploy on"
  type        = string
}

variable "clone" {
  description = "Template name to clone"
  type        = string
}

variable "cores" {
  description = "CPU cores"
  type        = number
}

variable "memory" {
  description = "Memory in MB"
  type        = number
}

variable "disk_size" {
  description = "Disk size (e.g. 20G)"
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

variable "vlan_tag" {
  description = "VLAN tag"
  type        = number
}

variable "ipconfig0" {
  description = "IP configuration string"
  type        = string
}

variable "nameserver" {
  description = "DNS server address"
  type        = string
}

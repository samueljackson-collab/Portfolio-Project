# Proxmox Provider Configuration
terraform {
  required_providers {
    proxmox = {
      source  = "telmate/proxmox"
      version = "~> 2.9"
    }
  }
}

provider "proxmox" {
  pm_api_url      = var.proxmox_api_url
  pm_user         = var.proxmox_user
  pm_password     = var.proxmox_password
  pm_tls_insecure = true
}

# VM Resource - Wiki.js
resource "proxmox_vm_qemu" "wikijs" {
  name        = "wikijs"
  target_node = "proxmox-01"
  clone       = "ubuntu-22.04-cloudimg"
  full_clone  = true
  
  cores   = 2
  memory  = 4096
  scsihw  = "virtio-scsi-single"
  
  disk {
    size    = "20G"
    storage = "local-lvm"
    type    = "scsi"
  }
  
  network {
    model  = "virtio"
    bridge = "vmbr0"
    tag    = 40
  }
  
  ipconfig0 = "ip=192.168.40.60/24,gw=192.168.40.1"
  nameserver = "192.168.40.35"
}

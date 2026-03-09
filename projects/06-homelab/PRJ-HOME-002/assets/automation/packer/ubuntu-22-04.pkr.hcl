packer {
  required_plugins {
    proxmox = {
      version = ">= 1.1.3"
      source  = "github.com/hashicorp/proxmox"
    }
  }
}

variable "proxmox_url" { type = string }
variable "proxmox_username" { type = string }
variable "proxmox_password" { type = string }

source "proxmox" "ubuntu" {
  proxmox_url              = var.proxmox_url
  username                 = var.proxmox_username
  password                 = var.proxmox_password
  insecure_skip_tls_verify = true

  node                 = "proxmox-01"
  vm_name              = "ubuntu-22.04-packer"
  template_name        = "ubuntu-22.04-cloudimg"
  template_description = "Ubuntu 22.04 base image with cloud-init"

  iso_url      = "https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img"
  iso_checksum = "sha256:PLACEHOLDER"

  cores  = 2
  memory = 2048
  disk_size = "20G"
  storage_pool = "local-lvm"
  network_adapters {
    bridge = "vmbr0"
    model  = "virtio"
  }

  ssh_username = "ubuntu"
  ssh_timeout  = "20m"
}

build {
  sources = ["source.proxmox.ubuntu"]

  provisioner "shell" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get install -y qemu-guest-agent curl",
      "sudo systemctl enable --now qemu-guest-agent"
    ]
  }
}

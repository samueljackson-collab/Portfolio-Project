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

source "proxmox" "debian" {
  proxmox_url              = var.proxmox_url
  username                 = var.proxmox_username
  password                 = var.proxmox_password
  insecure_skip_tls_verify = true

  node                 = "proxmox-01"
  vm_name              = "debian-12-packer"
  template_name        = "debian-12-cloudimg"
  template_description = "Debian 12 base image with cloud-init"

  iso_url      = "https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-genericcloud-amd64.qcow2"
  iso_checksum = "sha256:PLACEHOLDER"

  cores  = 2
  memory = 2048
  disk_size = "20G"
  storage_pool = "local-lvm"
  network_adapters {
    bridge = "vmbr0"
    model  = "virtio"
  }

  ssh_username = "debian"
  ssh_timeout  = "20m"
}

build {
  sources = ["source.proxmox.debian"]

  provisioner "shell" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get install -y qemu-guest-agent curl",
      "sudo systemctl enable --now qemu-guest-agent"
    ]
  }
}

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

source "proxmox" "rocky" {
  proxmox_url              = var.proxmox_url
  username                 = var.proxmox_username
  password                 = var.proxmox_password
  insecure_skip_tls_verify = true

  node                 = "proxmox-02"
  vm_name              = "rockylinux-9-packer"
  template_name        = "rockylinux-9-cloudimg"
  template_description = "Rocky Linux 9 base image with cloud-init"

  iso_url      = "https://dl.rockylinux.org/pub/rocky/9/images/x86_64/Rocky-9-GenericCloud.latest.x86_64.qcow2"
  iso_checksum = "sha256:PLACEHOLDER"

  cores  = 2
  memory = 2048
  disk_size = "20G"
  storage_pool = "local-lvm-pve02"
  network_adapters {
    bridge = "vmbr0"
    model  = "virtio"
  }

  ssh_username = "rocky"
  ssh_timeout  = "20m"
}

build {
  sources = ["source.proxmox.rocky"]

  provisioner "shell" {
    inline = [
      "sudo dnf -y update",
      "sudo dnf -y install qemu-guest-agent curl",
      "sudo systemctl enable --now qemu-guest-agent"
    ]
  }
}

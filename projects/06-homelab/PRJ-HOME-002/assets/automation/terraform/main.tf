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

locals {
  wikijs_vm = {
    name       = "wikijs"
    target     = "proxmox-01"
    clone      = var.vm_template
    cores      = 2
    memory     = 4096
    disk_size  = "20G"
    storage    = "local-lvm"
    bridge     = "vmbr0"
    vlan_tag   = 40
    ipconfig0  = "ip=192.168.40.60/24,gw=192.168.40.1"
    nameserver = "192.168.40.35"
  }
}

module "wikijs_vm" {
  source = "./modules/vm"

  name       = local.wikijs_vm.name
  target_node = local.wikijs_vm.target
  clone      = local.wikijs_vm.clone
  cores      = local.wikijs_vm.cores
  memory     = local.wikijs_vm.memory
  disk_size  = local.wikijs_vm.disk_size
  storage    = local.wikijs_vm.storage
  bridge     = local.wikijs_vm.bridge
  vlan_tag   = local.wikijs_vm.vlan_tag
  ipconfig0  = local.wikijs_vm.ipconfig0
  nameserver = local.wikijs_vm.nameserver
}

module "pihole_lxc" {
  source = "./modules/lxc"

  hostname    = "pihole"
  target_node = "proxmox-02"
  ostemplate  = "local:vztmpl/debian-12-standard_12.0-1_amd64.tar.zst"
  password    = var.proxmox_password
  cores       = 2
  memory      = 2048
  swap        = 512
  disk_size   = "8G"
  storage     = "local-lvm-pve02"
  bridge      = "vmbr0"
  ip          = "192.168.40.35/24"
  gateway     = "192.168.40.1"
  vlan_tag    = 40
}

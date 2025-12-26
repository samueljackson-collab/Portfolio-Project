resource "proxmox_vm_qemu" "vm" {
  name        = var.name
  target_node = var.target_node
  clone       = var.clone
  full_clone  = true

  cores  = var.cores
  memory = var.memory
  scsihw = "virtio-scsi-single"

  disk {
    size    = var.disk_size
    storage = var.storage
    type    = "scsi"
  }

  network {
    model  = "virtio"
    bridge = var.bridge
    tag    = var.vlan_tag
  }

  ipconfig0 = var.ipconfig0
  nameserver = var.nameserver
}

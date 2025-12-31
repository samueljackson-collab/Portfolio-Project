output "vm_name" {
  description = "Provisioned VM name"
  value       = proxmox_vm_qemu.vm.name
}

output "vm_id" {
  description = "Provisioned VM ID"
  value       = proxmox_vm_qemu.vm.vmid
}

output "container_hostname" {
  description = "Provisioned container hostname"
  value       = proxmox_lxc.container.hostname
}

output "container_id" {
  description = "Provisioned container ID"
  value       = proxmox_lxc.container.vmid
}

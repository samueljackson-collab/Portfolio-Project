output "wikijs_ip" {
  description = "Wiki.js VM IP address"
  value       = proxmox_vm_qemu.wikijs.default_ipv4_address
}

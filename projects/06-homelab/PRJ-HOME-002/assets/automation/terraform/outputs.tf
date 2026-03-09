output "wikijs_vm_name" {
  description = "Wiki.js VM name"
  value       = module.wikijs_vm.vm_name
}

output "wikijs_vm_id" {
  description = "Wiki.js VM ID"
  value       = module.wikijs_vm.vm_id
}

output "pihole_lxc_id" {
  description = "Pi-hole LXC ID"
  value       = module.pihole_lxc.container_id
}

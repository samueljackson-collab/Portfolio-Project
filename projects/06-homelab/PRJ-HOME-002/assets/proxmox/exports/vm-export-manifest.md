# VM Export Manifest

Sanitized summary of Proxmox VM exports used for cold storage, migration validation, and DR rehearsals.

## Export Scope
- **Cluster:** `homelab-cluster` (3 nodes)
- **Export Window:** 2025-10-28 01:00–04:00 UTC
- **Export Location:** `truenas-nfs01:/exports/proxmox/vm-exports/`
- **Export Format:** `vma.zst`
- **Checksum:** SHA-256 recorded per export

## VM Inventory (Sanitized)
| VM ID | Role | OS | Storage Tier | Export Filename | Size | Checksum Verified |
| --- | --- | --- | --- | --- | --- | --- |
| 101 | FreeIPA | AlmaLinux 9 | Ceph RBD | vm-101-freeipa-2025-10-28.vma.zst | 18.4 GB | ✅ |
| 102 | Pi-hole | Ubuntu 22.04 | Ceph RBD | vm-102-pihole-2025-10-28.vma.zst | 6.2 GB | ✅ |
| 103 | Nginx Proxy Manager | Ubuntu 22.04 | Ceph RBD | vm-103-npm-2025-10-28.vma.zst | 7.9 GB | ✅ |
| 104 | Wiki.js | Ubuntu 22.04 | Ceph RBD | vm-104-wikijs-2025-10-28.vma.zst | 12.7 GB | ✅ |
| 105 | Immich | Ubuntu 22.04 | Ceph RBD | vm-105-immich-2025-10-28.vma.zst | 32.3 GB | ✅ |
| 106 | Home Assistant | Ubuntu 22.04 | Ceph RBD | vm-106-homeassistant-2025-10-28.vma.zst | 10.5 GB | ✅ |
| 107 | Proxmox Backup Server | Debian 12 | Local LVM | vm-107-pbs-2025-10-28.vma.zst | 9.8 GB | ✅ |

## Export Commands (Reference)
```bash
# Export VM to NFS staging share
vzdump 104 --compress zstd --storage truenas-nfs01 --mode stop

# Verify checksum
sha256sum vm-104-wikijs-2025-10-28.vma.zst
```

## Validation Checklist
- [x] Export completed without errors
- [x] SHA-256 checksums recorded
- [x] Restore tests executed for at least one critical VM (see logs)
- [x] Exports copied to secondary backup share

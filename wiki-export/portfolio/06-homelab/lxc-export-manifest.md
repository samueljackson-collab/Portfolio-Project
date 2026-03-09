---
title: LXC Export Manifest
description: Sanitized summary of LXC container exports used for rollback and migration validation. - **Cluster:** `homelab-cluster` (3 nodes) - **Export Window:** 2025-10-28 04:30–05:15 UTC - **Export Location:**
tags: [documentation, portfolio]
path: portfolio/06-homelab/lxc-export-manifest
created: 2026-03-08T22:19:13.079067+00:00
updated: 2026-03-08T22:04:38.357902+00:00
---

# LXC Export Manifest

Sanitized summary of LXC container exports used for rollback and migration validation.

## Export Scope
- **Cluster:** `homelab-cluster` (3 nodes)
- **Export Window:** 2025-10-28 04:30–05:15 UTC
- **Export Location:** `truenas-nfs01:/exports/proxmox/lxc-exports/`
- **Export Format:** `tar.zst`
- **Checksum:** SHA-256 recorded per export

## LXC Inventory (Sanitized)
| CT ID | Role | OS | Storage Tier | Export Filename | Size | Checksum Verified |
| --- | --- | --- | --- | --- | --- | --- |
| 201 | Prometheus + Grafana | Debian 12 | Local LVM | ct-201-monitoring-2025-10-28.tar.zst | 5.6 GB | ✅ |
| 202 | Loki + Promtail | Debian 12 | Local LVM | ct-202-loki-2025-10-28.tar.zst | 3.1 GB | ✅ |
| 203 | Backup Agent | Debian 12 | Local LVM | ct-203-backup-agent-2025-10-28.tar.zst | 1.2 GB | ✅ |

## Export Commands (Reference)
```bash
# Export LXC to NFS staging share
vzdump 201 --compress zstd --storage truenas-nfs01 --mode stop

# Verify checksum
sha256sum ct-201-monitoring-2025-10-28.tar.zst
```

## Validation Checklist
- [x] Export completed without errors
- [x] SHA-256 checksums recorded
- [x] Restore tests executed for monitoring containers (see logs)
- [x] Exports copied to secondary backup share

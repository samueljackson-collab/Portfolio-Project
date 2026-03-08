---
title: VM Migration Procedures
description: - Shared storage (Ceph or NFS) - Network connectivity between nodes - Sufficient resources on target node qm status 100 qm migrate 100 proxmox-02 --online qm status 100 qm stop 100 qm migrate 100 prox
tags: [documentation, portfolio]
path: portfolio/06-homelab/vm-migration
created: 2026-03-08T22:19:13.074955+00:00
updated: 2026-03-08T22:04:38.363902+00:00
---

# VM Migration Procedures

## Live Migration (Zero Downtime)

### Prerequisites
- Shared storage (Ceph or NFS)
- Network connectivity between nodes
- Sufficient resources on target node

### Procedure
```bash
# 1. Check VM status
qm status 100

# 2. Migrate VM
qm migrate 100 proxmox-02 --online

# 3. Verify migration
qm status 100
```

## Offline Migration

```bash
# 1. Stop VM
qm stop 100

# 2. Migrate
qm migrate 100 proxmox-02

# 3. Start on new node
qm start 100
```

## HA Automatic Failover

HA-enabled VMs automatically migrate on node failure.
Monitor with: `ha-manager status`

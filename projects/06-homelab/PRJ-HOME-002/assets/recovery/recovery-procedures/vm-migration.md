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

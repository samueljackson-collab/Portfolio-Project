# Storage Failover Procedures

## Ceph Storage Recovery

### Check Ceph Status
```bash
ceph -s
ceph health detail
```

### OSD Failure Recovery
```bash
# 1. Identify failed OSD
ceph osd tree

# 2. Mark OSD out
ceph osd out osd.X

# 3. Replace disk and recreate OSD
ceph-volume lvm create --data /dev/sdX
```

## NFS Storage Failover

### Remount NFS
```bash
umount /mnt/pve/truenas-backups
mount -t nfs 192.168.40.20:/mnt/tank/proxmox/backups /mnt/pve/truenas-backups
```

### Switch to Alternative Storage
Edit `/etc/pve/storage.cfg` and activate backup storage

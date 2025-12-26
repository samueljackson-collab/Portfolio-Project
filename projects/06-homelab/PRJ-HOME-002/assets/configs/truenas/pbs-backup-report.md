# PBS Backup Report (Sanitized)

- **Job:** nightly-homelab
- **Targets:** proxmox/atlas, proxmox/hera, proxmox/zeus (VMs redacted)
- **Schedule:** daily @ 02:00 UTC
- **Retention:** 14 daily, 4 weekly, 6 monthly

## Last run
```
2024-05-10T02:00:03Z start backup job nightly-homelab
2024-05-10T02:00:14Z snapshot atlas/vm-101 OK (duration 00:00:45, size 3.2GiB)
2024-05-10T02:01:22Z snapshot hera/vm-204 OK (duration 00:01:03, size 6.8GiB)
2024-05-10T02:03:18Z snapshot zeus/lxc-301 OK (duration 00:00:33, size 850MiB)
2024-05-10T02:03:41Z prune: removed 0 backups
2024-05-10T02:03:42Z job status: OK (sanitized identifiers)
```

All node names and dataset IDs have been sanitized; no customer or personal data present.

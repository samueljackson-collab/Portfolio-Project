# Troubleshooting Guide

## Proxmox Cluster Issues
- **Check cluster quorum:** `pvecm status`
- **Corosync logs:** `/var/log/syslog` or `journalctl -u corosync`
- **Restart services:** `systemctl restart pve-cluster pvedaemon pveproxy`

## Storage Mount Failures
- **NFS:** `showmount -e 192.168.40.20` and `mount -a`
- **iSCSI:** `iscsiadm -m session` and `multipath -ll`
- **Ceph:** `ceph -s` and `pveceph status`

## Backup Failures
- Validate PBS datastore: `proxmox-backup-client list`.
- Inspect task logs: `/var/log/pve/tasks/`.
- Ensure PBS fingerprint matches `assets/proxmox/storage.cfg`.

## DNS/DHCP Issues
- Restart Pi-hole DNS: `systemctl restart pihole-FTL`.
- DHCP leases: `/var/lib/dhcp/dhcpd.leases`.
- Validate DHCP config: `dhcpd -t -cf /etc/dhcp/dhcpd.conf`.

## Reverse Proxy/TLS Issues
- Check Traefik logs: `docker logs traefik`.
- Validate Step CA ACME endpoint: `https://ca.homelab.local:9000/acme/acme/directory`.
- Confirm DNS records resolve to proxy IP.

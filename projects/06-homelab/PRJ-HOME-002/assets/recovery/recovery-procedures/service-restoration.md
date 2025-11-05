# Service Restoration Procedures

## Critical Service VM Restoration

### Pi-hole DNS Service

**RTO:** 1 hour | **RPO:** 24 hours | **Priority:** P0

1. Identify most recent backup
2. Restore VM: `qmrestore proxmox-backup:backup/vm-101-* 101`
3. Start VM: `qm start 101`
4. Verify DNS: `nslookup homelab.local 192.168.40.35`
5. Update pfSense to point to restored DNS

### FreeIPA Authentication

**RTO:** 1 hour | **RPO:** 24 hours | **Priority:** P0

1. Restore VM from backup
2. Verify Kerberos: `kinit admin`
3. Check LDAP: `ldapsearch -x -b dc=homelab,dc=local`
4. Test RADIUS authentication
5. Reconnect client devices

### Nginx Reverse Proxy

**RTO:** 2 hours | **RPO:** 24 hours | **Priority:** P1

1. Restore VM from backup
2. Verify certificates: `nginx -t`
3. Check upstream services
4. Test HTTPS connections
5. Update DNS records if needed

# Weekly Maintenance Runbook

**Purpose:** Regular maintenance procedures to ensure system health and prevent issues
**Frequency:** Weekly (recommended: Sunday mornings)
**Duration:** ~45-60 minutes
**Prerequisites:** VPN access, admin credentials

---

## Maintenance Window

**Recommended Schedule:**
- **Day:** Sunday
- **Time:** 06:00 - 08:00 local time
- **Impact:** Minimal (low usage period)
- **Notification:** Email to users 24 hours in advance

**Maintenance Window Template:**
```
Subject: Scheduled Homelab Maintenance - [Date]

Scheduled maintenance will occur:
Date: Sunday, [Month Day, Year]
Time: 06:00 - 08:00 [Timezone]
Duration: Up to 2 hours

Expected Impact:
- Brief service interruptions (< 5 minutes per service)
- Photo uploads may be temporarily unavailable
- No data loss expected

Services will be tested after maintenance completes.

Questions? Contact: Samuel Jackson

- Homelab Admin Team
```

---

## Pre-Maintenance Checklist

- [ ] Maintenance window notification sent (24h advance)
- [ ] Backup verification completed (all backups current)
- [ ] Change log reviewed (no conflicting changes)
- [ ] Rollback plan documented
- [ ] Emergency contact list current
- [ ] Maintenance terminal session ready

---

## Maintenance Procedures

### 1. System Updates (20 minutes)

#### Proxmox Host Updates

```bash
# SSH to Proxmox host
ssh root@192.168.10.10

# Check for available updates
apt update
apt list --upgradable

# Review changes before applying
# Avoid kernel updates during family events
apt upgrade -y

# Clean up old packages
apt autoremove -y
apt autoclean

# Reboot if kernel updated (schedule carefully)
# Only if necessary and during approved window
shutdown -r +5 "Proxmox host rebooting for kernel update in 5 minutes"
```

**Proxmox-specific updates:**
```bash
# Update Proxmox VE packages
pve-upgrade-checker

# Update subscription status (if applicable)
pveupdate

# Verify cluster status (if clustered)
pvecm status
```

#### TrueNAS Updates

```bash
# Access TrueNAS web UI
# https://192.168.10.11

# Navigate: System > Update
# Check for available updates
# Review release notes
# Download and apply if stable release
# Schedule reboot if required
```

**Pre-update checks:**
- [ ] ZFS pool status: ONLINE
- [ ] No scrub or resilver in progress
- [ ] Recent backup exists
- [ ] Snapshot created before update

#### Container Updates

```bash
# SSH to container host
ssh user@192.168.30.10

# Pull latest images
cd /opt/homelab/monitoring
docker-compose pull

cd /opt/homelab/immich
docker-compose pull

cd /opt/homelab/proxy
docker-compose pull

# Check for breaking changes in release notes
# Review docker-compose.yml for required changes

# Update containers (one stack at a time)
docker-compose down
docker-compose up -d

# Verify service health
docker-compose ps
docker-compose logs --tail 50

# Repeat for each service stack
```

**Container health verification:**
```bash
# Check all containers are running
docker ps --filter "status=exited"

# Verify no restart loops
docker ps --format "table {{.Names}}\t{{.Status}}"

# Test endpoints
curl -I https://photos.homelab.local
curl -I https://grafana.homelab.local
```

---

### 2. Security Patching (10 minutes)

#### Critical Security Updates

```bash
# Check for security updates only
apt list --upgradable | grep -i security

# Install security patches immediately
apt install --only-upgrade [package-name]

# Or install all security updates
unattended-upgrade --dry-run
unattended-upgrade
```

#### SSL Certificate Review

```bash
# Check certificate expiration dates
# Via Nginx Proxy Manager UI or:

openssl s_client -connect photos.homelab.local:443 -servername photos.homelab.local </dev/null 2>/dev/null | openssl x509 -noout -dates

# Check Let's Encrypt renewal status
# Nginx Proxy Manager handles auto-renewal
# Verify renewal job is scheduled

# Manual renewal if needed (NPM usually handles this)
# Via NPM UI: SSL Certificates > Renew
```

**Certificate expiration tracking:**
| Service | Current Expiry | Auto-Renewal | Status |
|---------|----------------|--------------|--------|
| photos.homelab.local | Check weekly | ✅ Enabled | 🟢 OK |
| grafana.homelab.local | Check weekly | ✅ Enabled | 🟢 OK |
| wiki.homelab.local | Check weekly | ✅ Enabled | 🟢 OK |

---

### 3. Security Hardening Verification (10 minutes)

#### Fail2ban + Audit Logging

```bash
# Fail2ban overall status
sudo fail2ban-client status

# Review banned IPs from the last week
sudo fail2ban-client status sshd | grep "Banned IP list" -A 1

# Audit log volume and shipping
sudo systemctl is-active auditd
sudo ausearch -m USER_LOGIN -ts this-week | tail -n 10
```

#### MQTT TLS + 2FA Review

```bash
# Verify MQTT TLS cert validity
openssl s_client -connect mqtt.homelab.local:8883 -servername mqtt.homelab.local </dev/null 2>/dev/null | openssl x509 -noout -dates

# Validate Mosquitto TLS listener is active
sudo ss -lntp | grep 8883
```

- [ ] Fail2ban jails active (sshd, nginx)
- [ ] auditd logs are forwarding to Loki
- [ ] MQTT TLS certificate not expiring within 30 days
- [ ] Admin MFA enforcement reviewed in SSO/Vaultwarden

---

### 4. Storage Maintenance (15 minutes)

#### ZFS Health Check

```bash
# SSH to TrueNAS
ssh root@192.168.10.11

# Check pool status
zpool status -v tank

# Expected output: "state: ONLINE" with no errors

# Check pool capacity
zpool list tank

# Warning if > 80% used
# Critical if > 90% used

# Check for recent errors
zpool events -v | grep -i error | tail -n 20
```

#### ZFS Scrub (Monthly, but check weekly)

```bash
# Check last scrub date
zpool status tank | grep scrub

# Initiate scrub if > 30 days
# Only start during low-activity period
zpool scrub tank

# Monitor scrub progress
watch -n 60 'zpool status tank'

# Expected completion: 4-8 hours for 2TB pool
# Scrub does not interrupt service
```

#### Disk Space Cleanup

```bash
# Check disk space across all systems

# Proxmox host
df -h | grep -v loop
# Clean: /var/log, /var/lib/vz/dump (old backups)

du -sh /var/log/* | sort -h | tail -n 10
journalctl --vacuum-size=500M

# Clean old VM backups (keep last 7 as per policy)
find /var/lib/vz/dump -name "*.vma.zst" -mtime +7 -delete

# Application servers
docker system prune -f
docker volume prune -f
docker image prune -af --filter "until=168h"

# Check Docker volumes
docker volume ls
# Remove unused volumes (careful!)
```

#### Database Maintenance

```bash
# PostgreSQL VACUUM and ANALYZE
docker exec -it immich_postgres psql -U immich -c "VACUUM ANALYZE;"
docker exec -it wikijs_postgres psql -U wikijs -c "VACUUM ANALYZE;"

# Check database sizes
docker exec -it immich_postgres psql -U immich -c "SELECT pg_size_pretty(pg_database_size('immich'));"

# Backup verification
docker exec -it immich_postgres pg_dump -U immich immich > /tmp/test-backup.sql
ls -lh /tmp/test-backup.sql
rm /tmp/test-backup.sql
```

---

### 4. Backup Verification (10 minutes)

#### Verify Backup Completion

```bash
# Check Proxmox backup logs
ssh root@192.168.10.10
cat /var/log/vzdump.log | grep "INFO: Backup job finished successfully"

# List recent backups
ls -lh /mnt/pve/truenas-nfs/dump/
```

#### Test Restore (Monthly, quick check weekly)

```bash
# Monthly: Full restore test to sandbox environment
# Weekly: Verify backup file integrity

# Check backup file sizes (detect corruption)
find /mnt/backups -name "*.vma.zst" -mtime -7 -ls

# Verify ZFS snapshots
ssh root@192.168.10.11
zfs list -t snapshot -o name,used,refer,creation | grep homelab

# Check snapshot count (should match schedule)
# Hourly: 24, Daily: 7, Weekly: 4, Monthly: 3-6
```

#### Offsite Backup Status

```bash
# Check Syncthing replication status
# Web UI: http://192.168.30.35:8384

# Verify last sync times for:
# - Thavy's house (in-state)
# - Dad's house (out-of-state)

# Expected: Synced within last 24 hours

# Check sync conflicts
# Syncthing > Conflicts folder
# Resolve any conflicts found
```

---

### 5. Network Maintenance (10 minutes)

#### Firewall Rule Review

```bash
# UniFi Gateway
# https://unifi.homelab.local

# Check firewall logs for:
# - Unusual blocked traffic
# - Repeated connection attempts (brute force)
# - Unexpected inter-VLAN traffic

# Review top blocked IPs
# Settings > Security > Firewall > Statistics
```

#### VPN Health Check

```bash
# Check WireGuard status
ssh root@192.168.20.10
wg show

# Expected output:
# - All peers with recent handshake (< 3 minutes)
# - Received/sent bytes increasing
# - No error messages

# Test VPN connectivity
# From admin laptop (connected via VPN)
ping -c 3 192.168.10.10
ping -c 3 192.168.10.11

# Check VPN logs for unauthorized attempts
grep -i wireguard /var/log/syslog | grep -i fail
```

#### DNS Health Check

```bash
# Test internal DNS resolution
nslookup photos.homelab.local 192.168.10.1
nslookup grafana.homelab.local 192.168.10.1

# Expected: Correct IP addresses returned
# No timeouts or failures

# Test external DNS
nslookup google.com 192.168.10.1

# Check DNS query logs (UniFi Gateway)
# Look for unusual query patterns
```

---

### 6. Monitoring Review (5 minutes)

#### Alert Tuning

```bash
# Review alerts from past week
# Prometheus: https://prometheus.homelab.local/alerts

# Identify:
# - False positives (tune thresholds)
# - Missed incidents (add new alerts)
# - Alert fatigue (too many low-value alerts)

# Update alerting rules
# File: assets/configs/monitoring/alerting-rules.yml
# Apply changes:
docker exec prometheus kill -HUP 1
```

#### Dashboard Review

```bash
# Grafana: https://grafana.homelab.local

# Review dashboards for:
# - Missing data (gaps in metrics)
# - Visualization errors
# - Outdated panels

# Update dashboards as needed
# Export updated dashboards to Git
```

---

### 7. Documentation Updates (5 minutes)

```bash
# Update the following if changed:
# - IP address allocations
# - Service configurations
# - Network topology
# - Access credentials (in secure vault)

# Commit changes to Git
cd /opt/homelab/documentation
git add .
git commit -m "Weekly maintenance - $(date +%Y-%m-%d)"
git push origin main
```

---

## Post-Maintenance Checklist

- [ ] All systems updated and rebooted (if needed)
- [ ] All services verified operational
- [ ] Backups completed successfully
- [ ] No active critical alerts
- [ ] Monitoring dashboards showing healthy metrics
- [ ] Security patches applied
- [ ] Documentation updated
- [ ] Maintenance window closed
- [ ] Users notified of completion

---

## Post-Maintenance Verification

### Service Health Matrix

| Service | Status | Response Time | Notes |
|---------|--------|---------------|-------|
| Proxmox Web UI | ✅ | < 500ms | |
| TrueNAS Web UI | ✅ | < 500ms | |
| Immich (Photos) | ✅ | < 1s | |
| Wiki.js | ✅ | < 1s | |
| Grafana | ✅ | < 500ms | |
| Prometheus | ✅ | < 500ms | |

### System Metrics (Post-Maintenance)

```bash
# Record baseline metrics after maintenance

# CPU usage
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')%"

# Memory usage
free -h

# Disk space
df -h | grep -v loop

# Network connectivity
ping -c 5 8.8.8.8
```

---

## Maintenance Log Template

```
=== WEEKLY MAINTENANCE LOG ===
Date: YYYY-MM-DD
Start Time: HH:MM
End Time: HH:MM
Performed By: Samuel Jackson

Updates Applied:
[ ] Proxmox host: [version or "none"]
[ ] TrueNAS: [version or "none"]
[ ] Containers: [list updated containers]
[ ] Security patches: [count or "none"]

Storage Maintenance:
[ ] ZFS scrub status: [last scrub date]
[ ] Disk space: [current utilization %]
[ ] Backup verification: [successful / issues]

Network Maintenance:
[ ] Firewall review: [no issues / notes]
[ ] VPN health: [all peers connected]
[ ] DNS functionality: [operational]

Issues Found:
1. [Issue description and resolution]
2. [...]

Follow-up Actions:
1. [Action item with due date]
2. [...]

Next Maintenance: YYYY-MM-DD

Notes:
_________________________________________________
_________________________________________________

Completed: [ ] Yes  [ ] Partial
```

---

## Troubleshooting Common Maintenance Issues

### Issue: Service won't start after update

**Symptoms:**
- Container exits immediately after `docker-compose up`
- Service shows "Exited (1)" status

**Resolution:**
```bash
# Check logs for error messages
docker logs [container-name]

# Common causes:
# - Configuration file syntax error
# - Missing environment variable
# - Port conflict
# - Volume mount issue

# Rollback to previous version
docker-compose down
docker pull [image]:[previous-tag]
# Update docker-compose.yml with previous tag
docker-compose up -d
```

### Issue: System slow after updates

**Symptoms:**
- High CPU usage
- Slow response times
- Services timing out

**Resolution:**
```bash
# Identify resource hog
htop
# or
docker stats

# Restart problematic service
docker restart [container-name]

# Check for update-related issues
journalctl -xe | grep -i error

# Reboot if needed (last resort)
shutdown -r now
```

### Issue: Network connectivity lost

**Symptoms:**
- Cannot access services
- Ping failures
- DNS resolution fails

**Resolution:**
```bash
# Check network interfaces
ip addr show

# Restart networking
systemctl restart networking

# Verify VLAN configuration
cat /etc/network/interfaces

# Check bridge status
brctl show

# Worst case: restore network config from backup
cp /etc/network/interfaces.backup /etc/network/interfaces
systemctl restart networking
```

---

## Related Documentation

- [Daily Operations Runbook](./daily-operations.md)
- [Incident Response Runbook](./incident-response.md)
- [Disaster Recovery Plan](./disaster-recovery.md)
- [System Update Procedures](../procedures/system-updates.md)

---

**Last Updated:** 2024-12-16
**Owner:** Samuel Jackson
**Review Frequency:** Quarterly
**Next Scheduled Maintenance:** TBD

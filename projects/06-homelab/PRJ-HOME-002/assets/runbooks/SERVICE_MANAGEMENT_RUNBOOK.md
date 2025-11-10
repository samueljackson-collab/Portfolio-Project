# Core Services Management Runbook

**Version:** 1.0
**Last Updated:** November 10, 2025
**Maintainer:** Samuel Jackson

---

## Table of Contents

1. [Overview](#overview)
2. [FreeIPA - Identity Management](#freeipa---identity-management)
3. [Pi-hole - DNS & Ad Blocking](#pi-hole---dns--ad-blocking)
4. [Nginx - Reverse Proxy](#nginx---reverse-proxy)
5. [Rsyslog - Centralized Logging](#rsyslog---centralized-logging)
6. [NTP - Time Synchronization](#ntp---time-synchronization)
7. [Service Dependencies](#service-dependencies)
8. [Troubleshooting](#troubleshooting)

---

## Overview

### Core Services Architecture

```
Services VLAN (192.168.40.0/24)
│
├─ FreeIPA (192.168.40.25)
│   ├─ LDAP Directory
│   ├─ Kerberos KDC
│   ├─ RADIUS Server (for WPA3 Enterprise)
│   └─ Internal CA
│
├─ Pi-hole (192.168.40.35)
│   ├─ DNS Server (port 53)
│   ├─ DHCP Server (optional)
│   └─ Web Interface (port 80/443)
│
├─ Nginx (192.168.40.40)
│   ├─ Reverse Proxy
│   ├─ SSL Termination
│   └─ Load Balancer
│
├─ Rsyslog (192.168.40.30)
│   ├─ Syslog Server (TCP/UDP 514)
│   └─ Log Storage
│
└─ NTP (192.168.40.45)
    ├─ Time Server (UDP 123)
    └─ Stratum 2 Server
```

### Service Priorities

| Priority | Service | RTO | Impact if Down |
|----------|---------|-----|----------------|
| P0 | FreeIPA | 1 hour | Authentication failure, wireless down |
| P0 | Pi-hole | 1 hour | DNS resolution fails, internet issues |
| P1 | Nginx | 4 hours | External service access fails |
| P2 | Rsyslog | 24 hours | Log collection stops (no immediate impact) |
| P2 | NTP | 24 hours | Time drift (gradual degradation) |

---

## FreeIPA - Identity Management

### Service Information
- **VM ID:** 102
- **IP Address:** 192.168.40.25
- **Hostname:** freeipa.homelab.local
- **OS:** CentOS Stream 9 / Rocky Linux 9
- **Purpose:** Centralized authentication, RADIUS for wireless
- **Web UI:** https://192.168.40.25
- **HA Enabled:** Yes

### Service Management

#### Check Service Status
```bash
# SSH to FreeIPA server
ssh admin@192.168.40.25

# Check all IPA services
ipactl status
# Expected: All services "RUNNING"

# Detailed status
systemctl status ipa
systemctl status radiusd  # RADIUS for wireless auth
systemctl status krb5kdc  # Kerberos
systemctl status dirsrv@HOMELAB-LOCAL  # LDAP
```

#### Start/Stop/Restart Services
```bash
# Stop all IPA services
ipactl stop

# Start all IPA services
ipactl start

# Restart all IPA services
ipactl restart

# Restart individual service (RADIUS)
systemctl restart radiusd
```

#### Service Health Check
```bash
# Test LDAP
ldapsearch -x -H ldap://192.168.40.25 -b "dc=homelab,dc=local"

# Test Kerberos
echo "password" | kinit admin
klist  # Should show valid ticket

# Test RADIUS (for wireless auth)
# Replace <test_password> and <radius_secret> with actual values from password manager
radtest testuser <test_password> 192.168.40.25 0 <radius_secret>
# Expected: "Access-Accept"

# Test Web UI
curl -k https://192.168.40.25/ipa/ui/
# Expected: HTTP 200
```

### User Management

#### Add New User
```bash
# Via CLI
ipa user-add jsmith \
  --first=John \
  --last=Smith \
  --email=jsmith@homelab.local \
  --password  # Will prompt for password

# User must change password on first login

# Via Web UI
# https://192.168.40.25 → Identity → Users → Add
```

#### Reset User Password
```bash
# Via CLI
ipa user-mod jsmith --password
# Enter new password

# Force password change on next login
ipa pwpolicy-mod --maxlife=1

# Via Web UI
# Identity → Users → Select user → Actions → Reset Password
```

#### Disable/Enable User
```bash
# Disable user account
ipa user-disable jsmith

# Enable user account
ipa user-enable jsmith

# Check user status
ipa user-show jsmith
```

#### Delete User
```bash
# Delete user (preserve by default)
ipa user-del jsmith

# Permanently delete
ipa user-del jsmith --preserve=False
```

### Group Management

#### Add Group
```bash
# Create group
ipa group-add engineers --desc="Engineering Team"

# Add user to group
ipa group-add-member engineers --users=jsmith

# List group members
ipa group-show engineers
```

### RADIUS Configuration (Wireless Auth)

#### Check RADIUS Status
```bash
# Check RADIUS service
systemctl status radiusd

# Test RADIUS authentication
radtest testuser password 192.168.40.25 0 testing123

# View RADIUS logs
journalctl -u radiusd -n 50

# Live RADIUS log monitoring
tail -f /var/log/radius/radius.log
```

#### Troubleshoot RADIUS Issues
```bash
# Common issue: Shared secret mismatch
# Verify shared secret matches UniFi Controller

# Edit RADIUS clients
vi /etc/raddb/clients.conf
# Verify UniFi Controller IP and shared secret

# Restart RADIUS
systemctl restart radiusd

# Test again
radtest testuser password 192.168.40.25 0 testing123
```

### Backup FreeIPA

```bash
# Full backup (includes all data)
ipa-backup
# Creates backup in: /var/lib/ipa/backup/

# Backup to remote location
ipa-backup
scp /var/lib/ipa/backup/ipa-full-$(date +%Y-%m-%d).tar \
  admin@192.168.40.20:/mnt/backups/freeipa/

# Backup frequency: Daily (automated via cron)
```

### Restore FreeIPA

```bash
# List available backups
ls -lh /var/lib/ipa/backup/

# Restore from backup
ipa-restore /var/lib/ipa/backup/ipa-full-2025-11-10.tar

# Or restore from remote backup
scp admin@192.168.40.20:/mnt/backups/freeipa/ipa-full-2025-11-10.tar /tmp/
ipa-restore /tmp/ipa-full-2025-11-10.tar

# Restart services
ipactl restart
```

### Disaster Recovery

**Scenario:** FreeIPA VM lost, need to rebuild

```bash
# 1. Restore VM from Proxmox backup
# See BACKUP_RECOVERY_RUNBOOK.md

# 2. Verify network connectivity
ping 192.168.40.25

# 3. Restore FreeIPA data
ssh admin@192.168.40.25
ipa-restore /var/lib/ipa/backup/ipa-full-latest.tar

# 4. Verify services
ipactl status
kinit admin
radtest testuser password localhost 0 testing123

# Expected RTO: 1 hour
# Expected RPO: 24 hours (daily backup)
```

---

## Pi-hole - DNS & Ad Blocking

### Service Information
- **VM ID:** 103
- **IP Address:** 192.168.40.35
- **Hostname:** pihole.homelab.local
- **OS:** Debian 12 / Ubuntu 22.04
- **Purpose:** Network-wide DNS and ad blocking
- **Web UI:** http://192.168.40.35/admin
- **HA Enabled:** Yes

### Service Management

#### Check Service Status
```bash
# SSH to Pi-hole server
ssh admin@192.168.40.35

# Check Pi-hole status
pihole status
# Expected: "Pi-hole blocking is enabled"

# Check DNS service (FTL)
systemctl status pihole-FTL

# Test DNS resolution
dig @127.0.0.1 google.com
# Expected: ANSWER section with IP address
```

#### Start/Stop/Restart Services
```bash
# Disable Pi-hole (allow all DNS)
pihole disable

# Enable Pi-hole (resume blocking)
pihole enable

# Restart DNS service
pihole restartdns

# Restart FTL daemon
systemctl restart pihole-FTL
```

#### Service Health Check
```bash
# Test DNS resolution
dig @192.168.40.35 google.com
# Expected: ANSWER with IP

# Test ad blocking
dig @192.168.40.35 doubleclick.net
# Expected: 0.0.0.0 (blocked)

# Check query statistics
pihole -c  # Console dashboard

# Via Web UI
# http://192.168.40.35/admin → Dashboard
```

### DNS Management

#### Add Custom DNS Records
```bash
# Via Web UI
# Local DNS → DNS Records → Add new domain/IP

# Via CLI - Edit /etc/pihole/custom.list
ssh admin@192.168.40.35
sudo nano /etc/pihole/custom.list

# Add entries (format: IP HOSTNAME)
192.168.40.10 proxmox-01.homelab.local
192.168.40.11 proxmox-02.homelab.local
192.168.40.12 proxmox-03.homelab.local

# Restart DNS
pihole restartdns
```

#### Add Custom DNS Forwarder
```bash
# Via Web UI
# Settings → DNS → Upstream DNS Servers
# Add: Custom 1: 1.1.1.1
# Add: Custom 2: 8.8.8.8

# Via CLI
sudo nano /etc/pihole/setupVars.conf
# Add: PIHOLE_DNS_1=1.1.1.1
# Add: PIHOLE_DNS_2=8.8.8.8

pihole restartdns
```

### Blocklist Management

#### Update Blocklists
```bash
# Update gravity (blocklists)
pihole -g
# Or: pihole updateGravity

# View last update time
pihole -c  # Check dashboard

# Scheduled updates: Weekly (Sunday 3am via cron)
```

#### Add Custom Blocklist
```bash
# Via Web UI
# Group Management → Adlists → Add a new adlist
# URL: https://example.com/blocklist.txt

# Update gravity after adding
pihole -g

# Via CLI
sudo sqlite3 /etc/pihole/gravity.db \
  "INSERT INTO adlist (address, enabled) VALUES ('https://example.com/blocklist.txt', 1);"
pihole -g
```

#### Whitelist Domain
```bash
# Via CLI
pihole -w example.com

# Multiple domains
pihole -w domain1.com domain2.com

# Via Web UI
# Whitelist → Add domain to whitelist
```

#### Blacklist Domain
```bash
# Via CLI
pihole -b bad-domain.com

# Via Web UI
# Blacklist → Add domain to blacklist
```

### Query Logging

#### View Recent Queries
```bash
# Tail live queries
pihole -t

# View log file
tail -f /var/log/pihole.log

# Via Web UI
# Query Log → Show recent queries
```

#### Disable Query Logging (Privacy)
```bash
# Disable logging
pihole logging off

# Enable logging
pihole logging on
```

### Backup Pi-hole Configuration

```bash
# Via Web UI
# Settings → Teleporter → Backup
# Downloads: pi-hole-config-YYYY-MM-DD.tar.gz

# Via CLI
ssh admin@192.168.40.35
pihole -a -t  # Creates teleporter backup

# Copy to backup server
scp /var/www/html/admin/teleporter_*.tar.gz \
  admin@192.168.40.20:/mnt/backups/pihole/
```

### Restore Pi-hole Configuration

```bash
# Via Web UI
# Settings → Teleporter → Restore
# Upload backup file

# Via CLI
scp admin@192.168.40.20:/mnt/backups/pihole/teleporter_latest.tar.gz /tmp/
sudo pihole -a -t /tmp/teleporter_latest.tar.gz
pihole restartdns
```

### Disaster Recovery

```bash
# 1. Restore VM from Proxmox backup
# 2. Update Pi-hole
ssh admin@192.168.40.35
pihole -up

# 3. Restore configuration
# Upload teleporter backup via Web UI

# 4. Verify DNS
dig @192.168.40.35 google.com

# Expected RTO: 1 hour
# Expected RPO: 24 hours
```

---

## Nginx - Reverse Proxy

### Service Information
- **VM ID:** 104
- **IP Address:** 192.168.40.40
- **Hostname:** nginx.homelab.local
- **OS:** Ubuntu 22.04
- **Purpose:** Reverse proxy, SSL termination, load balancing
- **HA Enabled:** Yes

### Service Management

#### Check Service Status
```bash
# SSH to Nginx server
ssh admin@192.168.40.40

# Check Nginx status
systemctl status nginx

# Test configuration
sudo nginx -t
# Expected: "syntax is ok" and "test is successful"

# Check listening ports
ss -tlnp | grep nginx
# Expected: :80 and :443
```

#### Start/Stop/Restart Services
```bash
# Stop Nginx
sudo systemctl stop nginx

# Start Nginx
sudo systemctl start nginx

# Restart Nginx (brief downtime)
sudo systemctl restart nginx

# Reload configuration (no downtime)
sudo systemctl reload nginx
```

#### Service Health Check
```bash
# Test HTTP
curl -I http://192.168.40.40
# Expected: HTTP 301 (redirect to HTTPS)

# Test HTTPS
curl -k -I https://192.168.40.40
# Expected: HTTP 200 or 302

# Test specific service proxy
curl -k -I https://192.168.40.40/proxmox
# Expected: HTTP 200
```

### Configuration Management

#### Nginx Configuration Structure
```
/etc/nginx/
├── nginx.conf              # Main config
├── sites-available/        # Available sites
│   ├── default
│   ├── proxmox.conf
│   ├── freeipa.conf
│   └── ...
└── sites-enabled/          # Enabled sites (symlinks)
    ├── default -> ../sites-available/default
    ├── proxmox.conf -> ../sites-available/proxmox.conf
    └── ...
```

#### Add New Reverse Proxy
```bash
# Create new site config
sudo nano /etc/nginx/sites-available/newservice.conf

# Example configuration:
server {
    listen 80;
    server_name newservice.homelab.local;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name newservice.homelab.local;

    ssl_certificate /etc/ssl/certs/homelab.crt;
    ssl_certificate_key /etc/ssl/private/homelab.key;

    location / {
        proxy_pass http://192.168.40.50:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/newservice.conf /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

#### Remove Reverse Proxy
```bash
# Disable site
sudo rm /etc/nginx/sites-enabled/oldservice.conf

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Optionally delete config file
sudo rm /etc/nginx/sites-available/oldservice.conf
```

### SSL Certificate Management

#### Check Certificate Expiry
```bash
# Check certificate
sudo openssl x509 -in /etc/ssl/certs/homelab.crt -noout -dates
# Note: Expiry date

# Check via web
echo | openssl s_client -connect 192.168.40.40:443 2>/dev/null | \
  openssl x509 -noout -dates
```

#### Renew Let's Encrypt Certificate
```bash
# If using Certbot
sudo certbot renew --nginx

# Test renewal (dry run)
sudo certbot renew --dry-run

# Auto-renewal via cron (already configured)
cat /etc/cron.d/certbot
```

### Access Logs

#### View Access Logs
```bash
# Real-time access log
tail -f /var/log/nginx/access.log

# Error log
tail -f /var/log/nginx/error.log

# Specific site logs
tail -f /var/log/nginx/proxmox-access.log
```

#### Analyze Logs
```bash
# Top IP addresses
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10

# Top requested URLs
awk '{print $7}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10

# HTTP status codes
awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn
```

### Backup Nginx Configuration

```bash
# Backup entire config
ssh admin@192.168.40.40
sudo tar -czf /tmp/nginx-config-$(date +%Y%m%d).tar.gz /etc/nginx

# Copy to backup server
scp /tmp/nginx-config-*.tar.gz \
  admin@192.168.40.20:/mnt/backups/nginx/
```

### Disaster Recovery

```bash
# 1. Restore VM from Proxmox backup
# 2. Restore configuration if needed
scp admin@192.168.40.20:/mnt/backups/nginx/nginx-config-latest.tar.gz /tmp/
sudo tar -xzf /tmp/nginx-config-latest.tar.gz -C /

# 3. Test and reload
sudo nginx -t
sudo systemctl restart nginx

# Expected RTO: 4 hours
```

---

## Rsyslog - Centralized Logging

### Service Information
- **VM ID:** 105
- **IP Address:** 192.168.40.30
- **Hostname:** syslog.homelab.local
- **OS:** Ubuntu 22.04
- **Purpose:** Centralized log collection
- **Ports:** TCP/UDP 514

### Service Management

#### Check Service Status
```bash
# SSH to syslog server
ssh admin@192.168.40.30

# Check rsyslog status
systemctl status rsyslog

# Check listening ports
ss -tlnp | grep rsyslog  # TCP 514
ss -ulnp | grep rsyslog  # UDP 514
```

#### Start/Stop/Restart Services
```bash
# Restart rsyslog
sudo systemctl restart rsyslog

# Check for config errors
sudo rsyslogd -N1
# Expected: "rsyslogd: version X, config validation run"
```

### Log Management

#### View Collected Logs
```bash
# Logs stored in: /var/log/remote/
ls -lh /var/log/remote/

# View logs from specific host
tail -f /var/log/remote/proxmox-01/syslog

# View all logs (live)
tail -f /var/log/remote/*/syslog
```

#### Configure Log Rotation
```bash
# Edit logrotate config
sudo nano /etc/logrotate.d/rsyslog-remote

# Example configuration:
/var/log/remote/*/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    sharedscripts
    postrotate
        /usr/bin/killall -HUP rsyslogd
    endscript
}

# Test logrotate
sudo logrotate -d /etc/logrotate.d/rsyslog-remote
```

### Configure Clients to Send Logs

#### Linux Client Configuration
```bash
# On client (Proxmox, VM, etc.)
sudo nano /etc/rsyslog.d/50-remote.conf

# Add:
*.* @192.168.40.30:514  # UDP
*.* @@192.168.40.30:514 # TCP (more reliable)

# Restart rsyslog on client
sudo systemctl restart rsyslog
```

#### pfSense Configuration
```
# Via pfSense WebGUI:
# Status → System Logs → Settings
# Remote Logging Options:
#   Enable Remote Logging: ✓
#   Remote log servers: 192.168.40.30:514
#   Everything: ✓
```

### Disaster Recovery

```bash
# Logs are ephemeral - recovery focuses on re-establishing collection
# 1. Restore VM
# 2. Verify clients are sending logs
# 3. Monitor for 24 hours

# Expected RTO: 24 hours (not critical)
```

---

## NTP - Time Synchronization

### Service Information
- **VM ID:** 106
- **IP Address:** 192.168.40.45
- **Hostname:** ntp.homelab.local
- **OS:** Ubuntu 22.04
- **Purpose:** Stratum 2 NTP server
- **Port:** UDP 123

### Service Management

#### Check Service Status
```bash
# SSH to NTP server
ssh admin@192.168.40.45

# Check chronyd status
systemctl status chronyd

# Check NTP sources
chronyc sources
# Expected: Multiple upstream servers marked with "*"

# Check synchronization status
chronyc tracking
# Note: System time offset should be <50ms
```

#### Start/Stop/Restart Services
```bash
# Restart chronyd
sudo systemctl restart chronyd

# Force time sync
sudo chronyc -a makestep
```

### Time Synchronization

#### Check Time Offset
```bash
# Check offset from upstream
chronyc tracking | grep "System time"
# Expected: <0.050 seconds

# Check all sources
chronyc sources -v
```

#### Add NTP Source
```bash
# Edit chrony config
sudo nano /etc/chrony/chrony.conf

# Add upstream server
server 0.pool.ntp.org iburst
server 1.pool.ntp.org iburst

# Restart service
sudo systemctl restart chronyd
```

### Configure Clients

#### Linux Client
```bash
# Configure to use local NTP
sudo nano /etc/chrony/chrony.conf

# Comment out default servers, add:
server 192.168.40.45 iburst

# Restart chronyd
sudo systemctl restart chronyd

# Verify
chronyc sources
# Should show ntp.homelab.local
```

#### Proxmox Node
```bash
# Edit chrony config
nano /etc/chrony/chrony.conf

# Add local NTP server
server 192.168.40.45 iburst prefer

# Restart
systemctl restart chronyd
```

---

## Service Dependencies

### Startup Order
1. **NTP** (no dependencies)
2. **FreeIPA** (depends on NTP for Kerberos)
3. **Pi-hole** (depends on FreeIPA for DNS forwarding)
4. **Nginx** (depends on Pi-hole for DNS resolution)
5. **Rsyslog** (no critical dependencies)

### Dependency Graph
```
NTP
 └─→ FreeIPA
      └─→ Pi-hole
           └─→ Nginx

Rsyslog (independent)
```

### Cross-Service Impacts

| Service Down | Impact on Other Services |
|--------------|--------------------------|
| **FreeIPA** | Wireless auth fails, LDAP queries fail |
| **Pi-hole** | DNS fails, internet access degraded |
| **Nginx** | External service access fails |
| **Rsyslog** | Log collection stops (logs stored locally) |
| **NTP** | Time drift causes Kerberos failures after ~5 minutes |

---

## Troubleshooting

### FreeIPA Issues

#### Kerberos Authentication Failing
```bash
# Check time sync (critical for Kerberos)
ssh admin@192.168.40.25
timedatectl
# Time must be within 5 minutes of NTP server

# Restart Kerberos
sudo systemctl restart krb5kdc

# Test kinit
kinit admin
# If fails, check /var/log/krb5kdc.log
```

#### RADIUS Not Working
```bash
# Check RADIUS service
systemctl status radiusd

# Test locally
radtest testuser password localhost 0 testing123

# Check logs
tail -f /var/log/radius/radius.log

# Common issue: Shared secret mismatch with UniFi
```

### Pi-hole Issues

#### DNS Not Resolving
```bash
# Check FTL service
systemctl status pihole-FTL

# Test DNS locally
dig @127.0.0.1 google.com

# If fails, restart FTL
sudo systemctl restart pihole-FTL

# Check upstream DNS
pihole -c
# Verify upstream servers are responding
```

#### Web Interface Not Accessible
```bash
# Check lighttpd (web server)
systemctl status lighttpd

# Restart web server
sudo systemctl restart lighttpd

# Check PHP
php -v

# Check web logs
tail -f /var/log/lighttpd/error.log
```

### Nginx Issues

#### 502 Bad Gateway
```bash
# Proxy target is down
# Check backend service:
curl http://192.168.40.50:8080  # Example backend

# If backend is down, start it

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log
```

#### Certificate Errors
```bash
# Check certificate validity
sudo openssl x509 -in /etc/ssl/certs/homelab.crt -noout -dates

# If expired, renew certificate
sudo certbot renew --nginx
```

---

## Automated Health Checks

### Health Check Script
**Location:** `/usr/local/bin/health-check.sh`

```bash
#!/bin/bash
# Service health check script

echo "=== Core Services Health Check ==="
echo "Timestamp: $(date)"
echo

# FreeIPA
echo -n "FreeIPA (192.168.40.25): "
if curl -k -s https://192.168.40.25/ipa/ui/ > /dev/null; then
  echo "✓ OK"
else
  echo "✗ FAIL"
fi

# Pi-hole
echo -n "Pi-hole DNS (192.168.40.35): "
if dig +short @192.168.40.35 google.com > /dev/null; then
  echo "✓ OK"
else
  echo "✗ FAIL"
fi

# Nginx
echo -n "Nginx (192.168.40.40): "
if curl -k -s -o /dev/null -w "%{http_code}" https://192.168.40.40 | grep -q "200\|301\|302"; then
  echo "✓ OK"
else
  echo "✗ FAIL"
fi

# Rsyslog
echo -n "Rsyslog (192.168.40.30): "
if nc -zv -w 2 192.168.40.30 514 2>&1 | grep -q "succeeded"; then
  echo "✓ OK"
else
  echo "✗ FAIL"
fi

# NTP
echo -n "NTP (192.168.40.45): "
if ntpdate -q 192.168.40.45 2>&1 | grep -q "offset"; then
  echo "✓ OK"
else
  echo "✗ FAIL"
fi

echo
echo "=== End Health Check ==="
```

**Usage:**
```bash
# Run manually
/usr/local/bin/health-check.sh

# Automated (via cron - every 5 minutes)
*/5 * * * * /usr/local/bin/health-check.sh | /usr/local/bin/send-alert-if-failure.sh
```

---

**End of Runbook**

*Last Reviewed: November 10, 2025*
*Next Review: February 10, 2026 (Quarterly)*

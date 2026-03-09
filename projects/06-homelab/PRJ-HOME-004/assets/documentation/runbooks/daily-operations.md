# Daily Operations Runbook

**Purpose:** Standard daily operational procedures for homelab infrastructure
**Audience:** System administrators
**Frequency:** Daily (morning routine)
**Duration:** ~15-20 minutes

---

## Prerequisites

- [ ] VPN connection established (WireGuard)
- [ ] Access to Grafana dashboards
- [ ] Access to Proxmox web interface
- [ ] Notification channels verified (email/Slack)

---

## Daily Health Check Procedures

### 1. System Health Overview (5 minutes)

**Access Grafana Dashboard:**
```
URL: https://grafana.homelab.local
Dashboard: "Homelab - System Overview"
```

**Check the following metrics:**

- [ ] **Overall Status:** All services showing green status
- [ ] **Uptime:** No unexpected restarts in last 24 hours
- [ ] **CPU Usage:** < 70% average across all hosts
- [ ] **Memory Usage:** < 80% on all systems
- [ ] **Disk Space:** > 20% free on all filesystems
- [ ] **Network Traffic:** No unusual spikes or drops

**Expected Values:**
| Metric | Normal Range | Alert Threshold |
|--------|--------------|-----------------|
| CPU Usage | 20-50% | > 80% |
| Memory Usage | 40-70% | > 90% |
| Disk I/O | < 80% saturation | > 95% |
| Network Latency | < 10ms internal | > 50ms |

### 2. Backup Verification (3 minutes)

**Check Proxmox Backup Status:**
```bash
# SSH to Proxmox host
ssh root@192.168.10.10

# Check last backup job status
pvesh get /cluster/backup --output-format json | jq '.[] | select(.enabled == 1)'

# Verify backup completion
cat /var/log/vzdump.log | tail -n 50
```

**Verification checklist:**
- [ ] All VMs backed up successfully (exit code 0)
- [ ] Backup duration within normal range (< 2 hours)
- [ ] No warnings or errors in backup logs
- [ ] Backup files present on NFS storage
- [ ] Backup file sizes reasonable (not 0 bytes)

**Expected backup times:**
| VM ID | Name | Expected Duration |
|-------|------|-------------------|
| 100 | nginx-proxy | 5-10 minutes |
| 101 | monitoring-stack | 15-20 minutes |
| 102 | immich-server | 30-45 minutes |
| 103 | wikijs | 10-15 minutes |

### 3. Alert Review (3 minutes)

**Check Prometheus Alerts:**
```
URL: https://prometheus.homelab.local/alerts
```

- [ ] No active critical alerts
- [ ] Review resolved alerts from last 24 hours
- [ ] Verify alert notification delivery
- [ ] Document any recurring warnings

**Common alerts and responses:**
| Alert Name | Severity | Typical Cause | Action Required |
|------------|----------|---------------|-----------------|
| HighCPUUsage | Warning | Batch job running | Monitor, no action unless prolonged |
| DiskSpaceWarning | Warning | Log growth | Schedule log rotation |
| BackupJobFailed | Critical | Storage full / VM locked | Investigate immediately |
| ServiceEndpointDown | Critical | Service crash | Restart service, check logs |

### 4. Log Review (4 minutes)

**Check Loki for critical logs:**
```
URL: https://grafana.homelab.local/explore
Query: {job=~".+"} |= "error" or "critical" or "fail"
Time range: Last 24 hours
```

**Review logs from:**
- [ ] Proxmox system logs (`/var/log/syslog`)
- [ ] Container logs (via Loki)
- [ ] Firewall logs (UniFi Gateway)
- [ ] VPN connection logs

**Key log indicators to watch:**
```bash
# SSH authentication failures (potential brute force)
ssh root@192.168.10.10
grep "Failed password" /var/log/auth.log | tail -n 20

# ZFS pool errors
ssh root@192.168.10.11
zpool status tank | grep -i error

# Docker container restarts
docker ps -a --filter "status=exited" --filter "since=24h"
```

### 5. Security Control Verification (2 minutes)

**Validate fail2ban and audit logging:**
```bash
# Fail2ban status for SSH
sudo fail2ban-client status sshd

# Audit daemon running
sudo systemctl is-active auditd

# Confirm auth events logged today
sudo ausearch -m USER_LOGIN -ts today | tail -n 5
```

**Validate MQTT TLS and 2FA enforcement:**
```bash
# MQTT TLS handshake
openssl s_client -connect mqtt.homelab.local:8883 -servername mqtt.homelab.local </dev/null 2>/dev/null | openssl x509 -noout -dates

# Confirm admin MFA policies in IdP/Vaultwarden/SSO dashboards
```

- [ ] Fail2ban active and banning as expected
- [ ] auditd running and shipping logs to Loki
- [ ] MQTT TLS certificate valid and not expiring within 30 days
- [ ] 2FA enforced on admin portals (Proxmox, UniFi, Vaultwarden)

### 6. Service Availability Test (2 minutes)

**Test critical service endpoints:**
```bash
# From admin workstation
curl -I https://photos.homelab.local
curl -I https://wiki.homelab.local
curl -I https://grafana.homelab.local

# Expected response: HTTP/2 200
# Response time: < 500ms
```

- [ ] Immich photo service responding
- [ ] Wiki.js responding
- [ ] Grafana responding
- [ ] Nginx Proxy Manager accessible
- [ ] All SSL certificates valid

### 7. Capacity Planning Check (3 minutes)

**Review growth trends:**
```
Dashboard: "Homelab - Capacity Planning"
```

- [ ] Storage growth rate (GB/day)
- [ ] Memory usage trends
- [ ] Network bandwidth utilization
- [ ] Container resource consumption

**Capacity thresholds:**
| Resource | Current | Growth Rate | Estimated Full |
|----------|---------|-------------|----------------|
| ZFS Pool | 45% | 2 GB/day | 6 months |
| RAM | 60% | 0.5%/week | > 1 year |
| CPU | 35% | Stable | N/A |

---

## Issue Triage and Escalation

### Severity Levels

**P0 - Critical (Immediate action required):**
- Complete service outage
- Data loss or corruption detected
- Security breach indicators
- Backup failures

**P1 - High (Action required within 4 hours):**
- Partial service degradation
- High resource utilization (>90%)
- SSL certificate expiring within 7 days
- Failed update installations

**P2 - Medium (Action required within 24 hours):**
- Performance degradation
- Non-critical service warnings
- Minor configuration drift
- Documentation updates needed

**P3 - Low (Action required within 1 week):**
- Optimization opportunities
- Nice-to-have features
- Cosmetic issues
- Routine maintenance

### Escalation Contacts

| Role | Contact | Responsibility |
|------|---------|----------------|
| Primary Admin | Samuel Jackson | All infrastructure issues |
| Sponsor | Andrew Vongsady | Budget and resource approvals |
| Family Support | N/A | User-facing service issues |

---

## Daily Checklist Summary

```
Daily Operations Checklist - Date: __________

[ ] Grafana dashboard review - All green
[ ] Backup verification - All successful
[ ] Alert review - No active criticals
[ ] Log review - No anomalies
[ ] Service availability - All responding
[ ] Capacity planning - No concerns

Notes:
_________________________________________________
_________________________________________________
_________________________________________________

Completed by: _________________ Time: _________
```

---

## Automation Opportunities

**Future enhancements:**
1. Automated daily health report (email digest)
2. Slack bot for alert notifications
3. Automated backup verification script
4. Dashboard screenshot capture for daily records
5. Synthetic transaction monitoring

---

## Related Documentation

- [Weekly Maintenance Procedures](./weekly-maintenance.md)
- [Incident Response Runbook](./incident-response.md)
- [Disaster Recovery Plan](./disaster-recovery.md)
- [Monitoring Dashboard Guide](../monitoring-guide.md)

---

**Last Updated:** 2024-12-16
**Owner:** Samuel Jackson
**Review Frequency:** Monthly

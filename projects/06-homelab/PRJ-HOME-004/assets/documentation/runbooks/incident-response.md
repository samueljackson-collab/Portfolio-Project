# Incident Response Runbook

**Purpose:** Structured approach to identifying, responding to, and resolving infrastructure incidents
**Audience:** System administrators, on-call engineers
**Scope:** All homelab infrastructure components

---

## Incident Severity Classification

### P0 - Critical (Response Time: Immediate)

**Criteria:**
- Complete service outage affecting all users
- Data loss or corruption in progress
- Active security breach
- Imminent risk of cascading failure

**Examples:**
- Proxmox host completely down
- Ransomware infection detected
- All services unreachable
- Critical backup failure detected

**Response:**
- Drop all other tasks immediately
- Notify sponsor within 15 minutes
- Begin incident log
- Engage disaster recovery procedures if needed

---

### P1 - High (Response Time: < 1 hour)

**Criteria:**
- Partial service degradation
- Single critical service down
- High resource exhaustion (>95%)
- Failed backup jobs

**Examples:**
- Photo service (Immich) unavailable
- Monitoring stack offline
- Disk space critical (>95%)
- SSL certificate expired

**Response:**
- Acknowledge alert within 15 minutes
- Begin troubleshooting
- Post status update
- Escalate to P0 if worsening

---

### P2 - Medium (Response Time: < 4 hours)

**Criteria:**
- Performance degradation
- Non-critical service warnings
- Approaching resource limits
- Single host/service affected

**Examples:**
- Slow response times (>2s)
- High CPU usage (>80%)
- Backup warnings (not failures)
- Minor configuration drift

**Response:**
- Review during next scheduled maintenance window
- Document for tracking
- Schedule fix within 24 hours

---

### P3 - Low (Response Time: < 1 week)

**Criteria:**
- Cosmetic issues
- Feature requests
- Optimization opportunities
- Documentation gaps

**Examples:**
- Dashboard formatting issues
- Missing documentation
- Performance optimization ideas
- Nice-to-have features

**Response:**
- Add to backlog
- Review during planning sessions
- Prioritize with other work

---

## Incident Response Process

### Phase 1: Detection & Triage (5 minutes)

**How incidents are detected:**
1. Automated alerts (Prometheus → Alertmanager)
2. Monitoring dashboard anomalies
3. User reports (family members)
4. Manual observation during daily checks

**Initial triage steps:**

```bash
# 1. Verify the alert is legitimate
# Check Grafana dashboard
open https://grafana.homelab.local

# 2. Determine affected service(s)
# Check service status
curl -I https://[affected-service].homelab.local

# 3. Quick connectivity tests
ping 192.168.10.10  # Proxmox
ping 192.168.10.11  # TrueNAS
ping 192.168.30.X   # Application services

# 4. Check for related alerts
# Prometheus: https://prometheus.homelab.local/alerts
```

**Create incident ticket:**
```
Incident ID: INC-YYYYMMDD-### (e.g., INC-20241216-001)
Severity: [P0/P1/P2/P3]
Start Time: [HH:MM UTC]
Affected Services: [list]
Impact: [user-facing / internal]
Status: INVESTIGATING
```

---

### Phase 2: Investigation & Diagnosis (15-30 minutes)

**Systematic troubleshooting approach:**

#### Step 1: Check Service Logs

```bash
# For containerized services
docker logs [container-name] --tail 100 --follow

# For system services
journalctl -u [service-name] -n 100 -f

# Via Loki (centralized logging)
# Grafana > Explore
# Query: {job="[service]"} |= "error" or "fail"
# Time range: Last 1 hour
```

#### Step 2: Check Resource Utilization

```bash
# CPU and memory
htop
# or via monitoring
# Dashboard: "Homelab - Resource Utilization"

# Disk space
df -h
zpool list

# Network connectivity
netstat -tulpn | grep LISTEN
ss -tulpn | grep [port]

# Docker container stats
docker stats --no-stream
```

#### Step 3: Check Dependencies

```bash
# Database connectivity
docker exec -it [db-container] psql -U [user] -c "SELECT 1"

# NFS mounts
df -h | grep nfs
showmount -e 192.168.10.11

# DNS resolution
nslookup photos.homelab.local
dig @192.168.10.1 grafana.homelab.local

# Network segmentation
# Check firewall rules in UniFi
# Verify VLAN connectivity
```

#### Step 4: Review Recent Changes

```bash
# Check recent configuration changes
git log --oneline --since="24 hours ago"

# Check recent system updates
grep "upgraded" /var/log/dpkg.log | tail -n 20

# Check cron jobs
crontab -l
ls -la /etc/cron.d/

# Check Docker container changes
docker ps -a --filter "since=24h"
```

---

### Phase 3: Containment & Mitigation (varies)

**Goal:** Stop the bleeding, prevent escalation

**Common mitigation strategies:**

#### Service Restart
```bash
# Restart Docker container
docker restart [container-name]

# Restart system service
systemctl restart [service-name]

# Restart VM
qm stop [vmid] && qm start [vmid]
```

#### Resource Relief
```bash
# Clear disk space
docker system prune -af
rm -rf /tmp/*
journalctl --vacuum-time=7d

# Kill runaway processes
top -o %CPU
kill [PID]

# Restart overloaded service
systemctl restart [service]
```

#### Traffic Redirection
```bash
# Update DNS to point to backup service
# Via Cloudflare or local DNS

# Enable maintenance mode
# Nginx proxy: return 503 with custom page
```

#### Rollback Changes
```bash
# Revert recent configuration
git revert [commit-hash]
git push

# Restore from backup
qmrestore /mnt/backups/vzdump-qemu-[vmid]-[date].vma.zst [vmid]

# Roll back container version
docker pull [image]:[previous-tag]
docker-compose up -d
```

---

### Phase 4: Recovery & Validation (15-60 minutes)

**Recovery steps:**

1. **Implement fix:**
   - Apply configuration change
   - Update service version
   - Replace failed hardware
   - Restore from backup

2. **Verify service restoration:**
   ```bash
   # Test service endpoints
   curl -I https://[service].homelab.local

   # Check service logs for errors
   docker logs [container] --tail 50

   # Monitor metrics for 5-10 minutes
   # Dashboard: "Homelab - Service Health"
   ```

3. **Validate data integrity:**
   ```bash
   # Database consistency check
   docker exec [db-container] pg_dump -U [user] [db] > /dev/null

   # File system check
   zpool scrub tank

   # Application-level verification
   # Log in and test critical workflows
   ```

4. **Re-enable monitoring:**
   ```bash
   # Unmute alerts in Alertmanager
   # Re-enable scheduled jobs
   # Verify alert notifications working
   ```

---

### Phase 5: Communication (throughout incident)

**Status update template:**

```
=== INCIDENT UPDATE ===
Incident ID: INC-20241216-001
Status: [INVESTIGATING / IDENTIFIED / MONITORING / RESOLVED]
Time: [HH:MM UTC]

Current Situation:
- [Brief description of current state]

Impact:
- Services affected: [list]
- Users affected: [count / "all" / "none"]
- Functionality impacted: [description]

Actions Taken:
- [Bullet list of steps taken]

Next Steps:
- [What's being done next]

Estimated Resolution: [time or "unknown"]
Next Update: [time]

Contact: Samuel Jackson (Admin)
```

**Communication channels:**
- **Internal:** Slack/Email (sponsor notification)
- **Users:** Service status page (if implemented)
- **Escalation:** Phone call for P0 incidents

---

### Phase 6: Post-Incident Review (within 48 hours)

**Required for P0 and P1 incidents, optional for P2/P3**

**Post-Incident Report Template:**

```markdown
# Post-Incident Review: INC-YYYYMMDD-###

## Incident Summary

| Field | Value |
|-------|-------|
| **Incident ID** | INC-20241216-001 |
| **Severity** | P1 |
| **Date** | 2024-12-16 |
| **Duration** | 2 hours 15 minutes |
| **Services Affected** | Immich photo service |
| **Users Impacted** | 5 family members |
| **Responders** | Samuel Jackson |

## Timeline

| Time (UTC) | Event |
|------------|-------|
| 14:00 | Alert fired: ServiceEndpointDown for Immich |
| 14:05 | Incident acknowledged, investigation started |
| 14:15 | Root cause identified: PostgreSQL disk full |
| 14:20 | Mitigation started: Log cleanup |
| 14:35 | Service restored, monitoring |
| 16:15 | Incident closed after stable operation |

## Root Cause Analysis

**What Happened:**
PostgreSQL transaction logs (WAL) filled the disk partition, causing the database to stop accepting connections. This made the Immich photo service unavailable.

**Why It Happened:**
- WAL archiving was not properly configured
- Disk space monitoring alert threshold too high (90% vs 80%)
- No automatic log rotation for PostgreSQL

**Contributing Factors:**
- Recent increase in photo uploads (holiday season)
- Monitoring dashboard not checked daily

## Impact Assessment

**Service Downtime:**
- Immich photo service: 2 hours 15 minutes
- Uptime impact: 0.95% (for 90-day period)

**User Impact:**
- 2 family members reported inability to upload photos
- No data loss
- No security implications

**Business Impact:**
- Minor inconvenience during holiday photo sharing
- No financial impact

## Resolution Steps

1. Cleared old PostgreSQL WAL files (freed 15GB)
2. Configured WAL archiving properly
3. Adjusted disk space alert threshold to 80%
4. Verified service restoration
5. Monitored for 2 hours to ensure stability

## What Went Well

✅ Alert fired correctly and promptly
✅ Investigation completed within 15 minutes
✅ Root cause identified quickly
✅ No data loss occurred
✅ Communication with sponsor timely

## What Went Wrong

❌ Alert threshold not aggressive enough
❌ Daily health checks were not performed
❌ PostgreSQL configuration incomplete
❌ No automatic remediation for disk space

## Action Items

| Action | Owner | Due Date | Priority | Status |
|--------|-------|----------|----------|--------|
| Configure WAL archiving for all databases | Samuel | 2024-12-20 | High | ✅ Done |
| Lower disk alert threshold to 80% | Samuel | 2024-12-17 | High | ✅ Done |
| Implement automated log rotation | Samuel | 2024-12-23 | Medium | 🟡 In Progress |
| Add PostgreSQL monitoring dashboard | Samuel | 2024-12-30 | Medium | ⚪ Pending |
| Schedule quarterly DR drill | Samuel | 2025-03-01 | Low | ⚪ Pending |

## Lessons Learned

1. **Proactive monitoring is critical:** Daily health checks would have identified the disk space issue before it became an incident.

2. **Alert tuning matters:** The 90% threshold was too late to take preventive action. 80% provides better lead time.

3. **Complete configuration is essential:** Partial PostgreSQL setup (missing WAL archiving) caused this incident.

4. **Documentation pays off:** Having runbooks available made troubleshooting faster and more systematic.

## Preventive Measures

- Automated daily health check script
- Enhanced PostgreSQL monitoring
- Disk space forecasting dashboard
- Quarterly configuration audits

---

**Report Completed By:** Samuel Jackson
**Review Date:** 2024-12-18
**Approved By:** Andrew Vongsady (Sponsor)
```

---

## Incident Management Tools

### Logging

```bash
# Incident log file location
/var/log/homelab/incidents/INC-YYYYMMDD-###.log

# Log format
[YYYY-MM-DD HH:MM:SS UTC] [SEVERITY] [ACTION] Description

# Example
echo "[$(date -u +%Y-%m-%d\ %H:%M:%S\ UTC)] [P1] [DETECTED] Immich service unreachable" >> /var/log/homelab/incidents/INC-20241216-001.log
```

### Status Page

```bash
# Simple status page (future enhancement)
# Static HTML served by Nginx

# Status options:
# ✅ Operational
# ⚠️ Degraded Performance
# ❌ Major Outage
# 🔧 Maintenance
```

### Communication Templates

**Initial Alert (Within 15 minutes):**
```
Subject: [P1] Homelab Service Degradation - Immich Photo Service

We are investigating an issue with the Immich photo service.

Status: INVESTIGATING
Start Time: 14:00 UTC
Affected Services: Photo uploads and sharing
User Impact: Unable to upload new photos

We will provide an update within 30 minutes.

- Homelab Admin Team
```

**Resolution Notice:**
```
Subject: [RESOLVED] Homelab Service Degradation - Immich Photo Service

The incident affecting the Immich photo service has been resolved.

Status: RESOLVED
Resolution Time: 16:15 UTC
Total Duration: 2 hours 15 minutes
Root Cause: Database disk space exhaustion

All services are now operational. A detailed post-incident report will be published within 48 hours.

Thank you for your patience.

- Homelab Admin Team
```

---

## On-Call Procedures

**Responsibilities:**
- Respond to alerts within SLA timeframes
- Triage and resolve incidents
- Communicate status updates
- Document all actions taken
- Escalate when appropriate

**On-Call Schedule:**
- Primary: Samuel Jackson (24/7)
- Backup: Andrew Vongsady (business hours)

**Escalation Criteria:**
- Unable to resolve within 1 hour (P1)
- Requires budget approval
- Impacts external dependencies
- Requires physical datacenter access

---

## Related Documentation

- [Daily Operations Runbook](./daily-operations.md)
- [Disaster Recovery Plan](./disaster-recovery.md)
- [Security Incident Response](../security/security-incident-response.md)
- [Service Dependency Map](../architecture/service-dependencies.md)

---

**Last Updated:** 2024-12-16
**Owner:** Samuel Jackson
**Review Frequency:** Quarterly

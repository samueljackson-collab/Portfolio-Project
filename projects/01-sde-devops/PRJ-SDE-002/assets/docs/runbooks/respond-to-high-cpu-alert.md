# Runbook: Respond to High CPU Alert

## Purpose
Systematic procedure for investigating and resolving high CPU utilization alerts triggered by Prometheus/Alertmanager.

## When to Use
- Alertmanager sends "HighCPUUsage" alert notification
- Grafana dashboard shows CPU >80% for >5 minutes
- User reports service slowness/degradation
- Proactive investigation before alert fires

## Prerequisites

### Required Access
- Grafana: http://192.168.40.201:3000
- Prometheus: http://192.168.40.201:9090
- SSH access to affected hosts
- Proxmox web interface: https://192.168.40.10:8006

### Required Tools
- Web browser (for Grafana/Prometheus)
- SSH client
- `htop`, `ps`, `top` commands

### Time Required
- Initial triage: 5-10 minutes
- Investigation: 10-30 minutes
- Resolution: Varies (immediate to 1 hour)

### Skill Level
Intermediate - Basic Linux system administration

---

## Alert Definition

**Alert Rule (from Prometheus):**
```yaml
alert: HighCPUUsage
expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
for: 5m
severity: warning
annotations:
  summary: "High CPU usage detected on {{ $labels.instance }}"
  description: "CPU usage is {{ $value }}% on {{ $labels.instance }}"
```

**Alert Triggers When:**
- CPU utilization >80% sustained for 5+ minutes
- Applies to any monitored instance
- Excludes brief spikes <5 minutes

---

## Pre-Investigation Checklist

Before starting investigation:

- [ ] Alert notification received (email/Slack)
- [ ] Current time noted (for correlation with events)
- [ ] Access to monitoring tools confirmed
- [ ] Any recent changes/deployments checked (change log)

---

## Procedure

### Step 1: Acknowledge and Assess Severity

**Goal:** Confirm alert validity and determine urgency

**Commands:**
```bash
# Check Alertmanager for active alerts
curl -s http://192.168.40.201:9093/api/v2/alerts | jq '.[] | select(.labels.alertname=="HighCPUUsage")'

# Expected output: JSON showing active alert(s)
```

**In Grafana:**
1. Open Infrastructure Overview dashboard
2. Locate affected instance panel
3. Note current CPU percentage

**Severity Assessment:**

| CPU % | Duration | Severity | Action |
|-------|----------|----------|--------|
| 80-89% | <15 min | Low | Investigate during business hours |
| 80-89% | >15 min | Medium | Investigate within 30 minutes |
| 90-95% | >5 min | High | Investigate immediately |
| >95% | Any | Critical | Immediate action required |

**Validation:**
- [ ] Alert is firing (not resolved)
- [ ] Affected instance identified
- [ ] Severity level determined
- [ ] Dashboard shows current CPU state

**If alert is resolved:** Document false positive, exit procedure.

---

### Step 2: Identify Affected Services

**Goal:** Determine which VM/container and services are impacted

**Prometheus Query:**
```promql
# View current CPU usage for all hosts
100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# View historical CPU (last 6 hours)
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[6h])) * 100)
```

**Check Proxmox for VM details:**
```bash
# SSH to Proxmox host
ssh root@192.168.40.10

# If affected host is 192.168.40.101, find VM ID
qm list | grep "192.168.40.101"
# or for containers:
pct list | grep "192.168.40.101"

# View VM resource usage
qm status [VMID]
```

**Identify running services:**
```bash
# SSH to affected instance
ssh 192.168.40.[IP]

# Quick service check
systemctl list-units --state=running --type=service

# Expected output: List of active services
```

**Validation:**
- [ ] Specific VM/container identified
- [ ] Services running on instance documented
- [ ] Impact to users assessed (service degradation vs. outage)

---

### Step 3: Identify Top CPU Consumers

**Goal:** Find exact processes consuming CPU

**Commands:**
```bash
# SSH to affected instance
ssh 192.168.40.[IP]

# Install htop if not present
apt install -y htop  # Ubuntu/Debian
# or
yum install -y htop  # CentOS/RHEL

# Interactive process viewer (sort by CPU)
htop
# Press F6 → Select PERCENT_CPU → Enter
# Note top 5 processes

# Alternative: top command
top -o %CPU -n 1

# List top CPU consumers (non-interactive)
ps aux --sort=-%cpu | head -n 10

# Expected output:
# USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
# postgres  1234 45.2  8.3 234567 89012 ?       Sl   10:23  12:34 /usr/bin/postgres
# node      5678 32.1  4.1 123456 45678 ?       Ssl  09:15   8:21 node /app/server.js
```

**Analyze process behavior:**
```bash
# Check process runtime
ps -p [PID] -o pid,etime,cmd
# Long runtime may indicate legitimate high usage

# Check process threads
ps -p [PID] -L
# Many threads may indicate concurrency issue

# View process I/O stats
pidstat -p [PID] 1 5
# High %iowait indicates disk-bound, not CPU-bound
```

**Validation:**
- [ ] Top 3-5 CPU-consuming processes identified
- [ ] Process names and PIDs documented
- [ ] Legitimate vs. anomalous processes distinguished

**Common Legitimate High CPU:**
- Scheduled backups (restic, borgbackup)
- Database maintenance (vacuum, reindex)
- Batch processing jobs
- System updates (apt, yum)

**Anomalous High CPU (investigate further):**
- Unknown process names
- Processes from `/tmp` or `/dev/shm`
- Multiple instances of same process (potential loop)
- Crypto-mining processes (xmrig, minerd)

---

### Step 4: Determine Root Cause

**Goal:** Identify why CPU usage is high

#### Scenario A: Legitimate High Usage (Scheduled Job)

**Check cron jobs:**
```bash
# View system cron
crontab -l

# View all user cron jobs
for user in $(cut -f1 -d: /etc/passwd); do
  echo "### Crontab for $user ###"
  crontab -u $user -l 2>/dev/null
done

# Check systemd timers
systemctl list-timers --all
```

**If scheduled job:**
- Note expected completion time
- Allow job to finish if within normal window
- Consider rescheduling to off-peak hours

#### Scenario B: Application Load (Increased Traffic)

**Check web server logs:**
```bash
# Nginx access log (last 100 requests)
tail -n 100 /var/log/nginx/access.log

# Count requests per minute
awk '{print $4}' /var/log/nginx/access.log | cut -d: -f1,2 | sort | uniq -c | tail -n 20

# Check for unusual IPs (potential DDoS)
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -n 10
```

**Check database load:**
```bash
# PostgreSQL active connections
psql -U postgres -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"

# Long-running queries
psql -U postgres -c "SELECT pid, now() - query_start AS duration, query FROM pg_stat_activity WHERE state = 'active' AND now() - query_start > interval '1 minute';"

# Terminate problematic query (if identified)
# psql -U postgres -c "SELECT pg_terminate_backend([PID]);"
```

**If traffic spike:**
- Validate legitimacy (marketing campaign, viral content)
- Scale resources if needed (see Step 5)
- Implement rate limiting if malicious

#### Scenario C: Memory Pressure (Swapping)

**Check swap usage:**
```bash
# View memory and swap
free -h

# Expected: Swap usage should be minimal (<10% of total)
#                total        used        free      shared  buff/cache   available
# Mem:            15Gi       8.2Gi       4.1Gi       124Mi       3.5Gi       6.8Gi
# Swap:          2.0Gi       1.8Gi       200Mi       <-- Problem if high

# View swap activity
vmstat 1 5
# High 'si' (swap in) or 'so' (swap out) indicates swapping

# Identify swap consumers
for pid in $(ls /proc | grep "^[0-9]"); do
  awk '/Swap/{swap+=$2} END {if(swap>0) print swap}' /proc/$pid/smaps 2>/dev/null | \
  awk -v pid=$pid '{print pid, $0}'
done | sort -k2 -rn | head -n 10
```

**If swapping heavily:**
- Immediate: Restart memory-hungry service to clear swap
- Short-term: Increase VM RAM allocation
- Long-term: Optimize application memory usage

#### Scenario D: Runaway Process (Bug/Loop)

**Check for process loops:**
```bash
# Monitor process CPU over time
pidstat -p [PID] 1 10
# Consistent 100% CPU indicates tight loop

# Check process strace (system calls)
strace -p [PID] -c
# Look for excessive futex, poll, or similar calls

# Example output indicating issue:
# % time     seconds  usecs/call     calls    errors syscall
# 99.98    1.234567           12    102345           futex
```

**Check application logs:**
```bash
# Application-specific logs
journalctl -u [SERVICE_NAME] -n 100 --no-pager

# Look for error loops:
# - Repeated connection failures
# - Infinite retry logic
# - Exception handling issues
```

**If runaway process:**
- Immediate action: Restart service (see Step 5)
- Log preservation: Copy logs before restart
- Root cause: Review code, fix bug, deploy patch

---

### Step 5: Implement Resolution

**Choose resolution based on root cause:**

#### Resolution A: Wait for Job Completion (Low Severity)

**When:** Scheduled backup/maintenance in progress

**Action:**
```bash
# Monitor job progress
watch "ps aux | grep [JOB_NAME]"

# Estimate completion time
# (Check logs for job start time and historical duration)

# Document in ticket/log
echo "$(date): Backup job running, expected completion in 15 minutes" >> /var/log/operations.log
```

**Expected Completion:** Alert auto-resolves when job finishes

---

#### Resolution B: Restart Service (Medium Severity)

**When:** Service misbehaving, runaway process, or memory leak

**Action:**
```bash
# Graceful restart
systemctl restart [SERVICE_NAME]

# Verify service restarted
systemctl status [SERVICE_NAME]
# Expected: active (running), new PID

# Monitor CPU post-restart (5 min)
watch "ps aux --sort=-%cpu | head -n 10"

# Expected: CPU drops below 50% within 2 minutes
```

**Validation:**
- [ ] Service restarted successfully
- [ ] No errors in service logs
- [ ] CPU normalized (<50%)
- [ ] Application functionality verified (HTTP 200, database queries work)

---

#### Resolution C: Scale Resources (High Severity - Persistent Load)

**When:** Legitimate increased load, insufficient resources

**Immediate (temporary):**
```bash
# Shutdown non-critical services to free CPU
systemctl stop [NON_CRITICAL_SERVICE]

# Example: Stop monitoring exporter temporarily
systemctl stop node_exporter

# Nice CPU-intensive job to lower priority
renice +10 -p [PID]
```

**Short-term (increase VM resources):**
```bash
# Via Proxmox CLI
# Shutdown VM first
qm stop [VMID]

# Increase CPU cores
qm set [VMID] --cores 4  # from 2 to 4

# Start VM
qm start [VMID]

# Verify new resources
ssh 192.168.40.[IP]
nproc  # Should show 4
```

**Long-term:**
- Horizontal scaling: Add load balancer + second instance
- Vertical scaling: Persistent resource increase
- Optimization: Profile code, optimize database queries

---

#### Resolution D: Kill Malicious Process (Critical - Security Incident)

**When:** Unknown/suspicious process, potential compromise

**Action (CAUTION - Security Incident Response):**
```bash
# Isolate affected VM (block network)
# Via Proxmox firewall or disconnect network adapter

# Kill suspicious process
kill -9 [PID]

# Check for persistence mechanisms
crontab -l
systemctl list-unit-files --state=enabled
cat /etc/rc.local

# Scan for malware
clamscan -r /home /tmp /var/tmp

# Document findings
echo "$(date): Killed suspicious PID [PID], process: [NAME], network isolated" >> /var/log/security-incidents.log
```

**IMPORTANT:** If security incident suspected:
1. Do NOT restart service immediately
2. Preserve evidence (logs, process dumps)
3. Isolate affected system
4. Follow incident response runbook
5. Consider full system rebuild

---

## Post-Resolution Validation

**Verify CPU normalized:**
```bash
# Check current CPU via Prometheus query
curl -s 'http://192.168.40.201:9090/api/v1/query?query=100-(avg(irate(node_cpu_seconds_total{mode="idle",instance="192.168.40.[IP]:9100"}[5m]))*100)' | jq '.data.result[0].value[1]'

# Expected: Value < 70%

# Monitor for 15 minutes
watch -n 60 'curl -s "http://192.168.40.201:9090/api/v1/query?query=..." | jq ".data.result[0].value[1]"'
```

**Check alert status:**
```bash
# Verify alert resolved in Alertmanager
curl -s http://192.168.40.201:9093/api/v2/alerts | jq '.[] | select(.labels.instance=="192.168.40.[IP]:9100" and .labels.alertname=="HighCPUUsage")'

# Expected: Empty array [] (no active alerts)
```

**Service health check:**
```bash
# Application-specific health check
curl -I https://[SERVICE].homelab.local/health
# Expected: HTTP/2 200

# Database connectivity
psql -U user -d database -c "SELECT 1;"
# Expected: 1
```

**Final validation checklist:**
- [ ] CPU < 70% for 15 minutes
- [ ] Alert resolved in Alertmanager
- [ ] Service responding normally
- [ ] No errors in application logs
- [ ] Monitoring dashboards green
- [ ] Incident documented

---

## Documentation & Follow-Up

**Incident Documentation (Required):**

Create entry in operations log:
```bash
cat >> /var/log/operations/cpu-incidents.log << EOF
---
Date: $(date +%Y-%m-%d)
Time: $(date +%H:%M:%S)
Alert: HighCPUUsage
Affected Instance: 192.168.40.[IP]
Service: [SERVICE_NAME]
Peak CPU: [XX]%
Duration: [XX] minutes
Root Cause: [BRIEF DESCRIPTION]
Resolution: [ACTION TAKEN]
Resolved By: [YOUR NAME]
---
EOF
```

**Follow-up Actions (Choose as appropriate):**

- [ ] Update capacity planning if resource-constrained
- [ ] Optimize application code if performance issue
- [ ] Adjust alert threshold if too sensitive
- [ ] Schedule job re-timing if scheduled task
- [ ] Implement rate limiting if traffic spike
- [ ] Security review if suspicious activity
- [ ] Document lessons learned

**Prevention Measures:**

| Root Cause | Prevention |
|------------|------------|
| Scheduled job | Move to off-peak hours (2-4 AM) |
| Traffic spike | Implement auto-scaling, CDN |
| Memory leak | Regular service restarts, fix code |
| Runaway process | Better error handling, circuit breakers |
| Insufficient resources | Proactive capacity monitoring, alerts at 70% |

---

## Escalation

**Escalate if:**
- Unable to identify root cause within 30 minutes
- Resolution attempts fail (CPU remains >80%)
- Security incident suspected
- Critical production service impacted >1 hour

**Escalation Path:**
1. Review with senior engineer (Slack: #infrastructure)
2. Engage on-call engineer (PagerDuty: Ops team)
3. Consider emergency maintenance window

---

## Related Runbooks
- [Respond to High Memory Alert](./respond-to-high-memory-alert.md)
- [Service Restart Procedure](./service-restart-procedure.md)
- [Incident Response: Security Compromise](./security-incident-response.md)
- [Resource Scaling Guide](./scale-vm-resources.md)

## Useful Prometheus Queries

```promql
# CPU usage by instance (current)
100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# CPU usage by mode (breakdown)
avg by(mode) (irate(node_cpu_seconds_total[5m])) * 100

# Top 5 CPU-consuming instances
topk(5, 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100))

# CPU usage correlation with load average
avg by(instance) (node_load15) / on(instance) count by(instance) (node_cpu_seconds_total{mode="idle"})

# Alert history (last 24h)
ALERTS{alertname="HighCPUUsage", alertstate="firing"}[24h]
```

---

**Document Version:** 1.0
**Last Updated:** November 6, 2025
**Author:** Sam Jackson
**Review Frequency:** Quarterly
**Average Resolution Time:** 15-30 minutes

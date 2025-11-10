---
title: Runbook - Host Down
description: Response procedure when a host becomes unreachable
published: true
date: 2025-11-07
tags: [runbook, infrastructure, alert, critical]
---

# Runbook: Host Down

**Alert Name**: `HostDown`
**Severity**: 🔴 Critical
**Response Time**: 5 minutes
**Prometheus Query**: `up == 0`

## Symptoms

- Prometheus alert `HostDown` firing
- Host not responding to ping
- Services on host unavailable
- Grafana dashboards showing "No Data" for host metrics

## Impact Assessment

**Immediate Impact**:
- All services on the affected host are unavailable
- Dependent services may be degraded or unavailable
- Monitoring gaps for the affected host
- Potential data loss if writes were in progress

**Affected Systems**:
- Applications running on the host
- Databases or data stores on the host
- Monitoring and logging for the host
- Downstream services depending on this host

## Immediate Actions (0-5 minutes)

### 1. Confirm the Alert

```bash
# Check Prometheus targets page
# Navigate to: http://prometheus:9090/targets
# Look for the down target

# Verify with ping
ping -c 4 <host_ip>
```

**Expected**: No response if truly down

### 2. Check Alert Context

Review the alert in Alertmanager or Slack:
- When did it start firing?
- How many consecutive scrapes failed?
- Are other hosts in the same network segment affected?

### 3. Identify the Host

```bash
# From Prometheus alert
instance: "192.168.1.21:9100"

# Lookup in inventory
# Check: wiki/projects/homelab/prj-home-002/inventory
```

Example inventory:
| IP | Hostname | Purpose | Critical? |
|----|----------|---------|-----------|
| 192.168.1.21 | wiki-vm | Wiki.js | Yes |
| 192.168.1.22 | homeassistant | Home Assistant | Medium |

## Investigation Steps (5-15 minutes)

### 4. Check Physical/Virtual Host Status

**For VMs (Proxmox)**:
```bash
# SSH to Proxmox host
ssh root@proxmox-host

# Check VM status
qm status <vmid>
# Expected: "status: running" or "status: stopped"

# Check VM resource usage
qm monitor <vmid>
```

**For Physical Hosts**:
- Check power status (lights, KVM)
- Check network cable connection
- Check switch port status

### 5. Check Network Connectivity

```bash
# From Proxmox host or another VM in same VLAN
ping -c 4 <down_host_ip>

# Check if it's a network-wide issue
ping -c 4 <other_host_in_same_vlan>

# Check ARP table
arp -a | grep <down_host_ip>

# Check VLAN configuration (pfSense)
# Navigate to: https://pfsense:443
# Status → DHCP Leases
# Firewall → Rules → [VLAN Interface]
```

### 6. Check Recent Changes

```bash
# Check deployment logs
cat /var/log/deployment/recent.log

# Check system journal (if accessible via console)
journalctl --since "1 hour ago" --priority=err

# Check Prometheus for pattern
# Query: up{instance="192.168.1.21:9100"}[1h]
# Look for: gradual degradation vs sudden stop
```

## Resolution Steps (15-30 minutes)

### Option A: VM/Container Stopped

```bash
# Start the VM
qm start <vmid>

# Monitor startup
qm status <vmid>

# Watch for services to come up (30-60 seconds)
watch -n 2 'curl -s http://<host_ip>:9100/metrics | head -1'

# Verify in Prometheus (wait 15 seconds for scrape)
# Check: http://prometheus:9090/targets
```

### Option B: VM Running But Unresponsive

```bash
# Try console access
qm terminal <vmid>
# or
qm vncproxy <vmid>

# If console responsive, check services
systemctl status node_exporter
systemctl status <critical_service>

# Check system resources
top
df -h
free -h

# Check network interface
ip addr show
ip route show

# Restart networking if needed
systemctl restart networking
```

### Option C: VM Crashed or Frozen

```bash
# Check VM console for kernel panic or errors
qm terminal <vmid>

# If frozen, try graceful shutdown (wait 60s)
qm shutdown <vmid> --timeout 60

# If no response, force stop
qm stop <vmid>

# Check system logs on Proxmox
journalctl -u qemu-server@<vmid>

# Check for resource constraints
pvesh get /nodes/<node>/status

# Start VM
qm start <vmid>
```

### Option D: Network Issue

```bash
# Check pfSense firewall
# Navigate to: Status → System Logs → Firewall
# Look for blocks to/from <host_ip>

# Check VLAN interface status
# Status → Interfaces

# Check DHCP lease
# Status → DHCP Leases

# If static IP conflict:
# Services → DHCP Server → [VLAN] → Static Mappings
# Verify no duplicate IPs

# Test connectivity from pfSense
# Diagnostics → Ping
# Target: <host_ip>

# Check switch port (UniFi Controller)
# Verify port is up and on correct VLAN
```

### Option E: Physical Hardware Issue

For physical hosts:
1. Check power supply (lights, fan noise)
2. Check monitor for POST errors
3. Check boot device (USB, hard drive)
4. Try IPMI/iDRAC if available
5. Physical reboot as last resort

## Verification (30-35 minutes)

### 7. Confirm Host is UP

```bash
# Prometheus should show target UP
# http://prometheus:9090/targets

# Alert should auto-resolve in Alertmanager
# http://alertmanager:9093

# Verify metrics flowing
curl http://<host_ip>:9100/metrics | grep "node_cpu"

# Verify in Grafana dashboards
# Check: Infrastructure Overview dashboard
```

### 8. Verify Services

```bash
# SSH to the host
ssh user@<host_ip>

# Check critical services
systemctl status node_exporter
systemctl status <app_service>

# Check application health endpoint
curl http://localhost:<app_port>/health

# Check logs for errors
journalctl -u <service> --since "5 minutes ago"
```

### 9. Check Dependent Services

```bash
# If this was a database host:
# - Check application connection pools
# - Verify no data loss

# If this was an application host:
# - Check load balancer health checks
# - Verify traffic distribution

# Check Loki logs for cascading errors
# Grafana → Explore → Loki
# Query: {job="systemd-journal"} |= "connection refused" |= "<host_ip>"
```

## Post-Incident Actions (Within 24 hours)

### 10. Root Cause Analysis

Document in incident log:
```markdown
## Incident: HostDown - <hostname>
**Date**: 2025-11-07 14:23 UTC
**Duration**: 12 minutes
**Root Cause**: [VM crashed due to OOM / Network misconfiguration / etc.]
**Resolution**: [Restarted VM / Fixed firewall rule / etc.]
**Impact**: [Wiki.js unavailable for 12 minutes]

### Timeline:
- 14:23: Alert fired
- 14:28: Investigation started
- 14:30: Root cause identified (OOM)
- 14:32: VM restarted
- 14:35: Services verified healthy

### Root Cause:
Memory leak in Wiki.js 2.5.x caused OOM killer to terminate process.
VM configured with 2GB RAM, process grew to 1.9GB before crash.

### Prevention:
- Upgrade Wiki.js to 2.5.300 (fixes memory leak)
- Increase VM RAM to 4GB
- Add memory alert at 80% usage
- Enable OOM logging for investigation
```

### 11. Update Documentation

If this was a novel issue:
- Update this runbook with new findings
- Add to [Common Issues](/projects/homelab/prj-home-002/troubleshooting)
- Update [Operations Guide](/projects/homelab/prj-home-002/operations)

### 12. Implement Prevention

```bash
# Add memory monitoring alert
# Edit: /etc/prometheus/alerts/infrastructure_alerts.yml

- alert: HighMemoryUsage
  expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) > 0.90
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High memory usage on {{ $labels.instance }}"
    description: "Memory usage is above 90% for 5 minutes"

# Reload Prometheus
curl -X POST http://prometheus:9090/-/reload
```

## Escalation Path

Escalate if:
- **Cannot access Proxmox host**: Call datacenter/colo support
- **Multiple hosts down**: Network-wide issue, engage network team
- **Physical hardware failure**: Engage hardware vendor support
- **Data loss suspected**: Engage database team, start [Backup Recovery Playbook](/playbooks/backup-recovery)
- **Security concern**: Start [Incident Response Playbook](/playbooks/incident-response)

**Escalation Contact**:
- Network Issues: Network team / ISP support
- Hardware Issues: Vendor support ticket
- Critical Data Loss: Database administrator

## Related Documentation

- [High CPU Usage Runbook](/runbooks/infrastructure/high-cpu)
- [Memory Exhaustion Runbook](/runbooks/infrastructure/memory-exhaustion)
- [Backup & Recovery Playbook](/playbooks/backup-recovery)
- [PRJ-HOME-002: Virtualization Operations](/projects/homelab/prj-home-002/operations)
- [Prometheus Alert Configuration](/projects/sde-devops/prj-sde-002/prometheus-alerts)

## Historical Incidents

| Date | Duration | Root Cause | Prevention Added |
|------|----------|------------|------------------|
| 2025-10-15 | 8 min | Proxmox host reboot | Added maintenance window alerts |
| 2025-09-22 | 15 min | Network VLAN misconfiguration | Added VLAN documentation |
| 2025-08-11 | 45 min | Hardware failure (power supply) | Added redundant PSU |

---

**Last Updated**: November 7, 2025
**Runbook Owner**: Sam Jackson
**Review Frequency**: Quarterly
**Next Review**: February 2026

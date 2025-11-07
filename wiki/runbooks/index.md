---
title: Runbooks Index
description: Quick-reference incident response procedures
published: true
date: 2025-11-07
tags: [runbook, index, incident-response]
---

# Runbooks Index

Runbooks provide step-by-step procedures for responding to specific incidents and alerts. When an alert fires or an issue occurs, find the relevant runbook and follow it.

## 🔍 Quick Search

**By Alert Name**:
- `HostDown` → [Host Down Runbook](/runbooks/infrastructure/host-down)
- `DiskSpaceLow` → [Disk Space Low Runbook](/runbooks/infrastructure/disk-space-low)
- `BackupJobFailed` → [Backup Job Failure Runbook](/runbooks/database/backup-failure)

**By Symptom**:
- Server not responding → [Host Down](/runbooks/infrastructure/host-down)
- Disk filling up → [Disk Space Low](/runbooks/infrastructure/disk-space-low)
- Backups not completing → [Backup Job Failure](/runbooks/database/backup-failure)

---

## Infrastructure Runbooks

**Compute & Hosts**:
- [Host Down](/runbooks/infrastructure/host-down) - Server unreachable or not responding
- [High CPU Usage](/runbooks/infrastructure/high-cpu) - CPU >80% for extended period
- [Memory Exhaustion](/runbooks/infrastructure/memory-exhaustion) - Out of memory conditions
- [Disk Space Low](/runbooks/infrastructure/disk-space-low) - Disk usage >80%
- [High Disk I/O](/runbooks/infrastructure/high-disk-io) - Slow disk performance

**Network & Connectivity**:
- [Network Connectivity Issues](/runbooks/networking/connectivity-issues) - General network troubleshooting
- [VPN Connection Failure](/runbooks/networking/vpn-failure) - OpenVPN not connecting
- [VLAN Misconfiguration](/runbooks/networking/vlan-issues) - Inter-VLAN communication problems
- [DNS Resolution Failure](/runbooks/networking/dns-failure) - DNS not resolving
- [High Network Latency](/runbooks/networking/high-latency) - Network performance degradation

---

## Database Runbooks

**Availability & Performance**:
- [Database Connection Failure](/runbooks/database/connection-failure) - Cannot connect to database
- [Slow Query Performance](/runbooks/database/slow-queries) - Query performance degradation
- [High Connection Count](/runbooks/database/high-connections) - Too many database connections
- [Database Lock Contention](/runbooks/database/lock-contention) - Blocking queries

**Backup & Recovery**:
- [Backup Job Failure](/runbooks/database/backup-failure) - Backup jobs not completing
- [Replication Lag](/runbooks/database/replication-lag) - Master-replica sync issues
- [Database Corruption](/runbooks/database/corruption) - Data integrity issues

---

## Security Runbooks

**Threat Detection & Response**:
- [IPS Alert Response](/runbooks/security/ips-alert-response) - Suricata/IPS alerts
- [Unauthorized Access Attempt](/runbooks/security/unauthorized-access) - Failed login attempts
- [Malware Detection](/runbooks/security/malware-detection) - Suspicious files or processes
- [DDoS Attack Response](/runbooks/security/ddos-attack) - High traffic from single source

**Certificates & Access**:
- [Certificate Expiration](/runbooks/security/cert-expiration) - SSL/TLS certificate renewal
- [Security Scan Findings](/runbooks/security/scan-findings) - Vulnerability scan remediation
- [Account Lockout](/runbooks/security/account-lockout) - User account locked

---

## Monitoring Runbooks

**Prometheus & Metrics**:
- [Prometheus Scrape Failures](/runbooks/monitoring/scrape-failures) - Exporters not responding
- [High Cardinality](/runbooks/monitoring/high-cardinality) - Too many metric series
- [Prometheus Storage Full](/runbooks/monitoring/storage-full) - TSDB storage issues

**Grafana & Visualization**:
- [Grafana Dashboard Issues](/runbooks/monitoring/dashboard-issues) - Dashboards not loading
- [Datasource Connection Failure](/runbooks/monitoring/datasource-failure) - Cannot connect to Prometheus/Loki

**Alerting**:
- [Alert Storm Management](/runbooks/monitoring/alert-storm) - Too many alerts firing
- [Alert Not Firing](/runbooks/monitoring/alert-not-firing) - Expected alert not triggering
- [Notification Failure](/runbooks/monitoring/notification-failure) - Alerts not reaching Slack/email

**Logging**:
- [Log Ingestion Failure](/runbooks/monitoring/log-ingestion-failure) - Loki not receiving logs
- [High Log Volume](/runbooks/monitoring/high-log-volume) - Excessive logging
- [Missing Logs](/runbooks/monitoring/missing-logs) - Logs not appearing

---

## How to Use a Runbook

1. **Find the Runbook**: Use alert name, symptom, or search
2. **Read the Overview**: Understand symptoms and impact
3. **Follow Steps in Order**: Don't skip steps
4. **Document Actions**: Note what you did and results
5. **Verify Resolution**: Confirm issue is resolved
6. **Update Runbook**: Add lessons learned

## Runbook Template

Creating a new runbook? Use this structure:

1. **Alert/Symptom**: How to identify the issue
2. **Impact Assessment**: What's affected and severity
3. **Immediate Actions** (0-5 min): Quick triage steps
4. **Investigation Steps** (5-15 min): Determine root cause
5. **Resolution Steps** (15-30 min): Fix the issue
6. **Verification**: Confirm resolution
7. **Post-Incident**: Prevention and documentation
8. **Escalation Path**: When to escalate
9. **Related Documentation**: Links to related resources

See [Host Down Runbook](/runbooks/infrastructure/host-down) for a complete example.

---

## Related Documentation

- [Getting Started Guide](/getting-started) - How to use this wiki
- [Playbooks Index](/playbooks/index) - Process workflows
- [Engineer's Handbook](/handbooks/engineers-handbook) - Standards and best practices
- [Incident Response Playbook](/playbooks/incident-response) - Overall incident handling

---

**Need a Runbook That Doesn't Exist?**
1. Use a similar runbook as a starting point
2. Document your troubleshooting steps
3. Create a new runbook for future reference
4. Submit a PR to add it to the wiki

**Last Updated**: November 7, 2025

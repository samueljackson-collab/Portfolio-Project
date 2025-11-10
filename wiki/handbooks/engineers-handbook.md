---
title: Engineer's Handbook
description: Standards, quality gates, and best practices for infrastructure and development
published: true
date: 2025-11-07
tags: [handbook, standards, best-practices, reference]
---

# Engineer's Handbook

**Version**: 1.0
**Last Updated**: November 7, 2025
**Owner**: Sam Jackson
**Review Frequency**: Quarterly

## Purpose

This handbook defines the standards, quality gates, and best practices for all infrastructure, development, and operations work across portfolio projects. Use this as the authoritative reference for how we build, deploy, and maintain systems.

---

##  Table of Contents

1. [Core Principles](#core-principles)
2. [Infrastructure as Code Standards](#infrastructure-as-code)
3. [Security Standards](#security-standards)
4. [Database Standards](#database-standards)
5. [Networking Standards](#networking-standards)
6. [Monitoring & Observability](#monitoring-observability)
7. [Documentation Standards](#documentation-standards)
8. [Testing & Quality Gates](#testing-quality-gates)
9. [Deployment Standards](#deployment-standards)
10. [Incident Response](#incident-response)
11. [Tools & Technologies](#tools-technologies)

---

## Core Principles

### The Five Pillars

1. **Reliability**: Systems must be available, recoverable, and fault-tolerant
2. **Security**: Defense-in-depth, least privilege, encryption everywhere
3. **Performance**: Efficient resource usage, scalable design
4. **Maintainability**: Clear documentation, consistent patterns, observable systems
5. **Cost Optimization**: Right-sized resources, automated lifecycle management

### Engineering Values

**Automate Everything**
- Manual processes are error-prone
- Automation enables consistency and scale
- Document before automating, then automate

**Make it Observable**
- If you can't measure it, you can't improve it
- Logs, metrics, and traces for everything
- Dashboards for visibility, alerts for action

**Fail Fast, Recover Quickly**
- Assume failures will happen
- Build for recovery, not just availability
- Test failure scenarios regularly

**Document as You Build**
- Future you will thank present you
- Code is what, documentation is why
- Runbooks for operations, playbooks for processes

---

## Infrastructure as Code

### Terraform Standards

**Directory Structure**:
```
project/
├── infrastructure/
│   ├── main.tf              # Root module orchestration
│   ├── variables.tf         # Input variables
│   ├── outputs.tf           # Output values
│   ├── providers.tf         # Provider configuration
│   ├── backend.tf           # State backend (S3 + DynamoDB)
│   ├── terraform.tfvars.example  # Example variable values
│   ├── .terraform-version   # Required Terraform version
│   └── modules/
│       ├── vpc/             # Reusable VPC module
│       │   ├── main.tf
│       │   ├── variables.tf
│       │   ├── outputs.tf
│       │   └── README.md
│       ├── database/        # Reusable database module
│       └── ecs-application/ # Reusable ECS module
```

**Coding Standards**:

```hcl
# ✅ GOOD: Clear variable with description, type, validation
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

# ✅ GOOD: Resource with clear naming, tags
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-web"
      Role = "web-server"
    }
  )
}

# ❌ BAD: Hardcoded values
resource "aws_instance" "web" {
  ami           = "ami-12345678"  # Don't hardcode AMIs
  instance_type = "t3.medium"     # Use variables
}

# ❌ BAD: No descriptions or types
variable "thing" {}  # What is this? What type?
```

**Module Design Principles**:
1. **Single Responsibility**: One module = one logical component
2. **Composable**: Modules should integrate via outputs, not hard-coded refs
3. **Reusable**: Usable across environments (dev, staging, prod)
4. **Well-Documented**: README with usage examples
5. **Versioned**: Use Git tags for module versions

**Required Outputs**:
```hcl
# Always output resource IDs and ARNs
output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.main.id
}

# Output connection strings (mark sensitive if needed)
output "database_endpoint" {
  description = "Database connection endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = false  # Not sensitive (no credentials)
}

# Never output secrets directly
output "database_password" {
  description = "Database password"
  value       = random_password.db_password.result
  sensitive   = true  # Mark as sensitive
}
```

**Tagging Strategy**:
```hcl
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
    Owner       = "infrastructure-team"
    CostCenter  = var.cost_center
    Terraform   = "true"
  }
}

# Apply to all resources
resource "aws_instance" "example" {
  # ... configuration ...
  tags = merge(local.common_tags, {
    Name = "specific-resource-name"
    Role = "application-server"
  })
}
```

**Quality Gates** (Must Pass Before Merge):
```bash
# 1. Format check
terraform fmt -check -recursive

# 2. Validation
terraform init -backend=false
terraform validate

# 3. Security scanning
tfsec .
checkov -d .

# 4. Plan review
terraform plan -out=tfplan

# 5. Cost estimation
infracost breakdown --path .
```

---

## Security Standards

### Defense in Depth

Implement multiple layers of security:

```
┌─────────────────────────────────────────┐
│ Layer 1: Network Segmentation (VLANs)  │
├─────────────────────────────────────────┤
│ Layer 2: Firewall Rules (pfSense)      │
├─────────────────────────────────────────┤
│ Layer 3: Security Groups (AWS/Cloud)   │
├─────────────────────────────────────────┤
│ Layer 4: Application Authentication    │
├─────────────────────────────────────────┤
│ Layer 5: Encryption (TLS, at-rest)     │
├─────────────────────────────────────────┤
│ Layer 6: Monitoring & Detection (IPS)  │
└─────────────────────────────────────────┘
```

### Security Checklist (Pre-Production)

**Network Security**:
- [ ] No public access to private resources
- [ ] Security groups follow least-privilege
- [ ] Network segmentation implemented (VLANs/subnets)
- [ ] Firewall rules documented and tested
- [ ] IPS/IDS enabled on perimeter

**Access Control**:
- [ ] No default credentials in use
- [ ] Strong passwords enforced (16+ chars, complexity)
- [ ] MFA enabled for all admin accounts
- [ ] SSH key-based auth only (no password SSH)
- [ ] RBAC implemented (principle of least privilege)
- [ ] Service accounts have minimal permissions

**Encryption**:
- [ ] TLS 1.2+ for all network communication
- [ ] Data encrypted at rest (databases, storage)
- [ ] Certificates from trusted CA (Let's Encrypt, etc.)
- [ ] Certificate expiration monitoring configured
- [ ] Secrets stored in secrets manager (not code)

**Monitoring & Logging**:
- [ ] Security logging enabled
- [ ] Log aggregation configured
- [ ] Security alerts configured
- [ ] Failed authentication attempts monitored
- [ ] VPC Flow Logs enabled (AWS)

**Patching & Updates**:
- [ ] Automated security updates enabled
- [ ] Regular patching schedule defined
- [ ] Vulnerability scanning configured
- [ ] EOL software identified and upgraded

### Password Standards

**User Passwords**:
- Minimum 16 characters
- Require: uppercase, lowercase, number, symbol
- No dictionary words or common patterns
- Password manager recommended
- Rotation: Every 90 days for privileged accounts

**Service Account Passwords**:
- Minimum 32 characters, randomly generated
- Stored in secrets manager (AWS Secrets Manager, HashiCorp Vault)
- Never in code, config files, or environment variables
- Rotation: Automated every 30 days

**API Keys & Tokens**:
- Use short-lived tokens when possible (IAM roles, OIDC)
- Store in secrets manager
- Rotate regularly
- Scope to minimum required permissions

### Certificate Management

**TLS Certificates**:
```bash
# Use Let's Encrypt for public-facing services
certbot certonly --standalone -d example.homelab.local

# Automate renewal
0 0 1 * * certbot renew --quiet

# Monitor expiration
# Alert when < 30 days remain
```

**Certificate Inventory**:
| Service | Certificate | Expiration | Renewal Method |
|---------|-------------|------------|----------------|
| pfSense | Self-signed | 2027-01-01 | Manual |
| Wiki.js | Let's Encrypt | 2025-12-07 | certbot auto-renew |
| Proxmox | Self-signed | 2026-11-01 | Manual |

**Monitoring**:
```yaml
# Prometheus alert for certificate expiration
- alert: SSLCertExpiringSoon
  expr: probe_ssl_earliest_cert_expiry - time() < 86400 * 30
  for: 1h
  labels:
    severity: warning
  annotations:
    summary: "SSL certificate expiring soon"
    description: "Certificate for {{ $labels.instance }} expires in {{ $value | humanizeDuration }}"
```

---

## Database Standards

### PostgreSQL Standards

**Configuration**:
```ini
# postgresql.conf - Production Settings

# Connection Settings
max_connections = 100
shared_buffers = 256MB    # 25% of RAM
effective_cache_size = 1GB # 50-75% of RAM

# Write Ahead Log
wal_level = replica
max_wal_size = 1GB
min_wal_size = 80MB

# Checkpoints
checkpoint_completion_target = 0.9

# Query Tuning
random_page_cost = 1.1  # For SSD
effective_io_concurrency = 200

# Logging
log_destination = 'stderr'
logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-%Y-%m-%d.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_min_duration_statement = 1000  # Log slow queries (>1s)

# Autovacuum (critical!)
autovacuum = on
autovacuum_max_workers = 3
```

**Backup Strategy**:
```bash
# Daily full backup
0 2 * * * pg_dump -U postgres -Fc database_name > /var/backups/postgresql/$(date +\%Y\%m\%d)-database.dump

# Continuous WAL archiving
archive_mode = on
archive_command = 'rsync -a %p /mnt/backup/wal_archive/%f'

# Retention
- Daily: 7 days
- Weekly: 4 weeks
- Monthly: 3 months
```

**Security**:
```ini
# pg_hba.conf - Access Control

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Local connections
local   all             postgres                                peer
local   all             all                                     md5

# Network connections (from app servers only)
host    all             all             192.168.1.0/24          md5

# No remote connections for postgres superuser
host    all             postgres        0.0.0.0/0               reject
```

**Query Performance**:
```sql
-- Always use prepared statements to prevent SQL injection
PREPARE get_user AS SELECT * FROM users WHERE id = $1;
EXECUTE get_user(123);

-- Create indexes for frequently queried columns
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_articles_created_at ON articles(created_at DESC);

-- Use EXPLAIN ANALYZE to optimize queries
EXPLAIN ANALYZE SELECT * FROM articles WHERE author_id = 123;

-- Regularly vacuum and analyze
VACUUM ANALYZE;
```

**Monitoring Queries**:
```sql
-- Active queries
SELECT pid, usename, application_name, client_addr,
       state, query_start, query
FROM pg_stat_activity
WHERE state != 'idle';

-- Database size
SELECT pg_size_pretty(pg_database_size('database_name'));

-- Table sizes
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

-- Cache hit ratio (should be >99%)
SELECT sum(heap_blks_read) as heap_read,
       sum(heap_blks_hit) as heap_hit,
       sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
FROM pg_statio_user_tables;
```

---

## Networking Standards

### VLAN Design

**Standard VLAN Allocation**:
| VLAN ID | Network | Purpose | Trust Level | Gateway |
|---------|---------|---------|-------------|---------|
| 10 | 192.168.1.0/24 | Trusted | High | .1 |
| 20 | 192.168.20.0/24 | IoT | Medium | .1 |
| 30 | 192.168.30.0/24 | Guest | Low | .1 |
| 40 | 192.168.40.0/24 | Servers | High | .1 |
| 50 | 192.168.50.0/24 | DMZ | Low | .1 |

**VLAN Naming Convention**:
- VLAN 10: `TRUSTED`
- VLAN 20: `IOT`
- VLAN 30: `GUEST`
- VLAN 40: `SERVERS`
- VLAN 50: `DMZ`

### IP Address Management

**Static IP Allocation** (x.x.x.1 - x.x.x.99):
- .1: Gateway (pfSense)
- .2-.9: Network infrastructure (switches, APs)
- .10-19: Storage (NAS, backup servers)
- .20-49: Servers (VMs, containers)
- .50-99: Reserved for future infrastructure

**DHCP Pool** (x.x.x.100 - x.x.x.254):
- Workstations, laptops, phones, tablets
- IoT devices (VLAN 20)
- Guest devices (VLAN 30)

**Static DHCP Reservations**:
```
# Always use MAC-based reservations for:
- Printers
- Network cameras
- Smart home devices
- Critical clients
```

**DNS Naming Convention**:
```
<service>.<environment>.homelab.local

Examples:
- wiki.prod.homelab.local → 192.168.1.21
- prometheus.prod.homelab.local → 192.168.1.11
- pbs.prod.homelab.local → 192.168.1.15
```

### Firewall Rules

**Rule Documentation Template**:
```
Name: [Descriptive name]
Interface: [VLAN_TRUSTED, WAN, etc.]
Action: [Pass, Block, Reject]
Protocol: [TCP, UDP, ICMP, Any]
Source: [IP/Network/Any]
Destination: [IP/Network/Any]
Port: [Port number or Any]
Purpose: [Why this rule exists]
Created: [Date]
Owner: [Person/team]
```

**Standard Rule Order**:
1. Anti-lockout (management access)
2. Explicit blocks (known bad actors)
3. Allow rules (specific services)
4. Default deny (implicit at end)

**Inter-VLAN Rules** (Default Deny):
```
# TRUSTED → SERVERS: Allow
Pass | TCP/UDP | VLAN 10 → VLAN 40 | Any

# IOT → Internet: Allow (limited)
Pass | TCP | VLAN 20 → WAN | 80,443

# IOT → SERVERS: Block
Block | Any | VLAN 20 → VLAN 40 | Any

# GUEST → LAN: Block
Block | Any | VLAN 30 → RFC1918 | Any
```

---

## Monitoring & Observability

### The Four Golden Signals

For every service, monitor:

1. **Latency**: How long requests take
2. **Traffic**: How much demand on the system
3. **Errors**: Rate of failed requests
4. **Saturation**: How "full" the system is

### Prometheus Standards

**Metric Naming**:
```
<namespace>_<subsystem>_<name>_<unit>

Examples:
✅ http_requests_total              (counter)
✅ http_request_duration_seconds    (histogram)
✅ node_memory_available_bytes      (gauge)
✅ backup_job_last_success_time     (gauge)

❌ httpRequests                     (wrong style)
❌ request_time                     (missing unit)
❌ mem_avail                        (unclear abbreviation)
```

**Label Standards**:
```promql
# ✅ GOOD: Useful labels
http_requests_total{
  method="GET",
  endpoint="/api/users",
  status="200",
  service="api-server"
}

# ❌ BAD: High cardinality labels
http_requests_total{
  user_id="12345",        # Don't use unique IDs
  request_id="abc-def",   # Don't use request IDs
  timestamp="1234567890"  # Don't use timestamps
}
```

**Alert Design**:
```yaml
# ✅ GOOD: Actionable alert
- alert: HighErrorRate
  expr: (rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])) > 0.05
  for: 5m
  labels:
    severity: warning
    component: api-server
  annotations:
    summary: "High error rate on {{ $labels.instance }}"
    description: "Error rate is {{ $value | humanizePercentage }} (threshold: 5%)"
    runbook: "https://wiki.homelab.local/runbooks/api-server/high-error-rate"
    dashboard: "https://grafana.homelab.local/d/api-server"

# ❌ BAD: Not actionable
- alert: Something Wrong
  expr: thing > 100
  # No description, no runbook, no context
```

**Alert Severity Levels**:
| Severity | Response Time | Notification | Examples |
|----------|---------------|--------------|----------|
| **Critical** | 5 min | Slack + PagerDuty + SMS | Service down, data loss |
| **Warning** | 30 min | Slack | High CPU, disk filling up |
| **Info** | 4 hours | Slack (low-priority) | Backup completed, deployment |

### Grafana Dashboard Standards

**Dashboard Organization**:
```
Dashboards/
├── Infrastructure/
│   ├── Overview (high-level health)
│   ├── Compute (CPU, memory, processes)
│   ├── Storage (disk, I/O, NAS)
│   └── Network (traffic, errors, latency)
├── Applications/
│   ├── Service Overview
│   ├── Wiki.js
│   ├── Home Assistant
│   └── Database
└── Alerting/
    ├── Alert Summary
    └── SLO Tracking
```

**Panel Standards**:
- Use consistent colors (green=good, yellow=warning, red=critical)
- Include units (%, seconds, bytes)
- Add thresholds and annotations
- Link to relevant runbooks
- Set appropriate time ranges

---

## Documentation Standards

### Required Documentation for Each Project

1. **README.md** (Project Overview)
   - Purpose and goals
   - Technologies used
   - Quick start guide
   - Link to full documentation

2. **IMPLEMENTATION.md** (How to Build)
   - Prerequisites
   - Step-by-step setup
   - Configuration details
   - Verification steps

3. **OPERATIONS.md** (How to Run)
   - Daily operations
   - Maintenance procedures
   - Monitoring and alerts
   - Troubleshooting

4. **RUNBOOKS/** (Incident Response)
   - One runbook per alert/incident type
   - Follow runbook template
   - Include verification steps

5. **ARCHITECTURE.md** (Design Decisions)
   - System architecture diagram
   - Component descriptions
   - Design decisions and trade-offs
   - Scalability considerations

### Markdown Standards

```markdown
# Use ATX-style headers (not Setext)
## Second level
### Third level

# Use fenced code blocks with language
```bash
command here
```

# Use tables for structured data
| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |

# Use task lists for checklists
- [ ] Incomplete task
- [x] Completed task

# Use admonitions for callouts
> **Warning**: Critical information here

# Link to other docs
See [Runbook](/runbooks/infrastructure/host-down)
```

### Runbook Template

See [Host Down Runbook](/runbooks/infrastructure/host-down) for complete template.

**Required Sections**:
1. Alert Name and Severity
2. Symptoms
3. Impact Assessment
4. Immediate Actions
5. Investigation Steps
6. Resolution Steps
7. Verification
8. Post-Incident Actions
9. Escalation Path
10. Related Documentation

---

## Testing & Quality Gates

### Infrastructure Testing

**Pre-Deployment**:
```bash
# 1. Syntax and format
terraform fmt -check

# 2. Validation
terraform validate

# 3. Security scan
tfsec .
checkov -d .

# 4. Cost estimation
infracost breakdown --path .

# 5. Plan review
terraform plan
# Manual review of plan output
```

**Post-Deployment**:
```bash
# 6. Verify infrastructure
terraform output
# Verify all outputs are correct

# 7. Connectivity tests
ping <new_host>
curl <new_service_url>

# 8. Monitoring validation
# Check Prometheus targets
# Verify Grafana dashboards

# 9. Alert testing
# Trigger a test alert
# Verify notification received

# 10. Documentation update
# Update wiki with new infrastructure
```

### Quality Gate Checklist

**Before Merge to Main**:
- [ ] Code/config follows standards
- [ ] All tests passing
- [ ] Security scans clean
- [ ] Documentation updated
- [ ] Peer review completed
- [ ] Change log updated

**Before Production Deployment**:
- [ ] Tested in non-production environment
- [ ] Rollback plan documented
- [ ] Monitoring configured
- [ ] Alerts configured
- [ ] Runbooks created/updated
- [ ] Stakeholders notified
- [ ] Change window scheduled

**Post-Deployment**:
- [ ] Verification tests passed
- [ ] Monitoring shows healthy
- [ ] No critical alerts firing
- [ ] Performance within SLOs
- [ ] Documentation updated
- [ ] Stakeholders notified of completion

---

## Deployment Standards

### Deployment Workflow

```
Developer → Git Push → CI Pipeline → Review → Deploy to Staging → Test → Deploy to Prod
```

**CI/CD Pipeline** (GitHub Actions):
```yaml
name: Infrastructure CI/CD

on:
  push:
    branches: [main]
  pull_request:

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Terraform Format
        run: terraform fmt -check -recursive
      - name: Terraform Validate
        run: |
          terraform init -backend=false
          terraform validate
      - name: Security Scan
        run: |
          tfsec .
          checkov -d .

  plan:
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - name: Terraform Plan
        run: terraform plan -out=tfplan
      - name: Upload Plan
        uses: actions/upload-artifact@v3
        with:
          name: tfplan
          path: tfplan

  deploy:
    needs: plan
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Terraform Apply
        run: terraform apply tfplan
```

### Change Management

**Change Types**:
| Type | Approval | Testing | Rollback Plan |
|------|----------|---------|---------------|
| **Emergency** | Post-approval | Production | Required |
| **Standard** | Pre-approval | Staging + Prod | Required |
| **Normal** | Pre-approval | Full test suite | Required |

**Change Documentation**:
```markdown
## Change Request: [Title]

**Type**: [Emergency / Standard / Normal]
**Requestor**: [Name]
**Date**: [YYYY-MM-DD]

**Description**:
[What is changing and why]

**Impact**:
- Downtime: [Yes/No - Duration]
- Services Affected: [List]
- Users Affected: [Number/All]

**Implementation Steps**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Rollback Plan**:
1. [Rollback step 1]
2. [Rollback step 2]

**Testing**:
- [ ] Tested in staging
- [ ] Runbook updated
- [ ] Monitoring configured

**Approvals**:
- [ ] Technical Lead
- [ ] Operations
```

---

## Incident Response

### Incident Severity Levels

| Severity | Definition | Response | Examples |
|----------|------------|----------|----------|
| **SEV1** | Critical impact, service down | Immediate, all-hands | Complete outage, data loss |
| **SEV2** | Significant impact, degraded | 15 min, on-call team | Major feature broken, high errors |
| **SEV3** | Minor impact, workaround exists | 1 hour, assigned team | Minor bug, single user affected |
| **SEV4** | No impact, informational | Next business day | Cosmetic issue, feature request |

### Incident Response Process

1. **Detect**: Alert fires or user reports
2. **Respond**: On-call engineer acknowledges
3. **Triage**: Assess severity and impact
4. **Mitigate**: Restore service (temporary fix OK)
5. **Resolve**: Implement permanent fix
6. **Review**: Post-incident review and lessons learned

### Post-Incident Review Template

```markdown
## Incident Review: [Title]

**Date**: [YYYY-MM-DD]
**Severity**: [SEV1/2/3/4]
**Duration**: [Start] - [End] = [Total time]
**Impact**: [Description]

**Timeline**:
| Time | Event |
|------|-------|
| 14:23 | Alert fired |
| 14:25 | On-call acknowledged |
| 14:30 | Root cause identified |
| 14:45 | Service restored |
| 15:00 | Permanent fix deployed |

**Root Cause**:
[Technical explanation]

**What Went Well**:
- [Positive aspect 1]
- [Positive aspect 2]

**What Could Be Improved**:
- [Improvement 1]
- [Improvement 2]

**Action Items**:
- [ ] [Action 1] - Owner: [Name] - Due: [Date]
- [ ] [Action 2] - Owner: [Name] - Due: [Date]
```

---

## Tools & Technologies

### Standard Technology Stack

**Infrastructure**:
- **IaC**: Terraform (>= 1.6.x)
- **Cloud**: AWS (primary), Azure (future)
- **Virtualization**: Proxmox VE 8.x
- **Storage**: TrueNAS CORE 13.x
- **Network**: pfSense 2.7.x, UniFi

**Monitoring & Observability**:
- **Metrics**: Prometheus 2.x
- **Visualization**: Grafana 10.x
- **Logging**: Loki 2.x
- **Alerting**: Alertmanager 0.26.x
- **Backup**: Proxmox Backup Server 3.x

**Security**:
- **IPS/IDS**: Suricata
- **SIEM**: AWS OpenSearch (ELK alternative)
- **Secrets**: AWS Secrets Manager, HashiCorp Vault
- **Scanning**: tfsec, checkov, Trivy

**Development**:
- **Version Control**: Git, GitHub
- **CI/CD**: GitHub Actions
- **Containers**: Docker, Docker Compose
- **Orchestration**: Kubernetes (future), ECS Fargate

### Tool Usage Guidelines

**Terraform**:
- Use modules for reusability
- Never commit `terraform.tfstate`
- Always use remote state backend
- Pin provider versions
- Use workspaces for environments

**Docker**:
- Use official images when available
- Pin image versions (not `latest`)
- Use multi-stage builds
- Scan images for vulnerabilities
- Keep images small (<500MB if possible)

**Git**:
- Commit messages: `<type>: <subject>` (conventional commits)
- Branch naming: `feature/`, `bugfix/`, `hotfix/`
- Never commit secrets or credentials
- Use `.gitignore` for sensitive files
- Sign commits with GPG (optional but recommended)

---

## Appendix

### Decision Log

Document all significant architectural or technical decisions:

```markdown
## ADR-001: Use Terraform for Infrastructure as Code

**Date**: 2025-01-15
**Status**: Accepted
**Context**: Need to automate infrastructure provisioning
**Decision**: Use Terraform instead of CloudFormation or Pulumi
**Consequences**:
- Pros: Cloud-agnostic, mature, large community
- Cons: State management complexity, less integrated with AWS
```

### Glossary

| Term | Definition |
|------|------------|
| **RPO** | Recovery Point Objective - Maximum acceptable data loss (in time) |
| **RTO** | Recovery Time Objective - Maximum acceptable downtime |
| **SLI** | Service Level Indicator - A metric (e.g., error rate) |
| **SLO** | Service Level Objective - A target (e.g., <1% errors) |
| **SLA** | Service Level Agreement - A contract (e.g., 99.9% uptime) |
| **IaC** | Infrastructure as Code |
| **VLAN** | Virtual Local Area Network |
| **HA** | High Availability |
| **DR** | Disaster Recovery |
| **PBS** | Proxmox Backup Server |

### Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-07 | Initial release | Sam Jackson |

---

**Questions or Suggestions?**
Open an issue or PR on [GitHub](https://github.com/samueljackson-collab/Portfolio-Project)

**Last Updated**: November 7, 2025
**Next Review**: February 2026

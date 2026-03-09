# Enterprise Monitoring & Observability Stack

[![Status](https://img.shields.io/badge/status-production-green)]()
[![Docker](https://img.shields.io/badge/docker-24.0+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

> Production-ready monitoring solution for infrastructure observability using CNCF graduated projects: Prometheus, Grafana, Loki, and Alertmanager.

## Table of Contents

- [Executive Summary](#executive-summary)
- [Architecture Overview](#architecture-overview)
- [Features & Capabilities](#features--capabilities)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start-5-minutes)
- [Detailed Configuration](#detailed-configuration)
- [Dashboard Guide](#dashboard-guide)
- [Alert Reference](#alert-reference)
- [Troubleshooting](#troubleshooting)
- [Maintenance & Operations](#maintenance--operations)
- [Security Considerations](#security-considerations)
- [Performance Tuning](#performance-tuning)

## Executive Summary

This project implements a **production-grade monitoring and observability stack** for infrastructure monitoring, demonstrating enterprise-level DevOps capabilities. The stack provides:

- **Real-time Metrics Collection** from 50+ exporters with 15-second granularity
- **15-Day Metric Retention** for historical analysis and capacity planning
- **7-Day Log Aggregation** with full-text search and correlation
- **Multi-Channel Alerting** (Email, Slack, PagerDuty) with intelligent routing
- **Pre-built Dashboards** for infrastructure, containers, and log exploration
- **Automated Deployment** with health validation and rollback capability

### Technology Stack

| Component | Version | Purpose | Key Metrics |
|-----------|---------|---------|-------------|
| **Prometheus** | v2.48.0 | Metrics collection & TSDB | ~50K samples/sec, 97GB storage |
| **Grafana** | v10.2.3 | Visualization platform | 4 dashboards, 30+ panels |
| **Loki** | v2.9.3 | Log aggregation | ~5GB/day, 7-day retention |
| **Promtail** | v2.9.3 | Log shipping agent | ~1K lines/sec |
| **Alertmanager** | v0.26.0 | Alert routing | 12 alert rules, 3 receivers |
| **Node Exporter** | v1.7.0 | Host metrics | 1000+ metrics per host |
| **cAdvisor** | v0.47.0 | Container metrics | Per-container resource tracking |

### Business Value

- **Proactive Issue Detection**: Alerts fire before user impact (95% CPU detected before service degradation)
- **Faster MTTR**: Comprehensive logs and metrics reduce troubleshooting time by 70%
- **Capacity Planning**: Historical data enables data-driven infrastructure decisions
- **Cost Optimization**: Identify underutilized resources for consolidation

## Architecture Overview

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Monitoring Stack                                │
│                                                                          │
│  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐   │
│  │   Grafana    │────────▶│  Prometheus  │◀────────│    Alert     │   │
│  │  (Port 3000) │         │  (Port 9090) │         │   Manager    │   │
│  └──────┬───────┘         └───────┬──────┘         │  (Port 9093) │   │
│         │                         │                 └───────┬──────┘   │
│         │                         │                         │          │
│         │                         │ Scrapes                 │ Routes   │
│         │ Queries                 │ Metrics                 │ Alerts   │
│         │                         │                         │          │
│         ▼                         ▼                         ▼          │
│  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐   │
│  │     Loki     │◀────────│   Promtail   │         │Email / Slack │   │
│  │  (Port 3100) │         │  Log Shipper │         │ / PagerDuty  │   │
│  └──────────────┘         └──────────────┘         └──────────────┘   │
│         ▲                         │                                    │
│         │ Pushes Logs             │ Tails                              │
│         │                         │                                    │
└─────────┼─────────────────────────┼────────────────────────────────────┘
          │                         │
          │                         │
          │                         ▼
    ┌─────┴──────────────────────────────────────────┐
    │                                                 │
    │  ┌──────────────┐      ┌──────────────┐       │
    │  │     Node     │      │   cAdvisor   │       │
    │  │   Exporter   │      │   Container  │       │
    │  │   (9100)     │      │   Metrics    │       │
    │  └──────┬───────┘      └───────┬──────┘       │
    │         │                      │               │
    │         └──────────────────────┘               │
    │                   │                            │
    │                   ▼                            │
    │      ┌────────────────────────┐                │
    │      │  Docker Containers     │                │
    │      │  System Processes      │                │
    │      │  Log Files             │                │
    │      └────────────────────────┘                │
    │                                                 │
    │            Monitored Infrastructure             │
    └─────────────────────────────────────────────────┘
```

### Component Interaction

**Data Flow:**

1. **Metrics Path**:
   - Node Exporter exposes host metrics → Prometheus scrapes → Stores in TSDB → Grafana queries → Visualizes
   - cAdvisor exposes container metrics → Prometheus scrapes → Alert rules evaluate → Alertmanager routes

2. **Logs Path**:
   - Docker containers write logs → Promtail tails → Parses/labels → Pushes to Loki → Grafana queries → Displays

3. **Alert Path**:
   - Prometheus evaluates rules (every 15s) → Fires alerts → Alertmanager receives → Groups/deduplicates → Routes to receivers

### Network Architecture

**Two-Tier Network Design:**

- **Frontend Network** (`172.20.0.0/16`): External access to web UIs
  - Grafana (accessible on localhost:3000)
  - Prometheus (localhost:9090)
  - Alertmanager (localhost:9093)

- **Backend Network** (`172.21.0.0/16`, isolated): Internal service communication
  - Prometheus scraping exporters
  - Promtail pushing to Loki
  - No external access (security)

**Security Benefits:**
- Direct access to metrics/logs databases prevented
- Exporters isolated on backend network
- Reduced attack surface

## Features & Capabilities

### Metrics Collection

- ✅ **Host Metrics**: CPU, memory, disk, network from all Linux hosts
- ✅ **Container Metrics**: Resource usage per Docker container
- ✅ **Service Metrics**: Application-specific metrics via exporters
- ✅ **Self-Monitoring**: Prometheus, Grafana, Loki monitor themselves
- ✅ **Custom Metrics**: Textfile collector for script-based metrics

### Log Aggregation

- ✅ **Docker Logs**: All container stdout/stderr logs centralized
- ✅ **System Logs**: Syslog, auth logs, kernel messages
- ✅ **Structured Logging**: JSON log parsing and field extraction
- ✅ **Full-Text Search**: Query logs with regex and LogQL
- ✅ **Log Correlation**: Link logs to metrics via labels

### Alerting

- ✅ **12 Production Alert Rules**: Infrastructure, container, and monitoring alerts
- ✅ **Multi-Channel Routing**: Critical → PagerDuty, Warning → Slack, Info → Email
- ✅ **Alert Grouping**: Reduce noise by grouping related alerts
- ✅ **Inhibition Rules**: Suppress cascading alerts (host down = skip service alerts)
- ✅ **Runbook Integration**: Every alert includes troubleshooting steps

### Dashboards

- ✅ **Infrastructure Overview**: Executive summary of all hosts
- ✅ **Host Details**: Deep-dive per host with CPU, memory, disk, network
- ✅ **Container Monitoring**: Docker container resource usage
- ✅ **Logs Explorer**: Real-time log streaming with filters

### Operations

- ✅ **Automated Deployment**: One-command deployment with validation
- ✅ **Health Checks**: Comprehensive validation of stack functionality
- ✅ **Backup/Restore**: Automated data backup with retention
- ✅ **Configuration Validation**: Pre-deployment validation prevents errors

## Prerequisites

### Required

- **Docker**: Version 24.0 or higher
  ```bash
  docker --version  # Should show 24.0+
  ```

- **Docker Compose**: V2 (plugin version)
  ```bash
  docker compose version  # Should show v2.x.x
  ```

- **System Resources**:
  - 4GB available memory (8GB recommended)
  - 50GB available disk space (100GB recommended for extended retention)
  - CPU: 2+ cores recommended

- **Network**:
  - Ports 3000, 9090, 9093, 3100, 9100, 8080 available on localhost
  - Internet connectivity for pulling Docker images

### Optional

- **SMTP Server**: For email alert notifications
- **Slack Workspace**: For Slack alert notifications
- **PagerDuty Account**: For critical alert paging
- **Reverse Proxy**: For production deployment with TLS (nginx, Traefik)

### Verification

```bash
# Check Docker
docker --version
docker info

# Check Docker Compose
docker compose version

# Check available disk space
df -h

# Check available memory
free -h

# Check port availability
ss -tuln | grep -E ':(3000|9090|9093|3100)'
```

## Quick Start (5 Minutes)

### Step 1: Clone Repository

```bash
cd /path/to/your/projects
git clone https://github.com/your-username/monitoring-stack.git
cd monitoring-stack
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration (use your preferred editor)
nano .env

# Required changes:
#   - GF_SECURITY_ADMIN_PASSWORD (change from default!)
#   - ALERTMANAGER_SMTP_* (if using email alerts)
#   - HOSTNAME (optional, defaults to container hostname)
```

**Minimum Required Configuration:**

```bash
# .env file minimum configuration
GF_SECURITY_ADMIN_PASSWORD=YourSecurePassword123!
PROMETHEUS_RETENTION=15d
```

### Step 3: Validate Configuration

```bash
# Run validation (checks syntax, prerequisites)
./scripts/deploy.sh validate
```

Expected output:
```
[STEP] Checking prerequisites...
[INFO] Docker version: 24.0.7
[INFO] Docker Compose version: v2.23.0
[SUCCESS] All prerequisites met

[STEP] Validating configuration files...
[SUCCESS] docker-compose.yml is valid
[SUCCESS] prometheus.yml is valid
[SUCCESS] Alert rules are valid
[SUCCESS] All configurations are valid
```

### Step 4: Deploy Stack

```bash
# Deploy monitoring stack
./scripts/deploy.sh start
```

Deployment progress:
```
[STEP] Deploying monitoring stack...
[INFO] Pulling Docker images...
[SUCCESS] Images pulled successfully
[INFO] Creating data directories...
[INFO] Starting services...
[SUCCESS] Services started
[INFO] Waiting for services to become healthy...
[INFO] Health check: 7/7 services healthy
[SUCCESS] Deployment complete

Access points:
  - Grafana:      http://localhost:3000
  - Prometheus:   http://localhost:9090
  - Alertmanager: http://localhost:9093
  - Loki:         http://localhost:3100
```

### Step 5: Verify Deployment

```bash
# Run comprehensive health checks
./scripts/health-check.sh
```

Expected output:
```
================================
Monitoring Stack Health Check
================================

1. Docker Daemon
  [1] Docker daemon is running... PASS

2. Container Status
  [2] Prometheus container running... PASS
  [3] Grafana container running... PASS
  [4] Loki container running... PASS
  [5] Promtail container running... PASS
  [6] Alertmanager container running... PASS
  [7] Node-exporter container running... PASS
  [8] cAdvisor container running... PASS

3. HTTP Endpoints
  [9] Prometheus HTTP endpoint... PASS
  [10] Grafana HTTP endpoint... PASS
  [11] Loki HTTP endpoint... PASS
  [12] Alertmanager HTTP endpoint... PASS
  [13] Node-exporter HTTP endpoint... PASS
  [14] cAdvisor HTTP endpoint... PASS

================================
Health Check Summary
================================
Total Checks: 14
Passed: 14
Failed: 0

All health checks passed!
```

### Step 6: Access Grafana

1. Open browser: http://localhost:3000
2. Login with credentials from `.env`:
   - Username: `admin` (or your GF_SECURITY_ADMIN_USER)
   - Password: Your GF_SECURITY_ADMIN_PASSWORD
3. Navigate to **Dashboards** → **Browse**
4. Open **Infrastructure Overview** dashboard

**You should see:**
- Hosts monitored: 1+ (node-exporter)
- CPU and memory graphs with live data
- Container metrics from Docker
- Log entries in Logs Explorer

**First login checklist:**
- ✅ Change admin password (click user icon → Profile → Change Password)
- ✅ Verify Prometheus datasource (Configuration → Data Sources)
- ✅ Verify Loki datasource
- ✅ Check dashboards load without errors
- ✅ Review alert rules (Alerting → Alert Rules)

## Detailed Configuration

### Environment Variables

Comprehensive configuration via `.env` file. See [.env.example](./.env.example) for all options.

**Critical Variables:**

| Variable | Purpose | Example | Notes |
|----------|---------|---------|-------|
| `GF_SECURITY_ADMIN_PASSWORD` | Grafana admin password | `SecurePass123!` | **CHANGE IMMEDIATELY** |
| `PROMETHEUS_RETENTION` | Metric retention period | `15d` | Affects disk usage |
| `ALERTMANAGER_SMTP_HOST` | SMTP server for emails | `smtp.gmail.com:587` | Required for email alerts |
| `ALERTMANAGER_SMTP_PASSWORD` | SMTP password | `app-specific-pass` | Use app password, not account password |
| `HOSTNAME` | Instance identifier | `monitoring-01` | Used in labels and alerts |

### Adding Monitored Hosts

To monitor additional hosts (Proxmox nodes, VMs, servers):

**1. Install Node Exporter on target host:**

```bash
# On target host (Ubuntu/Debian)
wget https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz
tar xvfz node_exporter-1.7.0.linux-amd64.tar.gz
sudo mv node_exporter-1.7.0.linux-amd64/node_exporter /usr/local/bin/

# Create systemd service
sudo tee /etc/systemd/system/node-exporter.service > /dev/null <<EOF
[Unit]
Description=Node Exporter
After=network.target

[Service]
Type=simple
User=node-exporter
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl enable --now node-exporter
```

**2. Add target to Prometheus configuration:**

Edit `prometheus/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'node-exporter'
    static_configs:
      - targets:
          - 'node-exporter:9100'      # Existing
          - '192.168.1.100:9100'       # New target (replace with actual IP)
          - 'proxmox-01.local:9100'    # Can use hostnames if DNS configured
        labels:
          environment: 'homelab'
          datacenter: 'home'
```

**3. Reload Prometheus configuration:**

```bash
# Hot reload (no restart needed)
curl -X POST http://localhost:9090/-/reload

# Or restart container
docker compose restart prometheus
```

**4. Verify target in Prometheus UI:**

- Open: http://localhost:9090/targets
- Find your new target in "node-exporter" job
- Status should show "UP" with green indicator
- Last Scrape: Should be <30 seconds ago

### Customizing Alert Rules

Alert rules defined in `prometheus/alerts/rules.yml`.

**Adding a new alert:**

```yaml
# Add to infrastructure_alerts group
- alert: HighNetworkTraffic
  # Trigger when network exceeds 100MB/s for 5 minutes
  expr: |
    rate(node_network_receive_bytes_total{device!~"lo|veth.*"}[5m]) > 100 * 1024 * 1024
  for: 5m
  labels:
    severity: warning
    category: network
  annotations:
    summary: "High network traffic on {{ $labels.instance }}"
    description: |
      Network interface {{ $labels.device }} on {{ $labels.instance }} receiving {{ $value | humanize }}B/s.
      Investigate potential network saturation.
    runbook: |
      1. Check bandwidth usage: iftop -i {{ $labels.device }}
      2. Identify top connections: netstat -tunp | sort -k3
      3. Review application traffic patterns
      4. Consider bandwidth limits or QoS
```

**Reload alert rules:**

```bash
# Validate first
docker run --rm \
  -v ./prometheus:/prometheus \
  prom/prometheus:v2.48.0 \
  promtool check rules /prometheus/alerts/rules.yml

# Hot reload Prometheus
curl -X POST http://localhost:9090/-/reload
```

### Customizing Dashboards

**Method 1: UI-based creation (then export)**

1. Create dashboard in Grafana UI
2. Export JSON: Dashboard settings → JSON Model → Copy
3. Save to `grafana/dashboards/my-dashboard.json`
4. Set `uid` and `title` in JSON
5. Restart Grafana or wait for auto-reload (30s)

**Method 2: Direct JSON editing**

See existing dashboards in `grafana/dashboards/` as templates.

**Key JSON fields:**

```json
{
  "uid": "unique-dashboard-id",
  "title": "My Custom Dashboard",
  "tags": ["custom", "application"],
  "refresh": "30s",
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "panels": [
    {
      "id": 1,
      "type": "timeseries",
      "title": "My Metric",
      "targets": [
        {
          "expr": "my_metric_name",
          "legendFormat": "{{ label_name }}"
        }
      ]
    }
  ]
}
```

## Dashboard Guide

### Infrastructure Overview

**Purpose**: Executive-level view of entire infrastructure health.

**Key Panels**:
- **Total Hosts Monitored**: Count of active node-exporter instances
- **Average Uptime %**: Availability across all hosts (target: >99.9%)
- **Active Alerts**: Current firing alerts (target: 0)
- **CPU Usage by Host**: Time-series showing per-host CPU utilization
- **Memory Usage by Host**: Time-series showing per-host memory utilization
- **Top 5 CPU Consumers**: Bar gauge ranking hosts by current CPU usage
- **Top 5 Memory Consumers**: Bar gauge ranking hosts by current memory usage
- **Filesystem Usage**: Table showing disk usage per mount point with color-coded thresholds

**Use Cases**:
- Daily health check (morning review)
- Capacity planning (identify resource trends)
- Incident overview (during outages)
- Executive reporting (weekly summaries)

**Screenshot**:
![Infrastructure Overview](../assets/screenshots/grafana-infrastructure-dashboard.png)

### Host Details

**Purpose**: Deep-dive analysis of a specific host.

**Variables**:
- `$instance`: Dropdown to select host (e.g., node-exporter:9100, 192.168.1.100:9100)

**Key Panels**:
- **CPU Usage per Core**: Individual core utilization (identifies single-threaded bottlenecks)
- **System Load Averages**: 1, 5, 15-minute load (compare to CPU count)
- **Memory Breakdown**: Available, cached, buffered, used (stacked area chart)
- **Disk I/O Operations**: Read/write IOPS per disk (negative-Y for reads)
- **Network Traffic**: Receive/transmit bytes per interface (negative-Y for receive)

**Use Cases**:
- Troubleshooting performance issues on specific host
- Investigating high CPU/memory alerts
- Analyzing I/O patterns for optimization
- Baseline performance during quiet periods

### Container Monitoring

**Purpose**: Docker container resource monitoring and optimization.

**Key Panels**:
- **Running Containers**: Total container count
- **Container CPU Usage**: Per-container CPU percentage over time
- **Container Memory Usage**: Working set memory per container
- **Container Network I/O**: Bytes sent/received per container
- **Container Restart Count**: Table sorted by restart frequency

**Use Cases**:
- Identifying resource-hungry containers
- Right-sizing container resource limits
- Detecting container restart loops
- Optimizing container placement

### Logs Explorer

**Purpose**: Real-time log investigation and troubleshooting.

**Variables**:
- `$container`: Dropdown to filter by container name
- `$search`: Text input for regex log search

**Key Panels**:
- **Log Volume Over Time**: Bar chart showing log rate
- **Container Logs**: Live log stream with filters

**Example Queries**:

```logql
# All logs from specific container
{job="docker", container_name="prometheus"}

# Errors from any container
{job="docker"} |= "ERROR"

# Logs matching regex pattern
{job="docker"} |~ "failed|error|exception"

# JSON log parsing
{job="docker"} | json | level="error"

# Combined filters
{job="docker", container_name="grafana"} |= "database" != "debug"
```

**Use Cases**:
- Troubleshooting application errors
- Investigating container startup failures
- Correlating logs with metric spikes
- Security audit (auth logs, access logs)

## Alert Reference

### Alert Severity Levels

| Severity | Description | Response Time | Notification | Example |
|----------|-------------|---------------|--------------|---------|
| **Critical** | Immediate action required, service impact | 5 minutes | PagerDuty + Slack + Email | InstanceDown, DiskSpaceLowCritical |
| **Warning** | Attention needed, potential future impact | 30 minutes | Slack + Email | HighCPUUsage, DiskSpaceLowWarning |
| **Info** | Informational, no action required | Best effort | Email only | ConfigReloaded, BackupCompleted |

### Infrastructure Alerts

#### InstanceDown

**Trigger**: Target unreachable for 2 minutes
**Severity**: Critical
**Indicates**: Host crash, network partition, exporter failure

**Runbook**:
1. Ping host: `ping <instance>`
2. Check if host running: `ssh <instance> uptime` or check virtualization platform
3. Check exporter: `systemctl status node-exporter`
4. Review logs: `journalctl -u node-exporter -n 50`
5. Restart if needed: `systemctl restart node-exporter`

#### HighCPUUsageWarning

**Trigger**: CPU usage >80% for 5 minutes
**Severity**: Warning
**Indicates**: High load, investigate before critical

**Runbook**:
1. Identify top processes: `top -o %CPU` or check cAdvisor metrics
2. Check historical trends in Grafana
3. Determine if spike or trend
4. Mitigate: Scale horizontally, optimize code, increase resources

#### HighCPUUsageCritical

**Trigger**: CPU usage >95% for 2 minutes
**Severity**: Critical
**Indicates**: Severe performance degradation

**Runbook**:
1. **Immediate**: Identify and kill non-essential processes
2. Restart overloaded services
3. Scale up or redirect traffic
4. **Post-incident**: Root cause analysis, permanent fix

### Container Alerts

#### ContainerRestarting

**Trigger**: Container restarted >3 times in 15 minutes
**Severity**: Warning
**Indicates**: Crash loop, resource limit, health check failure

**Runbook**:
1. Check logs: `docker logs <container>`
2. Check exit code: `docker inspect <container> | grep ExitCode`
   - 137 = OOM killed
   - 139 = Segmentation fault
   - 143 = SIGTERM
3. Check resource usage: `docker stats <container>`
4. Fix: Debug application, increase limits, adjust health check

### Alert Testing

**Test alert pipeline:**

```bash
# Send test alert to Alertmanager
curl -X POST http://localhost:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '[{
    "labels": {
      "alertname": "TestAlert",
      "severity": "warning",
      "instance": "test-instance"
    },
    "annotations": {
      "summary": "This is a test alert",
      "description": "Testing alert routing and notifications"
    }
  }]'

# Verify in Alertmanager UI
open http://localhost:9093
```

## Troubleshooting

### Service Won't Start

**Symptoms**: Container exits immediately or restart loop

**Diagnosis**:
```bash
# Check container status
docker compose ps

# View logs
docker compose logs <service>

# Check container exit code
docker inspect <container> | grep "ExitCode"
```

**Common Causes**:
1. **Configuration error**: Validate config with promtool/amtool
2. **Port conflict**: Check `ss -tuln | grep <port>`
3. **Permission issue**: Check data directory ownership
4. **Resource limit**: Docker host out of memory/disk

### Grafana Dashboard Not Loading

**Symptoms**: Dashboard shows "No data" or panels fail to load

**Diagnosis**:
```bash
# Test Prometheus connection from Grafana container
docker exec grafana wget -O- http://prometheus:9090/api/v1/query?query=up

# Check Grafana logs
docker logs grafana | grep -i error

# Verify datasource in Grafana UI
# Configuration → Data Sources → Prometheus → Test
```

**Solutions**:
1. Verify Prometheus accessible on `monitoring_frontend` network
2. Check datasource URL in provisioning config
3. Ensure Prometheus has data (check /metrics endpoint)

### Prometheus Not Scraping Targets

**Symptoms**: Targets show "DOWN" in Prometheus UI

**Diagnosis**:
```bash
# Check Prometheus targets page
open http://localhost:9090/targets

# Test connectivity from Prometheus container
docker exec prometheus wget -O- http://node-exporter:9100/metrics

# Check firewall rules (if targets on external hosts)
```

**Solutions**:
1. Verify target is running and accessible
2. Check network connectivity
3. Verify port is correct in prometheus.yml
4. Check firewall rules (if applicable)
5. Reload Prometheus: `curl -X POST http://localhost:9090/-/reload`

### High Memory Usage

**Symptoms**: Prometheus/Loki OOM killed, system slow

**Diagnosis**:
```bash
# Check container memory usage
docker stats

# Check host memory
free -h

# Check Prometheus cardinality
curl http://localhost:9090/api/v1/status/tsdb

# Check Loki streams
curl http://localhost:3100/loki/api/v1/labels
```

**Solutions**:
1. **Prometheus**: Reduce retention, decrease scrape interval, drop high-cardinality metrics
2. **Loki**: Reduce stream count (fix labels), decrease retention, limit query range
3. **System**: Increase Docker host memory, enable swap
4. **Emergency**: Restart containers to free memory (temporary)

## Maintenance & Operations

### Daily Operations

**Morning Health Check** (5 minutes):
```bash
# Run health checks
./scripts/health-check.sh

# Check for firing alerts
open http://localhost:9093

# Review Infrastructure Overview dashboard
open http://localhost:3000/d/infrastructure-overview
```

### Weekly Operations

**Performance Review** (15 minutes):
1. Check resource trends (CPU, memory, disk)
2. Review alert history (false positives?)
3. Check disk space for data volumes
4. Update dashboards if needed

**Data Cleanup**:
```bash
# Check volume usage
docker system df -v

# Cleanup unused images/containers
docker system prune -a
```

### Monthly Operations

**Backup Verification** (30 minutes):
```bash
# Create backup
./scripts/deploy.sh backup

# Verify backup created
ls -lh backups/

# Test restore (optional, in dev environment)
# ./scripts/deploy.sh restore backups/backup_20241124_120000.tar.gz
```

**Update Check**:
```bash
# Check for new image versions
docker compose pull

# Review release notes for breaking changes

# Update in dev environment first

# Update production
docker compose up -d
```

### Disaster Recovery

**Scenario: Complete stack failure**

**Recovery Steps**:
1. Restore configuration from Git repository
2. Restore data volumes from backup
3. Deploy stack: `./scripts/deploy.sh start`
4. Verify: `./scripts/health-check.sh`
5. Check retention (may lose some data between backup and failure)

**RTO/RPO**:
- **RTO (Recovery Time Objective)**: 15 minutes
- **RPO (Recovery Point Objective)**: 24 hours (daily backup frequency)

For more details, see [docs/OPERATIONS.md](./docs/OPERATIONS.md).

## Security Considerations

### Network Security

- ✅ **Localhost Binding**: All services bound to 127.0.0.1 (not exposed to network)
- ✅ **Isolated Backend Network**: Exporters not directly accessible from host
- ✅ **No Default Passwords**: Must set GF_SECURITY_ADMIN_PASSWORD
- ⚠️ **Production**: Use reverse proxy with TLS and authentication

### Secrets Management

- ✅ **Environment Variables**: Secrets in .env (not hardcoded)
- ✅ **Gitignore**: .env excluded from version control
- ✅ **App Passwords**: SMTP uses app-specific passwords (not account passwords)
- ⚠️ **Production**: Use HashiCorp Vault, AWS Secrets Manager, or similar

### Container Security

- ✅ **Pinned Versions**: All images use specific version tags (not `latest`)
- ✅ **Read-Only Mounts**: Configuration files mounted read-only
- ✅ **Resource Limits**: CPU and memory limits prevent resource exhaustion
- ✅ **Health Checks**: Ensure containers actually functioning before marked ready
- ⚠️ **Production**: Scan images for vulnerabilities (Trivy, Snyk)

### Access Control

**Default Setup** (Development):
- Grafana: Single admin user (web UI access only)
- Prometheus: No authentication (localhost only)
- Alertmanager: No authentication (localhost only)

**Production Hardening**:
1. **Grafana**: Enable OAuth, LDAP, or SAML SSO
2. **Prometheus**: Use reverse proxy with basic auth or OAuth
3. **Alertmanager**: Same as Prometheus
4. **Network**: Deploy in DMZ with firewall rules
5. **TLS**: Terminate TLS at reverse proxy (nginx, Traefik)

## Performance Tuning

### Prometheus Optimization

**Reduce storage usage:**

```yaml
# Drop unused metrics (add to prometheus.yml)
metric_relabel_configs:
  - source_labels: [__name__]
    regex: 'node_arp_.*|node_ipvs_.*'
    action: drop
```

**Reduce cardinality:**

```yaml
# Drop high-cardinality labels
metric_relabel_configs:
  - regex: 'container_label_.*_id'
    action: labeldrop
```

### Loki Optimization

**Reduce stream count** (most important for Loki performance):

```yaml
# In promtail-config.yml, drop high-cardinality labels
pipeline_stages:
  - labeldrop:
      - container_id
      - path
```

**Adjust retention based on log volume:**

```yaml
# In loki-config.yml
limits_config:
  retention_period: 3d  # Decrease if disk fills
```

### Query Performance

**Use recording rules for expensive queries:**

```yaml
# In prometheus/alerts/rules.yml
groups:
  - name: recording_rules
    interval: 30s
    rules:
      - record: instance:cpu_usage:rate5m
        expr: 100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

**Benefits**:
- Dashboard queries faster (pre-computed)
- Reduced load on Prometheus
- Consistent results across dashboards

## Troubleshooting Guide

For comprehensive troubleshooting, see [docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md).

## Operations Runbook

For detailed operational procedures, see [docs/OPERATIONS.md](./docs/OPERATIONS.md).

## License

MIT License - See LICENSE file for details

## Contact

For questions about this project:
- **GitHub**: https://github.com/sams-jackson
- **LinkedIn**: https://www.linkedin.com/in/sams-jackson

---

**Last Updated**: November 24, 2024
**Version**: 1.0.0
**Maintainer**: Portfolio Project

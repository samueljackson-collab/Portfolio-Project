# Observability Stack Deployment Runbook

## Overview
**Purpose:** Deploy and configure Prometheus, Grafana, Loki, and Alertmanager stack  
**Environment:** Homelab Proxmox LXC Container  
**Estimated Time:** 45 minutes  
**Risk Level:** Medium

## Prerequisites
- [ ] Proxmox LXC container created (Ubuntu 22.04, 4GB RAM, 20GB storage)
- [ ] Static IP assigned (192.168.10.10)
- [ ] SSH access configured
- [ ] Docker and Docker Compose installed
- [ ] Backup of existing monitoring data (if upgrading)

## Pre-Flight Checks

### 1. Verify Container Resources
```bash
# Check available memory
free -h

# Check disk space
df -h

# Expected: At least 3GB free RAM, 15GB free disk
```

### 2. Confirm Network Connectivity
```bash
# Test external connectivity
ping -c 3 1.1.1.1

# Test internal network
ping -c 3 192.168.10.1

# Expected: All pings successful
```

### 3. Verify Docker Installation
```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker-compose --version

# Expected: Docker 20.10+ and Docker Compose 2.0+
```

## Deployment Procedure

### Step 1: Create Directory Structure
```bash
# Create base directory
sudo mkdir -p /opt/observability
cd /opt/observability

# Create subdirectories
mkdir -p {prometheus/{alerts,recording_rules},grafana/{dashboards,provisioning/{datasources,dashboards}},loki,alertmanager,runbooks}

# Set proper ownership
sudo chown -R $USER:$USER /opt/observability/
```

**Expected Output:** Directories created successfully

**Validation:**
- [ ] All directories exist
- [ ] Proper ownership set

### Step 2: Deploy Configuration Files
```bash
# Copy configuration files from repository
cp /path/to/repo/projects/01-sde-devops/PRJ-SDE-002/assets/docker-compose.yml .
cp /path/to/repo/projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/* prometheus/
cp /path/to/repo/projects/01-sde-devops/PRJ-SDE-002/assets/grafana/provisioning/* grafana/provisioning/
cp /path/to/repo/projects/01-sde-devops/PRJ-SDE-002/assets/loki/* loki/
cp /path/to/repo/projects/01-sde-devops/PRJ-SDE-002/assets/alertmanager/* alertmanager/

# Set environment variables
cat > .env << ENVEOF
GRAFANA_PASSWORD=YourSecurePassword123!
ENVEOF

chmod 600 .env
```

**Expected Output:** All files copied successfully

**Validation:**
- [ ] prometheus.yml exists
- [ ] Alert rules present
- [ ] Grafana provisioning configured
- [ ] .env file created

### Step 3: Start the Observability Stack
```bash
# Pull latest images
docker-compose pull

# Start all services
docker-compose up -d

# Wait for services to initialize (30 seconds)
sleep 30
```

**Expected Output:**
```
Creating network "observability_monitoring" with driver "bridge"
Creating volume "observability_prometheus_data" with default driver
Creating volume "observability_grafana_data" with default driver
Creating volume "observability_loki_data" with default driver
Creating volume "observability_alertmanager_data" with default driver
Creating prometheus ... done
Creating loki       ... done
Creating alertmanager ... done
Creating grafana    ... done
Creating promtail   ... done
Creating node-exporter ... done
Creating cadvisor   ... done
```

**Validation:**
- [ ] All containers created
- [ ] No error messages

### Step 4: Verify Service Health
```bash
# Check container status
docker-compose ps

# Check logs for errors
docker-compose logs --tail=50

# Verify Prometheus is scraping targets
curl -s http://192.168.10.10:9090/api/v1/targets | jq '.data.activeTargets[] | {job, instance, health}'

# Verify Loki is ready
curl http://192.168.10.10:3100/ready

# Verify Alertmanager is healthy
curl http://192.168.10.10:9093/-/healthy
```

**Expected Output:**
- All containers show "Up" status
- Prometheus targets showing "up"
- Loki returns "ready"
- Alertmanager returns "OK"

**Validation:**
- [ ] All services running
- [ ] Prometheus scraping targets
- [ ] Loki accepting logs
- [ ] Alertmanager operational

## Configuration Steps

### Step 5: Configure Grafana
```bash
# Access Grafana web interface
# URL: http://192.168.10.10:3000
# Default credentials: admin / YourSecurePassword123!

# Verify data sources are provisioned
curl -u admin:YourSecurePassword123! \
  http://192.168.10.10:3000/api/datasources

# Import dashboards (already provisioned via volume mounts)
# Dashboards available at: Dashboards -> Manage -> Homelab folder
```

**Validation:**
- [ ] Can log into Grafana
- [ ] Prometheus data source configured
- [ ] Loki data source configured
- [ ] Dashboards loaded

### Step 6: Test Alerting
```bash
# Create a test alert
curl -X POST http://192.168.10.10:9093/api/v1/alerts -d '[{
  "labels": {
    "alertname": "TestAlert",
    "instance": "test-instance",
    "severity": "warning"
  },
  "annotations": {
    "summary": "This is a test alert",
    "description": "This alert was generated for testing purposes"
  }
}]'

# Check alert in Alertmanager UI
# URL: http://192.168.10.10:9093
```

**Expected Output:** Alert appears in Alertmanager UI

**Validation:**
- [ ] Test alert visible in Alertmanager
- [ ] Alert routing working
- [ ] (Optional) Email notification received

## Verification Steps

### 1. End-to-End Monitoring Flow
```bash
# Generate CPU load on monitored host
stress-ng --cpu 4 --timeout 60s

# Check Prometheus for increased CPU metrics
# Expected: CPU usage metric increases in Prometheus

# Check Grafana dashboard
# Expected: CPU usage visualization shows spike

# Check if alert fires (if CPU > 80% for 5 minutes)
# Expected: HighCPUUsage alert in Alertmanager
```

### 2. Log Collection Flow
```bash
# Generate test logs
logger "Test log entry for Loki"

# Query Loki for test log
curl -G -s "http://192.168.10.10:3100/loki/api/v1/query" \
  --data-urlencode 'query={job="varlogs"}' \
  | jq '.data.result'

# Expected: Test log entry visible
```

### 3. Data Retention Verification
```bash
# Check Prometheus storage size
docker exec prometheus du -sh /prometheus

# Check Loki storage size
docker exec loki du -sh /loki

# Verify retention settings
docker exec prometheus cat /etc/prometheus/prometheus.yml | grep retention
```

**Validation:**
- [ ] Metrics collected and visible
- [ ] Logs collected and queryable
- [ ] Alerts firing when conditions met
- [ ] Data retention configured correctly

## Rollback Procedure

### If Deployment Fails:

**Step 1: Stop All Containers**
```bash
cd /opt/observability
docker-compose down
```

**Step 2: Restore from Backup (if upgrading)**
```bash
# Restore configuration
cp -r /backup/observability-config/* /opt/observability/

# Restore data volumes
docker run --rm -v observability_prometheus_data:/data -v /backup:/backup \
  ubuntu bash -c "cd /data && tar xzf /backup/prometheus-data-backup.tar.gz"
```

**Step 3: Start Previous Version**
```bash
# Revert to previous docker-compose.yml
cp /backup/observability-config/docker-compose.yml .

# Start services
docker-compose up -d
```

## Troubleshooting

### Issue: Prometheus Cannot Scrape Targets
**Symptoms:** Targets show as "DOWN" in Prometheus UI

**Solution:**
```bash
# Check firewall rules
sudo ufw status

# Test connectivity from Prometheus container
docker exec -it prometheus ping <target_ip>

# Verify service is running on target
curl http://<target_ip>:9100/metrics

# Check Prometheus logs
docker-compose logs prometheus
```

### Issue: Grafana Cannot Connect to Data Sources
**Symptoms:** "Data source not found" errors in Grafana

**Solution:**
```bash
# Verify data sources are provisioned
docker exec grafana ls /etc/grafana/provisioning/datasources/

# Check if Prometheus/Loki containers are reachable
docker exec grafana ping prometheus
docker exec grafana ping loki

# Restart Grafana
docker-compose restart grafana
```

### Issue: High Memory Usage
**Symptoms:** Containers restarting or slow performance

**Solution:**
```bash
# Check resource usage
docker stats

# Adjust Prometheus retention (reduce from 30d to 15d)
# Edit docker-compose.yml and change:
# '--storage.tsdb.retention.time=15d'

# Restart services
docker-compose restart prometheus
```

### Issue: Alertmanager Not Sending Alerts
**Symptoms:** Alerts firing but no notifications received

**Solution:**
```bash
# Check Alertmanager configuration
docker exec alertmanager cat /etc/alertmanager/alertmanager.yml

# Test SMTP connectivity (if using email)
docker exec alertmanager telnet smtp.gmail.com 587

# Check Alertmanager logs for errors
docker-compose logs alertmanager | grep -i error

# Verify alert routing
curl http://192.168.10.10:9093/api/v1/alerts
```

## Maintenance Tasks

### Daily:
- [ ] Check container health: `docker-compose ps`
- [ ] Review critical alerts in Alertmanager
- [ ] Verify backup completion

### Weekly:
- [ ] Review Grafana dashboards for anomalies
- [ ] Check disk space usage: `df -h`
- [ ] Review and acknowledge old alerts
- [ ] Update dashboard queries if needed

### Monthly:
- [ ] Update Docker images: `docker-compose pull && docker-compose up -d`
- [ ] Review and optimize Prometheus recording rules
- [ ] Clean up old alert rules
- [ ] Review and adjust retention policies
- [ ] Backup configuration and data

## Sign-Off Criteria
- [ ] All containers running healthy
- [ ] Prometheus scraping all targets successfully
- [ ] Grafana dashboards displaying data
- [ ] Alertmanager receiving and routing alerts
- [ ] Loki ingesting logs
- [ ] Test alert successfully fired and routed
- [ ] Documentation updated with any deviations
- [ ] Backup scheduled and verified

---

**Deployed by:** _________________  
**Date:** _________________  
**Notes:** _________________

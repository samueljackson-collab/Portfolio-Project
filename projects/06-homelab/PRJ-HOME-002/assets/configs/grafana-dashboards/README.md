# Grafana Production Application Dashboard

This directory contains Grafana dashboard configurations for monitoring homelab services and applications.

## Dashboard Overview

**File:** `production-app-dashboard.json`

**Purpose:** Comprehensive application performance monitoring (APM) dashboard for production services running in the homelab environment.

**Metrics Source:** Prometheus
**Refresh Rate:** 30 seconds
**Schema Version:** 38 (Grafana 9.x/10.x compatible)

---

## Dashboard Panels (10 Total)

### Row 1: Request Metrics

#### 1. Request Rate (Graph)
- **Position:** Top-left (12 width × 8 height)
- **Metric:** `sum(rate(http_requests_total[5m])) by (service)`
- **Y-Axis:** Requests per second (reqps)
- **Purpose:** Monitor incoming HTTP request volume per service
- **Alert:** Fires when request rate > 1000 req/s for 5 minutes
  - **Notification:** Slack (#homelab-alerts)
  - **Severity:** Warning
  - **Use case:** Detect traffic spikes, DDoS attempts, or viral content

**Example Values:**
- Wiki.js: 15-25 req/s (normal), 200+ req/s (spike)
- Immich: 50-80 req/s (photo browsing), 300+ req/s (bulk upload)
- Nginx Proxy: 100-150 req/s (total traffic)

#### 2. Error Rate (Graph)
- **Position:** Top-right (12 width × 8 height)
- **Metric:** `sum(rate(http_request_errors_total[5m])) by (service, error_type)`
- **Threshold:** Critical if error rate > 1% (0.01)
- **Purpose:** Track 4xx and 5xx HTTP errors by type
- **Error Types:**
  - 400 Bad Request
  - 401 Unauthorized
  - 403 Forbidden
  - 404 Not Found
  - 500 Internal Server Error
  - 502 Bad Gateway
  - 503 Service Unavailable

**Healthy State:** < 0.1% error rate
**Warning:** 0.1% - 1% error rate
**Critical:** > 1% error rate

---

### Row 2: Latency & Users

#### 3. Response Time (P50, P95, P99) (Graph)
- **Position:** Middle-left (12 width × 8 height)
- **Metrics:**
  - P50 (median): 50% of requests complete in X seconds
  - P95: 95% of requests complete in X seconds
  - P99: 99% of requests complete in X seconds
- **Y-Axis:** Seconds
- **Purpose:** Measure application latency and identify performance degradation
- **Histogram:** Uses Prometheus histogram buckets for accurate percentile calculation

**Expected Values:**
- **Wiki.js:**
  - P50: 50ms (page cache hit)
  - P95: 200ms (database query)
  - P99: 500ms (complex search)
- **Immich:**
  - P50: 100ms (thumbnail load)
  - P95: 800ms (ML face detection)
  - P99: 2s (video transcoding)
- **PostgreSQL:**
  - P50: 5ms (indexed query)
  - P95: 50ms (join operation)
  - P99: 200ms (full table scan)

**SLA Targets:**
- P50 < 100ms
- P95 < 500ms
- P99 < 2s

#### 4. Active Users (Stat Panel)
- **Position:** Middle-right (6 width × 4 height)
- **Metric:** `active_users`
- **Display:** Single stat with color thresholds
- **Thresholds:**
  - Green: 0 - 8,000 users (normal)
  - Yellow: 8,000 - 10,000 users (high load)
  - Red: > 10,000 users (capacity limit)
- **Purpose:** Real-time count of concurrent active sessions
- **Calculation:** Unique sessions in last 5 minutes

**Typical Values:**
- Internal homelab: 5-10 concurrent users
- External access: 50-100 concurrent users (if public-facing)
- Peak: 200+ users (during events or viral content)

---

### Row 3: Backend Resources

#### 5. Database Connections (Graph)
- **Position:** Bottom-left (12 width × 8 height)
- **Metrics:**
  - `database_connections_active` - Queries in progress
  - `database_connections_idle` - Pooled connections waiting
- **Purpose:** Monitor database connection pool health
- **Alert Conditions:**
  - Idle connections = 0 (pool exhausted)
  - Active + Idle > max_connections (approaching limit)

**Expected Ratios:**
- **Healthy:** 80% idle, 20% active
- **Busy:** 50% idle, 50% active
- **Overloaded:** 10% idle, 90% active (scale up needed)

**Connection Pool Sizes** (from docker-compose configs):
- Wiki.js: 10 connections max
- Home Assistant: 20 connections max
- Immich: 15 connections max
- Total: 45 / 100 max (55 connections headroom)

#### 6. Cache Hit Rate (Gauge)
- **Position:** Bottom-right (6 width × 8 height)
- **Metrics:**
  - L1 Cache: Application-level cache (Redis, in-memory)
  - L2 Cache: Database query cache
- **Display:** Gauge (0-100%)
- **Thresholds:**
  - Red: 0-70% (poor cache performance)
  - Yellow: 70-90% (acceptable)
  - Green: 90-100% (optimal)
- **Purpose:** Measure cache effectiveness

**Cache Layers:**
- **L1 (Application):**
  - Wiki.js: Page rendering cache
  - Nginx: Static asset cache
  - Target: > 95% hit rate
- **L2 (Database):**
  - PostgreSQL shared buffers
  - Query result cache
  - Target: > 90% hit rate

**Impact of Cache Hit Rate:**
- 95% hit rate = 20x faster responses
- 80% hit rate = 5x faster responses
- < 70% hit rate = investigate cache config

---

### Row 4: Queue & Business Metrics

#### 7. Queue Size (Graph)
- **Position:** Left (12 width × 8 height)
- **Metric:** `queue_size` by queue name
- **Alert:** Fires when queue size > 1,000 messages for 5 minutes
- **Purpose:** Monitor background job queue depth
- **Queues:**
  - `email_queue` - Outbound email notifications
  - `thumbnail_queue` - Image processing (Immich)
  - `backup_queue` - Scheduled backup jobs
  - `ml_queue` - Machine learning tasks (face detection)

**Healthy State:** Queue size < 100
**Warning:** 100-1,000 messages (backlog building)
**Critical:** > 1,000 messages (workers can't keep up)

**Remediation:**
- Scale worker containers
- Increase worker concurrency
- Prioritize critical jobs

#### 8. Orders Created (Business Metric) (Graph)
- **Position:** Right (12 width × 8 height)
- **Metric:** `sum(rate(orders_created_total[5m])) by (status)`
- **Purpose:** Track business-level KPIs (example: e-commerce orders)
- **Statuses:**
  - `pending` - Order created, payment not processed
  - `confirmed` - Payment successful
  - `failed` - Payment failed or cancelled
  - `completed` - Order fulfilled

**Homelab Adaptation:**
This panel can be adapted for homelab-specific metrics:
- Wiki page edits per hour
- Photos uploaded to Immich
- Home Assistant automation triggers
- Backup jobs completed

**Example PromQL:**
```promql
# Wiki.js page edits
sum(rate(wiki_page_edits_total[5m])) by (user)

# Immich photo uploads
sum(rate(immich_photos_uploaded_total[5m])) by (user)

# Home Assistant automations fired
sum(rate(homeassistant_automation_triggered_total[5m])) by (automation_name)
```

---

### Row 5: Infrastructure Metrics

#### 9. CPU Usage by Service (Graph)
- **Position:** Bottom-left (12 width × 8 height)
- **Metric:** `sum(rate(container_cpu_usage_seconds_total[5m])) by (pod, container)`
- **Y-Axis:** CPU percentage (0-100%)
- **Purpose:** Monitor CPU utilization per container/service
- **Source:** cAdvisor (Kubernetes) or Docker stats

**Expected CPU Usage:**
- **Wiki.js:** 5-10% idle, 20-30% active
- **Home Assistant:** 10-15% (continuous sensor processing)
- **Immich:** 30-50% (ML processing), 80-100% (video transcoding)
- **PostgreSQL:** 15-25% (query processing)
- **Nginx Proxy:** 5-10% (reverse proxying)

**Alerts:**
- Warning: CPU > 80% for 10 minutes
- Critical: CPU > 95% for 5 minutes

#### 10. Memory Usage by Service (Graph)
- **Position:** Bottom-right (12 width × 8 height)
- **Metric:** `sum(container_memory_working_set_bytes) by (pod, container)`
- **Y-Axis:** Bytes (auto-formatted: MB, GB)
- **Purpose:** Monitor memory consumption and detect leaks

**Expected Memory Usage** (from docker-compose limits):
- **Wiki.js:** 500MB-2GB (limit: 2GB)
- **Home Assistant:** 1GB-3GB (limit: 3GB)
- **Immich:** 8GB-12GB (limit: 12GB for ML models)
- **PostgreSQL:** 4GB-12GB (limit: 12GB, shared buffers: 4GB)
- **Nginx Proxy:** 100MB-1GB (limit: 1GB)

**Memory Leak Detection:**
- Steady increase over 24 hours
- Memory usage approaching container limit
- OOMKilled events in logs

---

## Dashboard Variables (Templating)

### 1. Datasource Variable
- **Name:** `$datasource`
- **Type:** Datasource selector
- **Query:** `prometheus`
- **Purpose:** Allow switching between Prometheus instances (prod, staging, dev)

### 2. Environment Variable
- **Name:** `$environment`
- **Type:** Query
- **Query:** `label_values(http_requests_total, environment)`
- **Current Value:** `production`
- **Options:** production, staging, development, test
- **Purpose:** Filter metrics by deployment environment

### 3. Service Variable
- **Name:** `$service`
- **Type:** Query
- **Query:** `label_values(http_requests_total{environment="$environment"}, service)`
- **Multi-select:** Yes
- **Include All:** Yes
- **Purpose:** Filter dashboard to specific services

**Example Usage:**
- View all services: `$service = All`
- View only Wiki.js: `$service = wikijs`
- View Wiki + Immich: `$service = wikijs,immich`

---

## Annotations

### Alert Annotations
- **Datasource:** Prometheus
- **Query:** `ALERTS{alertstate="firing"}`
- **Icon Color:** Red
- **Step:** 60s
- **Tags:** `alertname`, `severity`
- **Title:** "Alert: {{alertname}}"
- **Purpose:** Show vertical lines on graphs when alerts fire

**Visualization:**
- Red vertical line appears when alert starts firing
- Tooltip shows alert name and severity
- Helps correlate alerts with metric spikes

---

## Import Instructions

### Import to Grafana (Web UI)

1. **Access Grafana:**
   ```
   http://192.168.40.30:3000
   ```

2. **Navigate to Dashboards:**
   - Click "+" icon in left sidebar
   - Select "Import"

3. **Import JSON:**
   - Click "Upload JSON file"
   - Select `production-app-dashboard.json`
   - Or paste JSON content directly

4. **Configure:**
   - Select Prometheus datasource
   - Choose folder (e.g., "Homelab")
   - Click "Import"

5. **Verify:**
   - Dashboard should load with all 10 panels
   - Check that metrics are populating
   - Test variable dropdowns (environment, service)

### Import via API

```bash
# Set Grafana URL and API key
GRAFANA_URL="http://192.168.40.30:3000"
API_KEY="your_api_key_here"

# Import dashboard
curl -X POST \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d @production-app-dashboard.json \
  "$GRAFANA_URL/api/dashboards/db"
```

### Import via Provisioning (GitOps)

**Directory structure:**
```
/etc/grafana/provisioning/dashboards/
├── dashboard.yml
└── production-app-dashboard.json
```

**dashboard.yml:**
```yaml
apiVersion: 1

providers:
  - name: 'Homelab Dashboards'
    orgId: 1
    folder: 'Homelab'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
```

**Benefits:**
- Dashboards automatically imported on Grafana startup
- Version controlled (git repository)
- Consistent across environments

---

## Metric Requirements

For this dashboard to work, your Prometheus instance must scrape these metrics:

### HTTP Metrics (from application instrumentation)
```yaml
# Request rate
http_requests_total{service="wikijs", method="GET", status="200"}

# Error rate
http_request_errors_total{service="wikijs", error_type="500"}

# Response time histogram
http_request_duration_seconds_bucket{service="wikijs", le="0.1"}
```

### Database Metrics (from PostgreSQL exporter)
```yaml
# Connection counts
database_connections_active{database="wikijs"}
database_connections_idle{database="wikijs"}
```

### Cache Metrics (from application or Redis exporter)
```yaml
# Cache hit rate
cache_hit_rate{cache_layer="l1", service="wikijs"}
cache_hit_rate{cache_layer="l2", service="postgresql"}
```

### Queue Metrics (from application or message queue exporter)
```yaml
# Queue depth
queue_size{queue_name="email_queue"}
queue_size{queue_name="thumbnail_queue"}
```

### Container Metrics (from cAdvisor or Docker exporter)
```yaml
# CPU usage
container_cpu_usage_seconds_total{pod="wikijs", container="wiki"}

# Memory usage
container_memory_working_set_bytes{pod="wikijs", container="wiki"}
```

### Business Metrics (custom application metrics)
```yaml
# Orders (example - adapt for homelab)
orders_created_total{status="confirmed"}

# Homelab adaptations
wiki_page_edits_total{user="admin"}
immich_photos_uploaded_total{user="sam"}
homeassistant_automation_triggered_total{automation_name="sunset_lights"}
```

---

## Alert Rules

The dashboard includes 2 built-in alerts:

### 1. High Request Rate
```yaml
Alert: High Request Rate
Condition: avg(http_requests_total) > 1000 req/s
Duration: 5 minutes
Severity: Warning
Notification: Slack (#homelab-alerts)
Runbook: Check for DDoS, viral content, or bot traffic
```

### 2. Queue Size Too Large
```yaml
Alert: Queue Size Too Large
Condition: avg(queue_size) > 1000 messages
Duration: 5 minutes
Severity: Warning
Notification: Slack (#homelab-alerts)
Runbook: Scale workers, investigate job failures
```

**Additional Alerts (configure in Prometheus):**
```yaml
# High error rate
- alert: HighErrorRate
  expr: sum(rate(http_request_errors_total[5m])) / sum(rate(http_requests_total[5m])) > 0.01
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Error rate above 1% for {{ $labels.service }}"

# Slow response time
- alert: SlowResponseTime
  expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 2
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "P95 latency above 2s for {{ $labels.service }}"

# Database connection pool exhaustion
- alert: DatabasePoolExhausted
  expr: database_connections_idle == 0
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "No idle database connections for {{ $labels.database }}"
```

---

## Customization for Homelab

### Adapt Panels for Homelab Services

**Panel 8: Orders Created → Homelab Activity**

Replace business metrics with homelab-specific KPIs:

```json
{
  "id": 8,
  "title": "Homelab Activity",
  "targets": [
    {
      "expr": "sum(rate(wiki_page_edits_total[5m])) by (user)",
      "legendFormat": "Wiki Edits - {{user}}"
    },
    {
      "expr": "sum(rate(immich_photos_uploaded_total[5m])) by (user)",
      "legendFormat": "Photos Uploaded - {{user}}"
    },
    {
      "expr": "sum(rate(homeassistant_automation_triggered_total[5m])) by (automation_name)",
      "legendFormat": "Automation - {{automation_name}}"
    }
  ]
}
```

### Add Homelab-Specific Panels

**Panel 11: SSL Certificate Expiry**
```json
{
  "id": 11,
  "title": "SSL Certificate Expiry",
  "type": "table",
  "targets": [
    {
      "expr": "(ssl_certificate_expiry_seconds - time()) / 86400",
      "format": "table",
      "instant": true
    }
  ],
  "transformations": [
    {
      "id": "organize",
      "options": {
        "excludeByName": {},
        "indexByName": {},
        "renameByName": {
          "domain": "Domain",
          "Value": "Days Until Expiry"
        }
      }
    }
  ],
  "thresholds": [
    {"value": 0, "color": "red"},
    {"value": 30, "color": "yellow"},
    {"value": 90, "color": "green"}
  ]
}
```

**Panel 12: Backup Status**
```json
{
  "id": 12,
  "title": "Backup Job Status",
  "type": "stat",
  "targets": [
    {
      "expr": "time() - proxmox_backup_last_success_timestamp",
      "legendFormat": "{{vm_name}}"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "s",
      "thresholds": {
        "steps": [
          {"value": null, "color": "green"},
          {"value": 86400, "color": "yellow"},
          {"value": 172800, "color": "red"}
        ]
      }
    }
  }
}
```

---

## Screenshots for Portfolio

### Generate Dashboard Screenshot

**Method 1: Grafana Built-in (Requires Grafana Image Renderer)**
```bash
# Install Grafana Image Renderer plugin
grafana-cli plugins install grafana-image-renderer

# Restart Grafana
systemctl restart grafana-server

# Access rendered PNG
curl "http://192.168.40.30:3000/render/d-solo/app-production?orgId=1&panelId=1&width=1000&height=500" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -o panel1-request-rate.png
```

**Method 2: Browser Screenshot**
1. Open dashboard: `http://192.168.40.30:3000/d/app-production`
2. Press `F11` (fullscreen mode)
3. Press `F12` (DevTools)
4. `Ctrl+Shift+P` → "Capture full size screenshot"
5. Save as `grafana-production-dashboard-fullview.png`

**Method 3: AI Generation (Use prompt from AI-PROMPTS.md)**

See: `../mockups/AI-PROMPTS.md` → Section 1: Grafana Dashboard

---

## Export Dashboard

### Export JSON (with variables resolved)
```bash
# Export dashboard JSON
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "http://192.168.40.30:3000/api/dashboards/uid/app-production" \
  | jq '.dashboard' > production-app-dashboard-export.json
```

### Export as PDF (requires Grafana Enterprise or plugin)
```bash
# Using Grafana Image Renderer
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "http://192.168.40.30:3000/api/reports/render/pdf" \
  -d '{"dashboardUid":"app-production","orientation":"landscape","layout":"grid"}' \
  -o dashboard.pdf
```

---

## Related Files

- **Configuration:** `production-app-dashboard.json`
- **Prometheus Config:** `../../prometheus/prometheus.yml` (if exists)
- **Alert Rules:** `../../prometheus/alert-rules.yml` (if exists)
- **AI Mockup Prompt:** `../mockups/AI-PROMPTS.md`

---

**Last Updated:** November 6, 2025
**Dashboard Version:** 1
**Schema Version:** 38
**Grafana Version:** 10.x compatible

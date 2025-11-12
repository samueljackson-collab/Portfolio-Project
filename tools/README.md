# Enterprise Portfolio - Tools & Automation

This directory contains automation tools, scripts, and configuration for the Enterprise Portfolio infrastructure.

## 📂 Directory Structure

```
tools/
├── grafana/              # Grafana provisioning
│   └── provisioning/
│       ├── datasources/  # Auto-configured data sources
│       └── dashboards/   # Dashboard providers
├── loki/                 # Loki log aggregation config
│   └── loki-config.yml
├── alertmanager/         # Alertmanager configuration
│   └── alertmanager.yml
├── wikijs_push.py        # Wiki.js documentation publisher
└── README.md             # This file
```

## 🛠️ Tools Overview

### Wiki.js Documentation Publisher

Automatically publishes Markdown documentation to Wiki.js via GraphQL API.

**Usage:**

```bash
# Set environment variables
export WIKI_URL="http://localhost:3000/graphql"
export WIKI_TOKEN="your-api-token-here"

# Publish single file
python tools/wikijs_push.py docs/project-overview.md

# Publish entire directory
python tools/wikijs_push.py docs/projects/ --pattern "*.md"

# Custom base path
python tools/wikijs_push.py docs/ --base-path "/portfolio"
```

**Features:**
- Automatic page creation and updates
- Support for directory batch publishing
- SHA-256 verification
- Error handling and retry logic

**Configuration:**
- `WIKI_URL`: Wiki.js GraphQL API endpoint
- `WIKI_TOKEN`: API authentication token
- `WIKI_BASE_PATH`: Base path for published pages (default: `/projects`)

### Grafana Provisioning

Automatically configures Grafana datasources and dashboards on startup.

**Datasources:**
- Prometheus (default): `http://prometheus:9090`
- Loki: `http://loki:3100`

**Dashboard Provisioning:**
Place dashboard JSON files in `grafana/provisioning/dashboards/` for automatic import.

### Loki Configuration

Log aggregation system with 7-day retention.

**Key Settings:**
- Retention: 168 hours (7 days)
- Storage: Filesystem-based
- Schema: v11 (BoltDB shipper)

**Querying Logs:**

```bash
# Via API
curl -G -s "http://localhost:3100/loki/api/v1/query" \
  --data-urlencode 'query={job="systemd-journal"}'

# Via LogQL in Grafana
{job="varlogs"} |= "error"
```

### Alertmanager Configuration

Routes and manages alerts from Prometheus.

**Alert Routing:**
- **Critical**: Routed to `critical` receiver
- **Warning**: Routed to `warning` receiver
- **Default**: All other alerts

**Customization:**

Edit `alertmanager/alertmanager.yml` to configure:
- Slack webhooks
- Email notifications
- PagerDuty integration
- Custom webhook receivers

## 🚀 Quick Start

### 1. Start Demo Stack

```bash
# From repository root
docker compose -f compose.demo.yml up -d

# Verify services
docker compose -f compose.demo.yml ps
```

### 2. Access Services

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)
- **Alertmanager**: http://localhost:9093
- **Loki**: http://localhost:3100

### 3. Publish Documentation to Wiki.js

```bash
# Install dependencies
pip install requests

# Set credentials
export WIKI_TOKEN="your-token"

# Publish project documentation
python tools/wikijs_push.py projects/01-sde-devops/PRJ-SDE-001/README.md
```

## 📊 Monitoring & Observability

### Prometheus Metrics

Access metrics at:
- Node Exporter: http://localhost:9100/metrics
- cAdvisor: http://localhost:8080/metrics
- Prometheus: http://localhost:9090/metrics

### Grafana Dashboards

Import pre-built dashboards:
1. Navigate to http://localhost:3001
2. Login (admin/admin)
3. Go to Dashboards → Import
4. Use dashboard IDs from https://grafana.com/grafana/dashboards/

**Recommended Dashboards:**
- 1860: Node Exporter Full
- 893: Docker and System Monitoring
- 13639: Loki Dashboard

### Alert Testing

Trigger test alerts:

```bash
# High CPU alert
stress-ng --cpu 8 --timeout 10m

# Disk space alert
dd if=/dev/zero of=/tmp/testfile bs=1G count=10
```

## 🔧 Configuration

### Environment Variables

Create `.env` file in repository root:

```bash
# Wiki.js
WIKI_URL=http://localhost:3000/graphql
WIKI_TOKEN=your-api-token
WIKI_BASE_PATH=/projects

# Monitoring
PROMETHEUS_RETENTION=30d
GRAFANA_ADMIN_PASSWORD=admin

# Alerting
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
PAGERDUTY_SERVICE_KEY=your-service-key
```

### Docker Compose Overrides

Create `compose.override.yml` for local customization:

```yaml
version: '3.8'

services:
  grafana:
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=custom_password
    ports:
      - "3000:3000"  # Different port

  prometheus:
    volumes:
      - ./custom-prometheus.yml:/etc/prometheus/prometheus.yml:ro
```

## 📝 Development Workflow

### 1. Make Changes

Edit configuration files in `tools/` directory.

### 2. Test Locally

```bash
# Restart affected service
docker compose -f compose.demo.yml restart prometheus

# View logs
docker compose -f compose.demo.yml logs -f prometheus
```

### 3. Validate

```bash
# Validate Prometheus config
docker exec portfolio-prometheus promtool check config /etc/prometheus/prometheus.yml

# Validate Alertmanager config
docker exec portfolio-alertmanager amtool config show
```

### 4. Commit Changes

```bash
git add tools/
git commit -m "feat: update monitoring configuration"
git push
```

## 🐛 Troubleshooting

### Grafana Can't Connect to Prometheus

```bash
# Check Prometheus is accessible
curl http://localhost:9090/-/healthy

# Check datasource configuration
docker exec portfolio-grafana cat /etc/grafana/provisioning/datasources/datasources.yml

# Restart Grafana
docker compose -f compose.demo.yml restart grafana
```

### Wiki.js Push Fails

```bash
# Test API connectivity
curl -H "Authorization: Bearer $WIKI_TOKEN" \
  http://localhost:3000/graphql \
  -d '{"query": "{ pages { list { id } } }"}'

# Enable debug mode
python -u tools/wikijs_push.py docs/test.md --api-url http://localhost:3000/graphql
```

### Loki Not Receiving Logs

```bash
# Check Loki health
curl http://localhost:3100/ready

# Test log push
curl -X POST http://localhost:3100/loki/api/v1/push \
  -H 'Content-Type: application/json' \
  -d '{"streams":[{"stream":{"job":"test"},"values":[["'$(date +%s)000000000'","test log"]]}]}'
```

## 📚 Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/)
- [Wiki.js Documentation](https://docs.requarks.io/)
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)

## 🤝 Contributing

1. Test changes in local Docker environment
2. Update documentation
3. Commit with conventional commit messages
4. Submit pull request with detailed description

---

**Last Updated**: 2025-11-10
**Maintainer**: Portfolio Project Team

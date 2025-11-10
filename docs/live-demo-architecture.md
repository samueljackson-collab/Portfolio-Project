# Live Demo Architecture — Portfolio Presentation

> **Purpose:** Show recruiters a working observability and automation ecosystem built with homelab code and DevOps patterns.

## 🏷️ Overview

**Title:** Enterprise Portfolio: Live Demo Architecture

**Docker Compose Stack Components:**
- **P01** - Observability Lite (Flask)
- **P09** - CI/CD FastAPI
- **Prometheus** - Metrics collection and alerting
- **Grafana** - Dashboard visualization

---

## 📊 Stack Components

| Component | Description | Key Ports | Skills Demonstrated |
|-----------|-------------|-----------|---------------------|
| P01 – Flask (Observability Lite) | REST API exposing `/healthz` and `/work` | 5000 | Flask, API Dev, Monitoring |
| P09 – FastAPI (CI/CD) | Backend app integrated with CI/CD pipeline | 8000 | FastAPI, Docker, REST |
| Prometheus | Metrics scraper and alerting | 9090 | Metrics, Configuration |
| Grafana | Dashboard visualization | 3001 | Observability, Data Viz |

---

## 🏗️ Architecture Flow

### Data & Service Flow

```
[ P01 Flask ] ──────→ [ Prometheus ]
       ↓                    ↓
[ P09 FastAPI ] ─────→ [ Grafana Dashboard ]
```

### Description

1. **Flask (P01)** and **FastAPI (P09)** expose health endpoints
2. **Prometheus** scrapes `/metrics` endpoints and stores time-series data
3. **Grafana** visualizes the metrics in real-time dashboards
4. **Docker Compose** orchestrates the services for easy local deployment

---

## 🔧 Docker Compose Configuration

**File:** `compose.demo.yml`

```yaml
services:
  p01:
    build: ./projects/P01-observability-lite
    ports:
      - "5000:5000"
    networks:
      - demo-network

  p09:
    build: ./projects/P09-cicd-fastapi
    ports:
      - "8000:8000"
    networks:
      - demo-network

  prometheus:
    image: prom/prometheus:v2.54.0
    ports:
      - "9090:9090"
    volumes:
      - ./projects/P11-monitoring-prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    networks:
      - demo-network

  grafana:
    image: grafana/grafana:11.1.0
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    networks:
      - demo-network

networks:
  demo-network:
    driver: bridge
```

---

## 🧠 Architecture Layers

| Layer | Function | Description |
|-------|----------|-------------|
| **Application** | P01, P09 | REST APIs and app logic |
| **Metrics Collection** | Prometheus | Scrapes `/metrics` endpoints |
| **Visualization** | Grafana | Dashboards for health & latency |
| **Orchestration** | Docker Compose | Local dev stack replicating cloud infra |

---

## 💡 Quick Start Demo Commands

### For Recruiter Demonstration

| Step | Command | Purpose |
|------|---------|---------|
| 1 | `docker compose -f compose.demo.yml up -d` | Launch full demo stack |
| 2 | `curl http://localhost:5000/healthz` | Test Flask API health |
| 3 | `curl http://localhost:8000/` | Test FastAPI |
| 4 | Open `http://localhost:9090` | Check Prometheus UI |
| 5 | Open `http://localhost:3001` | View Grafana Dashboard (admin/admin) |
| 6 | `docker compose -f compose.demo.yml down -v` | Stop & clean up |

### Full Demonstration Script

```bash
# 1. Start the demo environment
docker compose -f compose.demo.yml up -d

# 2. Wait for services to be ready
sleep 10

# 3. Test Flask API
echo "Testing Flask API..."
curl http://localhost:5000/healthz
curl http://localhost:5000/work

# 4. Test FastAPI
echo "Testing FastAPI..."
curl http://localhost:8000/
curl http://localhost:8000/docs

# 5. Check Prometheus targets
echo "Prometheus UI: http://localhost:9090/targets"

# 6. Open Grafana
echo "Grafana Dashboard: http://localhost:3001 (admin/admin)"

# 7. Generate some load for metrics
for i in {1..100}; do
  curl -s http://localhost:5000/work > /dev/null
  curl -s http://localhost:8000/ > /dev/null
done

# 8. Cleanup when done
# docker compose -f compose.demo.yml down -v
```

---

## 🧭 Network Diagram

```
┌─────────────────────────────────────────────┐
│         Docker Network: demo-network        │
│                                             │
│  ┌──────────┐         ┌──────────┐        │
│  │  Flask   │         │ FastAPI  │        │
│  │  (P01)   │         │  (P09)   │        │
│  │ :5000    │         │ :8000    │        │
│  └─────┬────┘         └─────┬────┘        │
│        │                    │              │
│        └────────┬───────────┘              │
│                 │                          │
│                 ▼                          │
│         ┌──────────────┐                   │
│         │  Prometheus  │                   │
│         │    :9090     │                   │
│         └──────┬───────┘                   │
│                │                           │
│                ▼                           │
│         ┌──────────────┐                   │
│         │   Grafana    │                   │
│         │    :3001     │                   │
│         └──────────────┘                   │
│                                            │
└────────────────────────────────────────────┘
```

**Data Direction:**
- Prometheus pulls metrics via HTTP (scrape model)
- Grafana queries Prometheus API
- Docker network links all services seamlessly

---

## 🧰 Technologies Used

### Containerization
- Docker
- Docker Compose

### Monitoring & Observability
- Prometheus (metrics collection)
- Grafana (visualization)

### Backend APIs
- Flask (Python microframework)
- FastAPI (modern async Python framework)

### CI/CD
- GitHub Actions
- YAML workflows
- Docker build automation

### Documentation
- MkDocs
- Wiki.js integration
- Markdown

---

## 📈 Grafana Dashboard Configuration

### Observability Dashboard Panels

**Dashboard Layout:**

```yaml
Dashboard: "Portfolio Demo - System Health"
Refresh: 5s

Panels:
  - Row 1: System Metrics
    - CPU Usage (%)
    - Memory Usage (MB)
    - Disk I/O

  - Row 2: API Performance
    - HTTP Request Rate
    - Response Time (P50, P95, P99)
    - Error Rate (5xx responses)

  - Row 3: Service Health
    - Flask Health Status
    - FastAPI Health Status
    - Uptime %

  - Row 4: Custom Metrics
    - Active Connections
    - Request Queue Depth
    - Cache Hit Rate
```

### Example Prometheus Queries

```promql
# Request rate
rate(http_requests_total[5m])

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# Service uptime
up{job="flask"} OR up{job="fastapi"}
```

---

## 📋 Project Structure

```
enterprise-portfolio/
├── compose.demo.yml                          # Main demo orchestration
├── projects/
│   ├── P01-observability-lite/
│   │   ├── Dockerfile
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── README.md
│   ├── P09-cicd-fastapi/
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── README.md
│   ├── P11-monitoring-prometheus/
│   │   ├── prometheus.yml
│   │   ├── alerts/
│   │   └── README.md
│   └── P13-grafana-dashboards/
│       ├── dashboards/
│       │   └── portfolio-demo.json
│       ├── datasources/
│       └── README.md
├── docs/
│   ├── projects/
│   │   ├── P01.md
│   │   ├── P09.md
│   │   ├── P11.md
│   │   └── P13.md
│   └── live-demo-architecture.md            # This document
└── .github/
    └── workflows/
        └── demo-stack.yml
```

---

## 🧩 Key Takeaways for Recruiters

✅ **Hands-on DevOps Experience**
- Built end-to-end observability environment from scratch
- Production-like monitoring stack using industry-standard tools

✅ **Observability Mindset**
- Instrumented applications with metrics endpoints
- Created meaningful dashboards for system health visibility
- Implemented alerting for proactive issue detection

✅ **Reproducible Architecture**
- Docker Compose for easy deployment
- Infrastructure-as-code approach
- Documented setup and teardown procedures

✅ **Documentation-First Workflow**
- Comprehensive guides via MkDocs
- Wiki.js integration for knowledge management
- Clear architecture diagrams and flow descriptions

✅ **Enterprise-Grade Structure**
- Versioned builds and releases
- CI/CD integration
- Security best practices (health checks, minimal base images)

---

## 🧾 Monitoring & Metrics

### Prometheus Configuration

**File:** `projects/P11-monitoring-prometheus/prometheus.yml`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'flask-p01'
    static_configs:
      - targets: ['p01:5000']
    metrics_path: '/metrics'

  - job_name: 'fastapi-p09'
    static_configs:
      - targets: ['p09:8000']
    metrics_path: '/metrics'

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

### Alert Rules

```yaml
groups:
  - name: demo_alerts
    interval: 30s
    rules:
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.job }} is down"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected on {{ $labels.job }}"
```

---

## 🧰 Learning & Troubleshooting

### Common Issues

| Error | Cause | Fix |
|-------|-------|-----|
| `docker: not found` | Docker not installed | Install Docker Desktop / Engine |
| Prometheus 404 | Wrong metrics target | Fix `prometheus.yml` service names |
| Grafana login fails | Default credentials changed | Use `admin/admin` or reset via ENV |
| Flask/FastAPI crash | Port conflict | Stop old containers: `docker ps` & `docker stop` |
| No metrics in Grafana | Datasource not configured | Add Prometheus datasource in Grafana UI |

### Debugging Commands

```bash
# Check running containers
docker compose -f compose.demo.yml ps

# View logs for specific service
docker compose -f compose.demo.yml logs p01
docker compose -f compose.demo.yml logs prometheus

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Test metrics endpoints directly
curl http://localhost:5000/metrics
curl http://localhost:8000/metrics

# Restart specific service
docker compose -f compose.demo.yml restart p01
```

---

## 🔗 Wiki.js Integration

### Automated Documentation Sync

**File:** `.github/workflows/wiki-sync.yml`

```yaml
name: Sync to Wiki.js

on:
  push:
    branches: [main]
    paths:
      - 'docs/**'
      - 'wiki/**'

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Push to Wiki.js
        env:
          WIKIJS_API_KEY: ${{ secrets.WIKIJS_API_KEY }}
          WIKIJS_URL: ${{ secrets.WIKIJS_URL }}
        run: |
          python tools/wikijs_push.py
```

### API Push Script

**File:** `tools/wikijs_push.py`

```python
#!/usr/bin/env python3
"""
Sync markdown documentation to Wiki.js via GraphQL API
"""
import os
import requests
from pathlib import Path

WIKIJS_URL = os.getenv('WIKIJS_URL', 'http://localhost:3000')
API_KEY = os.getenv('WIKIJS_API_KEY')

GRAPHQL_ENDPOINT = f"{WIKIJS_URL}/graphql"

def push_page(path: str, content: str, title: str):
    """Push a single page to Wiki.js"""
    mutation = """
    mutation CreatePage($content: String!, $path: String!, $title: String!) {
      pages {
        create(
          content: $content
          path: $path
          title: $title
          isPublished: true
          locale: "en"
          editor: "markdown"
        ) {
          responseResult {
            succeeded
            message
          }
        }
      }
    }
    """

    response = requests.post(
        GRAPHQL_ENDPOINT,
        json={
            'query': mutation,
            'variables': {
                'content': content,
                'path': path,
                'title': title
            }
        },
        headers={'Authorization': f'Bearer {API_KEY}'}
    )

    return response.json()

if __name__ == '__main__':
    docs_dir = Path('docs')
    for md_file in docs_dir.rglob('*.md'):
        with open(md_file) as f:
            content = f.read()

        relative_path = str(md_file.relative_to(docs_dir))
        title = md_file.stem.replace('-', ' ').title()

        result = push_page(relative_path, content, title)
        print(f"Pushed {relative_path}: {result}")
```

---

## 📚 Additional Resources

### Related Documentation
- [P01 Observability Lite Project](../projects/P01-observability-lite/README.md)
- [P09 CI/CD FastAPI Project](../projects/P09-cicd-fastapi/README.md)
- [P11 Prometheus Monitoring](../projects/P11-monitoring-prometheus/README.md)
- [P13 Grafana Dashboards](../projects/P13-grafana-dashboards/README.md)

### External References
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Dashboard Guide](https://grafana.com/docs/grafana/latest/dashboards/)
- [Flask Metrics with Prometheus](https://github.com/prometheus/client_python)
- [FastAPI Metrics Integration](https://github.com/stephenhillier/starlette_exporter)

---

## 🎯 Next Steps

### Enhancement Roadmap

1. **Add More Services**
   - PostgreSQL with pg_exporter
   - Redis with redis_exporter
   - Nginx with nginx_exporter

2. **Advanced Dashboards**
   - Multi-service correlation views
   - SLO/SLI tracking dashboards
   - Cost analysis per service

3. **Alerting Integration**
   - Slack notifications via Alertmanager
   - PagerDuty escalation policies
   - Email alerts for critical issues

4. **Security Enhancements**
   - TLS encryption for all endpoints
   - Authentication for Prometheus
   - Grafana LDAP/OAuth integration

5. **Performance Testing**
   - Load testing with Locust
   - Stress testing scenarios
   - Chaos engineering experiments

---

## 📧 Contact & Feedback

For questions about this demo architecture or to schedule a live walkthrough:

- **GitHub**: [@samueljackson-collab](https://github.com/samueljackson-collab)
- **LinkedIn**: [Sam Jackson](https://www.linkedin.com/in/sams-jackson)
- **Portfolio**: [Portfolio Project Repository](https://github.com/samueljackson-collab/Portfolio-Project)

---

*Last Updated: 2025-11-10*
*Version: 1.0*
*Maintained by: Sam Jackson*

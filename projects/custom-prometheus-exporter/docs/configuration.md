# Configuration Reference

The exporter is configured via YAML with optional environment overrides.

## Environment overrides

| Variable | Description |
| --- | --- |
| `EXPORTER_ADDRESS` | Server address (default `0.0.0.0`) |
| `EXPORTER_PORT` | Server port |
| `EXPORTER_LOG_LEVEL` | Log level (`debug`, `info`, `warn`, `error`) |
| `EXPORTER_SCRAPE_INTERVAL` | Scrape interval duration |
| `EXPORTER_ENABLE_API` | Enable API collection (`true`/`false`) |
| `EXPORTER_ENABLE_FILES` | Enable file collection (`true`/`false`) |
| `EXPORTER_ENABLE_SQL` | Enable SQL collection (`true`/`false`) |

## YAML structure

```yaml
server:
  address: "0.0.0.0"
  port: 9108

logging:
  level: "info"

scrape:
  interval: 30s

labels:
  environment: "dev"

feature_flags:
  enable_api: true
  enable_files: true
  enable_sql: false

metric_filter:
  disabled:
    - "custom_exporter_api_response_size_bytes"

api_endpoints:
  - name: "sample_api"
    url: "https://api.example.com/metrics"
    method: "GET"
    timeout: 5s
    value_path: "data.value"
    metric_type: "gauge" # gauge, counter, histogram, summary
    labels:
      service: "api"
    headers:
      Authorization: "Bearer token"

file_metrics:
  - name: "queue_depth"
    path: "/var/lib/custom-exporter/queue_depth.txt"
    trim_space: true
    metric_type: "gauge"
    labels:
      region: "us-east-1"

sql_metrics:
  - name: "orders_pending"
    driver: "sqlite"
    dsn: "/var/lib/custom-exporter/app.db"
    query: "select count(*) from orders where status = 'pending'"
    metric_type: "gauge"
    labels:
      component: "orders"
```

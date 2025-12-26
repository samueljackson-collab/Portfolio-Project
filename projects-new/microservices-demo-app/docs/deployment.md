# Deployment Guide

## Docker Compose (development)
```bash
docker compose -f docker-compose.dev.yml up --build
```

## Docker Compose (production)
```bash
docker compose -f docker-compose.prod.yml up --build
```

## Health checks
All services expose `/health` endpoints (Spring Boot uses `/actuator/health`).

## Observability
- Jaeger: http://localhost:16686
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Kibana: http://localhost:5601

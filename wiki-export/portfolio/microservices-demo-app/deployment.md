---
title: Deployment Guide
description: docker compose -f docker-compose.dev.yml up --build docker compose -f docker-compose.prod.yml up --build All services expose `/health` endpoints (Spring Boot uses `/actuator/health`). - Jaeger: http:/
tags: [documentation, portfolio]
path: portfolio/microservices-demo-app/deployment
created: 2026-03-08T22:19:13.942032+00:00
updated: 2026-03-08T22:04:38.059902+00:00
---

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

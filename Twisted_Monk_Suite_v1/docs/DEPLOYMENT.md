# Deployment Guide

This document describes how to deploy the Twisted Monk Suite to a production environment.

## 1. Infrastructure Requirements

- Container-friendly host (Kubernetes, ECS, or Docker host)
- Managed Redis instance (e.g., AWS ElastiCache, Azure Cache for Redis)
- Secure secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)
- HTTPS termination (load balancer or reverse proxy)
- CI/CD pipeline for automated builds and deployments

## 2. Build Pipeline

1. **Install dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```
2. **Run tests**
   ```bash
   pytest Twisted_Monk_Suite_v1/tests
   ```
3. **Build container image**
   ```bash
   docker build -t registry.example.com/twisted-monk-api:latest Twisted_Monk_Suite_v1/backend
   ```
4. **Push image**
   ```bash
   docker push registry.example.com/twisted-monk-api:latest
   ```

## 3. Environment Configuration

- Copy `.env.example` to a secure location and populate secrets.
- Store secrets in your secret manager and inject them as environment variables at runtime.
- Ensure `ALLOWED_ORIGINS` contains the production storefront domain.
- Configure Redis endpoint and credentials.

## 4. Application Deployment

### Docker Compose
```yaml
version: "3.8"
services:
  api:
    image: registry.example.com/twisted-monk-api:latest
    restart: always
    env_file: .env
    ports:
      - "8000:8000"
    depends_on:
      - redis
  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redis-data:/data
volumes:
  redis-data:
```

### Kubernetes (excerpt)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: twisted-monk-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: twisted-monk-api
  template:
    metadata:
      labels:
        app: twisted-monk-api
    spec:
      containers:
        - name: api
          image: registry.example.com/twisted-monk-api:latest
          ports:
            - containerPort: 8000
          envFrom:
            - secretRef:
                name: twisted-monk-env
```

## 5. Post-Deployment Checklist

- [ ] Health endpoint `/health` returns `200`
- [ ] Shopify storefront can reach the API
- [ ] Redis metrics are visible in monitoring system
- [ ] Alerting webhooks (Slack/email) fire correctly
- [ ] Logs are streaming to centralized log platform
- [ ] Backups scheduled for Redis and configuration storage

## 6. Rollback Strategy

- Maintain the previous Docker image tag.
- Use blue/green or canary deployments to minimize risk.
- For Shopify assets, keep prior versions in theme history.
- Document manual rollback procedure for operations scripts.

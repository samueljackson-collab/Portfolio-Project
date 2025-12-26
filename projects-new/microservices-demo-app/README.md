# Microservices Demo App

A portfolio-ready microservices architecture demonstrating API gateway routing, service-to-service communication (REST + gRPC), async messaging, and observability.

## What is included
- **Microservices**: API Gateway, User, Product, Order, Payment, Notification
- **Supporting services**: Postgres, Redis, RabbitMQ, Elasticsearch, Nginx
- **Observability**: OpenTelemetry + Jaeger, Prometheus + Grafana, ELK (Elasticsearch + Logstash + Kibana)
- **Testing**: Jest, pytest, Postman collection, k6 load test, contract test stub
- **Docs**: OpenAPI, architecture + deployment guides, service interaction flows

## Quick start (development)
```bash
cd /workspace/Portfolio-Project/projects-new/microservices-demo-app

docker compose -f docker-compose.dev.yml up --build
```

## Quick start (production-like)
```bash
docker compose -f docker-compose.prod.yml up --build
```

## Services & ports
| Service | Port | Notes |
| --- | --- | --- |
| API Gateway | 8080 | External entrypoint |
| User Service | 8081 | Auth endpoints |
| Product Service | 8082 | REST + gRPC server (50051) |
| Order Service | 8083 | REST + gRPC client |
| Payment Service | 8084 | Resilience4j circuit breaker demo |
| Notification Service | 8085 | RabbitMQ consumer |
| Nginx | 80 | Reverse proxy |
| Jaeger | 16686 | Tracing UI |
| Prometheus | 9090 | Metrics |
| Grafana | 3000 | Dashboards |
| Kibana | 5601 | Logs |

## Testing
```bash
# Gateway unit tests
cd services/api-gateway
npm test

# Product service unit tests
cd ../product-service
pytest

# Load test (k6)
cd ../../tests/load
k6 run load_test.js
```

## Docs
- `docs/architecture.md`
- `docs/service-flows.md`
- `docs/deployment.md`
- `docs/dev-setup.md`
- `docs/openapi.yaml`
- `docs/diagrams/architecture.mmd`

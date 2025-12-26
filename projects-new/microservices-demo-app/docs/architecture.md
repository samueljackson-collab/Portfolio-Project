# Architecture Overview

## Components
- **API Gateway (Node/Express)** routes external traffic to services.
- **User Service** handles authentication/authorization.
- **Product Service** exposes REST and gRPC for catalog lookups.
- **Order Service** uses gRPC to fetch product data and publishes events to RabbitMQ.
- **Payment Service (Spring Boot)** demonstrates Resilience4j circuit breaker usage.
- **Notification Service** consumes RabbitMQ messages.

## Supporting services
- PostgreSQL (primary database)
- Redis (cache)
- RabbitMQ (message queue)
- Elasticsearch + Logstash + Kibana (logging)
- Jaeger + OpenTelemetry (distributed tracing)
- Prometheus + Grafana (metrics)
- Nginx (reverse proxy)

## Service discovery
Docker Compose provides DNS-based discovery (`http://service-name:port`).

## Resilience
Resilience4j is configured in `services/payment-service/src/main/resources/application.yml` with a circuit breaker named `bankGateway`.

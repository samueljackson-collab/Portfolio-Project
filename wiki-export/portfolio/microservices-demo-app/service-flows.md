---
title: Service Interaction Flows
description: 1. Client calls **API Gateway** `/orders`. 2. Gateway forwards to **Order Service**. 3. Order Service fetches product details via **gRPC** from **Product Service**. 4. Order Service publishes a `notif
tags: [documentation, portfolio]
path: portfolio/microservices-demo-app/service-flows
created: 2026-03-08T22:19:13.941512+00:00
updated: 2026-03-08T22:04:38.060902+00:00
---

# Service Interaction Flows

## Checkout flow
1. Client calls **API Gateway** `/orders`.
2. Gateway forwards to **Order Service**.
3. Order Service fetches product details via **gRPC** from **Product Service**.
4. Order Service publishes a `notifications` event to **RabbitMQ**.
5. **Notification Service** consumes the event and logs delivery.
6. **Payment Service** processes payment with Resilience4j circuit breaker.

## Search flow
1. Client calls **API Gateway** `/products`.
2. Gateway forwards to **Product Service**.
3. Product Service queries Elasticsearch for indexed catalog data.

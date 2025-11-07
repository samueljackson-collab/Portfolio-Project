# ADR 003: Centralized API Gateway with Rate Limiting

## Status
Accepted

## Context
Multiple microservices need unified external API, authentication, rate limiting, and request routing.

## Decision
Implement Kong API Gateway with:
- JWT authentication
- Rate limiting per user/IP
- Request/response transformation
- Service discovery integration
- Comprehensive logging

### Configuration Example

```yaml
# kong.yml
_format_version: "3.0"

services:
  - name: user-service
    url: http://user-service:8080
    routes:
      - name: user-routes
        paths:
          - /api/users
        methods:
          - GET
          - POST
          - PUT
          - DELETE
        strip_path: false
    plugins:
      - name: jwt
      - name: rate-limiting
        config:
          minute: 100
          policy: local
      - name: cors
        config:
          origins:
            - "https://example.com"
          methods:
            - GET
            - POST
            - PUT
            - DELETE
          headers:
            - Accept
            - Authorization
            - Content-Type
          exposed_headers:
            - X-Auth-Token
          credentials: true
          max_age: 3600

  - name: product-service
    url: http://product-service:8080
    routes:
      - name: product-routes
        paths:
          - /api/products
    plugins:
      - name: jwt
      - name: rate-limiting
        config:
          minute: 1000
          policy: redis
          redis_host: redis
          redis_port: 6379
      - name: response-transformer
        config:
          add:
            headers:
              - "X-Service:product"

  - name: order-service
    url: http://order-service:8080
    routes:
      - name: order-routes
        paths:
          - /api/orders
    plugins:
      - name: jwt
      - name: rate-limiting
        config:
          minute: 50
          hour: 1000
      - name: request-size-limiting
        config:
          allowed_payload_size: 10
      - name: bot-detection

plugins:
  - name: prometheus
    config:
      per_consumer: true

  - name: file-log
    config:
      path: /var/log/kong/access.log
```

## Consequences
- Single entry point for all services
- Consistent authentication/authorization
- Protection against abuse
- Better observability
- Additional infrastructure component

## Alternatives Considered
- Service-level authentication (rejected: duplication)
- AWS API Gateway (rejected: vendor lock-in)
- Nginx+ (rejected: less feature-rich)

## Review Date
Review in 6 months based on:
- Performance metrics
- Operational complexity
- Cost considerations
- Team feedback

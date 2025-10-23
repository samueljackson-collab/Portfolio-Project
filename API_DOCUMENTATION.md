# 🔗 API Documentation

This reference covers the sample FastAPI service located in `examples/fullstack/api`. The service
provides health, telemetry, and event recording endpoints used by smoke and performance tests.

## Base URL

```
http://localhost:8080
```

## Authentication

No authentication is required for the sample service. Production deployments should layer OAuth2/JWT
protection before exposing these endpoints publicly.

## Endpoints

### `GET /health`
Returns overall health information for the API, database, and Redis.

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "checks": {
    "database": "pass",
    "redis": "pass"
  }
}
```

### `GET /health/db`
Executes a lightweight SQL query (`SELECT 1`) to confirm PostgreSQL connectivity.

**Response**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "checks": {
    "database": "pass"
  }
}
```

### `GET /health/redis`
Runs a Redis `PING` command to ensure the cache layer is reachable.

**Response**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "checks": {
    "redis": "pass"
  }
}
```

### `GET /metrics`
Returns simple counters that demonstrate how the API interacts with Redis and PostgreSQL. Each call
increments a Redis-based visit counter and reports the number of events stored in the database.

**Response**
```json
{
  "version": "0.1.0",
  "redis_visits": 5,
  "database_visits": 3
}
```

### `POST /metrics`
Persists an event payload into PostgreSQL for audit or analytics scenarios.

**Request**
```json
{
  "type": "page_view",
  "payload": {
    "page": "/dashboard",
    "user_id": "123"
  }
}
```

**Response**
```json
{
  "status": "recorded",
  "version": "0.1.0",
  "event_type": "page_view"
}
```

## Error Handling
- Database or Redis connectivity failures return `503 Service Unavailable` with diagnostic detail.
- Validation errors for `POST /metrics` return `400 Bad Request`.

## Rate Limiting
Rate limiting is not enforced in the sample service. Upstream gateways (e.g., API Gateway, Istio) are
expected to provide production-grade throttling.

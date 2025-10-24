# Portfolio API Documentation

The Portfolio API provides programmatic access to Sam Jackson's project catalog, automation artifacts, and operational telemetry. All endpoints are scoped under `/api/v1` and require authentication via JSON Web Tokens (JWTs) issued by the identity service described in [SECURITY.md](./SECURITY.md#identity-and-access-management).

## Base URL

| Environment | URL |
| --- | --- |
| Development | `https://api.dev.portfolio.example.com` |
| Staging | `https://api.staging.portfolio.example.com` |
| Production | `https://api.portfolio.example.com` |

## Authentication

1. Obtain a JWT by exchanging client credentials with the `/oauth/token` endpoint.
2. Include the token in each request header: `Authorization: Bearer <token>`.
3. Tokens expire after 60 minutes; refresh tokens last 24 hours.

Requests without a valid token return `401 Unauthorized`.

## Versioning

- Current version: **v1**.
- Breaking changes introduce a new major version (`/api/v2`).
- Minor enhancements are backward compatible and reflected in the OpenAPI schema located at [`documentation/openapi/portfolio-api.yaml`](./documentation/openapi/portfolio-api.yaml).

## Error Model

Errors use the following structure:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Portfolio item 123 not found",
    "correlation_id": "1d9c0f5d-2d18-4f12-8a6e-9092a5d5f83c"
  }
}
```

The `correlation_id` maps to logs exported to OpenSearch and traces in AWS X-Ray.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/v1/portfolio` | List published portfolio entries with pagination. |
| `GET` | `/api/v1/portfolio/{id}` | Retrieve a single portfolio entry with metadata, assets, and evidence links. |
| `POST` | `/api/v1/portfolio` | Create a new entry (requires `portfolio:write`). |
| `PATCH` | `/api/v1/portfolio/{id}` | Update fields on an existing entry. |
| `GET` | `/api/v1/artifacts` | Fetch automation artifacts and associated runbooks. |
| `POST` | `/api/v1/exports` | Trigger PDF/ZIP export jobs asynchronously. |
| `GET` | `/api/v1/jobs/{id}` | Retrieve export job status. |
| `GET` | `/api/v1/metrics` | Return aggregated analytics for dashboards. |

### List Portfolio Entries

**Request**

```http
GET /api/v1/portfolio?page=1&limit=20 HTTP/1.1
Host: api.portfolio.example.com
Authorization: Bearer <token>
Accept: application/json
```

**Response**

```json
{
  "data": [
    {
      "id": "PRJ-SDE-002",
      "title": "Observability & Backups Stack",
      "status": "done",
      "tags": ["prometheus", "grafana", "backup"],
      "updated_at": "2024-12-18T23:14:02Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 37
  }
}
```

### Retrieve Portfolio Entry

**Request**

```http
GET /api/v1/portfolio/PRJ-SDE-002 HTTP/1.1
Host: api.portfolio.example.com
Authorization: Bearer <token>
Accept: application/json
```

**Response**

```json
{
  "id": "PRJ-SDE-002",
  "title": "Observability & Backups Stack",
  "summary": "Monitoring/alerting stack using Prometheus, Grafana, Loki, and Alertmanager, integrated with Proxmox Backup Server.",
  "status": "done",
  "links": {
    "repository": "https://github.com/sams-jackson/Portfolio-Project",
    "evidence": "s3://portfolio-evidence/prj-sde-002/"
  },
  "artifacts": [
    {
      "type": "runbook",
      "title": "Grafana dashboard deployment",
      "uri": "https://docs.portfolio.example.com/runbooks/grafana"
    }
  ]
}
```

### Create Portfolio Entry

Requires `portfolio:write` scope.

```http
POST /api/v1/portfolio HTTP/1.1
Host: api.portfolio.example.com
Authorization: Bearer <token>
Content-Type: application/json

{
  "id": "PRJ-QA-003",
  "title": "UI Regression Automation",
  "summary": "Selenium + PyTest suite with GitHub Actions integration",
  "status": "planned",
  "tags": ["qa", "automation"],
  "links": {
    "repository": "https://github.com/sams-jackson/Portfolio-Project"
  }
}
```

**201 Created**

```json
{
  "id": "PRJ-QA-003",
  "created_at": "2025-02-11T19:05:44Z",
  "status": "pending_review"
}
```

### Trigger Export Job

Export jobs produce PDFs and ZIP bundles of the selected entries. Jobs are processed asynchronously via SQS and worker pods (see [ARCHITECTURE.md](./ARCHITECTURE.md#integration--messaging)).

```http
POST /api/v1/exports HTTP/1.1
Host: api.portfolio.example.com
Authorization: Bearer <token>
Content-Type: application/json

{
  "format": "pdf",
  "portfolio_ids": ["PRJ-SDE-002", "PRJ-HOME-001"],
  "notify": {
    "email": "sam@example.com"
  }
}
```

**202 Accepted**

```json
{
  "job_id": "job-01H6Y9W7XJ4T6A1Z3NT62H1W7R",
  "status": "queued",
  "estimated_completion": "2025-02-11T19:10:00Z"
}
```

### Webhooks

Clients can register webhooks to receive export completion events. Configure endpoints via `POST /api/v1/webhooks` with a JSON body containing the `target_url`, `secret`, and subscribed events. Webhook signatures use HMAC-SHA256 with the shared secret.

### Rate Limits

- 120 requests per minute per client for read operations.
- 30 requests per minute for write operations.
- Burst capacity is controlled via AWS API Gateway usage plans.

### SDKs & Examples

Language-specific examples are stored in [`examples/sdk/`](./examples/sdk/). Postman collections and VS Code `.http` files can be found in [`examples/api/`](./examples/api/). Each example references this documentation for payload definitions.


# Backend Service

FastAPI application providing authentication and content management APIs for the portfolio.

## Features
- Async SQLAlchemy 2.0 models backed by PostgreSQL.
- JWT access and refresh token issuance with bcrypt password hashing.
- Modular router organization (auth, content, health).
- Prometheus instrumentation for request metrics.

## Running Locally

```bash
uvicorn app.main:app --reload
```

Set environment variables via `.env` or export:

```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/portfolio
SECRET_KEY=local-secret
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Tests

```bash
pytest
```

## API Docs
Navigate to `/docs` for OpenAPI specification when the service is running.


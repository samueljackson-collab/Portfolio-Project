# Full-Stack Example Environment

This example powers the local development workflow described in the root README. It wires together
an API, PostgreSQL, Redis, and a static frontend so that the bundled smoke tests have concrete
endpoints to validate.

## Services

| Service   | Image / Build Context             | Port | Purpose                                   |
|-----------|-----------------------------------|------|-------------------------------------------|
| frontend  | `nginx:alpine` + static HTML      | 3000 | Serves the sample landing page             |
| api       | `examples/fullstack/api` (FastAPI) | 8080 | Provides health + telemetry endpoints      |
| db        | `postgres:15-alpine`              | 5432 | Stores application data                    |
| redis     | `redis:7-alpine`                  | 6379 | Tracks simple counters used by the API     |

## Usage

```bash
docker-compose up --build
./scripts/test/smoke-tests.sh
```

Shut everything down with:

```bash
docker-compose down -v
```

## Customisation Tips

- Replace the FastAPI app with your production API while keeping the health endpoints so the smoke
tests remain valid.
- Add additional services (e.g. Celery worker, Prometheus) by extending `docker-compose.yml`.
- Mount a local directory into the frontend container to iterate on UI prototypes quickly.

# AstraDup Video De-duplication Operational Runbook

## Overview
Operational procedures for maintaining and troubleshooting AstraDup services (API, Celery workers, Airflow, and observability stack).

## Service Map
| Service | Purpose | Default Port | Container |
| --- | --- | --- | --- |
| PostgreSQL | Metadata store | 5432 | `astradup-postgres` |
| Redis | Cache + Celery broker | 6379 | `astradup-redis` |
| Celery Worker | Video processing tasks | N/A | `astradup-worker` |
| Airflow Webserver | Orchestration UI | 8080 | `astradup-airflow-webserver` |
| Airflow Scheduler | DAG scheduling | N/A | `astradup-airflow-scheduler` |
| API | Health + metrics | 8000 | `astradup-api` |
| Prometheus | Metrics scraping | 9090 | `astradup-prometheus` |
| Grafana | Dashboards | 3000 | `astradup-grafana` |

## Prerequisites
- Docker + Docker Compose
- Access to `.env` values (see `.env.example`)
- FFmpeg available if running local feature extraction

## Common Operations

### Start the Stack
```bash
docker-compose up -d
```

### Stop the Stack
```bash
docker-compose down
```

### Restart a Single Service
```bash
docker-compose restart api
```

### Tail Logs
```bash
# All services

docker-compose logs -f

# Single service

docker-compose logs -f astradup-worker
```

## Health Checks

### Container Status
```bash
docker-compose ps
```

### API + Metrics
```bash
curl -f http://localhost:8000/health
curl -f http://localhost:8000/metrics
```

### Airflow
```bash
curl -f http://localhost:8080/health
```

### Redis
```bash
docker-compose exec redis redis-cli ping
```

### PostgreSQL
```bash
docker-compose exec postgres pg_isready -U astradup
```

## Airflow Operations

### Initialize the Airflow DB (first run)
```bash
docker-compose run --rm airflow-webserver airflow db init
```

### Create Admin User
```bash
docker-compose run --rm airflow-webserver airflow users create \
  --username admin \
  --firstname Astra \
  --lastname Dup \
  --role Admin \
  --email admin@example.com \
  --password changeme
```

### Trigger the Deduplication DAG
```bash
docker-compose exec airflow-webserver airflow dags trigger video_deduplication_pipeline
```

## Celery Operations

### Inspect Worker
```bash
docker-compose exec celery-worker celery -A src.pipeline.tasks inspect ping
```

### Run Sample Similarity Task
```bash
docker-compose exec celery-worker celery -A src.pipeline.tasks call astradup.healthcheck
```

## Troubleshooting

### Issue: API returns 5xx
**Symptoms:** `curl http://localhost:8000/health` fails.

**Diagnosis Steps:**
1. `docker-compose ps` to confirm `api` is healthy.
2. `docker-compose logs -f api` for stack traces.
3. Validate dependencies: PostgreSQL and Redis must be healthy.

**Resolution:**
- Restart API after dependencies are healthy: `docker-compose restart api`.

### Issue: Celery workers stuck
**Symptoms:** Tasks remain in queued state.

**Diagnosis Steps:**
1. Validate Redis: `docker-compose exec redis redis-cli ping`.
2. Inspect worker: `docker-compose exec celery-worker celery -A src.pipeline.tasks inspect active`.

**Resolution:**
- Restart worker: `docker-compose restart celery-worker`.

### Issue: Airflow UI unavailable
**Symptoms:** `http://localhost:8080` returns error.

**Diagnosis Steps:**
1. `docker-compose logs -f airflow-webserver` for startup errors.
2. Ensure DB initialized: run `airflow db init` if needed.

**Resolution:**
- Recreate webserver container: `docker-compose up -d airflow-webserver`.

## Monitoring and Alerts
- **Prometheus:** `http://localhost:9090` (config: `prometheus/prometheus.yml`)
- **Grafana:** `http://localhost:3000` (default user `admin`, password from `.env`)
- Alert rules live in `prometheus/rules.yml`.

## Backup and Recovery

### PostgreSQL Backup
```bash
mkdir -p ./backups
docker-compose exec postgres pg_dump -U astradup astradup > ./backups/astradup_backup.sql
```

### PostgreSQL Restore
```bash
docker-compose exec -T postgres psql -U astradup astradup < ./backups/astradup_backup.sql
```

### Redis Snapshot
```bash
docker-compose exec redis redis-cli save
```

## Contacts
- On-call engineer: [contact info]
- Team channel: [slack/teams channel]
- Escalation: [manager contact]

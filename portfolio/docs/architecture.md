# Architecture Overview

The portfolio platform is split into decoupled layers:

- **API Layer**: FastAPI async service exposing JWT-protected CRUD endpoints.
- **Client Layer**: React SPA built with Vite, leveraging React Router for navigation and Axios for API access.
- **Data Layer**: Async SQLAlchemy ORM over PostgreSQL (SQLite locally), with Alembic migrations.
- **Infrastructure Layer**: Terraform modules manage AWS resources including VPC, ECS/EKS placeholders, and remote state stored in S3 with DynamoDB locking.
- **Observability**: Prometheus, Grafana, and Loki placeholders gather metrics, dashboards, and logs.

Communication occurs via REST over HTTPS with JWT bearer tokens. Infrastructure uses Docker for local workflows and Helm for Kubernetes packaging.

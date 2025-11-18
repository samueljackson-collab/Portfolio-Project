# Backend

- **Framework:** FastAPI with async SQLAlchemy and JWT auth
- **Database:** PostgreSQL (asyncpg) with seed script for 25 projects
- **Key Endpoints:** `/auth/login`, `/auth/register`, `/auth/me`, `/projects/`
- **Testing:** `pytest -q` with SQLite-backed fixtures for isolated runs

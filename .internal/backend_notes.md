# Backend Maintenance Notes (Internal)

This document captures the rationale behind the trimmed in-code comments.
Keep it private to the team; do not publish externally.

## Configuration
- `app/config.py` exposes the `Settings` object consumed throughout the
  application. Set `DATABASE_URL` to either an asyncpg or aiosqlite DSN.
- The `testing` flag disables startup/shutdown hooks so pytest can swap the
  database dependency safely.

## Database Layer
- `app/database.py` builds an async engine. SQLite runs with `StaticPool` and
  `check_same_thread=False` to share connections across tasks.
- `get_db()` wraps each request in a transaction. Commit happens on success and
  a rollback is issued on failure.

## Authentication Helpers
- `app/auth.py` centralises password hashing (bcrypt) and JWT handling. Tokens
  carry a `sub` claim that matches the user email.

## HTTP Layer
- `app/routers/` contains the FastAPI routers. Health probes expose readiness
  checks, auth exposes registration/login, and content implements CRUD with
  access control (owners see drafts; anonymous users see published records).

## Testing
- `backend/tests/conftest.py` provisions an in-memory SQLite database, toggles
  `settings.testing`, and overrides `get_db` so API tests run against the
  ephemeral schema.
- Auth/content/health tests ensure the main workflows continue to operate.

Update this document whenever the architecture changes materially.

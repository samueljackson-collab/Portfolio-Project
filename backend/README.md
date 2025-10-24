# Backend Service

FastAPI-based REST API providing authentication and content management for the portfolio. The service uses async SQLAlchemy, Alembic migrations, and JWT-based authentication.

## Features
- User registration and login with bcrypt password hashing.
- JWT access and refresh tokens with configurable lifetimes.
- CRUD operations for content items owned by authenticated users.
- Health check endpoint for monitoring.

## Requirements
- Python 3.11
- PostgreSQL (production) or SQLite (development/testing)

## Local Development
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set environment variables (see `.env.example`).
3. Run database migrations:
   ```bash
   alembic upgrade head
   ```
4. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Testing
```bash
pytest
```

## Environment Variables
Refer to `.env.example` for required variables including `DATABASE_URL`, `SECRET_KEY`, and token expiry durations.

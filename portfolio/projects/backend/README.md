# Portfolio Backend Service

## Features
- FastAPI application with async SQLAlchemy ORM
- JWT-based authentication (30 minute access tokens)
- Alembic migrations and Dockerfile for containerized deployment

## Development
1. Copy `.env.example` to `.env` and configure secrets.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run the API: `uvicorn app.main:app --reload`.
4. Execute tests: `pytest`.

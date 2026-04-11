# Backend API — Setup Guide

## Overview

The Backend API is a **FastAPI** application written in Python 3.11. It exposes a RESTful JSON API over HTTP, handles JWT-based authentication, and persists data in a **PostgreSQL 15** database. Async database access is provided by SQLAlchemy with the `asyncpg` driver; schema migrations are managed by **Alembic**.

When running locally you will have:

- REST API at `http://localhost:8000`
- Interactive Swagger UI at `http://localhost:8000/docs`
- ReDoc documentation at `http://localhost:8000/redoc`
- Health-check endpoint at `http://localhost:8000/health`

---

## Architecture

```
┌─────────────────────────────────────┐
│            Your Browser             │
│      http://localhost:8000/docs     │
└──────────────────┬──────────────────┘
                   │ HTTP
┌──────────────────▼──────────────────┐
│          FastAPI (Uvicorn)          │
│          port 8000                  │
│  - JWT auth (python-jose)           │
│  - Pydantic validation              │
│  - Prometheus metrics               │
└──────────────────┬──────────────────┘
                   │ asyncpg
┌──────────────────▼──────────────────┐
│         PostgreSQL 15               │
│         port 5432                   │
│  - Managed by Alembic migrations    │
└─────────────────────────────────────┘
```

---

## Two Setup Paths

| Path | Best for | Requirements |
|------|----------|--------------|
| **A — Docker Compose** (recommended) | Fastest start, no local PostgreSQL needed | Docker + Docker Compose |
| **B — Native / Local** | Direct debugging, IDE integration | Python 3.11 + PostgreSQL 15 |

---

## Prerequisites

### Python 3.11 (Path B — Native only)

**Windows**

1. Download the Python 3.11 installer from https://www.python.org/downloads/
2. Run the installer. On the first screen check **"Add Python to PATH"** before clicking Install Now.
3. Open a new Command Prompt or PowerShell and verify:
   ```
   python --version
   ```
   Expected output: `Python 3.11.x`

**macOS**

Option 1 — Homebrew (recommended):
```bash
brew install python@3.11
echo 'export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
python3.11 --version
```

Option 2 — pyenv:
```bash
brew install pyenv
pyenv install 3.11
pyenv local 3.11
python --version
```

**Linux (Debian/Ubuntu)**
```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev
python3.11 --version
```

**Linux (Fedora)**
```bash
sudo dnf install -y python3.11
python3.11 --version
```

**Linux (Arch)**
```bash
sudo pacman -S python
python --version
```

---

### PostgreSQL 15 (Path B — Native only)

**Windows**

1. Download the Windows installer from https://www.postgresql.org/download/windows/
2. Run the installer. Note the password you set for the `postgres` superuser.
3. Ensure the PostgreSQL `bin` directory is on your PATH (the installer offers this).
4. Verify: open a new terminal and run `psql --version`

**macOS**
```bash
brew install postgresql@15
brew services start postgresql@15
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
psql --version
```

**Linux (Debian/Ubuntu)**
```bash
sudo apt update
sudo apt install -y postgresql-15 postgresql-client-15
sudo systemctl start postgresql
sudo systemctl enable postgresql
psql --version
```

**Linux (Fedora)**
```bash
sudo dnf install -y postgresql-server postgresql
sudo postgresql-setup --initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

---

### Docker & Docker Compose (Path A — Docker only)

See the [global prerequisites](./README.md#global-prerequisites) in the index guide.

---

## Step 1 — Clone the Repository

This step is the same on all operating systems.

```bash
git clone https://github.com/samueljackson-collab/portfolio-project.git
cd portfolio-project/backend
```

---

## Step 2 — Configure Environment Variables

The application reads configuration from a `.env` file in the `backend/` directory. A template is provided at `backend/.env.example`.

### Copy the template

**Windows (Command Prompt)**
```cmd
copy .env.example .env
```

**Windows (PowerShell)**
```powershell
Copy-Item .env.example .env
```

**macOS / Linux**
```bash
cp .env.example .env
```

### Edit the `.env` file

Open `.env` in any text editor and fill in the required values:

```dotenv
# Required — choose a strong password
POSTGRES_USER=portfolio_user
POSTGRES_PASSWORD=change-me-to-a-strong-password
POSTGRES_DB=portfolio_db

# Required — must match POSTGRES_* above
# For Docker Compose the host is "db"; for Native use "localhost"
DATABASE_URL=postgresql+asyncpg://portfolio_user:change-me-to-a-strong-password@localhost:5432/portfolio_db

# Required — generate a random 32-character hex string
# Run: openssl rand -hex 32
SECRET_KEY=replace-with-at-least-32-random-characters-here
```

> **Generating a SECRET_KEY**
>
> **macOS / Linux:** `openssl rand -hex 32`
>
> **Windows PowerShell:** `[System.Web.Security.Membership]::GeneratePassword(32, 4)`
>
> Copy the output and paste it as the value of `SECRET_KEY`.

The remaining variables in `.env.example` (APP_NAME, DEBUG, LOG_LEVEL, etc.) have sensible defaults and do not need to be changed for local development.

---

## Path A — Docker Compose Setup (Recommended)

Docker Compose starts both PostgreSQL and the FastAPI application in isolated containers, with no need to install or configure PostgreSQL locally.

### Step 3A — Start the Stack

```bash
docker-compose up --build
```

What this does:
1. Builds the FastAPI image from `backend/Dockerfile` using Python 3.11-slim.
2. Pulls the official `postgres:15-alpine` image.
3. Starts PostgreSQL, waits for its health check to pass, then starts the API.
4. Mounts `./app` into the container so code changes reload automatically (`--reload`).

> **Note:** The first build downloads dependencies and may take 2-3 minutes. Subsequent starts are fast.

### Step 4A — Run Database Migrations

Open a second terminal window in the same `backend/` directory and run:

```bash
docker-compose exec api alembic upgrade head
```

What this does: Alembic connects to PostgreSQL inside the container and applies all migration scripts in `backend/alembic/versions/`, creating the required tables.

### Step 5A — Verify the Application is Running

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

Open your browser and navigate to `http://localhost:8000/docs` to see the interactive Swagger UI.

### Stopping the Stack

```bash
docker-compose down
```

To also delete the database volume (full reset):
```bash
docker-compose down -v
```

---

## Path B — Native Local Setup

### Step 3B — Create a Python Virtual Environment

A virtual environment keeps the project's dependencies isolated from your system Python.

**Windows (Command Prompt)**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell)**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> If you receive an execution policy error in PowerShell, run:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**macOS / Linux**
```bash
python3.11 -m venv venv
source venv/bin/activate
```

Your terminal prompt will now show `(venv)` to confirm the environment is active.

### Step 4B — Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs all packages listed in `backend/requirements.txt`, including FastAPI, Uvicorn, SQLAlchemy, asyncpg, Alembic, pytest, and linting tools.

### Step 5B — Create the PostgreSQL Database and User

**Windows**

Open the PostgreSQL SQL Shell (`psql`) from the Start Menu, connect as `postgres`, then run:

```sql
CREATE USER portfolio_user WITH PASSWORD 'change-me-to-a-strong-password';
CREATE DATABASE portfolio_db OWNER portfolio_user;
GRANT ALL PRIVILEGES ON DATABASE portfolio_db TO portfolio_user;
\q
```

**macOS / Linux**

```bash
sudo -u postgres psql <<EOF
CREATE USER portfolio_user WITH PASSWORD 'change-me-to-a-strong-password';
CREATE DATABASE portfolio_db OWNER portfolio_user;
GRANT ALL PRIVILEGES ON DATABASE portfolio_db TO portfolio_user;
EOF
```

> Use the same password you put in `.env` for `POSTGRES_PASSWORD`.

Also update `DATABASE_URL` in your `.env` to use `localhost`:
```dotenv
DATABASE_URL=postgresql+asyncpg://portfolio_user:change-me-to-a-strong-password@localhost:5432/portfolio_db
```

### Step 6B — Run Database Migrations

With the virtual environment active:

```bash
alembic upgrade head
```

Alembic reads `backend/alembic.ini`, connects to your local PostgreSQL instance, and creates all required tables.

### Step 7B — Start the Development Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete.
```

The `--reload` flag means the server automatically restarts whenever you save a Python file.

---

## Step 6 — Verify the Application

Once the server is running (via either path), confirm everything is working:

1. **Health check** — visit `http://localhost:8000/health` or run:
   ```bash
   curl http://localhost:8000/health
   ```
   Expected: `{"status": "healthy"}`

2. **Swagger UI** — open `http://localhost:8000/docs` in your browser. You should see the full interactive API documentation.

3. **ReDoc** — open `http://localhost:8000/redoc` for the alternative documentation view.

---

## Step 7 — Run the Test Suite

The test suite uses `pytest` with `pytest-asyncio` for async test support. Configuration lives in `backend/pytest.ini`.

> Tests require a running PostgreSQL database. Use Path A (Docker) or ensure your local PostgreSQL is running.

### Running All Tests

With the virtual environment active (Path B) or after `docker-compose up` (Path A):

**Path A (Docker)**
```bash
docker-compose exec api pytest
```

**Path B (Native)**
```bash
pytest
```

### Running with Coverage

```bash
pytest --cov=app --cov-report=term-missing
```

### Running a Specific Test File

```bash
pytest tests/test_auth.py -v
```

### Running with Verbose Output

```bash
pytest -v
```

Expected final line: `X passed in Y.YYs`

---

## Step 8 — Code Quality Checks

Before committing or deploying, run the linters:

```bash
# Format check (Black)
black --check app/

# Linting (Ruff)
ruff check app/

# Type checking (MyPy)
mypy app/
```

Auto-fix formatting:
```bash
black app/
ruff check --fix app/
```

---

## Common Issues & Fixes

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `ModuleNotFoundError: No module named 'fastapi'` | Virtual env not activated | Run `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows) |
| `connection refused` on port 5432 | PostgreSQL not running | `sudo systemctl start postgresql` or `brew services start postgresql@15` |
| `POSTGRES_PASSWORD is required` from Docker | `.env` file missing or empty password | Ensure `.env` exists and `POSTGRES_PASSWORD` is set to a non-empty value |
| `SECRET_KEY is required` from Docker | `.env` file missing SECRET_KEY | Generate one: `openssl rand -hex 32` and add to `.env` |
| `alembic: command not found` | Virtual env not active | Activate the venv first; alembic is installed there |
| Port 8000 already in use | Another process is on 8000 | `lsof -i :8000` (macOS/Linux) or `netstat -ano \| findstr 8000` (Windows) to find the PID, then kill it |
| `asyncpg.exceptions.InvalidPasswordError` | Wrong password in DATABASE_URL | Ensure `POSTGRES_PASSWORD` in `.env` matches the DB user password |
| Docker build fails on `pip install` | Network issue or cache stale | `docker-compose build --no-cache` |
| PowerShell activation error | Execution policy restricted | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `POSTGRES_USER` | Yes | `portfolio_user` | PostgreSQL username |
| `POSTGRES_PASSWORD` | Yes | — | PostgreSQL password |
| `POSTGRES_DB` | Yes | `portfolio_db` | PostgreSQL database name |
| `DATABASE_URL` | Yes | — | Full async DB connection string |
| `SECRET_KEY` | Yes | — | JWT signing key (min 32 chars) |
| `APP_NAME` | No | `Portfolio API` | Application display name |
| `DEBUG` | No | `false` | Enable debug mode |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | JWT token lifetime |
| `ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `CORS_ORIGINS` | No | `http://localhost:3000,http://localhost:5173` | Allowed CORS origins |
| `MAX_PHOTO_SIZE_MB` | No | `20` | Max photo upload size |

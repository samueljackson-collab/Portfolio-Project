# Bug Hunter

A cross-platform static security vulnerability scanner with a real-time web UI.
Supports Android, iOS, Windows, macOS, and Web codebases with 125 built-in rules.

## Features

- 125 security rules across 5 platforms (25 per platform)
- Two-pass analysis with cross-rule context re-inspection
- Real-time finding streaming via Server-Sent Events
- HTML and PDF report export
- Risk scoring per scan
- Docker-based deployment

## Quick Start

### Docker (recommended)

```bash
cd bug-hunter
cp backend/.env.example backend/.env   # edit as needed
docker-compose up --build
```

Open http://localhost:5173 in your browser.

### Local development

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
# API available at http://localhost:8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
# UI available at http://localhost:5173
```

## Environment Variables

All variables are optional for local development. Copy `.env.example` as a starting point.

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | SQLite `bughunter.db` | Connection string. Use `postgresql+asyncpg://…` for production. |
| `API_KEY` | _(empty — auth off)_ | When set, all non-health endpoints require `X-API-Key: <value>` header. |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Comma-separated list of allowed origins. Use HTTPS in production. |
| `MAX_CODE_SIZE_BYTES` | `1048576` (1 MB) | Maximum `code_content` payload size. |
| `SCAN_TIMEOUT_SECONDS` | `300` | Seconds before a scan is marked `failed`. |
| `DEBUG` | `false` | Enables `/docs`, `/redoc`, and DEBUG logging. |

## API Endpoints

All endpoints (except `/health`) respect the `X-API-Key` header when `API_KEY` is configured.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness + DB readiness check |
| `POST` | `/api/scans` | Submit code for scanning (rate limited: 5/min per IP) |
| `GET` | `/api/scans` | List all scan sessions |
| `GET` | `/api/scans/{id}` | Get scan details with findings |
| `GET` | `/api/scans/{id}/events` | SSE stream of live findings |
| `GET` | `/api/reports` | List generated reports |
| `GET` | `/api/reports/{id}` | Get report metadata |
| `GET` | `/api/reports/{id}/html` | Download HTML report |
| `GET` | `/api/reports/{id}/pdf` | Download PDF report |

### Example: submit a scan

```bash
curl -X POST http://localhost:8000/api/scans \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key-here" \
  -d '{
    "platform": "android",
    "filename": "MainActivity.java",
    "code_content": "String q = \"SELECT * FROM users WHERE id = \" + userId;"
  }'
```

## Running Tests

```bash
cd backend
pip install pytest pytest-asyncio httpx
pytest tests/ -v
```

## Production Checklist

- Set a strong `API_KEY` environment variable
- Use PostgreSQL instead of SQLite (`DATABASE_URL=postgresql+asyncpg://…`)
- Set `CORS_ORIGINS` to your actual HTTPS domain
- Set `DEBUG=false`
- Place behind a TLS-terminating reverse proxy (nginx / Caddy / cloud LB)
- Review and tune `MAX_CODE_SIZE_BYTES` and `SCAN_TIMEOUT_SECONDS`

## Supported Platforms

| Platform | Language(s) | Rule Count |
|----------|-------------|------------|
| Android | Java, Kotlin | 25 |
| iOS | Swift, Objective-C | 25 |
| Windows | C#, C++ | 25 |
| macOS | Swift, Objective-C | 25 |
| Web | JavaScript, TypeScript, HTML, PHP | 25 |

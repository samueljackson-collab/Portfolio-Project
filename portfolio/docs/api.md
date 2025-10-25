# API Reference

## Base URL
```
http://localhost:8000
```

## Health Check
- **Endpoint:** `GET /health`
- **Response:** `{ "status": "ok" }`

## List Projects
- **Endpoint:** `GET /api/projects`
- **Description:** Returns curated portfolio entries.
- **Response:**
```json
[
  {
    "id": "proj-001",
    "name": "Developer Portfolio",
    "description": "Monorepo showcasing engineering accomplishments",
    "tags": ["fastapi", "react", "devops"]
  }
]
```

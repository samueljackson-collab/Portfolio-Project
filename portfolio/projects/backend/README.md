# Portfolio Backend

## Quickstart
```bash
python -m pip install -r ../../requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

```powershell
python -m pip install -r ..\..\requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Available Endpoints
- `GET /health`
- `GET /api/projects`

## Testing
```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

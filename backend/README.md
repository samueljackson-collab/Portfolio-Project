# Portfolio Backend API

A modern, production-ready REST API built with FastAPI, featuring JWT authentication, async database operations, and comprehensive testing.

## Features

- 🚀 **FastAPI Framework** - High-performance async web framework
- 🔐 **JWT Authentication** - Secure token-based authentication
- 📊 **PostgreSQL Database** - Async SQLAlchemy with connection pooling
- ✅ **Comprehensive Testing** - Unit and integration tests with pytest
- 🐳 **Docker Support** - Containerized deployment with Docker Compose
- 📝 **Auto-generated Documentation** - Interactive API docs with Swagger UI
- 🔄 **Database Migrations** - Alembic for schema versioning
- 🛡️ **Security Best Practices** - Password hashing, CORS, input validation

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker and Docker Compose (optional)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and secret key
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the development server**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at http://localhost:8000

7. **Access API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Docker Deployment

1. **Start services**
   ```bash
   docker-compose up -d
   ```

2. **Check logs**
   ```bash
   docker-compose logs -f api
   ```

3. **Stop services**
   ```bash
   docker-compose down
   ```

## API Endpoints

### Health Check
- `GET /health` - Service health status
- `GET /health/liveness` - Kubernetes liveness probe
- `GET /health/readiness` - Kubernetes readiness probe

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info (requires auth)

### Content Management
- `GET /content` - List all content (with pagination)
- `GET /content/{id}` - Get single content item
- `POST /content` - Create new content (requires auth)
- `PUT /content/{id}` - Update content (owner only)
- `DELETE /content/{id}` - Delete content (owner only)

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication utilities
│   ├── dependencies.py      # FastAPI dependencies
│   └── routers/
│       ├── __init__.py
│       ├── health.py        # Health check endpoints
│       ├── auth.py          # Authentication endpoints
│       └── content.py       # Content CRUD endpoints
├── alembic/                 # Database migrations
├── tests/                   # Test suite
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker services
└── README.md               # This file
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run tests matching pattern
pytest -k "test_login"
```

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | Portfolio API |
| `DEBUG` | Debug mode | False |
| `DATABASE_URL` | PostgreSQL connection URL | Required |
| `SECRET_KEY` | JWT secret key (min 32 chars) | Required |
| `CORS_ORIGINS` | Allowed CORS origins | ["http://localhost:3000"] |
| `LOG_LEVEL` | Logging level | INFO |

## Security Considerations

- Passwords are hashed using bcrypt with 12 rounds
- JWT tokens expire after 30 minutes (configurable)
- CORS is configured to only allow specified origins
- All input is validated using Pydantic schemas
- Database queries use parameterized statements (SQL injection prevention)
- Rate limiting should be implemented in production (not included)

## Development Guidelines

### Code Quality

```bash
# Format code with black
black app tests

# Lint with ruff
ruff check app tests

# Type checking with mypy
mypy app
```

### Adding New Endpoints

1. Define Pydantic schemas in `app/schemas.py`
2. Create or update router in `app/routers/`
3. Register router in `app/main.py`
4. Write tests in `tests/`
5. Update this README

## Production Deployment

### Environment Setup

1. Set `DEBUG=False` in production
2. Use a strong `SECRET_KEY` (32+ random characters)
3. Configure proper `DATABASE_URL` with connection pooling
4. Set up HTTPS/TLS termination
5. Implement rate limiting (e.g., with nginx)
6. Configure proper logging and monitoring
7. Set up database backups

### Scaling

- Use multiple uvicorn workers: `uvicorn app.main:app --workers 4`
- Deploy behind a load balancer (nginx, traefik)
- Use database connection pooling
- Implement caching (Redis)
- Monitor with Prometheus/Grafana

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps

# Check database logs
docker-compose logs db

# Test connection
psql -h localhost -U portfolio_user -d portfolio_db
```

### Import Errors

```bash
# Ensure virtual environment is activated
which python  # Should point to venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

### Migration Issues

```bash
# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
alembic upgrade head
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Ensure tests pass: `pytest`
5. Format code: `black app tests`
6. Submit pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Email: your.email@example.com

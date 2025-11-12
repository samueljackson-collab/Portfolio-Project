# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- FastAPI application with REST API endpoints
- SQLite database with SQLAlchemy ORM
- CRUD operations for items resource
- Health check endpoints (/health, /ready)
- Docker containerization with multi-stage build
- Docker Compose configuration
- pytest test suite with >90% coverage
- Structured logging
- API documentation (Swagger/OpenAPI)
- Environment-based configuration

### Security
- Input validation with Pydantic
- SQL injection prevention via ORM
- Non-root container user
- Environment variable configuration

## [1.0.0] - 2024-11-07

### Added
- Initial project structure
- FastAPI application

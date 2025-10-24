# Testing Strategy

This repository enforces a layered testing approach designed to provide fast feedback and high confidence in production readiness.

## Pyramid Overview

1. **Unit Tests (70%)**
   - Backend: `pytest` suites cover authentication, content workflows, and data access.
   - Frontend: `vitest` suites ensure components render, route, and integrate with API clients correctly.
2. **Integration Tests (20%)**
   - Backend API workflows executed through HTTP clients against ephemeral databases.
   - Frontend component integration verifying context/state management.
3. **End-to-End Tests (10%)**
   - Postman collection executes full user journeys.
   - k6 load tests measure performance under sustained and burst load.
   - OWASP ZAP scans surface security regressions.

## Running Tests

```bash
# backend unit + integration
make backend

# frontend unit tests
make frontend

# k6 scenarios
cd e2e-tests && ./tests/test_load.sh

# postman collection (using newman)
newman run e2e-tests/postman/collection.json
```

## Coverage Goals

- Backend: >= 80% line coverage, >= 90% branch coverage for auth flows.
- Frontend: >= 75% line coverage, focus on auth and dashboard components.
- Infrastructure and monitoring validated through automated Terraform plan checks and integration smoke tests.

## Continuous Integration

GitHub Actions pipelines (`.github/workflows/ci.yml`) execute unit tests, integration tests, and linting on every pull request. Scheduled security scans run nightly to ensure dependencies remain safe.


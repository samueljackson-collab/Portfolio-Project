# Testing Standards

**Version:** 2.1 | **Owner:** Engineering | **Last Updated:** 2026-01-10

---

## 1. Coverage Requirements

| Project Type | Unit Coverage | Integration Coverage | E2E Coverage |
|-------------|--------------|---------------------|-------------|
| New service | ≥ 80% | ≥ 60% | ≥ 40% |
| Existing service (additions) | Maintain existing + cover new code | — | — |
| Scripts / automation | ≥ 70% | — | — |
| Infrastructure modules | Structural validation | Plan output tests | — |

Coverage is measured on **line + branch** coverage (not just line).

---

## 2. Test Pyramid

```
        /\
       /E2E\         Few — high value flows only
      /------\
     /Integr. \      Medium — service boundaries, DB, external APIs
    /----------\
   /   Unit     \    Many — fast, isolated, deterministic
  /--------------\
```

### Test Naming Convention

```python
# Pattern: test_<what>_<condition>_<expected_outcome>
def test_create_user_with_duplicate_email_raises_conflict():
    ...

def test_process_payment_when_card_declined_returns_payment_failed():
    ...
```

---

## 3. Unit Tests

### Requirements

- Each test is independent — no shared mutable state between tests
- Tests must not make real network calls, database queries, or file I/O
- Use mocking/patching for all external dependencies
- Each test covers exactly one behaviour

```python
# GOOD — isolated, single responsibility, descriptive name
from unittest.mock import patch, MagicMock
import pytest

def test_send_notification_calls_email_service_with_correct_args():
    with patch("app.notifications.email_client") as mock_client:
        send_notification(user_id=42, message="Welcome!")
        mock_client.send.assert_called_once_with(
            to="user42@example.com",
            subject="Notification",
            body="Welcome!"
        )
```

---

## 4. Integration Tests

- Run against a real (Docker-based) database, queue, or cache
- Use `pytest-docker` or Docker Compose to spin up dependencies
- Clean up test data after each test (use transactions that rollback, or fixture teardown)
- Never run integration tests against production systems

```python
# Integration test with real DB (pytest fixture)
@pytest.fixture(scope="function")
def db_session(postgres_container):
    """Provide a clean DB session, rolling back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()
```

---

## 5. End-to-End Tests

- Cover the 5 most critical user journeys (as defined by product owner)
- Use Page Object Model (POM) for UI tests
- Run headless in CI, non-headless in local development
- Max 10-minute runtime for full E2E suite in CI

---

## 6. Testing in CI

All tests run on every PR. The pipeline is not optional:

```yaml
# Required CI stages (all must pass to merge)
test:
  stages:
    - unit-tests          # fast, < 2 min
    - integration-tests   # < 5 min
    - e2e-tests           # < 10 min (optional on draft PRs)
    - coverage-check      # fail if coverage drops below threshold
```

### Coverage Gate Configuration

```ini
# pytest.ini / setup.cfg
[tool:pytest]
addopts = --cov=src --cov-report=term-missing --cov-fail-under=80
```

---

## 7. Test Data Management

- **Unit tests:** Inline fixtures or factory functions — never shared files
- **Integration tests:** Seed scripts run before test suite; cleaned up after
- **E2E tests:** Dedicated test users and test tenants in staging environment
- **Production data:** Never used in tests. No exceptions.

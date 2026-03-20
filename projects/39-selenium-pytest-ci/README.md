# Selenium + PyTest CI — Portfolio Project 39

End-to-end UI test suite for a Flask web application, structured using the **Page Object Model (POM)** pattern and wired into a **GitHub Actions CI pipeline**. Tests run against a live Flask server (or the Flask test client for CI speed) and produce coverage reports automatically on every push.

---

## Project Overview

This project demonstrates professional-grade test automation practices:

- **Page Object Model** — UI selectors and interactions are encapsulated in reusable page classes
- **pytest fixtures** — session-scoped live server and per-test WebDriver/client setup
- **CI/CD integration** — GitHub Actions runs the full suite on every push to `main` or `claude/*`
- **Coverage reporting** — `pytest-cov` tracks line coverage and reports missed lines
- **Flask test client fallback** — tests run without a real browser in headless CI environments

---

## CI Pipeline Architecture

```mermaid
flowchart LR
    A[Code Push] --> B[GitHub Actions Trigger]
    B --> C[actions/checkout@v4]
    C --> D[actions/setup-python@v4\nPython 3.11]
    D --> E[pip install\nflask pytest pytest-cov]
    E --> F[python -m pytest tests/\n--cov=app --cov-report=term-missing]
    F --> G{All Tests Pass?}
    G -->|Yes| H[Coverage Report\n97% coverage]
    G -->|No| I[Build Fails\nAnnotated output]
```

---

## Test Architecture — Page Object Model

The POM pattern separates **what** to test from **how** to interact with the UI.

```
tests/
├── conftest.py              # Shared fixtures (live_server, driver)
├── pages/
│   ├── login_page.py        # LoginPage POM class
│   └── dashboard_page.py    # DashboardPage POM class
├── test_login.py            # Login + session + navigation tests
└── test_navigation.py       # Extended navigation & UI structure tests
```

### LoginPage POM Example

```python
class LoginPage:
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON   = (By.ID, "login-btn")

    def login(self, username, password):
        self.driver.find_element(*self.USERNAME_INPUT).send_keys(username)
        self.driver.find_element(*self.PASSWORD_INPUT).send_keys(password)
        self.driver.find_element(*self.LOGIN_BUTTON).click()
        return self
```

Tests call `page.login("admin", "Admin@1234")` — if the HTML changes, only the POM needs updating, not every test.

---

## Quick Start

```bash
# Clone and navigate
cd projects/39-selenium-pytest-ci

# Install dependencies
pip install -r requirements.txt

# Run all tests with coverage
python -m pytest tests/ -v --cov=app --cov-report=term-missing

# Run only login tests
python -m pytest tests/test_login.py -v

# Run the Flask app manually
python app/app.py
# Visit http://localhost:5002
```

**Test credentials:**
| Username | Password    |
|----------|-------------|
| admin    | Admin@1234  |
| demo     | Demo@5678   |
| test     | Test@9999   |

---

## CI/CD Pipeline

The workflow file at `.github/workflows/selenium-ci.yml` runs on every push:

```yaml
name: Selenium UI Tests
on:
  push:
    branches: [main, "claude/*"]
  pull_request:
    branches: [main]
jobs:
  ui-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          pip install flask pytest pytest-cov
          cd projects/39-selenium-pytest-ci
          pip install -r requirements.txt
      - name: Run UI tests
        run: |
          cd projects/39-selenium-pytest-ci
          python -m pytest tests/ -v --tb=short --cov=app --cov-report=term-missing
```

---

## Test Categories

| Category | File | Tests | What It Covers |
|---|---|---|---|
| Login Functionality | test_login.py | 5 | Page load, valid/invalid creds, empty form |
| Session Management | test_login.py | 3 | Auth guards on dashboard/profile, logout |
| Navigation | test_login.py | 2 | Root redirect for anon/authenticated users |
| UI Structure | test_navigation.py | 7 | Form fields, nav links, welcome msg, multi-user |
| **Total** | | **17** | **17 passed, 0 failed** |

---

## Live Demo

### Test Run Output

```
============================= test session starts ==============================
platform linux -- Python 3.11.14, pytest-9.0.2
collected 17 items

tests/test_login.py::TestLoginFunctionality::test_login_page_loads PASSED [  5%]
tests/test_login.py::TestLoginFunctionality::test_valid_login_redirects_to_dashboard PASSED [ 11%]
...
tests/test_navigation.py::test_welcome_message_contains_username PASSED  [100%]

============================== 17 passed in 0.26s ==============================
```

### Coverage Report

```
Name              Stmts   Miss  Cover   Missing
-----------------------------------------------
app/__init__.py       0      0   100%
app/app.py           38      1    97%   78
-----------------------------------------------
TOTAL                38      1    97%
```

Full output in [`demo_output/test_run.txt`](demo_output/test_run.txt) and [`demo_output/coverage_report.txt`](demo_output/coverage_report.txt).

---

## What This Demonstrates

- **Page Object Model** — maintainable, DRY test architecture used in enterprise QA
- **pytest fixtures** — session/function scoping, dependency injection via `conftest.py`
- **Flask test client** — fast, reliable in-process testing without a real browser needed in CI
- **GitHub Actions CI** — automated test execution and coverage reporting on every commit
- **97% code coverage** — only the `if __name__ == "__main__"` guard is untested (expected)
- **Real Selenium readiness** — POM classes use `selenium.webdriver` and are drop-in ready for Chrome/Firefox with WebDriver installed

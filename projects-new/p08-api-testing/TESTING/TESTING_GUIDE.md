# API Testing Guide

Comprehensive guide for running and extending API tests for P08 Backend API Testing project.

## Table of Contents

1. [Overview](#overview)
2. [Test Types](#test-types)
3. [Running Tests](#running-tests)
4. [Writing Tests](#writing-tests)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## Overview

This project provides two complementary testing approaches:

1. **Postman Collections** - Visual, interactive testing via Newman automation
2. **pytest Suite** - Programmatic, detailed functional testing

Both approaches can run independently or together as part of CI/CD pipelines.

## Test Types

### 1. Unit Tests (Postman Pre/Post request scripts)

Test individual request logic without full API calls:
- Token extraction from responses
- Environment variable population
- Response transformation

Example in Postman:
```javascript
pm.test('Extract token', function() {
    var jsonData = pm.response.json();
    pm.environment.set('authToken', jsonData.access_token);
});
```

### 2. Integration Tests (CRUD Operations)

Test complete workflows across multiple endpoints:
- Create an order (POST)
- Retrieve the order (GET)
- Update the order (PUT)
- Delete the order (DELETE)

Example pytest:
```python
def test_create_order_success(self, api_client, sample_order):
    response = api_client.post("/orders", json=sample_order)
    assert response.status_code == 201
```

### 3. Contract Tests (Schema Validation)

Validate API responses match expected schema:
- Required fields present
- Data types correct
- Response structure valid

Example:
```python
def test_order_response_structure(self, api_client, sample_order):
    response = api_client.post("/orders", json=sample_order)
    data = response.json()
    required_fields = ["id", "customer_id", "status", "items"]
    for field in required_fields:
        assert field in data
```

### 4. Error Condition Tests

Validate proper handling of invalid scenarios:
- Missing resources (404)
- Invalid payloads (400)
- Unauthorized access (401)
- Server errors (5xx)

Example:
```python
def test_get_nonexistent_order(self, api_client):
    response = api_client.get("/orders/invalid-id")
    assert response.status_code == 404
```

### 5. Performance Tests

Measure and validate response times:
- Baseline performance
- Regression detection
- SLA compliance

Example:
```python
def test_list_orders_response_time(self, api_client):
    response = api_client.get("/orders", params={"page": 1, "pageSize": 5})
    response_time_ms = response.elapsed.total_seconds() * 1000
    assert response_time_ms < 1000
```

### 6. Security Tests

Validate authentication and authorization:
- Token validation
- Authorization checks
- Secure header validation

Example:
```python
def test_request_without_auth_token(self, client, base_url):
    response = client.get(f"{base_url}/orders", headers={"Authorization": ""})
    assert response.status_code == 401
```

## Running Tests

### Prerequisites Setup

```bash
# 1. Navigate to project directory
cd projects-new/p08-api-testing

# 2. Copy environment template
cp .env.example .env

# 3. Update .env with your settings
nano .env

# 4. Ensure API is running
# docker-compose -f docker/compose.api.yaml up -d
# OR
# npm start (if local dev server)
# OR
# kubectl port-forward svc/api 8080:8080 (if in K8s)
```

### Running Newman (Postman Collections)

**Basic execution:**
```bash
./newman-run.sh -e local -c core
```

**With options:**
```bash
# Verbose mode
./newman-run.sh -e local -c core -v

# No bail (continue on failures)
./newman-run.sh -e local -c core --no-bail

# Custom timeout
./newman-run.sh -e local -c core --timeout 5000

# Generate reports
./newman-run.sh -e local -c core --reporters json,cli,html
```

**View results:**
```bash
# Check console output
cat out/newman-cli-report-*.txt

# Parse JSON report
python consumer/report.py --input out/newman-report-*.json

# Open HTML report
open out/newman-report-*.html
```

### Running pytest Tests

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run all tests:**
```bash
pytest tests/ -v
```

**Run specific test file:**
```bash
pytest tests/test_api_orders.py -v
pytest tests/test_api_authentication.py -v
```

**Run specific test class:**
```bash
pytest tests/test_api_orders.py::TestOrdersCRUD -v
pytest tests/test_api_authentication.py::TestAuthentication -v
```

**Run specific test:**
```bash
pytest tests/test_api_orders.py::TestOrdersCRUD::test_create_order_success -v
```

**Run with markers:**
```bash
# Integration tests
pytest -m "integration" tests/ -v

# Smoke tests (subset of critical tests)
pytest -m "smoke" tests/ -v

# Skip slow tests
pytest -m "not slow" tests/ -v

# Auth tests only
pytest -m "auth" tests/ -v
```

**Generate coverage report:**
```bash
pytest tests/ --cov=tests --cov-report=html
open htmlcov/index.html
```

**Generate JUnit XML report:**
```bash
pytest tests/ --junit-xml=out/pytest-report.xml
```

**Run with filtering:**
```bash
# Tests matching pattern
pytest tests/ -k "test_create" -v

# All except slow
pytest tests/ -m "not slow" -v

# Specific markers
pytest tests/ -m "integration and auth" -v
```

### Running Both Test Suites

**Sequential execution:**
```bash
./newman-run.sh -e local -c core && pytest tests/ -v
```

**Parallel execution (requires multiple terminals):**
```bash
# Terminal 1
./newman-run.sh -e local -c core

# Terminal 2
pytest tests/ -v
```

**Combined CI command:**
```bash
#!/bin/bash
set -e

echo "Running Newman tests..."
./newman-run.sh -e local -c core --reporters json,cli

echo "Running pytest tests..."
pytest tests/ --junit-xml=out/pytest-report.xml --cov=tests --cov-report=html

echo "All tests passed!"
```

## Writing Tests

### Structure of a Test

```python
class TestOrdersCRUD:
    """Test suite for Orders CRUD operations"""

    @pytest.fixture
    def api_client(self, base_url, auth_token):
        """Setup test dependencies"""
        return APIClient(base_url, auth_token)

    def test_create_order_success(self, api_client, sample_order):
        """
        Test Case: Create order with valid payload
        Expected: 201 Created with order ID and pending status
        """
        # 1. Arrange - Setup test data
        expected_customer = sample_order["customer_id"]

        # 2. Act - Execute API call
        response = api_client.post("/orders", json=sample_order)

        # 3. Assert - Validate results
        assert response.status_code == 201
        data = response.json()
        assert data["customer_id"] == expected_customer
        assert data["status"] == "pending"
```

### Test Organization

```
tests/
├── test_api_orders.py          # Orders CRUD tests
├── test_api_authentication.py  # Auth and authorization tests
├── test_api_products.py        # Products endpoint tests (future)
├── test_api_performance.py     # Performance baseline tests (future)
├── conftest.py                 # Fixtures and configuration
├── pytest.ini                  # Pytest settings
└── __init__.py                 # Package marker
```

### Adding a New Test

1. **Identify test category** (CRUD, auth, error, validation, performance)

2. **Add to appropriate test file** or create new one:
   ```python
   # tests/test_api_<resource>.py
   class Test<Resource><Category>:
       """Test suite for <Resource> <Category> tests"""

       @pytest.fixture
       def api_client(self, base_url, auth_token):
           """Create API client"""
           return APIClient(base_url, auth_token)

       def test_<scenario>_<expected_result>(self, api_client):
           """Test description"""
           # Test implementation
           pass
   ```

3. **Use descriptive names**:
   ```python
   # Good
   def test_create_order_with_multiple_items(self, api_client):
       pass

   # Bad
   def test_create(self, api_client):
       pass
   ```

4. **Follow AAA pattern** (Arrange, Act, Assert):
   ```python
   def test_update_order_status(self, api_client, sample_order):
       # Arrange
       create_resp = api_client.post("/orders", json=sample_order)
       order_id = create_resp.json()["id"]

       # Act
       update_resp = api_client.put(f"/orders/{order_id}",
                                    json={"status": "confirmed"})

       # Assert
       assert update_resp.status_code == 200
       assert update_resp.json()["status"] == "confirmed"
   ```

5. **Add test docstring**:
   ```python
   def test_something(self, api_client):
       """
       Test Case: Create order with valid payload
       Prerequisites: API is running, auth token is valid
       Expected: 201 Created response with order details
       """
       # Test code
   ```

6. **Run new test**:
   ```bash
   pytest tests/test_api_orders.py::TestOrdersCRUD::test_update_order_status -v
   ```

### Using Fixtures

**Built-in fixtures:**
```python
def test_example(self, base_url, auth_token, api_client, http_client):
    """Use provided fixtures"""
    # base_url: API base URL string
    # auth_token: Valid authentication token
    # api_client: Authenticated APIClient instance
    # http_client: requests.Session instance
    pass
```

**Factory fixtures:**
```python
def test_multiple_orders(self, api_client, order_factory):
    """Create multiple test orders"""
    order1 = order_factory(customer_id="CUST001", num_items=1)
    order2 = order_factory(customer_id="CUST002", num_items=3)

    resp1 = api_client.post("/orders", json=order1)
    resp2 = api_client.post("/orders", json=order2)

    assert resp1.status_code == 201
    assert resp2.status_code == 201
```

**Custom fixtures:**
```python
@pytest.fixture
def sample_order(self):
    """Provide sample order for tests"""
    return {
        "customer_id": "CUST001",
        "items": [{"product_id": "PROD001", "quantity": 2, "price": 29.99}],
        "shipping_address": {
            "street": "123 Main St",
            "city": "Springfield",
            "state": "IL",
            "zip": "62701"
        }
    }
```

## Best Practices

### 1. Test Naming
- Use descriptive names: `test_create_order_with_multiple_items_success`
- Include expected outcome: `test_invalid_payload_returns_400`
- Avoid generic names: `test_order`, `test_api`

### 2. Test Isolation
- Each test should be independent
- Use fixtures to setup/teardown data
- Clean up test data after test completion

```python
def test_create_and_delete_order(self, api_client, sample_order):
    # Create
    create_resp = api_client.post("/orders", json=sample_order)
    order_id = create_resp.json()["id"]

    # Verify created
    get_resp = api_client.get(f"/orders/{order_id}")
    assert get_resp.status_code == 200

    # Cleanup - delete
    delete_resp = api_client.delete(f"/orders/{order_id}")
    assert delete_resp.status_code in [200, 204]

    # Verify deleted
    final_resp = api_client.get(f"/orders/{order_id}")
    assert final_resp.status_code == 404
```

### 3. Assertion Best Practices
- One logical assertion per test (but multiple related checks OK)
- Use meaningful assertion messages

```python
# Good
assert response.status_code == 201, "Order creation should return 201"
assert data["status"] == "pending", "New orders should be pending"

# Bad
assert 201 == response.status_code
assert True == (data["status"] == "pending")
```

### 4. Error Handling
- Test both success and failure paths
- Validate error response structure

```python
# Success
def test_create_order_success(self, api_client, sample_order):
    response = api_client.post("/orders", json=sample_order)
    assert response.status_code == 201

# Failure
def test_create_order_missing_customer(self, api_client):
    invalid_order = {"items": []}
    response = api_client.post("/orders", json=invalid_order)
    assert response.status_code in [400, 422]
    assert "error" in response.json()
```

### 5. Performance Testing
- Set reasonable baselines
- Monitor for regressions

```python
def test_list_orders_performance(self, api_client):
    response = api_client.get("/orders", params={"page": 1, "pageSize": 5})

    response_time_ms = response.elapsed.total_seconds() * 1000
    baseline_ms = 1000  # 1 second baseline

    assert response_time_ms < baseline_ms, \
        f"Response took {response_time_ms}ms, baseline is {baseline_ms}ms"
```

### 6. Data Validation
- Validate data types
- Validate required fields
- Validate data ranges

```python
def test_order_data_types(self, api_client, sample_order):
    response = api_client.post("/orders", json=sample_order)
    data = response.json()

    assert isinstance(data["id"], str)
    assert isinstance(data["customer_id"], str)
    assert isinstance(data["items"], list)
    assert isinstance(data["total"], (int, float))
```

## Troubleshooting

### API Connection Issues

**Problem**: Cannot connect to API
```bash
# Check API is running
curl -i http://localhost:8080/health

# Check firewall
telnet localhost 8080

# Check environment variables
echo $API_BASE_URL

# Check .env file
cat .env
```

**Solution**:
- Start API server
- Update API_BASE_URL in .env
- Check firewall/network settings
- Verify port is correct

### Authentication Failures

**Problem**: Tests fail with 401 Unauthorized
```bash
# Verify credentials
echo $API_CLIENT_ID
echo $API_CLIENT_SECRET

# Test manually
curl -X POST http://localhost:8080/auth/token \
  -H "Content-Type: application/json" \
  -d '{"client_id":"demo","client_secret":"secret"}'

# Check token in pytest
pytest tests/ -v -s --log-cli-level=DEBUG
```

**Solution**:
- Verify credentials in .env
- Check API supports the auth scheme
- Check token is not expired
- Check API is returning tokens

### Test Failures

**Problem**: Tests fail inconsistently
```bash
# Run with verbose output
pytest tests/test_api_orders.py::TestOrdersCRUD::test_create_order_success -vv -s

# Enable debugging
DEBUG=true pytest tests/ -v

# Check logs
cat tests/pytest.log
```

**Solution**:
- Add logging to tests
- Check test data cleanup
- Verify API state
- Run tests in isolation
- Check for race conditions

### Fixture Issues

**Problem**: Fixture setup fails
```bash
# Check conftest.py is in tests directory
ls tests/conftest.py

# Test fixture directly
pytest tests/ --setup-show -v

# Debug fixture
pytest tests/ -v -s --capture=no
```

**Solution**:
- Verify conftest.py location
- Check fixture dependencies
- Check API is accessible from fixtures
- Add fixture logging

### Report Generation Issues

**Problem**: Reports not generated
```bash
# Check output directory exists
mkdir -p out

# Check permissions
ls -la out/

# Run with explicit output
pytest tests/ --junit-xml=out/pytest-report.xml

# Check reporter installed
pip show pytest-html
```

**Solution**:
- Create output directory
- Check file permissions
- Install required reporters
- Check disk space

## Advanced Topics

### Parametrized Tests

Test multiple scenarios with one test function:

```python
@pytest.mark.parametrize("status,expected", [
    ("pending", True),
    ("confirmed", True),
    ("shipped", True),
    ("invalid", False),
])
def test_order_status_validation(self, api_client, status, expected):
    order = {"customer_id": "CUST001", "status": status, "items": []}
    response = api_client.post("/orders", json=order)

    if expected:
        assert response.status_code == 201
    else:
        assert response.status_code in [400, 422]
```

### Mocking External Services

Mock external API calls for isolated testing:

```python
import responses

@responses.activate
def test_order_with_payment_mock(self, api_client, sample_order):
    # Mock payment API
    responses.add(
        responses.POST,
        "https://payment-api.example.com/charge",
        json={"transaction_id": "TXN123"},
        status=200,
    )

    # Test with mocked service
    response = api_client.post("/orders", json=sample_order)
    assert response.status_code == 201
```

### Load Testing

Basic load testing with pytest-benchmark:

```python
def test_list_orders_load(self, benchmark, api_client):
    """Benchmark list orders endpoint"""
    result = benchmark(
        api_client.get,
        "/orders",
        params={"page": 1, "pageSize": 5}
    )
    assert result.status_code == 200
```

### Continuous Integration

See main README.md for CI/CD integration examples.

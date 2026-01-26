# P08 Backend API Testing Pack

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


Complete artifact bundle for API regression and contract testing. Designed to align with the P06 prompt-pack layout and ready for Postman/Newman CI, Kubernetes smoke tests, and on-call operations.

## Overview

This project provides comprehensive API testing capabilities including:

- **Postman Collections**: Complete API test collections with CRUD operations, error handling, and data validation
- **Newman Automation**: Bash script for automated Postman collection execution
- **Python Test Suite**: pytest-based API tests for detailed functional and integration testing
- **Environment Configuration**: Multi-environment support with template files
- **Documentation**: Complete guides for running and extending tests

## Project Structure

```
p08-api-testing/
├── producer/                          # Postman collections and environments
│   ├── collections/
│   │   └── core.postman_collection.json    # Main API test collection
│   └── env/
│       └── local.postman_environment.json   # Local environment variables
├── tests/                             # Python pytest test suite
│   ├── test_api_orders.py              # Orders CRUD and error tests
│   ├── test_api_authentication.py      # Authentication tests
│   ├── conftest.py                     # Pytest configuration and fixtures
│   └── pytest.ini                      # Pytest settings
├── newman-run.sh                      # Automated Newman collection runner
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment configuration template
├── README.md                          # This file
└── docker/                            # Docker configuration
    └── compose.api.yaml               # Docker Compose for test environment
```

## Scope

- **CRUD Operations**: Create, Read, Update, Delete testing for API resources
- **Authentication**: Token generation, validation, and authorization testing
- **Error Handling**: 4xx and 5xx response handling and validation
- **Data Validation**: Response format, data type, and structure validation
- **Response Time**: Performance baseline testing
- **Environment Management**: Multi-environment support (local, staging, production)
- **OpenAPI-driven** contract checks and schema drift detection
- **K8s/Compose** harness for ephemeral environments
- **Operational** documentation, risk/threat coverage, and metrics

## Quick Start

### Prerequisites

- Node.js 14+ (for Newman)
- Python 3.7+ (for pytest)
- Git

### Installation

1. Clone the repository
```bash
cd projects-new/p08-api-testing
```

2. Install Node dependencies (for Newman)
```bash
npm install -g newman
npm install -g newman-reporter-html  # Optional, for HTML reports
```

3. Install Python dependencies
```bash
pip install -r requirements.txt
```

4. Setup environment variables
```bash
cp .env.example .env
# Edit .env with your API configuration
```

### Running Tests

#### Using Newman (Postman Collections)

Run the automated Newman runner:
```bash
./newman-run.sh -e local -c core
```

Or run directly with newman:
```bash
newman run producer/collections/core.postman_collection.json \
  -e producer/env/local.postman_environment.json \
  --reporters json,cli
```

#### Using pytest (Python Tests)

Run all tests:
```bash
pytest tests/ -v
```

Run specific test categories:
```bash
# Run only CRUD tests
pytest tests/test_api_orders.py -v

# Run only authentication tests
pytest tests/test_api_authentication.py -v -m auth

# Run specific test class
pytest tests/test_api_orders.py::TestOrdersCRUD -v

# Run with coverage
pytest tests/ --cov=tests --cov-report=html
```

Run with markers:
```bash
pytest -m "integration" tests/           # Run integration tests
pytest -m "smoke" tests/                 # Run smoke tests
pytest -m "not slow" tests/              # Skip slow tests
```

### Docker Compose

Start the test environment:
```bash
docker compose -f docker/compose.api.yaml up --build
```

### Kubernetes

Dry run:
```bash
kubectl apply -k k8s/overlays/dev --dry-run=client
```

## Features

### Postman Collection (core.postman_collection.json)

The collection includes:

#### Authentication
- Get Auth Token - OAuth2 style token generation
- Auth with Invalid Credentials - Error handling for invalid creds

#### Orders - CRUD Operations
- **Create Order** - POST /orders with full order data
- **List Orders** - GET /orders with pagination
- **Get Order by ID** - GET /orders/{id}
- **Update Order** - PUT /orders/{id} to update status/items
- **Delete Order** - DELETE /orders/{id}

#### Products
- List Products - GET /products with filtering
- Get Product by ID - GET /products/{id}

#### Error Conditions
- Not Found (404) - Missing resources
- Bad Request (400) - Invalid payloads
- Unauthorized (401) - Missing/invalid auth
- Server Errors (5xx) - Graceful error handling

#### Data Validation
- Response format validation
- Data type validation
- Required fields validation

### Python Test Suite

#### test_api_orders.py
- `TestOrdersCRUD` - CRUD operation tests
- `TestOrdersErrorHandling` - Error condition tests
- `TestOrdersDataValidation` - Data validation tests
- `TestOrdersResponseTime` - Performance tests

#### test_api_authentication.py
- `TestAuthentication` - Token generation and validation
- `TestAuthorization` - Authorization and access control
- `TestTokenRefresh` - Token refresh functionality
- `TestSessionManagement` - Session handling

#### Fixtures (conftest.py)
- `base_url` - API base URL
- `valid_credentials` - Test credentials
- `auth_token` - Session auth token
- `api_client` - Authenticated API client
- `http_client` - HTTP session
- `order_factory` - Order test data factory
- `product_factory` - Product test data factory
- `api_assertions` - Custom assertions

## Environment Configuration

### Local Development (.env)

```bash
API_BASE_URL=http://localhost:8080
API_CLIENT_ID=demo
API_CLIENT_SECRET=secret
TEST_ENVIRONMENT=local
LOG_LEVEL=INFO
```

### Postman Environment (producer/env/local.postman_environment.json)

Environment variables:
- `baseUrl` - API base URL (default: http://localhost:8080)
- `client_id` - OAuth2 client ID
- `client_secret` - OAuth2 client secret
- `authToken` - Bearer token (auto-populated)
- `page` - Default page number for pagination
- `pageSize` - Items per page
- `customerId` - Test customer ID
- `orderId` - Test order ID
- `category` - Product category

## Newman Runner (newman-run.sh)

Automated collection execution script with features:

- Multiple environment support
- Colored output with status indicators
- JSON and CLI reporting
- Report parsing and summary
- Error handling and retry logic
- Configurable timeouts and delays

### Usage

```bash
./newman-run.sh [options]

Options:
  -e, --environment ENV    Environment (default: local)
  -c, --collection COLL    Collection name (default: core)
  -v, --verbose            Verbose output
  --no-bail                Continue on test failure
  --timeout MS             Request timeout (default: 10000)
  --delay MS               Delay between requests (default: 100)
  -h, --help               Show help

Examples:
./newman-run.sh -e local -c core
./newman-run.sh -e staging --no-bail -v
./newman-run.sh -e prod --timeout 5000
```

## Test Execution Examples

### Full Test Suite

```bash
# Newman collection tests
./newman-run.sh -e local

# Python pytest tests
pytest tests/ -v

# Both with reporting
./newman-run.sh -e local --reporters json,html
pytest tests/ --cov=tests --cov-report=html
```

### Specific Test Categories

```bash
# Only CRUD operations
pytest tests/test_api_orders.py::TestOrdersCRUD -v

# Only authentication
pytest tests/test_api_authentication.py -v

# Only error handling
pytest tests/test_api_orders.py::TestOrdersErrorHandling -v

# Only validation
pytest tests/test_api_orders.py::TestOrdersDataValidation -v
```

### Performance Testing

```bash
# Test response times
pytest tests/test_api_orders.py::TestOrdersResponseTime -v

# With performance assertions
pytest tests/ -v --benchmark-only
```

## Reporting

### Newman Reports

Reports are generated in the `out/` directory:

- `newman-report-*.json` - Detailed JSON report
- `newman-cli-report-*.txt` - CLI output
- `newman-report-*.html` - HTML report (if html reporter installed)

Generate summary:
```bash
python consumer/report.py --input out/newman-report.json
```

### Pytest Reports

Generate coverage report:
```bash
pytest tests/ --cov=tests --cov-report=html
# Open htmlcov/index.html
```

Generate JUnit XML report:
```bash
pytest tests/ --junit-xml=out/pytest-report.xml
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: API Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: |
          npm install -g newman
          pip install -r requirements.txt
      - name: Run Newman tests
        run: ./newman-run.sh -e local
      - name: Run pytest tests
        run: pytest tests/ -v --junit-xml=out/report.xml
      - name: Upload reports
        uses: actions/upload-artifact@v2
        if: always()
        with:
          name: test-reports
          path: out/
```

## Troubleshooting

### API Connection Issues

```bash
# Check API is running
curl -i http://localhost:8080/health

# Check environment variables
cat .env

# Run with verbose output
./newman-run.sh -e local -v
pytest tests/ -v --log-cli-level=DEBUG
```

### Authentication Failures

```bash
# Verify credentials in .env
echo $API_CLIENT_ID
echo $API_CLIENT_SECRET

# Test token generation manually
curl -X POST http://localhost:8080/auth/token \
  -H "Content-Type: application/json" \
  -d '{"client_id":"demo","client_secret":"secret"}'
```

### Test Failures

```bash
# Run specific test with full output
pytest tests/test_api_orders.py::TestOrdersCRUD::test_create_order_success -vv -s

# Enable debugging
DEBUG=true pytest tests/ -v

# Check request/response details
pytest tests/ -v --log-cli-level=DEBUG
```

## Performance Baselines

Expected response times:
- List operations: < 1000ms
- Create operations: < 2000ms
- Get by ID: < 500ms
- Update operations: < 1000ms
- Delete operations: < 500ms

## Data Cleanup

The test suite automatically handles data cleanup. To enable/disable:

```bash
# In .env
CLEAN_DATA_AFTER_TESTS=true
RESET_DATABASE_BEFORE_TESTS=false
```

## Best Practices

1. **Environment Isolation**: Use different environments for different test stages
2. **Data Management**: Clean up test data after each test run
3. **Retry Logic**: Configure appropriate retry policies for flaky tests
4. **Logging**: Enable detailed logging for troubleshooting
5. **Version Control**: Keep test collections and scripts in version control
6. **Documentation**: Update docs when adding new tests
7. **Monitoring**: Set up alerts for test failures in CI/CD

## Documentation Structure

- `TESTING/` - Testing documentation and guides
- `ARCHITECTURE/` - System architecture documentation
- `RUNBOOKS/` - Operational runbooks
- `SOP/` - Standard operating procedures
- `PLAYBOOK/` - Incident response playbooks

## Contributing

1. Create a new branch for your changes
2. Add or update tests as needed
3. Run full test suite: `./newman-run.sh -e local && pytest tests/`
4. Update documentation
5. Submit pull request

## Support and Issues

For issues or questions:
1. Check the TESTING/ directory for detailed guides
2. Review test output and logs
3. Check API health and configuration
4. Review recent commits for context

## License

See LICENSE file in project root.

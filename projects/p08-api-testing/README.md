# P08 — Backend API Testing

## Overview
Comprehensive API testing framework using Postman collections and Newman CLI for automated testing. Includes positive/negative test scenarios, contract validation, performance testing, and CI/CD integration. Demonstrates REST API testing best practices and quality assurance automation.

## Key Outcomes
- [x] Postman collection for RESTful API testing
- [x] Newman CLI integration for CI/CD pipelines
- [x] Negative test cases (error handling, validation)
- [x] Authentication and authorization testing
- [x] Contract testing with JSON Schema validation
- [x] Performance testing with response time assertions

## Architecture
- **Components**: Postman Collections, Newman, Environment Variables, Test Scripts
- **Test Types**: Functional, Negative, Security, Performance, Contract
- **Dependencies**: Node.js 18+, Newman, newman-reporter-htmlextra

```mermaid
flowchart LR
    subgraph Test Suite
        Collection[Postman Collection]
        Env[Environment Variables]
        PreScripts[Pre-request Scripts]
        Tests[Test Scripts]
    end

    subgraph API Under Test
        Auth[/auth/login]
        Users[/api/users]
        Products[/api/products]
        Orders[/api/orders]
    end

    subgraph Execution
        Newman[Newman CLI]
        CI[GitHub Actions]
    end

    Collection --> PreScripts --> Auth
    Auth --> Tests
    Users --> Tests
    Products --> Tests
    Orders --> Tests
    Newman --> Collection
    CI --> Newman
    Tests --> Report[HTML Report]
    Tests --> Metrics[Test Metrics]
```

## Quickstart

```bash
make setup
make test
make report
```

## Configuration

| Env Var | Purpose | Example | Required |
|---------|---------|---------|----------|
| `API_BASE_URL` | Target API endpoint | `https://api.example.com` | Yes |
| `API_KEY` | API authentication key | `sk_test_abc123` | No |
| `AUTH_TOKEN` | Bearer token | `eyJhbGc...` | No |
| `TEST_USER_EMAIL` | Test account email | `test@example.com` | Yes |
| `TEST_USER_PASSWORD` | Test account password | `SecurePass123!` | Yes |

**Environment Files**: Create environment-specific JSON files for dev/staging/prod.

```bash
cp collections/environment.template.json collections/environment.dev.json
# Edit with your configuration
```

## Testing

```bash
# Run all tests
make test

# Run with specific environment
newman run collections/api-tests.json -e collections/environment.dev.json

# Run with detailed output
newman run collections/api-tests.json --verbose

# Run with HTML report
newman run collections/api-tests.json -r htmlextra --reporter-htmlextra-export reports/report.html

# Run specific folder from collection
newman run collections/api-tests.json --folder "User Management"
```

## Operations

### Logs, Metrics, Traces
- **Test Reports**: `reports/newman-report.html` (HTML report with charts)
- **CLI Output**: Console logs with pass/fail status
- **Metrics**: Response times, success rates, error counts
- **Newman Summary**: Detailed execution summary (JSON)

### Common Issues & Fixes

**Issue**: Tests fail with "ECONNREFUSED"
**Fix**: Verify API_BASE_URL is correct and API server is running.

**Issue**: Authentication tests fail
**Fix**: Check credentials in environment file, verify token hasn't expired.

**Issue**: JSON Schema validation fails
**Fix**: Update schema definition in test scripts to match API response format.

## Security

### Secrets Handling
- **Development**: Use environment files (gitignored), never commit credentials
- **CI/CD**: Store in GitHub Secrets → inject as environment variables
- **API Keys**: Rotate regularly, use separate keys for testing

### Test Data Security
- Use test accounts, not production data
- Sanitize all test data (no PII)
- Clean up test data after execution

## Roadmap

- [ ] Add GraphQL API testing
- [ ] Implement mutation testing
- [ ] Add load testing with Artillery
- [ ] Integrate with API mocking (Prism/WireMock)
- [ ] Add security testing (OWASP API Top 10)

## References

- [Postman Learning Center](https://learning.postman.com/)
- [Newman Documentation](https://github.com/postmanlabs/newman)
- [API Testing Best Practices](https://www.postman.com/api-platform/api-testing/)
- [JSON Schema Validation](https://json-schema.org/)


## Code Generation Prompts

This section contains AI-assisted code generation prompts that can help you recreate or extend project components. These prompts are designed to work with AI coding assistants like Claude, GPT-4, or GitHub Copilot.

### Test Automation

#### 1. End-to-End Tests
```
Create Playwright tests for a login flow, including form validation, authentication error handling, and successful redirect to dashboard
```

#### 2. API Tests
```
Generate pytest-based API tests that verify REST endpoints for CRUD operations, including request/response validation, error cases, and authentication
```

#### 3. Performance Tests
```
Write a Locust load test that simulates 100 concurrent users performing read/write operations, measures response times, and identifies bottlenecks
```

### How to Use These Prompts

1. **Copy the prompt** from the code block above
2. **Customize placeholders** (replace [bracketed items] with your specific requirements)
3. **Provide context** to your AI assistant about:
   - Your development environment and tech stack
   - Existing code patterns and conventions in this project
   - Any constraints or requirements specific to your use case
4. **Review and adapt** the generated code before using it
5. **Test thoroughly** and adjust as needed for your specific scenario

### Best Practices

- Always review AI-generated code for security vulnerabilities
- Ensure generated code follows your project's coding standards
- Add appropriate error handling and logging
- Write tests for AI-generated components
- Document any assumptions or limitations
- Keep sensitive information (credentials, keys) in environment variables


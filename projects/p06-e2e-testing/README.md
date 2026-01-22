# P06 — Web App Automated Testing (E2E)

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


## Overview
End-to-end testing framework using Playwright for web application testing, with parallel execution, visual regression testing, and CI/CD integration via GitHub Actions. Demonstrates modern QA automation practices, cross-browser testing, and comprehensive test reporting.

## Key Outcomes
- [x] Playwright test suite for login, checkout, and search flows
- [x] Cross-browser testing (Chromium, Firefox, WebKit)
- [x] Visual regression testing with screenshot comparison
- [x] GitHub Actions CI integration with artifact uploads
- [x] Parallel test execution and test retry logic
- [x] HTML/JSON test reports with trace viewer

## Architecture
- **Components**: Playwright Test, Page Object Model, CI/CD pipeline
- **Test Layers**: UI tests, API tests, visual regression tests
- **Dependencies**: Node.js 18+, Playwright 1.40+

```mermaid
flowchart TB
    subgraph CI[GitHub Actions CI]
        Trigger[Push/PR Trigger]
        Install[Install Dependencies]
        Browsers[Install Browsers]
        RunTests[Run Tests in Parallel]
        Upload[Upload Reports & Traces]
    end

    subgraph Tests[Test Suite]
        Login[Login Flow Tests]
        Checkout[Checkout Flow Tests]
        Search[Search Tests]
        Visual[Visual Regression]
        API[API Tests]
    end

    subgraph Browsers[Browser Matrix]
        Chrome[Chromium]
        FF[Firefox]
        Safari[WebKit]
    end

    Trigger --> Install --> Browsers --> RunTests
    RunTests --> Tests
    Tests --> Chrome & FF & Safari
    RunTests --> Upload
    Upload --> Report[HTML Report]
    Upload --> Trace[Trace Files]
```

## Quickstart

```bash
make setup
make test
make report
```

## Configuration

**Target URL**: Set `BASE_URL` to the application under test. Local default is `http://localhost:3000`; staging example: `https://staging.example.com`.

| Env Var | Purpose | Example | Required |
|---------|---------|---------|----------|
| `BASE_URL` | Target application URL | `https://example.com` | Yes |
| `TEST_USER` | Test account username | `test@example.com` | Yes |
| `TEST_PASSWORD` | Test account password | `SecurePass123!` | Yes |
| `HEADLESS` | Run tests headless | `true`, `false` | No (default: `true`) |
| `BROWSER` | Browser to test | `chromium`, `firefox`, `webkit` | No (default: `chromium`) |
| `WORKERS` | Parallel workers | `4` | No (default: `4`) |

**Secrets Management**: Store credentials in GitHub Secrets for CI. Use `.env` file locally (gitignored).

```bash
cp .env.example .env
# Edit .env with your test credentials
```

**CI Secrets (GitHub Actions)**:
- `P06_BASE_URL` (target URL)
- `P06_TEST_USER`
- `P06_TEST_PASSWORD`

## Testing

```bash
# Run all tests
make test

# Run specific test file
npx playwright test tests/login.spec.ts

# Run in headed mode (see browser)
npx playwright test --headed

# Run with specific browser
npx playwright test --project=firefox

# Debug mode
npx playwright test --debug

# Update visual snapshots
npx playwright test --update-snapshots
```

## Operations

### Logs, Metrics, Traces
- **Test Reports**: `reports/playwright-html/index.html` (generated after test run)
- **Machine-readable Reports**: `reports/playwright-report.json`, `reports/playwright-junit.xml`
- **Trace Viewer**: `npx playwright show-trace trace.zip`
- **Screenshots**: `reports/test-results/` directory (on failure)
- **Videos**: `reports/test-results/` directory (configurable)

### Common Issues & Fixes

**Issue**: Tests fail with "Timeout waiting for element"
**Fix**: Increase timeout in `playwright.config.ts` or use `waitForLoadState('networkidle')`.

**Issue**: Visual regression tests fail unexpectedly
**Fix**: Update snapshots: `npx playwright test --update-snapshots` (verify changes first).

**Issue**: Browser download fails in CI
**Fix**: Ensure `npx playwright install --with-deps` runs in CI setup.

## Security

### Secrets Handling
- **Development**: Use `.env` file (gitignored), never commit credentials
- **CI/CD**: Store in GitHub Secrets → inject as environment variables
- **Rotation**: Use short-lived test accounts, rotate passwords monthly

### Test Data Security
- Use dedicated test environment (not production)
- Sanitize test data (no PII/PHI)
- Clean up test data after execution

## Roadmap

- [ ] Add accessibility testing with @axe-core/playwright
- [ ] Implement performance testing with Lighthouse CI
- [ ] Add mobile viewport testing (responsive design)
- [ ] Integrate with test management tool (TestRail/Zephyr)
- [ ] Add contract testing for API endpoints

## References

- [Playwright Documentation](https://playwright.dev/)
- [Page Object Model Pattern](https://playwright.dev/docs/pom)
- [Visual Comparisons](https://playwright.dev/docs/test-snapshots)
- [CI/CD Integration](https://playwright.dev/docs/ci)


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

## Evidence & Verification

Verification summary: Evidence artifacts captured on 2025-11-14 to validate the quickstart configuration and document audit-ready supporting files.

**Evidence artifacts**
- Screenshot stored externally.
- [Run log](./docs/evidence/run-log.txt)
- [Dashboard export](./docs/evidence/dashboard-export.json)
- [Load test summary](./docs/evidence/load-test-summary.txt)

### Evidence Checklist

| Evidence Item | Location | Status |
| --- | --- | --- |
| Screenshot captured | Stored externally | ✅ |
| Run log captured | `docs/evidence/run-log.txt` | ✅ |
| Dashboard export captured | `docs/evidence/dashboard-export.json` | ✅ |
| Load test summary captured | `docs/evidence/load-test-summary.txt` | ✅ |

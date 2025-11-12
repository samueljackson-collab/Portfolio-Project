# Runbook — P06 (Web App Automated E2E Testing)

## Overview

Production operations runbook for the Playwright end-to-end testing framework. This runbook covers test execution, CI/CD pipeline management, test maintenance, visual regression testing, and troubleshooting procedures for automated web application testing.

**System Components:**
- Playwright Test framework with cross-browser support
- Page Object Model (POM) test architecture
- GitHub Actions CI/CD pipeline
- Visual regression testing with screenshot comparison
- HTML/JSON test reports with trace viewer
- Parallel test execution with retry logic

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Test suite success rate** | 95% | Passing tests / Total tests |
| **Test execution time** | < 10 minutes | Full suite runtime (parallel execution) |
| **Flaky test rate** | < 5% | Tests requiring retries / Total tests |
| **CI pipeline availability** | 99% | Successful GitHub Actions runs |
| **Test coverage** | > 80% | Critical user flows covered |
| **Visual regression accuracy** | 99% | False positives < 1% |

---

## Dashboards & Alerts

### Dashboards

#### Test Execution Dashboard
```bash
# View test report locally
make report
# Opens: playwright-report/index.html

# Check latest test run status
npx playwright show-report

# View trace for debugging
npx playwright show-trace test-results/trace.zip
```

#### GitHub Actions Dashboard
```bash
# View CI test runs
# Navigate to: https://github.com/<org>/<repo>/actions

# Check latest workflow run
gh run list --workflow=playwright-tests.yml --limit 5

# View specific run details
gh run view <run-id>

# Download test artifacts
gh run download <run-id>
```

#### Test Metrics Dashboard
```bash
# Analyze test results
cat playwright-report/results.json | jq '{
  total: .stats.expected,
  passed: .stats.ok,
  failed: .stats.unexpected,
  flaky: .stats.flaky,
  duration: .stats.duration
}'

# Check test timing
cat playwright-report/results.json | jq '.suites[].specs[] | {
  test: .title,
  duration: .results[0].duration
}' | sort -k2 -n
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | All tests failing (100% failure) | Immediate | Rollback deployment, investigate |
| **P1** | Critical flow failing (login/checkout) | 30 minutes | Fix test or application issue |
| **P1** | CI pipeline broken | 1 hour | Fix pipeline configuration |
| **P2** | Flaky test rate > 10% | 4 hours | Stabilize flaky tests |
| **P2** | Test execution time > 15 min | 24 hours | Optimize slow tests |
| **P3** | Visual regression false positives | 48 hours | Update snapshots |

#### Alert Queries

**Check for failing critical tests:**
```bash
# Check login test status
grep -i "login.*FAIL" playwright-report/index.html && echo "ALERT: Login tests failing"

# Check checkout flow
npx playwright test tests/checkout.spec.ts --reporter=list | grep -E "FAIL|ERROR"
```

**Monitor flaky tests:**
```bash
# Extract flaky tests from report
cat playwright-report/results.json | jq '.suites[].specs[] | select(.results | length > 1) | .title'

# Count retry attempts
cat playwright-report/results.json | jq '[.suites[].specs[].results | length] | add'
```

---

## Standard Operations

### Test Execution

#### Run Full Test Suite
```bash
# Local execution (headless)
make test

# Or manually
npx playwright test

# With specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit

# Parallel execution (default: 4 workers)
npx playwright test --workers=8
```

#### Run Specific Tests
```bash
# Single test file
npx playwright test tests/login.spec.ts

# Specific test by name
npx playwright test -g "should login successfully"

# Test folder
npx playwright test tests/checkout/

# Run tagged tests
npx playwright test --grep @smoke
npx playwright test --grep @regression
```

#### Debug Mode
```bash
# Interactive debug mode
npx playwright test --debug

# Step through specific test
npx playwright test tests/login.spec.ts --debug

# Headed mode (see browser)
npx playwright test --headed

# Slow motion (for observation)
npx playwright test --headed --slow-mo=1000
```

### Visual Regression Testing

#### Update Visual Snapshots
```bash
# Update all snapshots (use with caution)
npx playwright test --update-snapshots

# Update specific test snapshots
npx playwright test tests/homepage.spec.ts --update-snapshots

# Review snapshot changes before updating
git diff tests/**/*.png
```

#### Compare Snapshots
```bash
# View snapshot diff in report
npx playwright show-report

# Manual comparison
ls test-results/
# Look for -actual.png, -expected.png, -diff.png files
```

### CI/CD Pipeline Management

#### Trigger CI Pipeline
```bash
# Pipelines trigger automatically on push/PR
git add .
git commit -m "test: update checkout flow tests"
git push origin feature-branch

# Monitor pipeline
gh run watch

# View logs
gh run view --log
```

#### Manual Pipeline Trigger
```bash
# Trigger workflow manually
gh workflow run playwright-tests.yml

# With specific environment
gh workflow run playwright-tests.yml -f environment=staging
```

### Test Maintenance

#### Install/Update Dependencies
```bash
# Install all dependencies
make setup

# Or manually
npm install
npx playwright install --with-deps

# Update Playwright
npm update @playwright/test
npx playwright install
```

#### Update Test Data
```bash
# Update test credentials (from .env)
cp .env.example .env
vi .env
# Set BASE_URL, TEST_USER, TEST_PASSWORD

# Verify configuration
npx playwright test --reporter=list --dry-run
```

---

## Incident Response

### Detection

**Automated Detection:**
- GitHub Actions failure notifications
- Test report analysis
- Flaky test monitoring

**Manual Detection:**
```bash
# Check recent test runs
gh run list --workflow=playwright-tests.yml --limit 10

# Check test report
make report

# View failed tests
cat playwright-report/results.json | jq '.suites[].specs[] | select(.ok == false)'
```

### Triage

#### Severity Classification

**P0: Complete Test Failure**
- All tests failing (100% failure rate)
- CI pipeline completely broken
- Application completely down

**P1: Critical Flow Failure**
- Login tests failing
- Checkout flow broken
- Authentication issues
- > 50% test failure rate

**P2: Partial Test Failure**
- Single feature broken
- Flaky test rate > 10%
- Visual regression issues
- 10-50% test failure rate

**P3: Minor Issues**
- Individual test failing
- Performance degradation
- Non-critical visual changes
- < 10% test failure rate

### Incident Response Procedures

#### P0: All Tests Failing

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check if application is accessible
curl -I https://${BASE_URL}/

# 2. Verify test environment configuration
cat .env | grep BASE_URL

# 3. Run tests locally to reproduce
npx playwright test --workers=1 --reporter=list

# 4. Check recent deployments
git log --oneline -5

# 5. Check browser availability
npx playwright install --dry-run
```

**Investigation (5-15 minutes):**
```bash
# Check test logs
cat playwright-report/results.json | jq '.suites[].specs[].results[].error'

# Check screenshot evidence
ls test-results/**/*-failed-*.png

# Review trace files
npx playwright show-trace test-results/*/trace.zip

# Check for network issues
npx playwright test tests/login.spec.ts --trace on
```

**Mitigation:**
```bash
# If application issue: Rollback deployment
# (See application deployment runbook)

# If test environment issue: Update configuration
vi .env
# Fix BASE_URL or credentials

# If browser issue: Reinstall browsers
npx playwright install --force --with-deps

# If test code issue: Revert test changes
git revert <commit-hash>
git push
```

#### P1: Critical Flow Failing (Login Tests)

**Investigation:**
```bash
# Run only login tests with trace
npx playwright test tests/login.spec.ts --trace on

# View detailed error
npx playwright test tests/login.spec.ts --reporter=line

# Check screenshots
ls test-results/*login*/*-failed-*.png

# Review trace
npx playwright show-trace test-results/*login*/trace.zip
```

**Common Causes & Fixes:**

**Selector Change (element not found):**
```bash
# Test error: "Element not found: #login-button"

# Fix: Update selector in page object
vi tests/pages/LoginPage.ts
# Update selector to match current DOM

# Or use Playwright Inspector to find new selector
npx playwright codegen https://${BASE_URL}/login
```

**Timing Issue (element not ready):**
```bash
# Test error: "Timeout waiting for element"

# Fix: Add explicit wait
# In test file:
# await page.waitForLoadState('networkidle');
# await page.waitForSelector('#login-button', { state: 'visible' });

# Or increase timeout in playwright.config.ts:
# timeout: 30000  // 30 seconds
```

**Authentication Failure:**
```bash
# Test error: "Invalid credentials"

# Check credentials
echo $TEST_USER
echo $TEST_PASSWORD

# Verify credentials work manually
# Navigate to application and try logging in

# Update credentials in .env if changed
vi .env
```

#### P2: Visual Regression Failures

**Investigation:**
```bash
# Check visual diff
npx playwright show-report

# View diff images
ls test-results/**/*-diff.png

# Compare expected vs actual
open test-results/homepage-1-expected.png
open test-results/homepage-1-actual.png
```

**Mitigation:**
```bash
# If legitimate UI change: Update snapshots
git pull origin main  # Get latest changes
npx playwright test --update-snapshots

# Verify changes look correct
git diff tests/**/*.png

# Commit updated snapshots
git add tests/**/*.png
git commit -m "test: update visual snapshots after UI changes"
git push

# If false positive due to timing: Add wait
# In test: await page.waitForLoadState('networkidle');
```

#### P2: Flaky Tests

**Investigation:**
```bash
# Identify flaky tests
cat playwright-report/results.json | \
  jq '.suites[].specs[] | select(.results | length > 1)'

# Run specific test multiple times
for i in {1..10}; do
  npx playwright test tests/flaky-test.spec.ts --workers=1
done

# Check retry count
cat playwright-report/results.json | \
  jq '.suites[].specs[] | {test: .title, retries: (.results | length - 1)}'
```

**Common Causes & Fixes:**

**Race Condition:**
```typescript
// Bad: Race condition
await page.click('#submit');
await expect(page.locator('.success')).toBeVisible();

// Good: Wait for network to settle
await page.click('#submit');
await page.waitForLoadState('networkidle');
await expect(page.locator('.success')).toBeVisible();
```

**Animation/Transition Issues:**
```typescript
// Bad: Element still animating
await page.click('.modal-button');

// Good: Wait for animations to finish
await page.click('.modal-button');
await page.waitForTimeout(500);  // Wait for animation
// Or better: disable animations in test config
```

**Non-Deterministic Data:**
```typescript
// Bad: Depends on server state
await expect(page.locator('.item-count')).toHaveText('5 items');

// Good: Create known test data
await page.request.post('/api/reset-test-data');
await page.reload();
await expect(page.locator('.item-count')).toHaveText('5 items');
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Test Incident Report

**Date:** $(date)
**Severity:** P1
**Duration:** 45 minutes
**Affected Tests:** Login flow tests

## Timeline
- 14:00: Tests started failing in CI
- 14:15: Identified selector change in login form
- 14:30: Updated page object selectors
- 14:45: Tests passing again

## Root Cause
Application team changed login form HTML structure without updating tests

## Action Items
- [ ] Establish communication channel for UI changes
- [ ] Add data-testid attributes for stable selectors
- [ ] Implement visual regression baseline alerts

EOF

# Update test stability tracking
# Record flaky tests for future monitoring
```

---

## Monitoring & Troubleshooting

### Essential Troubleshooting Commands

#### Test Execution Issues
```bash
# Check Playwright installation
npx playwright --version
npx playwright install --dry-run

# Verify browsers installed
ls ~/.cache/ms-playwright/

# Check test configuration
cat playwright.config.ts

# Validate test files
npx playwright test --list

# Dry run (validate without executing)
npx playwright test --dry-run
```

#### Browser Issues
```bash
# Reinstall browsers
npx playwright install --force

# Install system dependencies (Linux)
npx playwright install-deps

# Check browser launch
npx playwright open https://example.com

# Test specific browser
npx playwright test --project=chromium --headed
```

#### Debugging Failed Tests
```bash
# Get detailed error output
npx playwright test --reporter=line

# Run with debug logs
DEBUG=pw:api npx playwright test

# Generate trace for analysis
npx playwright test --trace on

# View trace
npx playwright show-trace test-results/*/trace.zip

# Take screenshot at specific point
# In test: await page.screenshot({ path: 'debug.png' });
```

#### CI/CD Issues
```bash
# Check GitHub Actions workflow syntax
gh workflow view playwright-tests.yml

# View workflow runs
gh run list --workflow=playwright-tests.yml

# Download artifacts from failed run
gh run download <run-id>

# View logs from failed run
gh run view <run-id> --log-failed
```

### Common Issues & Solutions

#### Issue: "Browser executable not found"

**Symptoms:**
```bash
$ npx playwright test
Error: Browser executable not found at /path/to/chromium
```

**Diagnosis:**
```bash
# Check installed browsers
npx playwright install --dry-run
```

**Solution:**
```bash
# Install browsers
npx playwright install --with-deps

# Or specific browser
npx playwright install chromium
```

---

#### Issue: "Timeout waiting for selector"

**Symptoms:**
```bash
Error: Timeout 30000ms exceeded.
waiting for selector "#login-button"
```

**Diagnosis:**
```bash
# Run in headed mode to see what's happening
npx playwright test tests/login.spec.ts --headed --debug

# Check if element exists with different selector
npx playwright codegen https://${BASE_URL}/login
```

**Solution:**
```bash
# Option 1: Update selector
# Use data-testid for stability
# await page.click('[data-testid="login-button"]');

# Option 2: Increase timeout
# await page.click('#login-button', { timeout: 60000 });

# Option 3: Wait for element to appear
# await page.waitForSelector('#login-button', { state: 'visible' });
# await page.click('#login-button');
```

---

#### Issue: Visual regression test failing unexpectedly

**Symptoms:**
```bash
Error: Screenshot comparison failed:
expected: tests/screenshots/homepage.png
actual:   test-results/homepage-actual.png
diff:     test-results/homepage-diff.png
```

**Diagnosis:**
```bash
# View the diff
open test-results/homepage-diff.png

# Check what changed
git diff tests/screenshots/homepage.png
```

**Solution:**
```bash
# If change is intentional (UI update)
npx playwright test --update-snapshots

# If anti-aliasing or font rendering difference
# Add threshold in test:
# await expect(page).toHaveScreenshot({ maxDiffPixels: 100 });

# If viewport size issue
# Ensure consistent viewport in config:
# use: { viewport: { width: 1280, height: 720 } }
```

---

#### Issue: Tests pass locally but fail in CI

**Symptoms:**
- Tests pass on local machine
- Same tests fail in GitHub Actions

**Diagnosis:**
```bash
# Check environment differences
echo $BASE_URL
echo $CI

# Compare Playwright versions
npx playwright --version

# Check Node version
node --version
```

**Solution:**
```bash
# Match CI environment locally
# Use same Node version as CI
nvm use 18

# Run in Docker (matches CI environment)
docker run -it --rm -v $(pwd):/work -w /work mcr.microsoft.com/playwright:latest npx playwright test

# Add screenshots on failure in CI
# In playwright.config.ts:
# screenshot: 'only-on-failure'
# video: 'retain-on-failure'

# Check artifacts in GitHub Actions
gh run download <run-id>
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 0 minutes (tests in Git)
- **RTO** (Recovery Time Objective): 15 minutes (reinstall and run)

### Backup Strategy

**Test Code Backups:**
```bash
# All test code is in Git
git push origin main

# Backup test artifacts
tar -czf test-backups-$(date +%Y%m%d).tar.gz \
  playwright-report/ \
  test-results/ \
  playwright-snapshots/

# Store in S3 or artifact storage
aws s3 cp test-backups-*.tar.gz s3://test-artifacts/
```

**Configuration Backups:**
```bash
# Export environment configuration
cp .env .env.backup-$(date +%Y%m%d)

# Backup Playwright config
git add playwright.config.ts
git commit -m "backup: playwright configuration"

# Backup CI workflow
git add .github/workflows/playwright-tests.yml
```

### Disaster Recovery Procedures

#### Complete Environment Loss

**Recovery Steps (10-15 minutes):**
```bash
# 1. Clone repository
git clone <repo-url>
cd <repo-name>

# 2. Install dependencies
npm install

# 3. Install browsers
npx playwright install --with-deps

# 4. Restore configuration
cp .env.example .env
# Edit with actual values

# 5. Verify tests run
npx playwright test --workers=1

# 6. Generate report
npx playwright show-report
```

#### Test Data Recovery

**Recovery Steps:**
```bash
# Restore visual snapshots from backup
tar -xzf test-backups-*.tar.gz playwright-snapshots/

# Or regenerate from current application state
npx playwright test --update-snapshots

# Verify snapshots
git diff playwright-snapshots/
```

---

## Maintenance Procedures

### Routine Maintenance

#### Daily Tasks
```bash
# Review overnight test runs
gh run list --workflow=playwright-tests.yml --created=$(date +%Y-%m-%d)

# Check for flaky tests
cat playwright-report/results.json | \
  jq '.suites[].specs[] | select(.results | length > 1) | .title'

# Monitor test execution time
cat playwright-report/results.json | jq '.stats.duration'
```

#### Weekly Tasks
```bash
# Update dependencies
npm update
npx playwright install

# Review and refactor slow tests
cat playwright-report/results.json | \
  jq '.suites[].specs[] | {test: .title, duration: .results[0].duration}' | \
  sort -k2 -n | tail -10

# Clean up old test artifacts
rm -rf test-results/
rm -rf playwright-report/

# Update visual snapshots if needed
git status playwright-snapshots/
```

#### Monthly Tasks
```bash
# Major dependency updates
npm outdated
npm update @playwright/test

# Review test coverage
# Identify untested flows and add tests

# Audit page objects for reusability
# Consolidate duplicate selectors/methods

# Performance optimization
# Reduce unnecessary waits
# Parallelize independent tests
```

### Upgrade Procedures

#### Update Playwright Version
```bash
# 1. Check current version
npx playwright --version

# 2. Check for updates
npm outdated @playwright/test

# 3. Update Playwright
npm update @playwright/test

# 4. Reinstall browsers
npx playwright install

# 5. Run tests to verify
npx playwright test

# 6. Update CI workflow if needed
vi .github/workflows/playwright-tests.yml
# Update playwright version if pinned

# 7. Commit changes
git add package.json package-lock.json
git commit -m "chore: update Playwright to v1.40.0"
```

#### Migrate to New Test Pattern
```bash
# Example: Migrate to Page Object Model

# 1. Create page objects directory
mkdir -p tests/pages

# 2. Extract page objects from existing tests
# Move selectors and actions to page classes

# 3. Update tests to use page objects
# Replace direct page interactions with page object methods

# 4. Run tests to verify
npx playwright test

# 5. Remove old test code after verification
```

---

## Operational Best Practices

### Pre-Deployment Checklist
- [ ] All tests passing locally
- [ ] Visual snapshots reviewed and updated if needed
- [ ] Test data configuration verified
- [ ] CI pipeline green
- [ ] Test execution time within SLO (< 10 min)
- [ ] No new flaky tests introduced

### Post-Deployment Checklist
- [ ] CI tests passed after deployment
- [ ] No visual regression failures
- [ ] Critical flows verified (login, checkout)
- [ ] Test execution time monitored
- [ ] Flaky test rate checked

### Test Development Standards
```typescript
// Good practices:
// 1. Use data-testid for stable selectors
await page.click('[data-testid="submit-button"]');

// 2. Wait for network to settle
await page.waitForLoadState('networkidle');

// 3. Use Page Object Model
const loginPage = new LoginPage(page);
await loginPage.login(user, password);

// 4. Explicit waits instead of hardcoded timeouts
await page.waitForSelector('.success-message');

// 5. Clean test data
await page.request.post('/api/reset-test-data');
```

### Escalation Path

| Level | Role | Response Time | Contact |
|-------|------|---------------|---------|
| L1 | QA Engineer | 1 hour | Slack #qa-team |
| L2 | QA Lead | 4 hours | Direct message |
| L3 | Engineering Manager | 8 hours | Phone call |

---

## References

### Internal Documentation
- [P06 Project README](./README.md)
- [Playwright Configuration](./playwright.config.ts)
- [Test Suite](./tests/)
- [Page Objects](./tests/pages/)

### External Resources
- [Playwright Documentation](https://playwright.dev/)
- [Page Object Model Pattern](https://playwright.dev/docs/pom)
- [Visual Comparisons](https://playwright.dev/docs/test-snapshots)
- [CI/CD Integration](https://playwright.dev/docs/ci)
- [Debugging Tools](https://playwright.dev/docs/debug)

### Emergency Contacts
- **QA Team Slack:** #qa-automation
- **CI/CD Issues:** #platform-engineering
- **Escalation:** Follow escalation path above

---

## Quick Reference Card

### Most Common Operations
```bash
# Run all tests
make test

# Run specific test
npx playwright test tests/login.spec.ts

# Debug test
npx playwright test --debug

# Update snapshots
npx playwright test --update-snapshots

# View report
make report

# View trace
npx playwright show-trace test-results/*/trace.zip
```

### Emergency Response
```bash
# P0: All tests failing - check application
curl -I https://${BASE_URL}/

# P0: Reinstall browsers
npx playwright install --force --with-deps

# P1: Critical test failing - run with trace
npx playwright test tests/login.spec.ts --trace on

# P1: Update changed selectors
npx playwright codegen https://${BASE_URL}

# P2: Update visual snapshots
npx playwright test --update-snapshots
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** QA Engineering Team
- **Review Schedule:** Quarterly or after major test framework changes
- **Feedback:** Create issue or submit PR with updates

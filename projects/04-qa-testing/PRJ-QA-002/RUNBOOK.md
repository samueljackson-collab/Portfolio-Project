# Runbook — PRJ-QA-002 (Selenium + PyTest CI)

## Overview

Production operations runbook for automated UI testing with Selenium and PyTest in GitHub Actions CI/CD pipeline. This runbook covers test execution, browser automation, CI/CD integration, parallel execution, visual validation, and troubleshooting procedures for web UI sanity testing.

**System Components:**
- Selenium WebDriver (browser automation)
- PyTest test framework
- GitHub Actions CI/CD pipeline
- Headless browser execution (Chrome/Firefox)
- pytest-xdist (parallel test execution)
- Allure reporting framework
- Screenshot capture on failure
- Test retry mechanism

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Test suite success rate** | 95% | Passing tests / Total tests |
| **Test execution time** | < 10 minutes | Full UI sanity suite runtime |
| **CI pipeline success rate** | 98% | Successful GitHub Actions runs |
| **Flaky test rate** | < 5% | Tests requiring retries / Total tests |
| **Browser compatibility** | 100% | Tests passing across Chrome, Firefox |
| **Test coverage (critical paths)** | 100% | Key user journeys covered |

---

## Dashboards & Alerts

### Dashboards

#### Test Execution Dashboard
```bash
# View latest test run
cat test-results/latest/pytest-report.json | jq '{
  total: .summary.total,
  passed: .summary.passed,
  failed: .summary.failed,
  skipped: .summary.skipped,
  duration: .duration
}'

# Check Allure report
allure serve test-results/allure-results/

# View HTML report
python -m http.server 8000 --directory test-results/html-report/
# Open: http://localhost:8000
```

#### GitHub Actions Dashboard
```bash
# View recent workflow runs
gh run list --workflow=ui-tests.yml --limit 10

# Check specific run status
gh run view <run-id>

# Download test artifacts
gh run download <run-id> --name test-reports

# View workflow logs
gh run view <run-id> --log
```

#### Browser Test Dashboard
```bash
# Check browser execution results
ls -lh test-results/screenshots/
cat test-results/browser-compatibility.json | jq '.browsers[] | {
  browser: .name,
  passed: .passed,
  failed: .failed
}'

# View failed test screenshots
ls -lt test-results/screenshots/*-failed-*.png | head -10
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | All UI tests failing | Immediate | Check application, rollback if needed |
| **P1** | Critical path tests failing | 30 minutes | Investigate, fix or stabilize tests |
| **P1** | CI pipeline broken | 1 hour | Fix pipeline configuration |
| **P2** | Flaky test rate > 10% | 4 hours | Stabilize flaky tests |
| **P2** | Test execution time > 15 min | 8 hours | Optimize slow tests |
| **P3** | Single test failing | 24 hours | Fix test or update selectors |

#### Alert Queries

**Check for critical path failures:**
```bash
# Check login tests
grep -i "test_login.*FAILED" test-results/latest/pytest.log && \
  echo "ALERT: Login tests failing"

# Check checkout flow
grep -E "test_checkout|test_cart|test_payment" test-results/latest/pytest.log | \
  grep FAILED
```

**Monitor flaky tests:**
```bash
# Identify tests with retries
cat test-results/latest/pytest-report.json | \
  jq '.tests[] | select(.outcome == "passed" and .call.outcome == "rerun") | .nodeid'

# Count flaky tests
FLAKY_COUNT=$(grep -c "RERUN" test-results/latest/pytest.log)
TOTAL_COUNT=$(grep -c "test_.*" test-results/latest/pytest.log)
FLAKY_RATE=$(echo "scale=2; ($FLAKY_COUNT / $TOTAL_COUNT) * 100" | bc)
echo "Flaky test rate: ${FLAKY_RATE}%"
```

**Monitor CI/CD health:**
```bash
# Check recent CI runs
gh run list --workflow=ui-tests.yml --json conclusion | \
  jq 'map(select(.conclusion == "failure")) | length'

# Alert if multiple consecutive failures
FAILURES=$(gh run list --workflow=ui-tests.yml --limit 5 --json conclusion | \
  jq 'map(select(.conclusion == "failure")) | length')
if [ "$FAILURES" -ge 3 ]; then
  echo "ALERT: 3+ consecutive CI failures"
fi
```

---

## Standard Operations

### Test Execution

#### Run Full Test Suite
```bash
# Run all UI tests locally
make test

# Or with pytest directly
pytest tests/ -v --tb=short

# Run with specific markers
pytest tests/ -v -m "smoke"
pytest tests/ -v -m "regression"
pytest tests/ -v -m "critical"

# Run with HTML report
pytest tests/ --html=test-results/report.html --self-contained-html
```

#### Run Tests by Module
```bash
# Login tests only
pytest tests/test_login.py -v

# Navigation tests
pytest tests/test_navigation.py -v

# Form submission tests
pytest tests/test_forms.py -v

# Search functionality tests
pytest tests/test_search.py -v
```

#### Run with Different Browsers
```bash
# Chrome (default)
pytest tests/ --browser=chrome

# Firefox
pytest tests/ --browser=firefox

# Headless Chrome
pytest tests/ --browser=chrome --headless

# Both browsers (using pytest-xdist)
pytest tests/ --browser=chrome --browser=firefox
```

#### Parallel Execution
```bash
# Run tests in parallel (4 workers)
pytest tests/ -n 4

# Auto-detect number of CPUs
pytest tests/ -n auto

# Parallel with specific workers
pytest tests/ -n 8 --dist=loadfile
```

#### Debug Mode
```bash
# Run with verbose output
pytest tests/ -vv

# Show print statements
pytest tests/ -v -s

# Drop into debugger on failure
pytest tests/ --pdb

# Step through test
pytest tests/test_login.py --trace

# Run single test with debugging
pytest tests/test_login.py::test_valid_login -vv -s
```

#### Test Retry on Failure
```bash
# Retry failed tests once
pytest tests/ --reruns 1

# Retry up to 3 times with delay
pytest tests/ --reruns 3 --reruns-delay 2

# Only retry specific tests
pytest tests/ -m flaky --reruns 2
```

### Screenshot and Evidence Capture

#### Automatic Screenshot on Failure
```bash
# Screenshots are automatically captured on test failure
# Location: test-results/screenshots/

# View failed test screenshots
ls -lt test-results/screenshots/*-failed-*.png

# Open latest failure screenshot
open $(ls -t test-results/screenshots/*-failed-*.png | head -1)
```

#### Manual Screenshot Capture
```python
# In test code:
def test_something(driver):
    # Take screenshot at any point
    driver.save_screenshot('test-results/screenshots/checkpoint.png')

    # Or use pytest-selenium plugin
    driver.get_screenshot_as_file('test-results/screenshots/step1.png')
```

### CI/CD Pipeline Operations

#### Trigger CI Pipeline
```bash
# Automatic trigger on push to main or PRs
git add .
git commit -m "test: update UI test suite"
git push origin feature-branch

# Monitor pipeline
gh run watch

# View live logs
gh run view --log-failed
```

#### Manual Pipeline Trigger
```bash
# Trigger workflow manually
gh workflow run ui-tests.yml

# With specific browser
gh workflow run ui-tests.yml -f browser=chrome

# With specific test marker
gh workflow run ui-tests.yml -f marker=smoke

# List recent runs
gh run list --workflow=ui-tests.yml --limit 5
```

#### Download Test Artifacts from CI
```bash
# List artifacts for a run
gh run view <run-id> --log | grep "artifact"

# Download all artifacts
gh run download <run-id>

# Download specific artifact
gh run download <run-id> --name test-reports
gh run download <run-id> --name screenshots

# Extract and view
tar -xzf screenshots.tar.gz
ls screenshots/
```

### Test Data Management

#### Setup Test Data
```bash
# Create test users and data
python scripts/create_test_data.py

# Load test fixtures
python scripts/load_fixtures.py

# Verify test data
python scripts/verify_test_data.py
```

#### Clean Test Data
```bash
# Clean up after test run
python scripts/cleanup_test_data.py

# Reset to baseline
python scripts/reset_test_environment.py
```

---

## Incident Response

### Detection

**Automated Detection:**
- GitHub Actions failure notifications
- Slack alerts on test failures
- Email notifications for broken builds
- Quality gate violations

**Manual Detection:**
```bash
# Check recent test runs
gh run list --workflow=ui-tests.yml

# Review test logs
cat test-results/latest/pytest.log | grep -E "FAILED|ERROR"

# Check for screenshots (indicates failures)
ls -l test-results/screenshots/ | grep failed

# View test report
open test-results/latest/report.html
```

### Triage

#### Severity Classification

**P0: Complete Test Failure**
- All UI tests failing (100% failure rate)
- CI pipeline completely broken
- Application completely inaccessible
- Browser driver failures

**P1: Critical Path Failure**
- Login tests failing
- Checkout/payment flow broken
- > 50% test failure rate
- Multiple consecutive CI failures

**P2: Partial Failure**
- Single feature tests failing
- Flaky test rate > 10%
- Test execution time doubled
- 10-50% test failure rate

**P3: Minor Issues**
- Individual test failing
- Single selector update needed
- Performance within acceptable limits
- < 10% test failure rate

### Incident Response Procedures

#### P0: All UI Tests Failing

**Immediate Actions (0-5 minutes):**
```bash
# 1. Verify application is accessible
curl -I ${BASE_URL}

# 2. Test manual access
# Open browser and navigate to ${BASE_URL}

# 3. Check if it's an environment issue
ping $(echo ${BASE_URL} | sed 's|http[s]*://||g' | cut -d'/' -f1)

# 4. Check recent deployments
git log --oneline -5

# 5. Check CI logs
gh run view --log-failed
```

**Investigation (5-15 minutes):**
```bash
# Run tests locally to reproduce
pytest tests/ -v --tb=short

# Check browser driver versions
chromedriver --version
geckodriver --version

# Check Selenium version
pip show selenium

# View detailed error logs
cat test-results/latest/pytest.log | grep -A 20 "ERROR\|FAILED"

# Check screenshots for visual issues
ls -lt test-results/screenshots/*-failed-*.png | head -5
```

**Mitigation:**
```bash
# If application down: Coordinate with dev team
# If application recently deployed: Consider rollback

# If browser driver issue: Update drivers
pip install --upgrade selenium
# Update chromedriver/geckodriver to match browser version

# If test configuration issue: Fix configuration
vi pytest.ini
vi conftest.py

# If test code issue: Rollback test changes
git log --oneline tests/ | head -5
git revert <commit-hash>

# Verify mitigation
pytest tests/ -v -k "smoke"
```

#### P1: Login Tests Failing

**Investigation:**
```bash
# 1. Run login tests with verbose output
pytest tests/test_login.py -vv -s --tb=long

# 2. Check login page accessibility
curl ${BASE_URL}/login

# 3. Review failure screenshots
ls -lt test-results/screenshots/*login*-failed-*.png

# 4. Test login manually
# Open browser and attempt manual login

# 5. Check for selector changes
pytest tests/test_login.py -vv | grep -i "no such element\|element not found"
```

**Common Causes & Fixes:**

**Selector Changed (Element Not Found):**
```python
# Error: NoSuchElementException: Unable to locate element: #username

# Diagnosis: Inspect the page to find new selector
from selenium import webdriver
driver = webdriver.Chrome()
driver.get(f"{BASE_URL}/login")
# Use browser DevTools to find new selector

# Fix: Update page object or test
# Before:
username_field = driver.find_element(By.ID, "username")

# After (if ID changed to "user-input"):
username_field = driver.find_element(By.ID, "user-input")

# Or use more stable selector:
username_field = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
username_field = driver.find_element(By.XPATH, "//input[@name='username']")
```

**Timing Issue (Element Not Ready):**
```python
# Error: ElementNotInteractableException: element not interactable

# Fix: Add explicit wait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Instead of:
driver.find_element(By.ID, "submit").click()

# Use:
wait = WebDriverWait(driver, 10)
submit_btn = wait.until(EC.element_to_be_clickable((By.ID, "submit")))
submit_btn.click()

# Or wait for element to be visible:
wait.until(EC.visibility_of_element_located((By.ID, "username")))
```

**Credential Issue:**
```python
# Error: Login assertion failed - expected success page

# Diagnosis: Check if test credentials still valid
import os
print(f"Test user: {os.getenv('TEST_USER')}")
print(f"Test password: {'*' * len(os.getenv('TEST_PASSWORD'))}")

# Fix: Update credentials in CI secrets or .env file
# GitHub: Settings → Secrets → Update TEST_USER and TEST_PASSWORD
# Local: Update .env file

# Verify credentials work manually first
```

**JavaScript Not Loaded:**
```python
# Error: Element exists but click does nothing

# Fix: Wait for JavaScript to load
driver.execute_script("return document.readyState") == "complete"

# Or wait for specific JavaScript library
wait.until(lambda d: d.execute_script("return typeof jQuery !== 'undefined'"))

# Or use JavaScript click instead
element = driver.find_element(By.ID, "submit")
driver.execute_script("arguments[0].click();", element)
```

#### P1: CI Pipeline Broken

**Investigation:**
```bash
# 1. Check workflow file syntax
cat .github/workflows/ui-tests.yml

# 2. View failed run logs
gh run view <run-id> --log

# 3. Check for common CI issues
gh run view <run-id> --log | grep -E "error|fatal|failed"

# 4. Verify CI environment
# Check if dependencies are installing correctly
# Check if browsers are available in CI
```

**Common CI Issues & Fixes:**

**Browser Not Installed:**
```yaml
# Error: chromedriver not found

# Fix: Add browser setup to CI workflow
- name: Setup Chrome
  uses: browser-actions/setup-chrome@latest

- name: Install ChromeDriver
  run: |
    # Use the new JSON endpoints to find the correct ChromeDriver URL for the latest stable version.
    CHROMEDRIVER_URL=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | jq -r '.channels.Stable.downloads.chromedriver[] | select(.platform=="linux64") | .url')
    wget -q "$CHROMEDRIVER_URL" -O chromedriver-linux64.zip
    unzip chromedriver-linux64.zip
    sudo mv chromedriver-linux64/chromedriver /usr/local/bin/
    CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%.*}")
    wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
    unzip chromedriver_linux64.zip
    sudo mv chromedriver /usr/local/bin/
    sudo chmod +x /usr/local/bin/chromedriver
```

**Headless Mode Issues:**
```python
# Error: Tests pass locally but fail in CI

# Fix: Ensure headless mode is enabled in CI
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
if os.getenv('CI'):  # Running in CI
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')

driver = webdriver.Chrome(options=chrome_options)
```

**Permission Issues:**
```yaml
# Error: Permission denied when creating screenshot directory

# Fix: Create directory with proper permissions
- name: Setup test directories
  run: |
    mkdir -p test-results/screenshots
    chmod 777 test-results/screenshots
```

#### P2: Flaky Tests

**Investigation:**
```bash
# 1. Identify flaky tests
pytest tests/ --reruns 5 --reruns-delay 1 | tee flaky-analysis.log

# 2. Analyze patterns
grep -E "RERUN|passed on rerun" flaky-analysis.log

# 3. Run specific test multiple times
for i in {1..20}; do
  pytest tests/test_checkout.py::test_complete_purchase -v
done | grep -E "PASSED|FAILED" | sort | uniq -c

# 4. Check timing of failures
cat test-results/latest/pytest.log | grep -B 5 "RERUN"
```

**Common Causes & Fixes:**

**Race Condition:**
```python
# Bad: No wait between actions
driver.find_element(By.ID, "add-to-cart").click()
driver.find_element(By.ID, "checkout").click()

# Good: Explicit waits
wait = WebDriverWait(driver, 10)
wait.until(EC.element_to_be_clickable((By.ID, "add-to-cart"))).click()
wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "cart-updated")))
wait.until(EC.element_to_be_clickable((By.ID, "checkout"))).click()
```

**Stale Element Reference:**
```python
# Bad: Element reference becomes stale
element = driver.find_element(By.ID, "dynamic-content")
# Page refreshes or content updates
element.click()  # StaleElementReferenceException

# Good: Re-find element
def click_with_retry(by, value, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            element = driver.find_element(by, value)
            element.click()
            return
        except StaleElementReferenceException:
            if attempt == max_attempts - 1:
                raise
            time.sleep(0.5)
```

**Timing-Dependent Assertions:**
```python
# Bad: Immediate assertion
driver.find_element(By.ID, "submit").click()
assert "Success" in driver.page_source

# Good: Wait for expected condition
driver.find_element(By.ID, "submit").click()
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "success-message")))
assert "Success" in driver.page_source
```

**Parallel Test Conflicts:**
```python
# Bad: Tests share data or state
TEST_USER = "shared@example.com"  # Same user for all tests

# Good: Unique data per test
import uuid
TEST_USER = f"test_{uuid.uuid4()}@example.com"

# Or use pytest fixtures with scope
@pytest.fixture(scope="function")
def unique_user():
    return f"test_{uuid.uuid4()}@example.com"
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# UI Test Incident Report

**Date:** $(date)
**Severity:** P1/P2/P3
**Duration:** [duration]
**Affected Tests:** [test names]

## Timeline
- [Time]: Tests started failing
- [Time]: Root cause identified
- [Time]: Fix implemented
- [Time]: Tests passing

## Root Cause
[Detailed root cause]

## Impact
- CI builds blocked: [yes/no]
- Deployment delayed: [yes/no]
- False positives: [number]

## Resolution
[How the issue was resolved]

## Prevention
- [ ] Add more stable selectors (data-testid attributes)
- [ ] Improve wait strategies
- [ ] Add test to flaky test tracking
- [ ] Update test documentation
- [ ] Add monitoring/alerting

## Lessons Learned
[Key takeaways]
EOF

# Update flaky test tracking
echo "$(date +%Y-%m-%d),test_name,rerun_count,resolution" >> \
  metrics/flaky-tests.csv

# Update runbook if needed
# Add new troubleshooting procedures
```

---

## Monitoring & Troubleshooting

### Essential Troubleshooting Commands

#### Selenium WebDriver Issues
```bash
# Check Selenium version
pip show selenium

# Check browser versions
google-chrome --version
firefox --version

# Check driver versions
chromedriver --version
geckodriver --version

# Update Selenium
pip install --upgrade selenium

# Install/update browser drivers
# Chrome
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
# Follow download and installation steps

# Firefox
# geckodriver is usually managed by selenium-manager
```

#### PyTest Configuration Issues
```bash
# Validate pytest installation
pytest --version

# List all tests
pytest --collect-only tests/

# Check test markers
pytest --markers

# Verify pytest.ini configuration
cat pytest.ini

# Check conftest.py for fixtures
cat conftest.py
```

#### Browser Automation Issues
```bash
# Test browser can be launched
python -c "
from selenium import webdriver
driver = webdriver.Chrome()
driver.get('https://www.google.com')
print(f'Title: {driver.title}')
driver.quit()
"

# Test headless mode
python -c "
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.get('https://www.google.com')
print(f'Headless title: {driver.title}')
driver.quit()
"

# Check display for headless (Linux)
echo $DISPLAY
export DISPLAY=:99
```

#### Test Environment Issues
```bash
# Verify base URL is accessible
curl -I ${BASE_URL}

# Check if login page loads
curl ${BASE_URL}/login | grep -i "login\|username\|password"

# Test network latency
ping -c 5 $(echo ${BASE_URL} | sed 's|http[s]*://||g' | cut -d'/' -f1)

# Check DNS resolution
nslookup $(echo ${BASE_URL} | sed 's|http[s]*://||g' | cut -d'/' -f1)
```

### Common Issues & Solutions

#### Issue: "WebDriverException: Message: 'chromedriver' executable needs to be in PATH"

**Symptoms:**
```bash
$ pytest tests/
selenium.common.exceptions.WebDriverException: Message: 'chromedriver' executable needs to be in PATH
```

**Diagnosis:**
```bash
# Check if chromedriver is installed
which chromedriver

# Check Chrome version
google-chrome --version
```

**Solution:**
```bash
# Install chromedriver
# Option 1: Using webdriver-manager (recommended)
pip install webdriver-manager

# Update test code to use WebDriver Manager:
# from webdriver_manager.chrome import ChromeDriverManager
# driver = webdriver.Chrome(ChromeDriverManager().install())

# Option 2: Manual installation
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+' | head -1)
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}
# Download and install matching version

# Option 3: Use selenium-manager (Selenium 4.6+)
# Selenium automatically manages drivers
pip install --upgrade selenium
```

---

#### Issue: "ElementNotInteractableException: element not interactable"

**Symptoms:**
```python
selenium.common.exceptions.ElementNotInteractableException:
Message: element not interactable
```

**Diagnosis:**
```python
# Check if element is visible and enabled
element = driver.find_element(By.ID, "submit")
print(f"Displayed: {element.is_displayed()}")
print(f"Enabled: {element.is_enabled()}")
print(f"Size: {element.size}")
print(f"Location: {element.location}")
```

**Solution:**
```python
# Fix 1: Wait for element to be clickable
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 10)
element = wait.until(EC.element_to_be_clickable((By.ID, "submit")))
element.click()

# Fix 2: Scroll element into view
element = driver.find_element(By.ID, "submit")
driver.execute_script("arguments[0].scrollIntoView(true);", element)
time.sleep(0.5)  # Allow scroll animation
element.click()

# Fix 3: Use JavaScript click
element = driver.find_element(By.ID, "submit")
driver.execute_script("arguments[0].click();", element)

# Fix 4: Wait for overlays to disappear
wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "loading-overlay")))
element.click()
```

---

#### Issue: Tests pass locally but fail in CI

**Symptoms:**
- All tests pass on local machine
- Same tests fail in GitHub Actions CI

**Diagnosis:**
```bash
# Compare environments
echo "Local Python: $(python --version)"
echo "Local Selenium: $(pip show selenium | grep Version)"

# Check CI logs for environment info
gh run view <run-id> --log | grep -E "Python|Selenium|Chrome"
```

**Solution:**
```python
# 1. Add CI-specific configurations
import os

def get_driver():
    options = Options()

    if os.getenv('CI'):  # Detect CI environment
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(options=options)
    return driver

# 2. Increase timeouts in CI
if os.getenv('CI'):
    driver.implicitly_wait(20)  # Instead of 10
else:
    driver.implicitly_wait(10)

# 3. Add screenshots on failure in CI
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == 'call' and rep.failed:
        if os.getenv('CI'):
            driver = item.funcargs.get('driver')
            if driver:
                driver.save_screenshot(f'test-results/screenshots/{item.name}-failed.png')
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 0 minutes (tests in Git)
- **RTO** (Recovery Time Objective): 15 minutes (restore and execute)

### Backup Strategy

**Test Code Backups:**
```bash
# All test code in Git
git add tests/ conftest.py pytest.ini
git commit -m "backup: UI test suite $(date +%Y-%m-%d)"
git push origin main

# Backup test results
tar -czf backups/test-results-$(date +%Y%m%d).tar.gz test-results/
```

**Configuration Backups:**
```bash
# Backup test configuration
cp pytest.ini pytest.ini.backup-$(date +%Y%m%d)
cp .env .env.backup-$(date +%Y%m%d)

# Backup CI workflow
git add .github/workflows/ui-tests.yml
git commit -m "backup: CI workflow configuration"
```

### Disaster Recovery Procedures

#### Complete Environment Loss

**Recovery Steps (15 minutes):**
```bash
# 1. Clone repository
git clone <repo-url>
cd PRJ-QA-002

# 2. Setup Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install browsers and drivers
# Chrome
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt-get update
sudo apt-get install google-chrome-stable

# 5. Configure environment
cp .env.example .env
vi .env  # Update with actual values

# 6. Verify setup
pytest tests/ --collect-only

# 7. Run smoke tests
pytest tests/ -m smoke -v

# 8. Run full suite
pytest tests/ -v
```

---

## Maintenance Procedures

### Routine Maintenance

#### Daily Tasks
```bash
# Run smoke tests
pytest tests/ -m smoke -v

# Check for failures
cat test-results/latest/pytest.log | grep -E "FAILED|ERROR"

# Review flaky tests
grep -c "RERUN" test-results/latest/pytest.log
```

#### Weekly Tasks
```bash
# Update dependencies
pip list --outdated
pip install --upgrade selenium pytest pytest-xdist

# Run full regression suite
pytest tests/ -v

# Clean old screenshots
find test-results/screenshots/ -mtime +7 -delete

# Update browser drivers
pip install --upgrade webdriver-manager

# Check for deprecated Selenium methods
grep -r "find_element_by_" tests/
# Replace with new By locators
```

#### Monthly Tasks
```bash
# Review test coverage
pytest tests/ --cov=tests --cov-report=html

# Analyze flaky tests
cat metrics/flaky-tests.csv | sort | uniq

# Update test selectors for stability
# Add data-testid attributes where possible

# Refactor page objects
# Consolidate duplicate code

# Performance optimization
# Identify and optimize slow tests
pytest tests/ --durations=10
```

---

## Quick Reference Card

### Most Common Operations
```bash
# Run all tests
pytest tests/ -v

# Run smoke tests
pytest tests/ -m smoke

# Run with retries
pytest tests/ --reruns 2

# Run in parallel
pytest tests/ -n auto

# Run specific test
pytest tests/test_login.py::test_valid_login -v

# Generate HTML report
pytest tests/ --html=report.html

# Run in headless mode
pytest tests/ --headless
```

### Emergency Response
```bash
# P0: All tests failing - check application
curl -I ${BASE_URL}

# P1: Login tests failing - run with debug
pytest tests/test_login.py -vv -s --tb=long

# P1: CI broken - check workflow logs
gh run view --log-failed

# P2: Flaky tests - identify and mark
pytest tests/ --reruns 5 | grep RERUN
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** QA Engineering Team
- **Review Schedule:** Quarterly or after major framework changes
- **Feedback:** Create issue or submit PR with updates

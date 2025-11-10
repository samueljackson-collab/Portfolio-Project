# Runbook — P08 (Backend API Testing)

## Overview

Production operations runbook for the Postman/Newman API testing framework. This runbook covers collection management, test execution, CI/CD integration, contract validation, performance testing, and troubleshooting procedures for automated API testing.

**System Components:**
- Postman Collections (test definitions)
- Newman CLI (test runner)
- Environment files (configuration management)
- Test scripts (assertions and validation)
- newman-reporter-htmlextra (enhanced reporting)
- GitHub Actions CI/CD pipeline

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Test suite success rate** | 95% | Passing tests / Total tests |
| **Test execution time** | < 5 minutes | Full collection runtime |
| **API response time (p95)** | < 500ms | 95th percentile response time |
| **Contract validation pass rate** | 100% | Schema validations / Total |
| **CI pipeline availability** | 99% | Successful GitHub Actions runs |
| **Test coverage** | > 80% | API endpoints covered by tests |

---

## Dashboards & Alerts

### Dashboards

#### Test Execution Dashboard
```bash
# View HTML report
make report
# Opens: reports/newman-report.html

# Check latest test run summary
newman run collections/api-tests.json --reporters cli,json \
  --reporter-json-export reports/summary.json

cat reports/summary.json | jq '{
  total: .run.stats.requests.total,
  passed: .run.stats.tests.passed,
  failed: .run.stats.tests.failed,
  avg_response_time: .run.timings.responseAverage
}'
```

#### API Performance Dashboard
```bash
# Extract response times from report
cat reports/summary.json | jq '.run.executions[] | {
  request: .item.name,
  response_time: .response.responseTime,
  status: .response.code
}' | sort -k2 -n

# Calculate percentiles
cat reports/summary.json | jq '[.run.executions[].response.responseTime] | sort' | \
  jq 'length as $len | {
    p50: .[$len/2 | floor],
    p95: .[$len*0.95 | floor],
    p99: .[$len*0.99 | floor]
  }'
```

#### GitHub Actions Dashboard
```bash
# View CI test runs
gh run list --workflow=newman-tests.yml --limit 10

# Check specific run
gh run view <run-id>

# Download test reports
gh run download <run-id> --name test-reports
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | All tests failing (100% failure) | Immediate | Check API availability, rollback |
| **P1** | Auth tests failing | 30 minutes | Fix authentication, verify credentials |
| **P1** | Critical endpoint down | 30 minutes | Investigate API, escalate |
| **P2** | Contract validation failures | 2 hours | Update schema or fix API response |
| **P2** | Performance degradation (p95 > 1s) | 4 hours | Investigate API performance |
| **P3** | Single test failing | 24 hours | Fix test or update assertions |

#### Alert Queries

**Check for API downtime:**
```bash
# Test API availability
curl -f ${API_BASE_URL}/health || echo "ALERT: API down"

# Check specific endpoint
curl -f ${API_BASE_URL}/api/users || echo "ALERT: Users endpoint down"
```

**Monitor response times:**
```bash
# Extract slow requests (> 1 second)
cat reports/summary.json | jq '.run.executions[] |
  select(.response.responseTime > 1000) | {
    request: .item.name,
    response_time: .response.responseTime
  }'
```

**Check authentication status:**
```bash
# Run auth tests only
newman run collections/api-tests.json --folder "Authentication" --reporters cli

# Check for auth failures
cat reports/summary.json | jq '.run.executions[] |
  select(.item.name | contains("Login")) |
  select(.assertions[].error != null)'
```

---

## Standard Operations

### Test Execution

#### Run Full Test Suite
```bash
# Local execution
make test

# Or manually with Newman
newman run collections/api-tests.json \
  -e collections/environment.dev.json \
  -r cli,htmlextra \
  --reporter-htmlextra-export reports/newman-report.html

# Run against different environments
newman run collections/api-tests.json -e collections/environment.staging.json
newman run collections/api-tests.json -e collections/environment.prod.json
```

#### Run Specific Test Folders
```bash
# Authentication tests only
newman run collections/api-tests.json --folder "Authentication"

# User management tests
newman run collections/api-tests.json --folder "User Management"

# Product API tests
newman run collections/api-tests.json --folder "Products"

# Multiple folders
newman run collections/api-tests.json --folder "Authentication" --folder "Users"
```

#### Debug Mode
```bash
# Verbose output
newman run collections/api-tests.json --verbose

# Show all request/response details
newman run collections/api-tests.json -r cli --reporter-cli-show-body

# Delay between requests (for debugging)
newman run collections/api-tests.json --delay-request 2000  # 2 seconds

# Bail on first failure
newman run collections/api-tests.json --bail
```

### Collection Management

#### Export Collection from Postman
```bash
# In Postman UI:
# 1. Click collection > Export
# 2. Choose Collection v2.1
# 3. Save to collections/api-tests.json

# Verify export
cat collections/api-tests.json | jq '.info.name'
```

#### Update Environment Variables
```bash
# Edit environment file
vi collections/environment.dev.json

# Example structure:
cat > collections/environment.dev.json << 'EOF'
{
  "name": "Development",
  "values": [
    {
      "key": "API_BASE_URL",
      "value": "https://api-dev.example.com",
      "enabled": true
    },
    {
      "key": "API_KEY",
      "value": "dev_api_key_123",
      "enabled": true
    },
    {
      "key": "TEST_USER_EMAIL",
      "value": "test@example.com",
      "enabled": true
    }
  ]
}
EOF
```

#### Validate Collection
```bash
# Check collection structure
cat collections/api-tests.json | jq '.item[] | .name'

# Count total requests
cat collections/api-tests.json | jq '[.item[].item[]] | length'

# List all test scripts
cat collections/api-tests.json | jq '.. | .event? | select(. != null) |
  select(.[].listen == "test") | .[].script.exec[]'
```

### CI/CD Pipeline Management

#### Trigger CI Pipeline
```bash
# Automatic trigger on push
git add collections/
git commit -m "test: update API test collection"
git push origin feature-branch

# Monitor pipeline
gh run watch

# View logs
gh run view --log
```

#### Manual Pipeline Execution
```bash
# Trigger workflow manually
gh workflow run newman-tests.yml

# With environment parameter
gh workflow run newman-tests.yml -f environment=staging

# List recent runs
gh run list --workflow=newman-tests.yml --limit 5
```

### Performance Testing

#### Run Performance Tests
```bash
# Run with timing report
newman run collections/api-tests.json \
  -e collections/environment.dev.json \
  -r cli,json \
  --reporter-json-export reports/performance.json

# Analyze timings
cat reports/performance.json | jq '.run.timings'

# Extract slow requests
cat reports/performance.json | jq '.run.executions[] |
  select(.response.responseTime > 500) | {
    name: .item.name,
    time: .response.responseTime
  }'
```

#### Load Testing
```bash
# Run collection multiple times
for i in {1..10}; do
  newman run collections/api-tests.json \
    -e collections/environment.dev.json \
    --reporters cli
done

# Parallel execution (stress test)
for i in {1..5}; do
  newman run collections/api-tests.json &
done
wait
```

---

## Incident Response

### Detection

**Automated Detection:**
- GitHub Actions failure notifications
- CI/CD pipeline alerts
- Test report analysis

**Manual Detection:**
```bash
# Check API health
curl -f ${API_BASE_URL}/health

# Run quick smoke test
newman run collections/api-tests.json --folder "Smoke Tests"

# Check recent test runs
gh run list --workflow=newman-tests.yml --json status,conclusion
```

### Triage

#### Severity Classification

**P0: Complete API Failure**
- All tests failing (100%)
- API unreachable (ECONNREFUSED)
- Authentication completely broken
- Production API down

**P1: Critical Endpoint Failure**
- Login endpoint failing
- Core business API broken
- > 50% test failure rate
- Production data inconsistency

**P2: Partial Failure**
- Single endpoint failing
- Schema validation failures
- Performance degradation
- 10-50% test failure rate

**P3: Minor Issues**
- Single test failing
- Non-critical endpoint issue
- Minor schema mismatch
- < 10% test failure rate

### Incident Response Procedures

#### P0: API Completely Down

**Immediate Actions (0-5 minutes):**
```bash
# 1. Verify API is unreachable
curl -I ${API_BASE_URL}

# 2. Check different endpoints
curl ${API_BASE_URL}/health
curl ${API_BASE_URL}/api/users

# 3. Test with direct IP (bypass DNS)
curl -I http://<api-server-ip>:8000

# 4. Check recent deployments
git log --oneline -5

# 5. Notify on-call team
# Slack: #incidents
# PagerDuty: trigger incident
```

**Investigation (5-15 minutes):**
```bash
# Check API server logs
# (See API deployment runbook)

# Test from different locations
curl -I ${API_BASE_URL} --connect-timeout 5

# Check DNS resolution
nslookup api.example.com

# Test authentication separately
curl -X POST ${API_BASE_URL}/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

**Mitigation:**
```bash
# If API deployment issue: Rollback
# (See deployment runbook)

# If network issue: Check firewall/load balancer
# (See infrastructure runbook)

# If authentication service down: Restart auth service
# (See auth service runbook)

# Verify mitigation
newman run collections/api-tests.json --folder "Smoke Tests"
```

#### P1: Authentication Tests Failing

**Investigation:**
```bash
# 1. Run auth tests with verbose output
newman run collections/api-tests.json \
  --folder "Authentication" \
  --verbose

# 2. Test login endpoint manually
curl -X POST ${API_BASE_URL}/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"'${TEST_USER_EMAIL}'","password":"'${TEST_USER_PASSWORD}'"}'

# 3. Check if credentials expired
echo "User: ${TEST_USER_EMAIL}"
echo "API Key: ${API_KEY}"

# 4. Check environment variables
cat collections/environment.dev.json | jq '.values[] |
  select(.key == "TEST_USER_EMAIL" or .key == "API_KEY")'
```

**Common Causes & Fixes:**

**Expired Credentials:**
```bash
# Update test user password
vi collections/environment.dev.json
# Update TEST_USER_PASSWORD value

# Or regenerate API key
curl -X POST ${API_BASE_URL}/api/keys \
  -H "Authorization: Bearer ${OLD_TOKEN}" \
  -d '{"name":"test-key"}'

# Update environment file
vi collections/environment.dev.json
# Update API_KEY value
```

**Token Refresh Issue:**
```bash
# Check token expiration in pre-request script
cat collections/api-tests.json | jq '.event[] |
  select(.listen == "prerequest") | .script.exec'

# Fix: Add token refresh logic
# In Postman pre-request script:
# if (pm.environment.get("token_expires_at") < Date.now()) {
#     // Refresh token logic
# }
```

**Schema Change:**
```bash
# API response format changed
# Update test assertions to match new schema

# Example: Login response changed
# Old: { "token": "..." }
# New: { "access_token": "...", "token_type": "Bearer" }

# Fix: Update test script
# pm.test("Token exists", function() {
#     pm.expect(pm.response.json()).to.have.property("access_token");
# });
```

#### P2: Contract Validation Failures

**Investigation:**
```bash
# 1. Run tests to identify failing validations
newman run collections/api-tests.json -r cli,json \
  --reporter-json-export reports/failures.json

# 2. Extract schema validation errors
cat reports/failures.json | jq '.run.executions[] |
  select(.assertions[].error != null) | {
    request: .item.name,
    error: .assertions[].error
  }'

# 3. Get actual response
newman run collections/api-tests.json --folder "Users" \
  --verbose | grep -A 20 "Response Body"
```

**Mitigation:**
```bash
# Option 1: Update schema in test
# If API schema intentionally changed

# In Postman test script, update JSON Schema:
cat > new-schema.json << 'EOF'
{
  "type": "object",
  "required": ["id", "email", "name"],
  "properties": {
    "id": {"type": "integer"},
    "email": {"type": "string", "format": "email"},
    "name": {"type": "string"},
    "created_at": {"type": "string", "format": "date-time"}
  }
}
EOF

# Option 2: Fix API response
# If API is returning incorrect format
# (See API development runbook)

# Verify fix
newman run collections/api-tests.json --folder "Users"
```

#### P2: Performance Degradation

**Investigation:**
```bash
# 1. Run performance analysis
newman run collections/api-tests.json \
  -r cli,json \
  --reporter-json-export reports/perf.json

# 2. Identify slow endpoints
cat reports/perf.json | jq '.run.executions[] |
  select(.response.responseTime > 1000) | {
    endpoint: .item.name,
    time_ms: .response.responseTime,
    url: .request.url.raw
  }'

# 3. Check API server metrics
# (See monitoring runbook)

# 4. Test specific slow endpoint
time curl ${API_BASE_URL}/api/products?limit=1000
```

**Mitigation:**
```bash
# Temporary: Increase timeout in tests
# In Postman request settings:
# Timeout: 5000ms → 10000ms

# Permanent: Optimize API endpoint
# Add caching, database indexes, etc.
# (See API optimization runbook)

# Adjust test assertions
# Update expected response time in test:
# pm.expect(pm.response.responseTime).to.be.below(2000);  // Was 500
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# API Test Incident Report

**Date:** $(date)
**Severity:** P1
**Duration:** 1 hour
**Affected Tests:** Authentication tests

## Timeline
- 10:00: Auth tests started failing in CI
- 10:15: Identified expired API key
- 10:30: Generated new API key
- 10:45: Updated environment file
- 11:00: Tests passing

## Root Cause
Test API key expired after 90 days

## Action Items
- [ ] Set up API key rotation automation
- [ ] Add expiration monitoring
- [ ] Document key rotation process
- [ ] Add alert for keys expiring < 7 days

EOF

# Update test metrics
cat reports/summary.json | jq '.run.stats' > metrics/test-run-$(date +%Y%m%d-%H%M).json
```

---

## Monitoring & Troubleshooting

### Essential Troubleshooting Commands

#### Collection Issues
```bash
# Validate collection JSON
cat collections/api-tests.json | jq '.' > /dev/null && echo "Valid JSON"

# Check collection version
cat collections/api-tests.json | jq '.info.schema'

# List all requests
cat collections/api-tests.json | jq '.. | .request? | select(. != null) | .url.raw'

# Count tests
cat collections/api-tests.json | jq '[.. | .event? | select(. != null) |
  select(.[].listen == "test")] | length'
```

#### Environment Issues
```bash
# Validate environment file
cat collections/environment.dev.json | jq '.' > /dev/null && echo "Valid JSON"

# List all variables
cat collections/environment.dev.json | jq '.values[] | {key: .key, value: .value}'

# Check required variables
REQUIRED_VARS=("API_BASE_URL" "API_KEY" "TEST_USER_EMAIL")
for var in "${REQUIRED_VARS[@]}"; do
  cat collections/environment.dev.json | jq -e ".values[] | select(.key == \"$var\")" > /dev/null || \
    echo "Missing: $var"
done
```

#### Request Debugging
```bash
# Test single request with curl
# Extract from collection
cat collections/api-tests.json | jq '.item[0].item[0].request'

# Manual curl equivalent
curl -X GET "${API_BASE_URL}/api/users" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -v

# Test with different HTTP methods
curl -X POST "${API_BASE_URL}/api/users" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com"}'
```

#### Newman Issues
```bash
# Check Newman version
newman --version

# Update Newman
npm install -g newman
npm install -g newman-reporter-htmlextra

# Run with maximum debugging
DEBUG=* newman run collections/api-tests.json

# Test with minimal collection
echo '{
  "info": {"name": "Test"},
  "item": [{
    "name": "Health Check",
    "request": {"method": "GET", "url": "'${API_BASE_URL}'/health"}
  }]
}' | newman run -
```

### Common Issues & Solutions

#### Issue: "ECONNREFUSED" error

**Symptoms:**
```bash
Error: connect ECONNREFUSED 127.0.0.1:8000
```

**Diagnosis:**
```bash
# Check if API is running
curl -I ${API_BASE_URL}

# Check port
netstat -tuln | grep 8000

# Check URL in environment
cat collections/environment.dev.json | jq '.values[] | select(.key == "API_BASE_URL")'
```

**Solution:**
```bash
# Start API server
# (See API deployment runbook)

# Or update API_BASE_URL to correct endpoint
vi collections/environment.dev.json
# Change API_BASE_URL to correct value

# Verify
newman run collections/api-tests.json --folder "Health Check"
```

---

#### Issue: "401 Unauthorized" on all requests

**Symptoms:**
```bash
All requests returning 401 status code
```

**Diagnosis:**
```bash
# Check authentication headers
newman run collections/api-tests.json --folder "Users" --verbose | \
  grep -A 5 "Request Headers"

# Test auth endpoint
curl -X POST ${API_BASE_URL}/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"'${TEST_USER_EMAIL}'","password":"'${TEST_USER_PASSWORD}'"}'
```

**Solution:**
```bash
# Option 1: Regenerate token
# Run login request to get fresh token
newman run collections/api-tests.json --folder "Authentication"

# Option 2: Update API_KEY
vi collections/environment.dev.json
# Update API_KEY value

# Option 3: Check pre-request script
# Ensure token is being set correctly:
# pm.environment.set("token", pm.response.json().access_token);
```

---

#### Issue: JSON Schema validation failing

**Symptoms:**
```bash
Error: JSON Schema validation failed
Expected property 'created_at' not found in response
```

**Diagnosis:**
```bash
# Get actual response
newman run collections/api-tests.json --folder "Users" --verbose | \
  grep -A 30 "Response Body"

# Compare with expected schema
cat collections/api-tests.json | jq '.item[] | .. | .test? |
  select(. != null) | select(. | contains("schema"))'
```

**Solution:**
```bash
# Option 1: Update schema to match actual response
# In Postman test script, update JSON Schema

# Option 2: Make field optional
# Change "required": ["id", "name", "created_at"]
# To:     "required": ["id", "name"]

# Option 3: Fix API to return expected fields
# (See API development runbook)
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 0 minutes (collections in Git)
- **RTO** (Recovery Time Objective): 10 minutes (restore and run)

### Backup Strategy

**Collection Backups:**
```bash
# All collections in Git version control
git add collections/
git commit -m "backup: API test collections"
git push origin main

# Export from Postman regularly
# Postman → Collection → Export → Save to collections/

# Backup to S3/cloud storage
aws s3 sync collections/ s3://test-artifacts/api-tests/collections/
```

**Report Archives:**
```bash
# Archive test reports
tar -czf reports-archive-$(date +%Y%m%d).tar.gz reports/

# Upload to artifact storage
aws s3 cp reports-archive-*.tar.gz s3://test-artifacts/api-tests/archives/

# Clean up old local reports
find reports/ -name "*.html" -mtime +30 -delete
```

### Disaster Recovery Procedures

#### Complete Environment Loss

**Recovery Steps (10 minutes):**
```bash
# 1. Clone repository
git clone <repo-url>
cd <repo-name>

# 2. Install dependencies
npm install

# 3. Install Newman globally
npm install -g newman newman-reporter-htmlextra

# 4. Restore environment configuration
cp collections/environment.template.json collections/environment.dev.json
vi collections/environment.dev.json
# Update with actual values

# 5. Verify collection
newman run collections/api-tests.json --folder "Health Check"

# 6. Run full test suite
make test
```

---

## Maintenance Procedures

### Routine Maintenance

#### Daily Tasks
```bash
# Review overnight test runs
gh run list --workflow=newman-tests.yml --created=$(date +%Y-%m-%d)

# Check for failures
newman run collections/api-tests.json --folder "Smoke Tests"

# Monitor API response times
cat reports/summary.json | jq '.run.timings.responseAverage'
```

#### Weekly Tasks
```bash
# Update dependencies
npm update newman newman-reporter-htmlextra

# Review test coverage
cat collections/api-tests.json | jq '[.item[].item[]] | length'
# Compare against total API endpoints

# Clean up old reports
rm -rf reports/newman-*.html
rm -rf reports/*.json

# Sync collections from Postman
# Export from Postman UI and commit to Git
```

#### Monthly Tasks
```bash
# Review and refactor tests
# Consolidate duplicate tests
# Remove obsolete tests

# Update environment variables
# Rotate API keys
# Update test credentials

# Performance baseline
newman run collections/api-tests.json \
  -r json --reporter-json-export reports/baseline-$(date +%Y%m).json

# Archive old reports
tar -czf reports-$(date +%Y%m).tar.gz reports/
aws s3 cp reports-*.tar.gz s3://test-artifacts/api-tests/
```

---

## Quick Reference

### Common Commands
```bash
# Run tests
make test

# Run specific folder
newman run collections/api-tests.json --folder "Authentication"

# Generate report
newman run collections/api-tests.json -r htmlextra --reporter-htmlextra-export reports/report.html

# Run with environment
newman run collections/api-tests.json -e collections/environment.dev.json

# Debug mode
newman run collections/api-tests.json --verbose
```

### Emergency Response
```bash
# P0: Check API status
curl -I ${API_BASE_URL}/health

# P1: Test auth endpoint
curl -X POST ${API_BASE_URL}/auth/login -d '{"email":"test@example.com","password":"test"}'

# P1: Run smoke tests
newman run collections/api-tests.json --folder "Smoke Tests"

# P2: Update environment
vi collections/environment.dev.json

# P2: Regenerate API key
# (See API key management docs)
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** QA Engineering Team
- **Review Schedule:** Quarterly or after major API changes
- **Feedback:** Create issue or submit PR with updates

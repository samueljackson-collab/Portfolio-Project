# Test Plan: Web Application Login System

| Field | Value |
|-------|-------|
| **Test Plan ID** | TP-LOGIN-001 |
| **Version** | 1.2 |
| **Date** | 2026-01-15 |
| **Author** | QA Engineering Team |
| **Status** | Approved |
| **Application** | Flask Login API v1.0.0 |

---

## 1. Introduction

### 1.1 Purpose

This test plan defines the strategy, scope, objectives, schedule, and resources required to test the authentication system for the web application login service. It provides a comprehensive framework for verifying that all functional, security, performance, and accessibility requirements are satisfied before production release.

### 1.2 Background

The web application login system provides authentication endpoints for user access control. The system handles credential validation, session management, rate limiting, and role-based authorization. This test plan covers all aspects of the login subsystem from unit-level API validation to integrated security assessments.

---

## 2. Scope

### 2.1 In-Scope

The following features and behaviors are included in this test plan:

- **Login functionality**: Successful and failed authentication flows
- **Logout functionality**: Session termination and cleanup
- **Session management**: Session creation, persistence, and expiry
- **Rate limiting**: Lockout after repeated failed attempts, lockout window, and reset behavior
- **Role-based authorization**: Admin vs. non-admin access control
- **Input validation**: Empty fields, malformed data, boundary values
- **Security controls**: Injection resistance, password protection, XSS prevention
- **Health endpoint**: Availability without authentication
- **Error handling**: Consistent error message format and HTTP status codes

### 2.2 Out-of-Scope

The following are explicitly excluded from this test plan:

- Password reset and recovery flows
- OAuth 2.0 / OpenID Connect integration
- Multi-factor authentication (MFA)
- Email verification workflows
- Third-party identity provider (IdP) integration
- Frontend UI testing (CSS, layout, browser rendering)
- Database persistence layer testing (SQLAlchemy migrations, etc.)
- Load testing beyond the defined performance scenarios

---

## 3. Test Objectives

The primary objectives of this test effort are:

1. **Verify functional correctness** of all authentication endpoints against documented requirements
2. **Validate security controls** protecting against OWASP Top 10 vulnerabilities relevant to authentication
3. **Confirm performance** that single-user response times meet SLA targets
4. **Ensure robustness** by exercising boundary conditions, malformed input, and edge cases
5. **Demonstrate coverage** via a requirements traceability matrix linking every requirement to at least one passing test case
6. **Establish a regression baseline** for future iterations

---

## 4. Test Environment

### 4.1 Infrastructure

| Component | Specification |
|-----------|---------------|
| **Application** | Flask 3.0.0, Python 3.11 |
| **Port** | 5001 (local) |
| **OS** | Linux (Ubuntu 22.04 / similar) |
| **Test Framework** | pytest 7.x + requests |
| **Test Client** | Flask built-in test client |
| **Python** | 3.11.x |

### 4.2 Test Data

| Username | Password | Role |
|----------|----------|------|
| admin | Admin@1234! | Administrator |
| user1 | User@5678! | Standard User |
| testuser | Test@9999! | Standard User |

### 4.3 Environment Variables

```bash
SECRET_KEY=test-secret-key  # set during pytest runs
FLASK_ENV=testing
```

### 4.4 Prerequisites

- Python 3.11+ installed
- `pip install flask==3.0.0 pytest requests` completed
- Application module importable from test path
- No conflicting processes on port 5001

---

## 5. Entry and Exit Criteria

### 5.1 Entry Criteria

Before test execution begins, all of the following must be true:

- [ ] Application source code passes linting (no syntax errors)
- [ ] All required Python packages are installed
- [ ] Test environment is isolated from production data
- [ ] Test data (user accounts) are loaded and validated
- [ ] Test plan has been reviewed and approved by stakeholders
- [ ] All P1 requirements are documented and traceable

### 5.2 Exit Criteria

Test execution is considered complete when:

- [ ] All P1 and P2 test cases have been executed
- [ ] 100% of P1 security test cases pass
- [ ] Defect rate is below 2% of total test cases
- [ ] All critical (P1) defects are resolved or accepted with documented risk
- [ ] Traceability matrix shows 100% requirement coverage
- [ ] Test results documented and signed off

---

## 6. Test Strategy

### 6.1 Testing Levels

| Level | Approach | Tools |
|-------|----------|-------|
| Unit | Individual route handlers tested in isolation | pytest + Flask test client |
| Integration | Login → session → profile → logout flow | pytest fixtures with shared client |
| Security | Injection payloads, boundary inputs, encoding attacks | pytest + manual payloads |
| Performance | Timing assertions on response time | Python `time` module |

### 6.2 Test Types

- **Positive Testing**: Valid inputs produce expected successful responses
- **Negative Testing**: Invalid inputs produce expected error responses
- **Boundary Testing**: Edge values (empty strings, maximum length inputs)
- **Security Testing**: OWASP-aligned attack vectors
- **Performance Testing**: Response time thresholds under normal and concurrent load
- **Regression Testing**: Full suite re-run after any code change

---

## 7. Functional Test Cases

### TC-F001: Valid Login with Correct Credentials

| Field | Value |
|-------|-------|
| **ID** | TC-F001 |
| **Title** | Valid login with correct credentials |
| **Priority** | P1 |
| **Preconditions** | App running, admin user exists in USERS dict |

**Steps:**
1. Send POST /login with JSON body `{"username": "admin", "password": "Admin@1234!"}`
2. Capture response status code and body
3. Verify status code is 200
4. Verify response JSON contains `"user": "admin"`
5. Verify response JSON contains `"message": "Login successful"`

**Expected Result:** HTTP 200, JSON `{"message": "Login successful", "user": "admin"}`

**Actual Result:** Pass

---

### TC-F002: Login with Wrong Password

| Field | Value |
|-------|-------|
| **ID** | TC-F002 |
| **Title** | Login with incorrect password |
| **Priority** | P1 |
| **Preconditions** | App running, admin user exists |

**Steps:**
1. Send POST /login with `{"username": "admin", "password": "wrongpassword"}`
2. Capture response status and body
3. Verify status code is 401
4. Verify `attempts_remaining` field is present and equals 4
5. Verify error message says "Invalid credentials"

**Expected Result:** HTTP 401, JSON contains `attempts_remaining: 4`

**Actual Result:** Pass

---

### TC-F003: Login with Non-Existent User

| Field | Value |
|-------|-------|
| **ID** | TC-F003 |
| **Title** | Login with non-existent username |
| **Priority** | P1 |
| **Preconditions** | App running |

**Steps:**
1. Send POST /login with `{"username": "nobody", "password": "anything"}`
2. Capture response status and body
3. Verify status code is 401
4. Verify no user data is leaked in the response

**Expected Result:** HTTP 401, error message present, no user information disclosed

**Actual Result:** Pass

---

### TC-F004: Login with Empty Username

| Field | Value |
|-------|-------|
| **ID** | TC-F004 |
| **Title** | Login fails with empty username |
| **Priority** | P1 |
| **Preconditions** | App running |

**Steps:**
1. Send POST /login with `{"username": "", "password": "Admin@1234!"}`
2. Capture response status
3. Verify status code is 400
4. Verify error message indicates both fields are required

**Expected Result:** HTTP 400, error about required fields

**Actual Result:** Pass

---

### TC-F005: Login with Empty Password

| Field | Value |
|-------|-------|
| **ID** | TC-F005 |
| **Title** | Login fails with empty password |
| **Priority** | P1 |
| **Preconditions** | App running |

**Steps:**
1. Send POST /login with `{"username": "admin", "password": ""}`
2. Verify status code is 400
3. Verify error message indicates both fields are required

**Expected Result:** HTTP 400

**Actual Result:** Pass

---

### TC-F006: Rate Limiting After 5 Failed Attempts

| Field | Value |
|-------|-------|
| **ID** | TC-F006 |
| **Title** | Account lockout triggers after 5 failures |
| **Priority** | P1 |
| **Preconditions** | App running, rate limit counter cleared |

**Steps:**
1. Send 5x POST /login with wrong password from the same IP
2. Send a 6th POST /login with wrong password
3. Verify 6th response status code is 429
4. Verify error message says "Too many failed attempts"

**Expected Result:** HTTP 429 on 6th attempt

**Actual Result:** Pass

---

### TC-F007: Rate Limit Resets on Successful Login

| Field | Value |
|-------|-------|
| **ID** | TC-F007 |
| **Title** | Successful login clears rate limit counter |
| **Priority** | P1 |
| **Preconditions** | App running |

**Steps:**
1. Send 4x POST /login with wrong password
2. Send POST /login with correct credentials
3. Verify success response (200)
4. Send POST /login with wrong password again
5. Verify status is 401 (not 429) — counter was reset

**Expected Result:** After success, fresh failure returns 401 not 429

**Actual Result:** Pass

---

### TC-F008: Authenticated Profile Access

| Field | Value |
|-------|-------|
| **ID** | TC-F008 |
| **Title** | Authenticated user can access their profile |
| **Priority** | P1 |
| **Preconditions** | App running |

**Steps:**
1. Send POST /login with valid user1 credentials
2. Send GET /profile using same session
3. Verify status code is 200
4. Verify `user` field matches logged-in username
5. Verify `role` field is present
6. Verify `login_time` field is present

**Expected Result:** HTTP 200, JSON with user, role, login_time fields

**Actual Result:** Pass

---

### TC-F009: Unauthenticated Profile Access

| Field | Value |
|-------|-------|
| **ID** | TC-F009 |
| **Title** | Profile endpoint rejects unauthenticated requests |
| **Priority** | P1 |
| **Preconditions** | App running, no active session |

**Steps:**
1. Send GET /profile without any prior login
2. Verify status code is 401
3. Verify error message is present

**Expected Result:** HTTP 401

**Actual Result:** Pass

---

### TC-F010: Logout Clears Session

| Field | Value |
|-------|-------|
| **ID** | TC-F010 |
| **Title** | Successful logout invalidates session |
| **Priority** | P1 |
| **Preconditions** | App running, user logged in |

**Steps:**
1. Login with valid admin credentials
2. Send POST /logout
3. Verify logout response is 200
4. Send GET /profile
5. Verify status code is 401 (session cleared)

**Expected Result:** POST /logout returns 200; subsequent GET /profile returns 401

**Actual Result:** Pass

---

### TC-F011: Admin User Accesses Admin Endpoint

| Field | Value |
|-------|-------|
| **ID** | TC-F011 |
| **Title** | Admin role grants access to /admin/users |
| **Priority** | P1 |
| **Preconditions** | App running |

**Steps:**
1. Login with admin credentials
2. Send GET /admin/users
3. Verify status code is 200
4. Verify response contains `users` array
5. Verify `admin` is in the users list

**Expected Result:** HTTP 200, users list returned

**Actual Result:** Pass

---

### TC-F012: Non-Admin Blocked from Admin Endpoint

| Field | Value |
|-------|-------|
| **ID** | TC-F012 |
| **Title** | Non-admin role blocked from /admin/users |
| **Priority** | P1 |
| **Preconditions** | App running |

**Steps:**
1. Login with user1 credentials (non-admin)
2. Send GET /admin/users
3. Verify status code is 403
4. Verify error says "Forbidden"

**Expected Result:** HTTP 403

**Actual Result:** Pass

---

### TC-F013: Health Check No Auth Required

| Field | Value |
|-------|-------|
| **ID** | TC-F013 |
| **Title** | Health endpoint accessible without authentication |
| **Priority** | P2 |
| **Preconditions** | App running |

**Steps:**
1. Without any session, send GET /health
2. Verify status code is 200
3. Verify `status` field is "healthy"
4. Verify `version` field is present

**Expected Result:** HTTP 200, `{"status": "healthy", "version": "1.0.0"}`

**Actual Result:** Pass

---

### TC-F014: Login Returns User Field on Success

| Field | Value |
|-------|-------|
| **ID** | TC-F014 |
| **Title** | Login response contains authenticated username |
| **Priority** | P2 |
| **Preconditions** | App running |

**Steps:**
1. Login with user1 credentials
2. Verify response JSON contains `user` field
3. Verify `user` equals `"user1"`

**Expected Result:** `{"message": "Login successful", "user": "user1"}`

**Actual Result:** Pass

---

### TC-F015: Concurrent Sessions Same User Different IPs

| Field | Value |
|-------|-------|
| **ID** | TC-F015 |
| **Title** | Multiple simultaneous sessions for same user are independent |
| **Priority** | P3 |
| **Preconditions** | App running, two isolated test clients |

**Steps:**
1. Create client A, login as admin with X-Forwarded-For: 10.0.0.1
2. Create client B, login as admin with X-Forwarded-For: 10.0.0.2
3. Verify both clients receive 200
4. Logout client A
5. Verify client A profile returns 401
6. Verify client B profile still returns 200

**Expected Result:** Sessions are independent; logout of one does not affect other

**Actual Result:** Pass

---

## 8. Security Test Cases

### TC-S001: SQL Injection in Username Field

| Field | Value |
|-------|-------|
| **ID** | TC-S001 |
| **Title** | SQL injection string in username is safely rejected |
| **Priority** | P1 |
| **OWASP** | A03:2021 – Injection |

**Test Vectors:**
- `' OR 1=1 --`
- `admin'--`
- `' UNION SELECT * FROM users --`

**Steps:**
1. Send POST /login with `{"username": "' OR 1=1 --", "password": "x"}`
2. Verify status is 400 or 401 (not 200, not 500)

**Expected Result:** 400 or 401, no server error

**Actual Result:** Pass

---

### TC-S002: SQL Injection in Password Field

| Field | Value |
|-------|-------|
| **ID** | TC-S002 |
| **Title** | SQL injection in password field is safely rejected |
| **Priority** | P1 |
| **OWASP** | A03:2021 – Injection |

**Steps:**
1. Send POST /login with `{"username": "admin", "password": "' OR '1'='1"}`
2. Verify status is 401 (not 200)

**Expected Result:** HTTP 401

**Actual Result:** Pass

---

### TC-S003: XSS Payload in Username

| Field | Value |
|-------|-------|
| **ID** | TC-S003 |
| **Title** | XSS payload is not reflected in response |
| **Priority** | P1 |
| **OWASP** | A03:2021 – Injection / A07:2021 – XSS |

**Test Vectors:**
- `<script>alert(1)</script>`
- `"><img src=x onerror=alert(1)>`
- `javascript:alert(document.cookie)`

**Steps:**
1. Send POST /login with XSS payload as username
2. Verify response status is 400 or 401
3. Verify `<script>` tag is NOT present in raw response bytes

**Expected Result:** Payload rejected; no script execution vectors in response

**Actual Result:** Pass

---

### TC-S004: Password Not Returned in Response

| Field | Value |
|-------|-------|
| **ID** | TC-S004 |
| **Title** | Plaintext password and hash never appear in any response |
| **Priority** | P1 |
| **OWASP** | A02:2021 – Cryptographic Failures |

**Steps:**
1. Send POST /login with admin credentials
2. Check response body for plaintext password string
3. Compute SHA-256 hash of password
4. Check response body for hash string
5. Verify neither appears

**Expected Result:** Neither plaintext password nor hash in any response

**Actual Result:** Pass

---

### TC-S005: Session Cookie HttpOnly Flag

| Field | Value |
|-------|-------|
| **ID** | TC-S005 |
| **Title** | Session cookie has HttpOnly flag set |
| **Priority** | P1 |
| **OWASP** | A07:2021 – Identification and Authentication Failures |

**Steps:**
1. Login via browser or requests session
2. Inspect Set-Cookie response header
3. Verify HttpOnly attribute is present
4. Verify Secure attribute is present (in HTTPS deployment)

**Expected Result:** `Set-Cookie: session=...; HttpOnly; Secure`

**Actual Result:** Pass (Flask sets HttpOnly by default)

---

### TC-S006: Null Bytes in Credentials

| Field | Value |
|-------|-------|
| **ID** | TC-S006 |
| **Title** | Null bytes in credentials handled gracefully |
| **Priority** | P1 |
| **OWASP** | A03:2021 – Injection |

**Steps:**
1. Send POST /login with `{"username": "admin\x00extra", "password": "test"}`
2. Verify status is 400 or 401
3. Verify status is NOT 500

**Expected Result:** Graceful rejection, no server error

**Actual Result:** Pass

---

### TC-S007: Very Long Username (1000 chars)

| Field | Value |
|-------|-------|
| **ID** | TC-S007 |
| **Title** | 1000-character username handled gracefully |
| **Priority** | P1 |
| **OWASP** | A04:2021 – Insecure Design (buffer handling) |

**Steps:**
1. Construct username string of 1000 'a' characters
2. Send POST /login with this username
3. Verify status is 400 or 401
4. Verify status is NOT 500

**Expected Result:** No crash, status 400 or 401

**Actual Result:** Pass

---

### TC-S008: Very Long Password (1000 chars)

| Field | Value |
|-------|-------|
| **ID** | TC-S008 |
| **Title** | 1000-character password handled gracefully |
| **Priority** | P1 |
| **OWASP** | A04:2021 – Insecure Design |

**Steps:**
1. Construct password string of 1000 'p' characters
2. Send POST /login with admin username and this password
3. Verify status is 401 (wrong password but no crash)

**Expected Result:** HTTP 401, no server error

**Actual Result:** Pass

---

### TC-S009: JSON Injection via Nested Objects

| Field | Value |
|-------|-------|
| **ID** | TC-S009 |
| **Title** | Nested JSON objects in credential fields are rejected |
| **Priority** | P1 |
| **OWASP** | A03:2021 – Injection |

**Steps:**
1. Send POST /login with `{"username": {"$ne": null}, "password": "x"}`
2. Verify status is 400 or 401
3. Verify status is NOT 500

**Expected Result:** Graceful rejection

**Actual Result:** Pass

---

### TC-S010: Rate Limiting Not Bypassed by Username Case

| Field | Value |
|-------|-------|
| **ID** | TC-S010 |
| **Title** | Rate limiting is IP-based and cannot be bypassed by changing username |
| **Priority** | P1 |
| **OWASP** | A07:2021 – Identification and Authentication Failures |

**Steps:**
1. Send 5x POST /login with `{"username": "admin", "password": "wrong"}` from same IP
2. Send POST /login with `{"username": "ADMIN", "password": "wrong"}` from same IP
3. Verify 6th request returns 429

**Expected Result:** Rate limit enforced regardless of username change

**Actual Result:** Pass

---

## 9. Performance Test Cases

### TC-P001: Single Login Response Time < 100ms

| Field | Value |
|-------|-------|
| **ID** | TC-P001 |
| **Title** | Login endpoint responds within 100ms |
| **Priority** | P2 |

**Steps:**
1. Record timestamp before POST /login
2. Execute successful login request
3. Record timestamp after response
4. Calculate elapsed time
5. Assert elapsed < 100ms

**Expected Result:** Response time under 100 milliseconds

**Actual Result:** Pass (~2-5ms typical)

---

### TC-P002: 10 Concurrent Login Requests Complete Within 2s

| Field | Value |
|-------|-------|
| **ID** | TC-P002 |
| **Title** | 10 concurrent requests handled within 2 seconds |
| **Priority** | P2 |

**Steps:**
1. Launch 10 threads each sending POST /login simultaneously
2. Record total wall-clock time from first request to last response
3. Assert total time < 2000ms

**Expected Result:** All 10 requests complete in under 2 seconds

**Actual Result:** Pass

---

### TC-P003: Health Check Response < 10ms

| Field | Value |
|-------|-------|
| **ID** | TC-P003 |
| **Title** | Health endpoint responds within 10ms |
| **Priority** | P3 |

**Steps:**
1. Time GET /health request
2. Assert elapsed < 10ms

**Expected Result:** Health check under 10ms

**Actual Result:** Pass (~0.5ms typical)

---

### TC-P004: Rate Limit Check Adds Minimal Overhead

| Field | Value |
|-------|-------|
| **ID** | TC-P004 |
| **Title** | Rate limiting check adds less than 5ms overhead |
| **Priority** | P3 |

**Steps:**
1. Time 100 login attempts with rate limit active
2. Calculate per-request overhead vs baseline
3. Assert overhead < 5ms

**Expected Result:** Overhead under 5ms

**Actual Result:** Pass

---

### TC-P005: 100 Sequential Requests Do Not Leak Memory

| Field | Value |
|-------|-------|
| **ID** | TC-P005 |
| **Title** | 100 sequential requests do not cause unbounded memory growth |
| **Priority** | P3 |

**Steps:**
1. Record process memory before loop
2. Execute 100 sequential login requests (mix of success and failure)
3. Record process memory after loop
4. Assert memory growth < 10MB

**Expected Result:** Memory stable, no leak

**Actual Result:** Pass

---

## 10. Defect Management

### 10.1 Defect Priority Definitions

| Priority | Definition | SLA |
|----------|------------|-----|
| **P1 – Critical** | Data loss, security breach, complete feature failure | Fix within 4 hours |
| **P2 – High** | Major functionality broken, workaround unavailable | Fix within 24 hours |
| **P3 – Medium** | Minor functionality issue, workaround exists | Fix within current sprint |
| **P4 – Low** | Cosmetic or documentation issue | Address in backlog |

### 10.2 Defect Lifecycle

```
New → Assigned → In Progress → Fixed → Verification → Closed
                    ↓
                Rejected / Won't Fix
```

---

## 11. Test Schedule

| Phase | Activities | Duration |
|-------|-----------|----------|
| Planning | Review requirements, write test plan | 2 days |
| Test Design | Write test cases, prepare test data | 3 days |
| Test Execution | Run all test suites | 2 days |
| Defect Resolution | Fix and retest P1/P2 defects | 2 days |
| Sign-off | Review results, update traceability matrix | 1 day |

**Total Estimated Duration:** 10 business days

---

## 12. Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Rate limit counter not reset between tests | High | High | Use autouse fixture to clear LOGIN_ATTEMPTS before each test |
| Session state bleeds across test cases | Medium | High | Use fresh test client per test class |
| Timing assertions flaky in CI | Medium | Low | Use generous thresholds; note typical values in docs |
| Rate limit window of 300s makes cleanup tests slow | Low | Medium | Inject frozen time or clear state via fixture |

---

## 13. Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| QA Lead | J. Martinez | Approved | 2026-01-15 |
| Dev Lead | S. Patel | Approved | 2026-01-15 |
| Security | R. Kim | Approved | 2026-01-15 |
| Product Owner | T. Williams | Approved | 2026-01-16 |

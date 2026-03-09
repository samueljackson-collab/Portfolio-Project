# Test Plan: Web Application Login Functionality

**Project:** Web Application Security & Functionality Testing
**Component:** User Authentication System
**Test Level:** System Integration Testing
**Test Type:** Functional, Security, Performance
**Version:** 1.0
**Date:** November 6, 2025
**Author:** Sam Jackson

---

## 1. Executive Summary

### 1.1 Purpose
Comprehensive testing of web application login functionality to ensure:
- **Functional correctness** (valid users can log in)
- **Security posture** (invalid access prevented, credentials protected)
- **Performance standards** (response time <2s, supports 100 concurrent users)
- **User experience** (clear error messages, accessibility standards met)

### 1.2 Scope

**In Scope:**
- Login form (username/email + password)
- Authentication API endpoint (`POST /api/auth/login`)
- Session management (cookie/token issuance)
- Password reset flow ("Forgot Password" link)
- "Remember Me" functionality
- Account lockout after failed attempts
- Multi-factor authentication (MFA) if enabled
- OAuth/SSO integration (Google, GitHub) if present

**Out of Scope:**
- User registration (separate test plan)
- Profile management post-login
- Backend database testing (unit test coverage)
- Third-party identity provider internal testing

### 1.3 Test Environment

| Component | Specification |
|-----------|---------------|
| **Application URL** | https://staging.example.com |
| **Backend API** | https://api.staging.example.com/v1 |
| **Test Environment** | AWS EC2 t3.medium (2 vCPU, 4GB RAM) |
| **Database** | PostgreSQL 14.5 (staging instance) |
| **Load Balancer** | AWS ALB (Application Load Balancer) |
| **Session Store** | Redis 7.0 |
| **CDN** | CloudFlare (for static assets) |

**Test Data Environment:**
- **Staging database** with anonymized production data
- **Test users** created specifically for testing (auto-cleanup)
- **Isolated from production** (separate AWS account)

### 1.4 Test Schedule

| Phase | Start Date | End Date | Duration |
|-------|-----------|----------|----------|
| Test Plan Review | Nov 6, 2025 | Nov 7, 2025 | 1 day |
| Test Case Development | Nov 8, 2025 | Nov 10, 2025 | 3 days |
| Test Environment Setup | Nov 11, 2025 | Nov 12, 2025 | 2 days |
| Test Execution (Manual) | Nov 13, 2025 | Nov 15, 2025 | 3 days |
| Test Execution (Automated) | Nov 16, 2025 | Nov 17, 2025 | 2 days |
| Performance Testing | Nov 18, 2025 | Nov 18, 2025 | 1 day |
| Security Testing | Nov 19, 2025 | Nov 19, 2025 | 1 day |
| Defect Retesting | Nov 20, 2025 | Nov 21, 2025 | 2 days |
| Test Report | Nov 22, 2025 | Nov 22, 2025 | 1 day |
| **Total** | | | **15 days** |

---

## 2. Test Strategy

### 2.1 Test Levels

| Test Level | Responsibility | Tools |
|-----------|----------------|-------|
| **Unit Testing** | Development team | Jest, PyTest |
| **Integration Testing** | QA team (this plan) | Postman, Selenium |
| **Performance Testing** | QA team | JMeter, Locust |
| **Security Testing** | QA + Security team | Burp Suite, OWASP ZAP |
| **User Acceptance** | Product owner + stakeholders | Manual testing |

### 2.2 Test Types

#### 2.2.1 Functional Testing
- **Positive testing:** Valid credentials → successful login
- **Negative testing:** Invalid credentials → appropriate error
- **Boundary testing:** Max length inputs, special characters
- **State testing:** Session persistence, logout behavior

#### 2.2.2 Security Testing
- **Authentication bypass** attempts (SQL injection, auth bypass)
- **Brute force protection** (account lockout after N failed attempts)
- **Password security** (hashing verification, no plaintext storage)
- **Session security** (HTTPS only, HttpOnly cookies, CSRF tokens)
- **OWASP Top 10** vulnerability scan

#### 2.2.3 Performance Testing
- **Load testing:** 100 concurrent users logging in simultaneously
- **Stress testing:** Increase load until failure (find breaking point)
- **Spike testing:** Sudden traffic surge (e.g., 0→500 users in 10s)
- **Endurance testing:** Sustained load for 1 hour (memory leaks)

#### 2.2.4 Usability/Accessibility Testing
- **WCAG 2.1 Level AA compliance** (keyboard navigation, screen readers)
- **Error message clarity** (user-friendly, actionable)
- **Mobile responsiveness** (iOS Safari, Android Chrome)
- **Browser compatibility** (Chrome, Firefox, Safari, Edge)

### 2.3 Entry Criteria

Testing will begin when:
- [ ] Login feature deployed to staging environment
- [ ] API documentation provided (Swagger/OpenAPI spec)
- [ ] Test user accounts created in staging database
- [ ] Test cases reviewed and approved by product owner
- [ ] All P0/P1 bugs from previous sprint resolved

### 2.4 Exit Criteria

Testing complete when:
- [ ] 100% of test cases executed
- [ ] Pass rate ≥95% (critical path tests)
- [ ] No P0 (critical) or P1 (high) defects open
- [ ] Performance benchmarks met (login <2s, 100 concurrent users)
- [ ] Security scan shows no critical/high vulnerabilities
- [ ] Test summary report approved by stakeholders

### 2.5 Suspension & Resumption Criteria

**Suspend testing if:**
- Critical environment issue (database down, API unavailable)
- >25% test failures indicate systemic issue
- Major blocking defect preventing test execution
- Test data corruption requiring refresh

**Resume testing when:**
- Environment restored and verified stable
- Blocking defects resolved and deployed
- Test data refreshed and validated

---

## 3. Test Deliverables

| Deliverable | Format | Recipient | Delivery Date |
|------------|--------|-----------|---------------|
| Test Plan | Markdown/PDF | Product Owner, Dev Lead | Nov 7, 2025 |
| Test Cases | Excel/Google Sheets | QA Team, Dev Team | Nov 10, 2025 |
| Test Scripts (Automated) | Python (Selenium) | QA Team, CI/CD pipeline | Nov 17, 2025 |
| Defect Reports | Jira tickets | Dev Team, Product Owner | Ongoing |
| Performance Test Results | JMeter HTML report | Dev Lead, Ops Team | Nov 18, 2025 |
| Security Scan Report | PDF (Burp Suite) | Security Team, CISO | Nov 19, 2025 |
| Test Summary Report | Markdown/PDF | All stakeholders | Nov 22, 2025 |

---

## 4. Test Cases

### 4.1 Functional Test Cases

#### TC-001: Successful Login with Valid Credentials
**Priority:** CRITICAL
**Type:** Functional - Positive

**Preconditions:**
- User account exists: `testuser@example.com` / `SecurePass123!`
- User is not already logged in
- No account lockout active

**Test Steps:**
1. Navigate to https://staging.example.com/login
2. Enter email: `testuser@example.com`
3. Enter password: `SecurePass123!`
4. Click "Log In" button
5. Wait for redirect

**Expected Results:**
- ✅ User redirected to dashboard: `/dashboard`
- ✅ HTTP 200 response from `/api/auth/login`
- ✅ Session cookie set: `session_id` (HttpOnly, Secure)
- ✅ User profile visible in top-right corner
- ✅ Login page no longer accessible (auto-redirect to dashboard if authenticated)

**Actual Results:** _[Fill during execution]_
**Status:** ⬜ PASS / ⬜ FAIL / ⬜ BLOCKED

**Automation:** Yes (Selenium)

---

#### TC-002: Failed Login with Invalid Password
**Priority:** CRITICAL
**Type:** Functional - Negative

**Preconditions:**
- User account exists: `testuser@example.com`
- User is not logged in

**Test Steps:**
1. Navigate to https://staging.example.com/login
2. Enter email: `testuser@example.com`
3. Enter password: `WrongPassword999`
4. Click "Log In" button

**Expected Results:**
- ✅ HTTP 401 Unauthorized from API
- ✅ Error message displayed: "Invalid email or password"
- ✅ No session cookie set
- ✅ User remains on login page
- ✅ Password field cleared for security
- ✅ Email field retains value (UX improvement)

**Actual Results:** _[Fill during execution]_
**Status:** ⬜ PASS / ⬜ FAIL / ⬜ BLOCKED

**Automation:** Yes (Selenium)

---

#### TC-003: Failed Login with Non-Existent User
**Priority:** HIGH
**Type:** Functional - Negative

**Preconditions:**
- Email `nonexistent@example.com` does NOT exist in database

**Test Steps:**
1. Navigate to login page
2. Enter email: `nonexistent@example.com`
3. Enter password: `AnyPassword123`
4. Click "Log In"

**Expected Results:**
- ✅ HTTP 401 Unauthorized
- ✅ Generic error message: "Invalid email or password" (don't reveal user existence)
- ✅ Response time similar to valid user (prevent user enumeration via timing attack)
- ✅ No session cookie set

**Actual Results:** _[Fill during execution]_
**Status:** ⬜ PASS / ⬜ FAIL / ⬜ BLOCKED

**Security Note:** Error message should NOT distinguish between "user not found" vs. "wrong password" to prevent account enumeration.

---

#### TC-004: Account Lockout After Failed Attempts
**Priority:** HIGH
**Type:** Security - Brute Force Protection

**Preconditions:**
- User account exists: `lockouttest@example.com`
- Account lockout threshold: 5 failed attempts
- Lockout duration: 15 minutes

**Test Steps:**
1. Attempt login with wrong password (5 times consecutively)
2. On 6th attempt, use correct password
3. Wait 15 minutes
4. Attempt login with correct password again

**Expected Results:**
- ✅ After 5 failed attempts: HTTP 403 Forbidden
- ✅ Error message: "Account locked due to too many failed login attempts. Try again in 15 minutes."
- ✅ 6th login with correct password still fails (locked)
- ✅ Email notification sent to user about account lockout
- ✅ After 15 minutes, account automatically unlocked
- ✅ Login succeeds after lockout expires

**Actual Results:** _[Fill during execution]_
**Status:** ⬜ PASS / ⬜ FAIL / ⬜ BLOCKED

**Automation:** Yes (API test script)

---

#### TC-005: "Remember Me" Functionality
**Priority:** MEDIUM
**Type:** Functional

**Preconditions:**
- User account exists
- "Remember Me" checkbox present on login form

**Test Steps:**
1. Login with valid credentials
2. Check "Remember Me" checkbox
3. Close browser completely
4. Re-open browser and navigate to application
5. Observe if still logged in

**Expected Results:**
- ✅ Session persists after browser restart
- ✅ Cookie expiration set to 30 days (not session-only)
- ✅ Unchecked: Session expires when browser closes (session cookie)

**Actual Results:** _[Fill during execution]_
**Status:** ⬜ PASS / ⬜ FAIL / ⬜ BLOCKED

---

#### TC-006: Password Reset Flow
**Priority:** HIGH
**Type:** Functional

**Preconditions:**
- User account exists: `resettest@example.com`
- Email server accessible (or mock server for testing)

**Test Steps:**
1. Click "Forgot Password?" link on login page
2. Enter email: `resettest@example.com`
3. Submit form
4. Check email for reset link
5. Click reset link
6. Enter new password: `NewSecurePass456!`
7. Confirm password
8. Submit
9. Login with new password

**Expected Results:**
- ✅ HTTP 200 from password reset request API
- ✅ Email received within 2 minutes
- ✅ Reset link contains unique token (UUID format)
- ✅ Reset link expires after 1 hour
- ✅ New password successfully set
- ✅ Old password no longer works
- ✅ New password allows successful login
- ✅ Reset link becomes invalid after use (one-time use)

**Actual Results:** _[Fill during execution]_
**Status:** ⬜ PASS / ⬜ FAIL / ⬜ BLOCKED

---

#### TC-007: Multi-Factor Authentication (MFA)
**Priority:** HIGH
**Type:** Security

**Preconditions:**
- User account has MFA enabled (TOTP via Google Authenticator)
- Correct credentials known

**Test Steps:**
1. Login with valid email/password
2. Enter 6-digit TOTP code from authenticator app
3. Submit

**Expected Results:**
- ✅ After correct email/password: Redirected to MFA input page
- ✅ Session not fully established until MFA verified
- ✅ Correct TOTP code: Login succeeds
- ✅ Incorrect TOTP code: Error message, remain on MFA page
- ✅ Expired TOTP code (>30s old): Rejected
- ✅ TOTP code cannot be reused

**Actual Results:** _[Fill during execution]_
**Status:** ⬜ PASS / ⬜ FAIL / ⬜ BLOCKED

---

#### TC-008: Session Timeout
**Priority:** MEDIUM
**Type:** Security

**Preconditions:**
- User logged in
- Session timeout: 30 minutes of inactivity

**Test Steps:**
1. Login successfully
2. Wait 30 minutes without interacting
3. Attempt to access protected page (e.g., `/dashboard`)

**Expected Results:**
- ✅ After 30 min inactivity: Session expired
- ✅ Redirect to login page
- ✅ Message: "Your session has expired. Please log in again."
- ✅ Activity (page refresh, API call) resets timeout counter

**Actual Results:** _[Fill during execution]_
**Status:** ⬜ PASS / ⬜ FAIL / ⬜ BLOCKED

---

#### TC-009: OAuth/SSO Login (Google)
**Priority:** HIGH
**Type:** Integration

**Preconditions:**
- OAuth integration configured (Google)
- Test Google account: `testuser@gmail.com`

**Test Steps:**
1. Click "Sign in with Google" button
2. Redirected to Google login
3. Enter Google credentials
4. Authorize application access
5. Redirected back to application

**Expected Results:**
- ✅ Redirect to `accounts.google.com`
- ✅ After Google auth: Redirect to application callback URL
- ✅ User profile created/updated in application database
- ✅ Session established (same as email/password login)
- ✅ User dashboard accessible

**Actual Results:** _[Fill during execution]_
**Status:** ⬜ PASS / ⬜ FAIL / ⬜ BLOCKED

---

#### TC-010: Input Validation - SQL Injection Attempt
**Priority:** CRITICAL
**Type:** Security

**Preconditions:**
- None (testing malicious input handling)

**Test Steps:**
1. Enter email: `' OR '1'='1' --`
2. Enter password: `anything`
3. Submit login form

**Expected Results:**
- ✅ Input sanitized/escaped before database query
- ✅ Login fails with "Invalid email or password"
- ✅ No database error exposed to user
- ✅ Backend logs show attempted SQL injection (for security monitoring)
- ✅ No successful authentication

**Actual Results:** _[Fill during execution]_
**Status:** ⬜ PASS / ⬜ FAIL / ⬜ BLOCKED

**Related Tests:**
- XSS injection: `<script>alert('XSS')</script>`
- LDAP injection: `*)(uid=*)`
- Command injection: `; ls -la`

---

### 4.2 Performance Test Cases

#### TC-PERF-001: Login Response Time (Single User)
**Priority:** HIGH
**Type:** Performance

**Test Configuration:**
- 1 user
- Valid credentials
- Measure end-to-end time (submit click → dashboard load)

**Acceptance Criteria:**
- ✅ 95th percentile: <2 seconds
- ✅ 99th percentile: <3 seconds
- ✅ Average: <1.5 seconds

**Execution:**
```bash
# JMeter test plan
jmeter -n -t login-performance.jmx -l results.jtl
```

**Status:** ⬜ PASS / ⬜ FAIL

---

#### TC-PERF-002: Concurrent User Load (100 Users)
**Priority:** CRITICAL
**Type:** Performance - Load

**Test Configuration:**
- 100 concurrent users
- All submit login form simultaneously
- Duration: 5 minutes sustained load
- Ramp-up: 10 seconds (0→100 users)

**Acceptance Criteria:**
- ✅ All requests complete successfully (0% error rate)
- ✅ Average response time: <3 seconds
- ✅ 95th percentile: <5 seconds
- ✅ CPU usage: <70% on application servers
- ✅ Database connections: <200 active

**Metrics to Monitor:**
| Metric | Target | Threshold |
|--------|--------|-----------|
| Throughput | >20 req/s | Fail if <15 req/s |
| Error Rate | 0% | Fail if >1% |
| Response Time (avg) | <3s | Fail if >5s |
| CPU Utilization | <70% | Warn if >80% |
| Memory Usage | <80% | Warn if >90% |

**Status:** ⬜ PASS / ⬜ FAIL

---

#### TC-PERF-003: Stress Test (Find Breaking Point)
**Priority:** MEDIUM
**Type:** Performance - Stress

**Test Configuration:**
- Start: 100 users
- Increment: +50 users every 2 minutes
- Continue until errors >5% or timeout

**Goal:** Identify maximum capacity before degradation

**Expected Result:**
- Document maximum concurrent users supported
- Identify bottleneck (CPU, memory, database connections, network)

**Status:** ⬜ PASS / ⬜ FAIL

---

### 4.3 Usability Test Cases

#### TC-UI-001: Keyboard Navigation
**Priority:** MEDIUM
**Type:** Accessibility

**Test Steps:**
1. Navigate to login page
2. Press Tab key to cycle through elements
3. Press Enter to submit form

**Expected Results:**
- ✅ Tab order: Email → Password → Remember Me → Submit → Forgot Password
- ✅ Focus indicators visible (outline/highlight)
- ✅ Enter key submits form from any input field

**Status:** ⬜ PASS / ⬜ FAIL

---

#### TC-UI-002: Screen Reader Compatibility
**Priority:** MEDIUM
**Type:** Accessibility

**Tools:** NVDA (Windows), VoiceOver (Mac)

**Expected Results:**
- ✅ Form labels properly associated with inputs
- ✅ Error messages announced by screen reader
- ✅ Button purposes clear ("Submit Login Form")
- ✅ ARIA labels present where needed

**Status:** ⬜ PASS / ⬜ FAIL

---

#### TC-UI-003: Mobile Responsiveness
**Priority:** HIGH
**Type:** Usability

**Devices:** iPhone 13 (iOS 16), Samsung Galaxy S21 (Android 12)

**Expected Results:**
- ✅ Form elements sized appropriately (min 44×44px touch targets)
- ✅ No horizontal scrolling required
- ✅ Text readable without zoom (min 14px font)
- ✅ Submit button accessible without keyboard obscuring input

**Status:** ⬜ PASS / ⬜ FAIL

---

## 5. Defect Management

### 5.1 Defect Severity Classification

| Severity | Description | Example | Response Time |
|----------|-------------|---------|---------------|
| **P0 - Critical** | Complete feature failure, security vulnerability | Login broken for all users, SQL injection possible | 4 hours |
| **P1 - High** | Major functionality impaired, workaround exists | MFA not working, password reset broken | 24 hours |
| **P2 - Medium** | Minor functionality issue, cosmetic defect | Error message typo, slow response (3-5s) | 3 days |
| **P3 - Low** | Enhancement request, edge case | Improved UX suggestion, rare browser issue | 1 week |

### 5.2 Defect Reporting Template

```markdown
**Defect ID:** [AUTO-GENERATED]
**Summary:** [One-line description]
**Severity:** P0/P1/P2/P3
**Component:** Login Authentication
**Environment:** Staging (AWS)
**Test Case:** TC-XXX

**Steps to Reproduce:**
1. Step 1
2. Step 2
3. Step 3

**Expected Result:** [What should happen]
**Actual Result:** [What actually happened]

**Screenshots:** [Attach if applicable]
**Logs:** [API response, browser console errors]
**Browser/Device:** Chrome 119 / Windows 11

**Suggested Fix:** [Optional]
```

---

## 6. Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Staging environment downtime | High | Medium | Backup environment in Docker Compose locally |
| Test data corruption | Medium | Low | Automated database refresh script |
| Incomplete requirements | High | Medium | Clarify with product owner before test execution |
| Third-party OAuth downtime (Google) | Medium | Low | Test with mock OAuth server |
| Security vulnerabilities discovered | High | Medium | Dedicated security testing phase, pen test engagement |

---

## 7. Test Metrics

### 7.1 Metrics to Track

| Metric | Target | Measurement |
|--------|--------|-------------|
| Test Case Execution Rate | 100% | (Executed / Total) × 100 |
| Pass Rate | ≥95% | (Passed / Executed) × 100 |
| Defect Detection Rate | N/A | Defects found / Test cases executed |
| Defect Fix Rate | 100% P0/P1 | Fixed defects / Total defects |
| Test Automation Coverage | ≥80% | Automated test cases / Total test cases |

### 7.2 Sample Metrics Dashboard

```
Total Test Cases: 45
Executed: 45 (100%)
Passed: 43 (95.6%)
Failed: 2 (4.4%)
Blocked: 0 (0%)

Defects Found: 7
  P0: 0
  P1: 1 (Fixed)
  P2: 4 (2 Fixed, 2 Open)
  P3: 2 (Open)

Performance:
  Avg Login Time: 1.2s ✅
  100 Concurrent Users: 2.8s avg ✅
  Error Rate: 0.2% ✅

Security:
  Critical Vulnerabilities: 0 ✅
  High Vulnerabilities: 0 ✅
  Medium Vulnerabilities: 1 (Accepted risk)
```

---

## 8. Test Tools

| Tool | Purpose | License |
|------|---------|---------|
| **Selenium WebDriver** | Automated functional testing | Open Source |
| **Pytest** | Test framework (Python) | Open Source |
| **Postman/Newman** | API testing | Free tier |
| **JMeter** | Performance/load testing | Open Source |
| **Burp Suite Community** | Security scanning | Free |
| **OWASP ZAP** | Security testing | Open Source |
| **Lighthouse** | Accessibility auditing | Open Source |
| **BrowserStack** | Cross-browser testing | Paid subscription |
| **Jira** | Defect tracking | Paid subscription |

---

## 9. Approval & Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **QA Lead** | Sam Jackson | _____________ | ______ |
| **Product Owner** | _____________ | _____________ | ______ |
| **Development Lead** | _____________ | _____________ | ______ |
| **Security Lead** | _____________ | _____________ | ______ |

---

## 10. References

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [JMeter Best Practices](https://jmeter.apache.org/usermanual/best-practices.html)

---

**Document Version:** 1.0
**Last Updated:** November 6, 2025
**Next Review:** February 6, 2026
**Document Owner:** Sam Jackson, QA Engineer

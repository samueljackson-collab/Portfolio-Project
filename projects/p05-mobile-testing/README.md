# P05 — Mobile App Manual Testing

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


## Overview

Comprehensive manual testing approach for mobile applications (iOS/Android) covering functional,
usability, compatibility, and regression testing. Demonstrates test planning, charter-based
exploratory testing, defect reporting, and device matrix management for quality assurance roles.

## Key Outcomes

- [x] Test charter template for exploratory testing sessions
- [x] Device/OS compatibility matrix (iOS 14-17, Android 10-14)
- [x] Sample defect reports with reproduction steps
- [x] Regression test checklist (critical user flows)
- [x] Test case repository (login, signup, checkout, notifications)

## Architecture

- **Components**: Mobile app (iOS/Android), Test management (Jira/TestRail), Device farm
- **Test environments**: Dev, Staging, Production-like
- **Dependencies**: Physical devices, emulators (Android Studio/Xcode), Charles Proxy

```mermaid
flowchart LR
    subgraph TestPlan[Test Planning]
        Charter[Test Charters]
        Matrix[Device Matrix]
        Cases[Test Cases]
    end

    subgraph Execution[Test Execution]
        Manual[Manual Testing]
        Explore[Exploratory Testing]
        Regress[Regression Testing]
    end

    subgraph Reporting[Defect Management]
        Defects[Defect Reports]
        Metrics[Test Metrics]
        Sign[Sign-off]
    end

    TestPlan --> Execution
    Execution --> Reporting

    style Manual fill:#4CAF50
    style Defects fill:#E53935
```text

## Quickstart

```bash
# Review test charter template
cat docs/test-charter-template.md

# Check device matrix
cat config/device-matrix.csv

# Review sample test cases
cat test-cases/login-flow.md
```text

## Configuration

| Artifact | Purpose | Location |
|----------|---------|----------|
| Test Charters | Exploratory testing sessions | `docs/test-charters/` |
| Device Matrix | Supported devices/OS versions | `config/device-matrix.csv` |
| Test Cases | Functional test scenarios | `test-cases/` |
| Defect Reports | Sample bug reports | `defects/` |

## Testing

### Test Charter Example

**Mission**: Explore login functionality for security and usability issues.
**Areas**: Login screen, forgot password, biometric auth, session handling.
**Time**: 90 minutes.
**Risks**: SQL injection, weak password validation, session hijacking.

### Device Matrix

| Device | OS Version | Screen Size | Priority | Status |
|--------|-----------|-------------|----------|--------|
| iPhone 15 Pro | iOS 17 | 6.1" | P0 | ✓ Tested |
| iPhone 12 | iOS 16 | 6.1" | P1 | ✓ Tested |
| Samsung S23 | Android 14 | 6.1" | P0 | ✓ Tested |
| Pixel 7 | Android 13 | 6.3" | P1 | Pending |

### Sample Defect Report

**Title**: [Login] User remains logged in after password reset on another device
**Severity**: High
**Steps to Reproduce**:

1. Log in on Device A with user credentials
2. On Device B, initiate password reset via email
3. Complete password reset on Device B
4. Return to Device A - observe user is still logged in
**Expected**: Device A should force re-authentication after password reset
**Actual**: Device A session remains active (security risk)

## Operations

### Test Cycle Management

1. **Test Planning**: Define scope, create charters, identify devices
2. **Execution**: Run test cases, perform exploratory testing, log defects
3. **Regression**: Re-test critical flows before release
4. **Sign-off**: Review metrics (pass rate, defect density), approve/reject build

### Common Issues & Fixes

**Issue**: App crashes on iOS 14 but works on iOS 17
**Fix**: Check deprecated API usage, memory leaks on older OS versions.

**Issue**: UI elements overlap on small screens (iPhone SE)
**Fix**: Verify responsive layout constraints, test edge cases (small/large screens).

## Roadmap

- [ ] Automated screenshot comparison (visual regression)
- [ ] Integration with CI/CD (trigger smoke tests on build)
- [ ] Performance testing (app launch time, memory usage)

## References

- [iOS Testing Best Practices](https://developer.apple.com/library/archive/documentation/DeveloperTools/Conceptual/testing_with_xcode/)
- [Android Testing Fundamentals](https://developer.android.com/training/testing/fundamentals)
- [RUNBOOK](./RUNBOOK.md) | [HANDBOOK](./HANDBOOK.md)

## Code Generation Prompts

This section contains AI-assisted code generation prompts that can help you recreate or extend project components. These prompts are designed to work with AI coding assistants like Claude, GPT-4, or GitHub Copilot.

### Test Automation

#### 1. End-to-End Tests

```text
Create Playwright tests for a login flow, including form validation, authentication error handling, and successful redirect to dashboard
```text

#### 2. API Tests

```text
Generate pytest-based API tests that verify REST endpoints for CRUD operations, including request/response validation, error cases, and authentication
```text

#### 3. Performance Tests

```text
Write a Locust load test that simulates 100 concurrent users performing read/write operations, measures response times, and identifies bottlenecks
```text

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
- [Screenshot](./docs/evidence/screenshot.svg)
- [Run log](./docs/evidence/run-log.txt)
- [Dashboard export](./docs/evidence/dashboard-export.json)
- [Load test summary](./docs/evidence/load-test-summary.txt)

### Evidence Checklist

| Evidence Item | Location | Status |
| --- | --- | --- |
| Screenshot captured | `docs/evidence/screenshot.svg` | ✅ |
| Run log captured | `docs/evidence/run-log.txt` | ✅ |
| Dashboard export captured | `docs/evidence/dashboard-export.json` | ✅ |
| Load test summary captured | `docs/evidence/load-test-summary.txt` | ✅ |

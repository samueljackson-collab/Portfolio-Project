# Test Case: Login Flow

**Test Case ID**: TC-LOGIN-001
**Feature**: User Authentication
**Priority**: P0 (Critical)
**Preconditions**: App installed, user account exists (`testuser@example.com` / `TestPass123!`)

---

## TC-LOGIN-001: Successful login with valid credentials

**Steps**:

1. Launch app
2. Tap "Log In" button
3. Enter email: `testuser@example.com`
4. Enter password: `TestPass123!`
5. Tap "Submit"

**Expected Result**:

- User redirected to home screen
- Username displayed in top right corner
- Session persists after app restart

**Status**: ✓ Pass

---

## TC-LOGIN-002: Login failure with invalid password

**Steps**:

1. Launch app
2. Tap "Log In" button
3. Enter email: `testuser@example.com`
4. Enter password: `WrongPassword`
5. Tap "Submit"

**Expected Result**:

- Error message displayed: "Invalid email or password"
- User remains on login screen
- Password field cleared

**Status**: ✓ Pass

---

## TC-LOGIN-003: Forgot password flow

**Steps**:

1. On login screen, tap "Forgot Password?"
2. Enter email: `testuser@example.com`
3. Tap "Send Reset Link"
4. Check email inbox

**Expected Result**:

- Success message: "Password reset link sent to your email"
- Email received within 2 minutes
- Reset link opens app with reset form

**Status**: ⚠ Pending email integration test

---

## TC-LOGIN-004: Biometric login (Face ID / Fingerprint)

**Preconditions**: User previously enabled biometric auth in settings

**Steps**:

1. Launch app
2. Observe biometric prompt appears automatically
3. Authenticate with Face ID / Fingerprint

**Expected Result**:

- Biometric prompt displayed
- On success, user redirected to home screen
- On failure, fallback to password login

**Status**: ✓ Pass (iOS 17, Android 14)

---

## TC-LOGIN-005: Session timeout after inactivity

**Steps**:

1. Log in successfully
2. Leave app in background for 30 minutes
3. Return to app

**Expected Result**:

- User redirected to login screen
- Session expired message displayed (optional)
- No sensitive data visible

**Status**: ✗ Fail - BUG-201: Session persists beyond timeout

---

## Test Summary

- **Total**: 5 test cases
- **Passed**: 3
- **Failed**: 1
- **Pending**: 1
- **Pass Rate**: 60%

# Mobile App Manual Test Plan

## Test Environment
- **Platform**: iOS 14+, Android 11+
- **Devices**: iPhone 12, Samsung Galaxy S21, iPad Air
- **Test Build**: v1.0.0-beta

## Test Cases

| Test ID | Category | Description | Preconditions | Steps | Expected Result | Pass/Fail | Notes |
|---------|----------|-------------|---------------|-------|-----------------|-----------|-------|
| TC-001 | Authentication | User login with valid credentials | App installed, user registered | 1. Launch app<br>2. Enter valid username<br>3. Enter valid password<br>4. Tap Login | User successfully logged in, redirected to home screen | | |
| TC-002 | Authentication | User login with invalid password | App installed, user registered | 1. Launch app<br>2. Enter valid username<br>3. Enter invalid password<br>4. Tap Login | Error message displayed: "Invalid credentials" | | |
| TC-003 | Authentication | User logout | User logged in | 1. Tap profile icon<br>2. Tap Logout<br>3. Confirm logout | User logged out, redirected to login screen | | |
| TC-004 | Authentication | Password reset | User registered | 1. Tap "Forgot Password"<br>2. Enter email<br>3. Tap Submit<br>4. Check email | Reset link sent, email received within 2 minutes | | |
| TC-005 | Core Flow | Create new item | User logged in | 1. Tap "+" button<br>2. Fill in required fields<br>3. Tap Save | Item created successfully, appears in list | | |
| TC-006 | Core Flow | Edit existing item | User logged in, item exists | 1. Tap on item<br>2. Tap Edit<br>3. Modify fields<br>4. Tap Save | Item updated successfully, changes reflected | | |
| TC-007 | Core Flow | Delete item | User logged in, item exists | 1. Swipe left on item<br>2. Tap Delete<br>3. Confirm deletion | Item removed from list, confirmation shown | | |
| TC-008 | Core Flow | Search functionality | User logged in, multiple items exist | 1. Tap search icon<br>2. Enter search term<br>3. View results | Relevant items displayed, others hidden | | |
| TC-009 | Core Flow | Filter by category | User logged in, multiple categories | 1. Tap filter icon<br>2. Select category<br>3. Apply filter | Only items in selected category shown | | |
| TC-010 | Core Flow | Sort items | User logged in, multiple items | 1. Tap sort icon<br>2. Select sort option (date/name)<br>3. View results | Items displayed in selected order | | |
| TC-011 | Edge Cases | Network offline - create item | User logged in, no network | 1. Disable network<br>2. Create item<br>3. Tap Save | Item saved locally, sync pending indicator shown | | |
| TC-012 | Edge Cases | Network offline - view cached data | User logged in, no network, data cached | 1. Disable network<br>2. View items list | Cached data displayed, offline indicator shown | | |
| TC-013 | Edge Cases | Resume from background | App in background | 1. Send app to background<br>2. Wait 30 seconds<br>3. Resume app | App resumes correctly, data not lost | | |
| TC-014 | Edge Cases | Low memory condition | Many apps running | 1. Open multiple apps<br>2. Return to test app | App handles low memory gracefully, no crash | | |
| TC-015 | Edge Cases | Long text input | User on input screen | 1. Enter 1000+ character text<br>2. Save | Text saved correctly, displays properly | | |
| TC-016 | Edge Cases | Special characters | User on input screen | 1. Enter unicode, emoji, symbols<br>2. Save | Special characters handled correctly | | |
| TC-017 | Error Handling | API timeout | User attempting action | 1. Simulate slow network<br>2. Attempt API call | Timeout message shown, retry option available | | |
| TC-018 | Error Handling | Server error (500) | User attempting action | 1. Trigger server error<br>2. View response | Error message displayed, action can be retried | | |
| TC-019 | Error Handling | Invalid data format | User entering data | 1. Enter invalid email format<br>2. Tap Save | Validation error shown, field highlighted | | |
| TC-020 | Error Handling | Session expiry | User logged in, session expired | 1. Wait for session timeout<br>2. Attempt action | Prompted to re-login, original action queued | | |
| TC-021 | Permissions | Camera access | User needs camera | 1. Tap take photo<br>2. Grant camera permission | Camera opens, photo can be taken | | |
| TC-022 | Permissions | Location access | User needs location | 1. Tap use location<br>2. Grant location permission | Location detected and used correctly | | |
| TC-023 | Permissions | Notifications | User receives notification | 1. Enable notifications<br>2. Trigger notification | Notification received and displayed | | |
| TC-024 | UI/UX | Landscape orientation | User on any screen | 1. Rotate device to landscape | Layout adjusts appropriately, no UI breaks | | |
| TC-025 | UI/UX | Dark mode | User in settings | 1. Enable dark mode<br>2. Navigate through app | All screens display in dark mode correctly | | |
| TC-026 | UI/UX | Accessibility - VoiceOver | VoiceOver enabled | 1. Enable VoiceOver<br>2. Navigate app | All elements properly labeled and accessible | | |
| TC-027 | UI/UX | Accessibility - Large text | Large text enabled in OS | 1. Enable large text<br>2. Open app | Text scales appropriately, no overflow | | |
| TC-028 | Performance | App launch time | App closed | 1. Launch app<br>2. Measure time to interactive | App launches within 3 seconds | | |
| TC-029 | Performance | List scrolling | Large list loaded | 1. Scroll through 1000+ items<br>2. Observe smoothness | Scrolling is smooth, 60fps maintained | | |
| TC-030 | Performance | Image loading | Multiple images in view | 1. View screen with many images<br>2. Observe loading | Images load progressively, no blocking | | |

## Test Execution Summary

**Test Date**: _________
**Tester**: _________
**Build Version**: _________
**Environment**: _________

**Results**:
- Total Test Cases: 30
- Passed: _____
- Failed: _____
- Blocked: _____
- Not Executed: _____

**Pass Rate**: _____%

## Critical Bugs Found
| Bug ID | Severity | Description | Steps to Reproduce | Status |
|--------|----------|-------------|-------------------|--------|
| | | | | |

## Sign-off
- **Tester**: _________________ Date: _______
- **Lead**: _________________ Date: _______

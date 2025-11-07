# BUG-201: Session timeout not enforced after inactivity

**Reported By**: QA Team
**Date**: 2024-11-07
**Severity**: High
**Priority**: P1
**Status**: Open
**Affected Versions**: v1.2.0, v1.2.1
**Devices**: All (iPhone 15 iOS 17, Samsung S23 Android 14)

## Description
User session persists indefinitely even after 30+ minutes of inactivity. Expected behavior is to force re-authentication after 30 minutes of inactivity for security.

## Steps to Reproduce
1. Launch app and log in with valid credentials
2. Verify user is on home screen
3. Press home button to background the app
4. Wait 30 minutes (or simulate time change in device settings)
5. Reopen app from background

## Expected Result
- User is redirected to login screen
- Optional: "Your session has expired. Please log in again." message displayed

## Actual Result
- User remains logged in
- Home screen displayed immediately
- No session timeout warning

## Impact
- **Security Risk**: Shared devices (family member can access account)
- **Compliance**: May violate security policies for financial/health apps
- **User Experience**: Unexpected for users expecting auto-logout

## Environment
- **App Version**: 1.2.1 (build 456)
- **OS**: iOS 17.0, Android 14
- **Network**: WiFi / Cellular (both affected)

## Attachments
- Screenshot: session-timeout-fail.png
- Video: session-timeout-reproduce.mp4

## Root Cause (Suspected)
Session token stored in Keychain/Keystore with no expiration check on app resume.

## Recommended Fix
- Add session expiration timestamp to token
- Check expiration on `applicationDidBecomeActive()` / `onResume()`
- Clear session and redirect to login if expired

## Related Tickets
- SEC-45: Implement token refresh mechanism
- COMP-12: PCI DSS compliance audit findings

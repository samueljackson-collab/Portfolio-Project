# Test Charter Template

**Charter ID**: TC-001
**Date**: YYYY-MM-DD
**Tester**: [Your Name]
**Build**: [App version / build number]

## Mission
*What are you trying to discover or accomplish in this session?*

Example: Explore the checkout flow for payment processing issues, edge cases, and usability problems.

## Areas to Explore
*Which features, screens, or components will you focus on?*

- [ ] Cart summary screen
- [ ] Payment method selection
- [ ] Billing address validation
- [ ] Order confirmation
- [ ] Error handling (declined cards, network failures)

## Time Estimate
*How long will this session take?*

60-90 minutes

## Risks to Investigate
*What could go wrong? What are the high-risk scenarios?*

- Payment processing failures (declined cards, expired cards)
- Network interruptions during checkout
- Data loss (cart items, billing info)
- Security: stored payment methods, PCI compliance

## Test Data / Setup
*What accounts, devices, or configurations are needed?*

- Test credit card: 4242 4242 4242 4242 (Stripe test mode)
- Devices: iPhone 15 (iOS 17), Pixel 7 (Android 13)
- Account: `test+checkout@example.com` with items in cart

## Notes / Observations
*Document findings, defects, questions during the session.*

- [Time] Observation 1: Checkout button disabled when billing address invalid (expected behavior)
- [Time] Defect: App crashes when switching payment methods rapidly (see BUG-123)
- [Time] Question: Should expired cards be detected client-side or server-side?

## Defects Logged
- BUG-123: App crash on rapid payment method switching
- BUG-124: Address autocomplete fails for Canadian postal codes

## Coverage Assessment
*How much of the area did you explore? What's left?*

- 80% coverage of happy path
- 50% coverage of error scenarios
- Not tested: International payment methods, multi-currency

## Sign-off
- [ ] Session complete
- [ ] All defects logged
- [ ] Follow-up charter needed? (yes/no)

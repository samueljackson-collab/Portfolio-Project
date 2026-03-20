# Physical Security Bypass

- **Role Category:** Red Team
- **Status:** Completed

## Executive Summary
Tested badge cloning and tailgating controls for a regional office, including social engineering resilience.

## Scenario & Scope
Two-floor office with HID badges, visitor kiosks, and mantrap entry.

## Responsibilities
- Captured badge IDs using proximity readers
- Attempted clone with reflashable cards
- Conducted staff awareness checks and debriefs

## Tools & Technologies
- Proxmark3
- Flipper Zero
- GoPro
- Kali

## Architecture Notes
Coordinated with facilities and security; all tests logged with timestamps and video capture for auditability.

## Process Walkthrough
- Surveyed entry points and badge readers
- Captured card data and attempted clones
- Validated door controller logging and alarms
- Ran awareness recap with office leadership

## Outcomes & Metrics
- Upgraded to SEOS badges for cryptographic validation
- Improved tailgating enforcement through policy updates
- Added door event feeds into SOC dashboards

## Evidence Links
- reports/p-rt-05/physical-bypass.pdf

## Reproduction Steps
- Use lab-issued test badges with Proxmark3
- Attempt clone and test against demo door controller
- Review SOC alerts for unauthorized entries

## Interview Points
- Physical security integration with SOC
- Badge technology differences (HID vs SEOS)
- Coordinating red-team ops with facilities

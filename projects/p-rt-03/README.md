# Wireless Intrusion Assessment

- **Role Category:** Red Team
- **Status:** Completed

## Executive Summary
Evaluated enterprise Wi-Fi security by performing rogue AP, evil-twin, and PMKID harvesting attacks.

## Scenario & Scope
Office SSIDs with WPA2-Enterprise and guest networks segmented via VLANs.

## Responsibilities
- Configured rogue AP with automatic credential capture
- Performed controlled deauth and PMKID collection
- Delivered hardening guidance for RADIUS and certificate validation

## Tools & Technologies
- Kali
- hostapd-wpe
- hcxdumptool
- Wireshark
- Aircrack-ng

## Architecture Notes
Used battery-powered rogue AP kit with 4G uplink; logs streamed to central syslog for chain-of-custody.

## Process Walkthrough
- Surveyed spectrum and SSIDs
- Executed evil-twin and deauth scenarios
- Captured PMKID handshakes and attempted offline crack
- Validated 802.1X certificate pinning settings

## Outcomes & Metrics
- Enabled EAP-TLS enforcement for corporate devices
- Blocked legacy TKIP negotiation
- Added rogue AP detection alerts to NMS

## Evidence Links
- reports/p-rt-03/wifi-assessment.pdf

## Reproduction Steps
- Flash the rogue AP SD card with the provided image
- Run the collection script and monitor syslog
- Test 802.1X validation on sample devices

## Interview Points
- Defending against evil-twin attacks
- Why certificate validation stops most credential theft
- Coordinating wireless testing with facilities

# Network Security Policy
**Environment:** PRJ-HOME-001 – UniFi Residential Network  \
**Effective Date:** 2024-06-09

---

## 1. Scope
Applies to all network infrastructure, wireless SSIDs, and connected devices (trusted, IoT, guest, services) at 5116 S 142nd St. Covers configuration management, authentication, segmentation, and monitoring controls.

## 2. Access Control
- **Administrative Access:**
  - MFA required for UniFi OS console and remote VPN access.
  - SSH access limited to Trusted VLAN IP range; key-based auth only.
  - Session timeouts enforced after 10 minutes of inactivity.
- **Wireless Authentication:**
  - Home-Trusted uses WPA3-Enterprise backed by UniFi Identity with certificate-based onboarding.
  - Home-IoT uses unique WPA2-PSK rotated every 90 days; MAC filtering for doorbells.
  - Home-Guest uses WPA2-PSK with captive portal acknowledgment and client isolation.

## 3. Network Segmentation & Firewall
- Default deny for inter-VLAN traffic; only explicitly allowed flows:
  - Trusted → Management (HTTPS/SSH/Inform ports)
  - Trusted → Services (SMB/NFS/HTTPS)
  - IoT → Services (NTP/DNS/Protect ports)
  - Services → Internet (required updates/backups)
- GeoIP filtering enabled for management interfaces (US + Canada only).
- IDS/IPS enabled in UniFi Threat Management with balanced profile.

## 4. Device Hardening
- Disable unused switch ports; apply port isolation for guest-facing Ethernet.
- Enforce automatic lockout on failed admin login attempts (5 strikes).
- Maintain vendor firmware currency (max 30 days behind latest stable).
- Utilize device tagging and inventory tracking for all PoE endpoints.

## 5. Logging & Monitoring
- Forward system logs and security events to centralized syslog server on Services VLAN.
- Alerting thresholds defined in Monitoring Strategy (see `monitoring-alerting-strategy.md`).
- Retain logs for minimum 90 days; archive monthly snapshots to NAS + cloud storage.

## 6. Incident Response
1. Detect anomaly via alert or user report.
2. Contain by isolating affected device (switch port disable or wireless quarantine).
3. Eradicate by applying patches, reconfiguring, or replacing compromised hardware.
4. Recover services following Disaster Recovery Plan.
5. Conduct post-incident review within 72 hours; update policies/runbooks accordingly.

## 7. Compliance & Review
- Quarterly policy review; update as environment evolves (e.g., addition of new IoT devices).
- Annual penetration-style assessment using tools such as Nmap and Wireshark within lab parameters.
- Document all reviews and approvals in change log with sign-off.


# Network Security Policies

## Document Information

**Document Title:** Homelab Network Security Policies  
**Version:** 1.0  
**Last Updated:** November 5, 2025  
**Owner:** Samuel Jackson  
**Classification:** Internal Use Only  

---

## Table of Contents

1. [Security Overview](#security-overview)
2. [Access Control Policies](#access-control-policies)
3. [Firewall Rule Matrix](#firewall-rule-matrix)
4. [Network Segmentation](#network-segmentation)
5. [Wireless Security](#wireless-security)
6. [VPN Access Policy](#vpn-access-policy)
7. [Intrusion Prevention](#intrusion-prevention)
8. [Incident Response](#incident-response)
9. [Maintenance Windows](#maintenance-windows)
10. [Compliance and Audit](#compliance-and-audit)

---

## Security Overview

### Defense-in-Depth Strategy

The homelab network implements a multi-layered security approach:

1. **Perimeter Security:** pfSense firewall with default-deny rules
2. **Network Segmentation:** 5 VLANs with isolated security zones
3. **Intrusion Prevention:** Suricata IPS on WAN and DMZ interfaces
4. **Access Control:** Role-based access with WPA3/802.1X authentication
5. **Monitoring:** Centralized logging and alerting
6. **Encryption:** All wireless traffic encrypted, VPN for remote access

### Security Principles

- **Principle of Least Privilege:** Users and devices granted minimum necessary access
- **Zero Trust:** Internal network traffic is not inherently trusted
- **Defense in Depth:** Multiple overlapping security controls
- **Fail Secure:** System failures default to secure state (blocked)
- **Logging and Monitoring:** All security events logged and reviewed

---

## Access Control Policies

### User Access Levels

#### Level 1: Administrator
- **Access:** Full access to all VLANs and management interfaces
- **Authentication:** WPA3 Enterprise + SSH Key + MFA
- **Networks:** Trusted (VLAN 10), Servers (VLAN 40)
- **Privileges:** Firewall management, device configuration, full internet access

#### Level 2: User
- **Access:** Trusted network access only
- **Authentication:** WPA3 Enterprise
- **Networks:** Trusted (VLAN 10)
- **Privileges:** Internet access, access to approved services on Server VLAN

#### Level 3: IoT Device
- **Access:** Restricted internet access, no internal network access
- **Authentication:** WPA2-PSK
- **Networks:** IoT (VLAN 20)
- **Privileges:** HTTP/HTTPS/DNS/NTP only, blocked from all internal networks

#### Level 4: Guest
- **Access:** Internet-only access
- **Authentication:** Captive portal with time-limited password
- **Networks:** Guest (VLAN 30)
- **Privileges:** HTTP/HTTPS/DNS only, bandwidth limited, content filtered

#### Level 5: DMZ Service
- **Access:** Internet access for updates, inbound HTTP/HTTPS from internet
- **Authentication:** None (network-based)
- **Networks:** DMZ (VLAN 50)
- **Privileges:** Outbound updates only, blocked from all internal networks

### Device Registration

All devices must be registered before connecting to the network:

1. **Trusted Devices:** MAC address registered in pfSense DHCP static mapping
2. **IoT Devices:** Documented in device inventory with justification
3. **Server Hardware:** Static IP assignment with MAC filtering on switch ports
4. **Guest Devices:** Temporary access via captive portal (max 4 hours)

---

## Firewall Rule Matrix

### VLAN Security Zones

| VLAN | Zone | Trust Level | Internet | Internal Access |
|------|------|-------------|----------|-----------------|
| 10 - Trusted | Corporate | High | Full | Full to approved VLANs |
| 20 - IoT | Restricted | Medium | Limited | Blocked |
| 30 - Guest | Public | Low | Limited | Blocked |
| 40 - Servers | Infrastructure | High | Limited | Inter-server only |
| 50 - DMZ | Public-Facing | Low | Limited | Blocked |

### Detailed Firewall Rules

#### WAN Interface Rules
```
Priority 1: Block all inbound traffic (default deny)
Priority 2: Allow HTTP (80) to DMZ VLAN (192.168.50.0/24)
Priority 3: Allow HTTPS (443) to DMZ VLAN (192.168.50.0/24)
Priority 4: Allow OpenVPN (1194/UDP) to pfSense
Priority 5: Block and log all other inbound
```

**Justification:**
- Default deny prevents unauthorized access
- DMZ services accessible for public-facing web applications
- VPN enables secure remote access
- Logging provides audit trail

#### LAN/Trusted VLAN Rules
```
Priority 1: Allow all outbound to internet
Priority 2: Allow TCP/UDP to IoT VLAN (management access)
Priority 3: Allow TCP/UDP to Servers VLAN (service access)
Priority 4: Block to DMZ VLAN
Priority 5: Block to Guest VLAN
```

**Justification:**
- Trusted users require full internet access
- Administrators need to manage IoT devices
- Users need access to internal services
- DMZ isolation prevents compromise from spreading
- Guest network isolation maintains security

#### IoT VLAN Rules (Strict)
```
Priority 1: Allow TCP 80 outbound (HTTP)
Priority 2: Allow TCP 443 outbound (HTTPS)
Priority 3: Allow UDP 53 outbound (DNS)
Priority 4: Allow UDP 123 outbound (NTP)
Priority 5: Block to RFC1918 addresses (all internal)
Priority 6: Block and log all other traffic
```

**Justification:**
- IoT devices often have poor security
- Limited to essential protocols only
- Blocked from internal networks prevents lateral movement
- Many IoT devices phone home; allow necessary cloud services
- Block prevents exploitation of internal resources

#### Guest VLAN Rules (Internet-Only)
```
Priority 1: Allow TCP 80 outbound (HTTP)
Priority 2: Allow TCP 443 outbound (HTTPS)
Priority 3: Allow UDP 53 outbound (DNS)
Priority 4: Block to RFC1918 addresses (all internal)
Priority 5: Block and log all other traffic
```

**Justification:**
- Guests only need internet access
- Complete isolation from homelab resources
- Content filtering applied to protect network reputation
- Bandwidth limits prevent abuse
- NTP blocked (use DHCP-provided time)

#### Servers VLAN Rules
```
Priority 1: Allow all within Servers VLAN (inter-server)
Priority 2: Allow TCP 80/443 outbound (updates)
Priority 3: Allow UDP 53 outbound (DNS)
Priority 4: Allow UDP 123 outbound (NTP)
Priority 5: Block to all other VLANs
Priority 6: Block and log all other traffic
```

**Justification:**
- Servers need to communicate for clustering and services
- Updates essential for security patching
- DNS required for package repositories
- NTP critical for accurate logging and authentication
- Isolated from other VLANs for security

#### DMZ VLAN Rules (Restrictive)
```
Priority 1: Allow TCP 80/443 outbound (updates)
Priority 2: Allow UDP 53 outbound (DNS)
Priority 3: Block to RFC1918 addresses (all internal)
Priority 4: Block and log all other traffic
```

**Justification:**
- DMZ hosts are public-facing and high-risk
- Updates required but strictly controlled
- Complete isolation from internal networks
- If compromised, cannot pivot to internal resources
- IPS monitoring on all DMZ traffic

### Anti-Spoofing Rules

Applied on all interfaces:
- Block packets with source addresses from other internal VLANs
- Block bogon addresses (RFC 1918, 5735)
- Block packets with source address equal to firewall IP
- Enable Unicast Reverse Path Forwarding (uRPF)

---

## Network Segmentation

### VLAN Architecture

#### High Trust Zones
- **VLAN 10 (Trusted):** Personal devices, management interfaces
- **VLAN 40 (Servers):** Infrastructure services, hypervisors

**Security Controls:**
- Strong authentication (WPA3 Enterprise, SSH keys)
- Full logging and monitoring
- Regular security updates
- Access to all approved resources

#### Medium Trust Zones
- **VLAN 20 (IoT):** Smart home devices, IP cameras

**Security Controls:**
- Pre-shared key authentication (rotated quarterly)
- Client isolation enabled
- Restricted firewall rules (whitelist)
- Scheduled access windows
- No internal network access

#### Low Trust Zones
- **VLAN 30 (Guest):** Visitor devices
- **VLAN 50 (DMZ):** Public-facing services

**Security Controls:**
- Open network with captive portal (Guest)
- Complete internal network isolation
- Bandwidth limitations
- Content filtering
- IPS monitoring (DMZ)
- Short DHCP lease times

### Inter-VLAN Routing Policy

**Allowed Paths:**
1. Trusted → IoT (one-way management)
2. Trusted → Servers (service access)
3. Trusted → Internet (full access)
4. IoT → Internet (limited protocols)
5. Guest → Internet (limited protocols, bandwidth limited)
6. Servers ↔ Servers (full access within VLAN)
7. Servers → Internet (updates only)
8. DMZ → Internet (updates only)
9. Internet → DMZ (HTTP/HTTPS only)

**Blocked Paths:**
- IoT → Trusted (prevents compromise spread)
- IoT → Servers (prevents infrastructure attack)
- Guest → Any internal VLAN
- DMZ → Any internal VLAN
- All VLANs → pfSense management (except Trusted)

---

## Wireless Security

### SSID Security Configuration

#### Homelab-Secure (WPA3 Enterprise)

**Authentication Method:** 802.1X (RADIUS)  
**RADIUS Server:** FreeIPA (192.168.40.25:1812)  
**Encryption:** AES-256-CCMP  
**PMF (802.11w):** Required  

**Key Security Features:**
- Individual per-user encryption keys
- Certificate-based authentication option
- Forward secrecy (session keys rotated)
- Protected Management Frames prevent deauth attacks
- RADIUS accounting for connection audit trail

**User Enrollment:**
1. User account created in FreeIPA
2. Certificate issued (optional but recommended)
3. Device configured with 802.1X profile
4. Connection attempt triggers RADIUS authentication
5. Success grants network access with dynamic VLAN assignment

#### Homelab-IoT (WPA2-PSK)

**Authentication Method:** Pre-Shared Key  
**Encryption:** AES-128-CCMP  
**PMF (802.11w):** Optional (some IoT devices don't support)  

**Key Management:**
- PSK rotated every 90 days
- Key stored in password manager
- Devices must be re-enrolled after rotation
- Only approved IoT devices receive PSK

**Access Control:**
- Client isolation prevents device-to-device communication
- MAC address whitelist (optional, device dependent)
- Scheduled access (6 AM - 11 PM daily)

#### Homelab-Guest (Open + Captive Portal)

**Authentication Method:** Captive Portal with password  
**Encryption:** None (open network for compatibility)  

**Portal Configuration:**
- Password changes weekly
- Password provided to guests verbally or via QR code
- Session timeout: 4 hours
- Automatic disconnection and re-authentication required
- HTTPS redirect to portal for security

**Content Filtering:**
- Malware and phishing sites blocked
- Adult content blocked
- Gambling sites blocked
- Safe search enforced on search engines

### Rogue Access Point Detection

- **Monitoring:** Continuous wireless scanning by UniFi APs
- **Detection:** Unknown APs with matching SSID names flagged
- **Alerting:** Email notification to administrator
- **Containment:** Manual review and response (auto-containment disabled)

### Wireless Channel Security

- **WPA3 SAE:** Protects against dictionary attacks on PSK
- **Management Frame Protection:** Prevents deauthentication attacks
- **Beacon Protection:** Not yet widely supported
- **Band Steering:** Preferentially steers clients to 5 GHz for better performance and less congestion

---

## VPN Access Policy

### OpenVPN Remote Access

**Purpose:** Secure remote access to Trusted and Servers VLANs

**Connection Requirements:**
- OpenVPN client configured with provided .ovpn file
- Certificate-based authentication (no passwords)
- TLS 1.3 or higher
- Client must have up-to-date OS and security patches

**Access Granted:**
- Tunnel network: 10.8.0.0/24
- Access to Trusted VLAN (192.168.1.0/24)
- Access to Servers VLAN (192.168.40.0/24)
- Full internet access through tunnel

**Access Denied:**
- IoT VLAN (no remote management of IoT devices)
- Guest VLAN (unnecessary)
- DMZ VLAN (public-facing, no internal management)

**Security Controls:**
- Certificate authentication (TLS client certificates)
- AES-256-GCM encryption
- SHA256 authentication
- Perfect Forward Secrecy (DHE/ECDHE)
- LZ4 compression
- Maximum 10 concurrent connections
- Connection logging and monitoring
- Certificate revocation list (CRL) checking

**Certificate Management:**
- Certificates issued per-device
- Certificate validity: 1 year
- Renewal required before expiration
- Revoked certificates immediately denied
- Private keys stored securely on client device only

**Usage Policy:**
- VPN access for authorized administrators only
- Access logged and audited monthly
- Suspicious activity triggers immediate review
- Lost/stolen device: certificate revoked immediately

---

## Intrusion Prevention

### Suricata IPS Configuration

**Interfaces Monitored:**
1. WAN Interface (all inbound/outbound traffic)
2. DMZ Interface (public-facing services)

**Operating Mode:** IPS (Inline Blocking)

**Rulesets Enabled:**
- Emerging Threats Open
- Emerging Malware
- Emerging Exploit
- Emerging Scan
- Emerging Web Attacks (DMZ only)

**Update Schedule:**
- Automatic daily updates at 3:00 AM
- Manual update after security announcements

**Alert Actions:**
1. **Drop:** Traffic blocked and logged (High severity threats)
2. **Alert:** Traffic logged but allowed (Medium/Low severity)
3. **Pass:** Traffic explicitly allowed (False positive handling)

**Tuning:**
- False positives reviewed weekly
- Suppress rules created for known-good traffic
- Custom rules for specific threats
- Performance monitoring (CPU < 50%)

**Common Detected Threats:**
- Port scanning attempts
- SQL injection attacks
- Cross-site scripting (XSS)
- Remote code execution attempts
- Malware callbacks
- Brute force attacks

**Response Procedures:**
1. Critical alert: Investigate immediately
2. High alert: Review within 4 hours
3. Medium alert: Review daily
4. Low alert: Weekly batch review

---

## Incident Response

### Incident Classification

#### Severity 1: Critical
- **Examples:** Active breach, ransomware, data exfiltration
- **Response Time:** Immediate
- **Actions:** Isolate affected systems, engage incident response procedure

#### Severity 2: High
- **Examples:** Malware infection, successful intrusion attempt
- **Response Time:** Within 1 hour
- **Actions:** Investigate, contain, remediate

#### Severity 3: Medium
- **Examples:** Multiple failed authentication attempts, policy violations
- **Response Time:** Within 4 hours
- **Actions:** Investigate and document

#### Severity 4: Low
- **Examples:** Single failed login, minor policy violation
- **Response Time:** Within 24 hours
- **Actions:** Log and review during routine security review

### Incident Response Procedure

#### Phase 1: Detection and Analysis (0-15 minutes)
1. Alert received from IPS, firewall logs, or monitoring system
2. Initial triage: Determine severity and affected systems
3. Document initial observations with timestamps
4. Declare incident if criteria met

#### Phase 2: Containment (15-60 minutes)
1. **Short-term Containment:**
   - Block source IPs at firewall
   - Disable compromised user accounts
   - Isolate affected VLAN if necessary
   - Take snapshots of affected VMs

2. **Long-term Containment:**
   - Apply temporary firewall rules
   - Reset credentials
   - Deploy emergency patches

#### Phase 3: Eradication (1-4 hours)
1. Identify and remove threat (malware, backdoors, etc.)
2. Apply security patches
3. Harden affected systems
4. Update firewall rules permanently
5. Update IPS signatures

#### Phase 4: Recovery (4-24 hours)
1. Restore services in isolated environment
2. Monitor for indicators of re-infection
3. Gradually restore normal operations
4. Verify all systems operational

#### Phase 5: Post-Incident Activity (1-7 days)
1. Document incident in detail
2. Conduct lessons learned session
3. Update policies and procedures
4. Implement additional controls if needed
5. Train staff on new procedures

### Emergency Contacts

| Role | Contact Method | Response Time |
|------|---------------|---------------|
| Primary Administrator | Mobile: [REDACTED] | Immediate |
| Secondary Contact | Email: [REDACTED] | 1 hour |
| ISP Technical Support | Phone: [REDACTED] | Varies |
| Hardware Vendor Support | Online Portal | 4-24 hours |

### Incident Communication Plan

- **Internal:** Email to admin team
- **External:** None required (home lab)
- **Documentation:** Incident logged in internal wiki
- **Reporting:** Monthly security review includes incident summary

---

## Maintenance Windows

### Scheduled Maintenance

#### Weekly Maintenance (Sundays, 2:00 AM - 4:00 AM)
- Security updates for pfSense
- Backup verification
- Log review and cleanup
- Monitoring system check

#### Monthly Maintenance (First Sunday, 2:00 AM - 6:00 AM)
- pfSense minor version updates
- UniFi firmware updates
- IPS ruleset review
- Certificate expiration check
- Performance optimization
- Configuration backup to offsite

#### Quarterly Maintenance (Planned 4-hour window)
- pfSense major version updates
- Network hardware firmware updates
- Security policy review
- Full system audit
- Penetration testing
- Disaster recovery test

### Emergency Maintenance

**Criteria for Emergency Maintenance:**
- Critical security vulnerability disclosed
- Active security incident requiring immediate remediation
- Hardware failure requiring replacement
- Service outage affecting critical systems

**Procedure:**
1. Assess urgency and impact
2. Notify users if downtime expected
3. Create configuration backup
4. Execute change with rollback plan
5. Verify functionality
6. Document emergency change

### Change Management

All non-emergency changes follow this process:
1. **Request:** Document change with justification
2. **Plan:** Create detailed implementation and rollback plan
3. **Approve:** Self-approval for home lab, documented
4. **Test:** Test in lab environment if possible
5. **Implement:** Execute during maintenance window
6. **Verify:** Confirm change successful
7. **Document:** Update documentation and diagrams

---

## Compliance and Audit

### Security Baseline

All systems must meet these minimum requirements:
- ✅ Default deny firewall rules
- ✅ Strong authentication (no default passwords)
- ✅ Encrypted management traffic (HTTPS, SSH)
- ✅ Regular security updates
- ✅ Logging enabled and centralized
- ✅ Unused services disabled
- ✅ Time synchronization configured

### Audit Schedule

#### Daily
- Review IPS alerts for critical threats
- Monitor system availability

#### Weekly
- Review firewall logs for anomalies
- Check for unauthorized devices
- Verify backup completion

#### Monthly
- Review user access logs
- Audit firewall rule changes
- Check certificate expiration (60-day warning)
- Review IoT device inventory

#### Quarterly
- Full security policy review
- Compliance with security baseline
- Vulnerability assessment
- Penetration testing (simulated attacks)
- Update security documentation

### Security Metrics

Tracked monthly:
- Number of IPS alerts by severity
- Number of blocked connection attempts
- VPN connection logs
- Failed authentication attempts
- Bandwidth usage by VLAN
- System uptime percentage
- Patch compliance percentage

### Vulnerability Management

1. **Scanning:** Monthly automated scans with OpenVAS or similar
2. **Assessment:** Prioritize by CVSS score and exploitability
3. **Remediation:** Critical (7 days), High (30 days), Medium (90 days)
4. **Verification:** Re-scan after patching
5. **Documentation:** Track in vulnerability register

---

## Policy Review and Updates

### Review Schedule
- **Annual:** Full security policy review
- **Quarterly:** Updates based on new threats or technology
- **As-Needed:** After security incidents or major changes

### Approval Process
1. Draft policy changes
2. Test impact on network operations
3. Update documentation
4. Implement changes
5. Communicate to users

### Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-05 | Initial security policy documentation | Samuel Jackson |

---

## Appendix

### Acronyms and Definitions

- **AES:** Advanced Encryption Standard
- **AP:** Access Point
- **DMZ:** Demilitarized Zone
- **IPS:** Intrusion Prevention System
- **NAT:** Network Address Translation
- **NTP:** Network Time Protocol
- **PMF:** Protected Management Frames (802.11w)
- **PSK:** Pre-Shared Key
- **RADIUS:** Remote Authentication Dial-In User Service
- **RSTP:** Rapid Spanning Tree Protocol
- **SSID:** Service Set Identifier
- **TLS:** Transport Layer Security
- **VLAN:** Virtual Local Area Network
- **VPN:** Virtual Private Network
- **WPA3:** Wi-Fi Protected Access 3

### Related Documents
- Network Inventory and Documentation
- Network Architecture Diagram
- Disaster Recovery Plan
- Incident Response Playbook

---

**Document Control**

This document contains sensitive information about network security controls. Distribution is limited to authorized administrators only.

**Classification:** Internal Use Only  
**Next Review Date:** November 5, 2026  
**Document Owner:** Samuel Jackson

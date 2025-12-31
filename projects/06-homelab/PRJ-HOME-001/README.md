# Homelab & Secure Network Build

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../../DOCUMENTATION_INDEX.md).


**Status:** 🟢 Done

## Description

Designed and wired a home network from scratch: rack-mounted gear, VLAN segmentation, and secure Wi-Fi for isolated IoT, guest, and trusted networks.

## Links

- [Parent Documentation](../../../README.md)
- [Evidence Assets](./assets)

## Next Steps

- Review new evidence artifacts (diagrams, screenshots, configs) for audit-readiness.
- Keep sanitized screenshots refreshed quarterly to reflect controller upgrades.
- Align future firmware updates with the VLAN segmentation design to avoid drift.

## Contact

For questions about this project, please reach out via [GitHub](https://github.com/sams-jackson) or [LinkedIn](https://www.linkedin.com/in/sams-jackson).

---

## Code Generation Prompts

- [x] README scaffold produced from the [Project README generation prompt](../../../AI_PROMPT_LIBRARY.md#project-readme-baseline).
- [x] Homelab evidence checklist aligned to the [Prompt Execution Framework workflow](../../../AI_PROMPT_EXECUTION_FRAMEWORK.md#prompt-execution-workflow).

---

## Evidence Artifacts
- **Network Topology:** `assets/diagrams/network-topology.mmd` (Mermaid source) depicts WAN → pfSense → UniFi → downstream gear.
- **VLAN Segmentation:** `assets/diagrams/vlan-segmentation.mmd` captures the five-zone isolation model.
- **Monitoring Evidence:** `assets/configs/monitoring-snapshots.md` includes Prometheus, Grafana, and Loki excerpts with sensitive values redacted.
- **Screenshots:** `assets/screenshots/` includes sanitized UniFi, pfSense, and VLAN overview captures.
- **Logs:** `assets/logs/` contains sanitized controller and firewall summary logs.

# PRJ-HOME-001: Homelab & Secure Network Build

**Status:** ✅ Completed  
**Category:** Homelab & Network Infrastructure  
**Technologies:** pfSense, UniFi, VLANs, Suricata IPS, OpenVPN, 802.1X  
**Complexity:** Advanced  

---

## Overview

Designed and implemented a production-grade secure network infrastructure featuring defense-in-depth security principles, comprehensive network segmentation across 5 VLANs, enterprise-grade wireless access with WPA3, and integrated intrusion prevention systems.

This project demonstrates enterprise networking skills including advanced firewall configuration, VLAN design, wireless security implementation, and security policy development.

## Architecture Highlights

- **5-VLAN Segmentation:** Trusted, IoT, Guest, Servers, and DMZ networks
- **pfSense Firewall:** Advanced routing, NAT, DHCP, DNS, IPS, and VPN
- **UniFi Network:** Managed switching and wireless with centralized controller
- **Security Zones:** High/Medium/Low trust levels with appropriate controls
- **Defense-in-Depth:** Multiple overlapping security layers

## Network Topology

```
Internet → pfSense Firewall (WAN + 5 VLANs)
    ↓
UniFi Switch 24 POE (VLAN-aware, trunk ports)
    ↓
├─→ 2x U6 Pro Access Points (PoE, 3 SSIDs)
├─→ Proxmox Cluster (3 nodes) on VLAN 40
├─→ TrueNAS Storage on VLAN 40
└─→ Client Devices across VLANs 10, 20, 30
```

For detailed network architecture, see [Network Architecture Diagram](assets/documentation/network-architecture.mermaid).

## VLAN Design

| VLAN | Network | Purpose | Trust Level | Key Features |
|------|---------|---------|-------------|--------------|
| **10** | 192.168.1.0/24 | Trusted | High | WPA3 Enterprise, full access |
| **20** | 192.168.20.0/24 | IoT | Medium | Client isolation, restricted protocols |
| **30** | 192.168.30.0/24 | Guest | Low | Captive portal, bandwidth limits |
| **40** | 192.168.40.0/24 | Servers | High | Infrastructure services |
| **50** | 192.168.50.0/24 | DMZ | Low | Public-facing, IPS monitoring |

## Security Features

### Firewall Protection

- **Default Deny:** All traffic blocked unless explicitly allowed
- **Stateful Inspection:** Connection tracking and validation
- **Inter-VLAN Rules:** Precise control over traffic between networks
- **Anti-Spoofing:** Protection against IP and MAC spoofing
- **Rate Limiting:** Protection against flood attacks

### Intrusion Prevention

- **Suricata IPS:** Active threat blocking on WAN and DMZ
- **Rulesets:** Emerging Threats (malware, exploits, scans)
- **Daily Updates:** Automated signature updates
- **Inline Mode:** Real-time blocking of malicious traffic

### Wireless Security

- **Homelab-Secure:** WPA3 Enterprise with RADIUS authentication
- **Homelab-IoT:** WPA2-PSK with client isolation and scheduled access
- **Homelab-Guest:** Open with captive portal, content filtering, bandwidth limits

### VPN Access

- **OpenVPN:** Secure remote access to Trusted and Servers VLANs
- **Certificate-Based:** Strong authentication without passwords
- **AES-256-GCM:** Military-grade encryption
- **Split Tunneling:** Optional for performance

### Additional Security

- **DNS Security:** Unbound resolver with DNSSEC validation
- **Traffic Shaping:** QoS for VoIP and critical services
- **Centralized Logging:** All events forwarded to syslog server
- **Automated Backups:** Daily configuration backups

## Hardware Configuration

### pfSense Firewall

- **Model:** Custom build or Protectli Vault
- **CPU:** Intel Quad-Core
- **RAM:** 8GB
- **Storage:** 128GB SSD
- **NICs:** 6x Gigabit Ethernet (1 WAN, 5 VLANs)

### UniFi Switch 24 POE (US24P250)

- **Ports:** 24x Gigabit (16x PoE+)
- **PoE Budget:** 250W
- **Features:** VLAN support, port security, RSTP

### 2x UniFi U6 Pro Access Points

- **Standard:** Wi-Fi 6 (802.11ax)
- **2.4 GHz:** Channels 1 & 6 (non-overlapping)
- **5 GHz:** Channels 36 & 149 (80 MHz width)
- **Features:** Band steering, fast roaming, 300 client capacity

## Project Artifacts

### Configuration Files

- [`pfsense-config.xml`](assets/pfsense/pfsense-config.xml) - Complete pfSense configuration with all interfaces, firewall rules, DHCP, DNS, IPS, VPN, and traffic shaping
- [`unifi-config.json`](assets/unifi/unifi-config.json) - UniFi Controller configuration including wireless networks, devices, port profiles, and security settings

### Documentation

- [`network-architecture.mermaid`](assets/documentation/network-architecture.mermaid) - Visual network topology with security zones and device placement
- [`network-inventory.md`](assets/documentation/network-inventory.md) - Complete IP allocation tables, device inventory, switch port assignments, and hardware specifications
- [`security-policies.md`](assets/documentation/security-policies.md) - Comprehensive security policies including firewall rules, access control, incident response, and maintenance procedures

## Deployment Instructions

### Prerequisites

1. pfSense 2.6+ installed on firewall hardware
2. UniFi Controller 7.5+ running (self-hosted or cloud)
3. UniFi Switch and Access Points adopted in controller

### pfSense Configuration

1. Backup existing configuration
2. Review `pfsense-config.xml` and adjust for your environment:
   - WAN interface settings (adjust for your ISP)
   - Static DHCP mappings (update MAC addresses)
   - OpenVPN certificates (generate your own)
3. Import configuration via Diagnostics → Backup & Restore
4. Verify interface assignments and reboot if needed
5. Test connectivity on each VLAN

### UniFi Configuration

1. Backup existing UniFi controller configuration
2. Review `unifi-config.json` and customize:
   - Device MAC addresses
   - Wireless network credentials
   - RADIUS server settings (if using 802.1X)
3. Import configuration or manually apply settings
4. Provision/re-provision devices as needed
5. Verify wireless networks broadcast correctly

### Validation

- [ ] All VLANs can reach internet
- [ ] Inter-VLAN rules enforced (test blocking)
- [ ] Wireless clients connect successfully
- [ ] VPN connects and routes correctly
- [ ] IPS alerts visible in pfSense logs
- [ ] DHCP assignments working per VLAN
- [ ] DNS resolution working (test homelab.local)

## Skills Demonstrated

### Network Engineering

- Multi-VLAN network design and implementation
- Advanced routing and switching concepts
- Wireless network planning and optimization
- Channel planning for minimal interference

### Security

- Firewall policy development and implementation
- Defense-in-depth security architecture
- Intrusion prevention system deployment
- WPA3 Enterprise and 802.1X authentication
- VPN configuration for secure remote access
- Security policy documentation

### Systems Administration

- pfSense firewall administration
- UniFi network management
- DNS and DHCP server configuration
- Network monitoring and logging
- Configuration backup and disaster recovery

### Documentation

- Network architecture diagramming
- Technical documentation writing
- Security policy creation
- Standard operating procedures

## Operational Procedures

### Daily Operations

- Monitor Suricata IPS alerts
- Review system logs for anomalies
- Verify backup completion

### Weekly Maintenance

- Review firewall logs
- Check DHCP lease utilization
- Update IPS signatures (automated)

### Monthly Maintenance

- Audit firewall rules
- Review security incidents
- Test VPN connectivity
- Rotate guest network credentials

### Quarterly Maintenance

- Apply pfSense and UniFi updates
- Full security audit
- Penetration testing
- Documentation review and updates

## Lessons Learned

1. **Plan Before Implementing:** Detailed VLAN and IP addressing scheme saved significant rework
2. **Defense in Depth:** Multiple security layers provide resilience against single point of failure
3. **Document Everything:** Comprehensive documentation critical for troubleshooting and changes
4. **Test Firewall Rules:** Verify both allow and deny rules work as intended
5. **Monitor Continuously:** IPS and logging catch issues that might otherwise go unnoticed
6. **Backup Configurations:** Regular backups essential before any changes

## Future Enhancements

- [ ] Implement IPv6 throughout network
- [ ] Add network monitoring with Prometheus and Grafana
- [ ] Deploy NetFlow/sFlow for traffic analysis
- [ ] Implement automated configuration backups to Git
- [ ] Add pfBlockerNG for DNS-based ad blocking
- [ ] Deploy multi-WAN failover with secondary ISP
- [ ] Implement 802.1X wired authentication on switch ports

## References

- [pfSense Documentation](https://docs.netgate.com/pfsense/en/latest/)
- [UniFi Controller Guide](https://help.ui.com/hc/en-us/categories/200320654-UniFi-Wireless)
- [Suricata IPS Documentation](https://suricata.readthedocs.io/)
- [WPA3 Security](https://www.wi-fi.org/discover-wi-fi/security)

---

**Project Completed:** November 5, 2025  
**Last Updated:** November 5, 2025  
**Maintainer:** Samuel Jackson

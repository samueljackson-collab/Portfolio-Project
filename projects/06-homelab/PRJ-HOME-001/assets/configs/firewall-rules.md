# UniFi Dream Machine Pro Firewall Rules – PRJ-HOME-001

The UniFi Dream Machine Pro (UDMP) enforces a strict, zone-based security policy for the segmented homelab network. Rules are evaluated **top-to-bottom** with a first-match-wins strategy. Logging is enabled on critical deny rules to simplify incident response while noisy allow rules remain unlogged to conserve storage and controller performance.

| Rule # | Name | Source | Destination | Protocol/Port | Action | Purpose | Logging |
|--------|------|--------|-------------|---------------|--------|---------|---------|
| 1 | Admin Workstations to Management | VLAN 10 – Trusted Admin Subnet | VLAN 1 – Management | TCP 22, 443, 8443 | ALLOW | Permit administrators to SSH/HTTPS into network gear and UniFi controller. | ✅ |
| 2 | Protect Management Plane | VLANs 10/50/99/100 | VLAN 1 – Management | ANY | DENY | Block all non-admin traffic from reaching management interfaces. | ✅ |
| 3 | Trusted to IoT Control | VLAN 10 – Trusted | VLAN 50 – IoT | UDP 5353, TCP 80, TCP 443 | ALLOW | Allow Home Assistant and mobile devices to discover and control IoT endpoints. | ❌ |
| 4 | Trusted to Lab Access | VLAN 10 – Trusted | VLAN 100 – Lab | ANY | ALLOW | Allow trusted devices to reach lab resources for testing. | ✅ |
| 5 | Trusted Isolation from Guest | VLAN 10 – Trusted | VLAN 99 – Guest | ANY | DENY | Prevent lateral movement from trusted devices into guest Wi-Fi. | ✅ |
| 6 | IoT Internet Egress | VLAN 50 – IoT | WAN (Internet) | TCP 80, TCP 443, UDP 53 | ALLOW | Provide IoT cloud connectivity for updates/telemetry. | ❌ |
| 7 | IoT to Management Block | VLAN 50 – IoT | VLAN 1 – Management | ANY | DENY | Prevent IoT gadgets from accessing network infrastructure. | ✅ |
| 8 | IoT to Trusted Block | VLAN 50 – IoT | VLAN 10 – Trusted | ANY | DENY | Eliminate lateral movement from IoT toward sensitive systems. | ✅ |
| 9 | IoT to Guest/Lab Block | VLAN 50 – IoT | VLANs 99 & 100 | ANY | DENY | Preserve isolation between IoT and other sandbox/guest zones. | ✅ |
| 10 | Guest Internet Egress | VLAN 99 – Guest | WAN (Internet) | TCP 80, TCP 443, UDP 53 | ALLOW | Provide guests with basic internet and DNS access. | ❌ |
| 11 | Guest Isolation | VLAN 99 – Guest | VLANs 1/10/50/100 | ANY | DENY | Enforce complete isolation of guest clients from internal networks. | ✅ |
| 12 | Lab Internet Access | VLAN 100 – Lab | WAN (Internet) | ANY | ALLOW | Allow controlled internet access for testing; shaped to 50 Mbps per client. | ✅ |
| 13 | Lab to Trusted (Web Ports) | VLAN 100 – Lab | VLAN 10 – Trusted | TCP 8080, TCP 8443 | ALLOW | Permit lab workloads to reach staging services in trusted zone on specific ports. | ✅ |
| 14 | Lab Containment | VLAN 100 – Lab | VLANs 1/50/99 | ANY | DENY | Prevent lab malware from escaping into other zones. | ✅ |
| 15 | Implicit Default Deny | Any | Any | ANY | DENY | Catch-all block for unclassified traffic (implicit in UniFi). | ✅ |

## Additional Enforcement Layers

- **Rate Limiting**
  - Guest SSID limited to **10 Mbps** per client and capped at **5 GB** per voucher to prevent abuse.
  - Lab VLAN shaped to **50 Mbps** per host to reduce risk during penetration testing.
- **Geo-IP Filtering**: WAN firewall blocks inbound connections from high-risk regions (CN, RU, IR, KP) while allowing WireGuard VPN and HTTPS management from trusted countries only.
- **Port Forwarding**
  - UDP 51820 → WireGuard VPN server (authenticated users only).
  - No other inbound services exposed; remote management occurs through VPN tunnel.

## Rule Maintenance

- Review firewall logs **monthly** to identify noisy denies or attempted intrusions.
- Trigger a change review whenever adding new IoT gear or lab workloads.
- Export the firewall configuration to the documentation repository after each quarterly review for change tracking.

## Troubleshooting Checklist

1. **Device cannot reach the internet**: Verify Rules 6 (IoT) or 10 (Guest) and confirm DHCP assigned correct DNS/gateway.
2. **Admin workstation blocked from controller**: Ensure Rule 1 remains above Rule 2 and workstation IP is in the trusted admin group.
3. **Lab service unreachable from trusted device**: Confirm Rule 13 includes the required port and that the lab host firewall allows inbound traffic.
4. **Unexpected management access attempts**: Review Rule 2 logs; investigate MAC/IP and consider quarantine on the switch.

Maintain this document alongside UniFi backups so restoration aligns with documented policy.

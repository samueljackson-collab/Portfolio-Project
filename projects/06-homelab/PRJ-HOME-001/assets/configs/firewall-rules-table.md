# Firewall Rules Table (Redacted)

| Rule ID | Source | Destination | Ports/Protocols | Action | Purpose |
| --- | --- | --- | --- | --- | --- |
| FW-001 | VLAN10 (Trusted) | WAN | 80, 443 TCP, 53 TCP/UDP | Allow | Standard internet access for trusted clients. |
| FW-002 | VLAN20 (IoT) | WAN | 80, 443 TCP, 53 TCP/UDP | Allow | Restricted internet access for IoT devices. |
| FW-003 | VLAN30 (Guest) | WAN | 80, 443 TCP, 53 TCP/UDP | Allow | Guest internet access only. |
| FW-004 | VLAN40 (Servers) | WAN | 80, 443, 123 TCP/UDP | Allow | Patch updates and time sync for servers. |
| FW-005 | VLAN10 (Trusted) | VLAN40 (Servers) | 22, 443, 3389 TCP | Allow | Administrative access to server VLAN. |
| FW-006 | VLAN10 (Trusted) | VLAN20 (IoT) | 5353 UDP, 443 TCP | Allow | mDNS + HTTPS control to IoT hubs only. |
| FW-007 | VLAN40 (Servers) | VLAN50 (DMZ) | 443 TCP | Allow | Reverse proxy access to DMZ services. |
| FW-008 | VLAN50 (DMZ) | WAN | 443 TCP | Allow | NAT for public HTTPS services. |
| FW-009 | VLAN20 (IoT) | RFC1918 | Any | Deny | Prevent lateral movement from IoT. |
| FW-010 | VLAN30 (Guest) | RFC1918 | Any | Deny | Guests blocked from internal networks. |
| FW-011 | VLAN50 (DMZ) | VLAN10 (Trusted) | Any | Deny | DMZ cannot reach trusted LAN. |
| FW-012 | VLAN40 (Servers) | VLAN10 (Trusted) | Any | Deny | Servers cannot initiate to trusted clients. |

## Notes
- RFC1918 refers to private address space (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16).
- Specific host/group objects are redacted for portfolio distribution.

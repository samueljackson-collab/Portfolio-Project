# IP Address Management Plan

## 1. Scope
This document tracks IPv4 addressing, DHCP scopes, and static assignments for the UniFi-powered residence at 5116 S 142nd St. The plan assumes a /24 per VLAN, leaving ample capacity for expansion and simplifying ACL writing.

## 2. Summary Table
| VLAN | Subnet | DHCP Scope | Gateway | DNS | Notes |
| --- | --- | --- | --- | --- | --- |
| 10 – Management | 10.10.10.0/24 | 10.10.10.50-10.10.10.199 | 10.10.10.1 | 10.10.10.5 (Services DNS) | Static leases preferred |
| 20 – Trusted | 10.10.20.0/24 | 10.10.20.50-10.10.20.230 | 10.10.20.1 | 10.10.50.10, 1.1.1.1 | Split DNS (internal/external) |
| 30 – IoT | 10.10.30.0/24 | 10.10.30.100-10.10.30.230 | 10.10.30.1 | 10.10.50.10 | Static for cameras/flood lights |
| 40 – Guest | 10.10.40.0/24 | 10.10.40.100-10.10.40.240 | 10.10.40.1 | 1.1.1.1, 8.8.8.8 | Client isolation, captive portal |
| 50 – Services | 10.10.50.0/24 | 10.10.50.100-10.10.50.150 | 10.10.50.1 | 10.10.50.10 | NAS, hypervisor, backup server |

## 3. Reserved Static Assignments
| Device | VLAN | IP Address | Justification |
| --- | --- | --- | --- |
| UDM-Pro | 10 | 10.10.10.1 | Default gateway + controller |
| Switch Pro 24 PoE | 10 | 10.10.10.2 | Simplifies switch management |
| Cloud Key Gen2 Plus | 10 | 10.10.10.3 | UniFi Protect host |
| UPS Network Card | 10 | 10.10.10.10 | SNMP monitoring |
| NAS (TrueNAS) | 50 | 10.10.50.10 | DNS + backup target |
| Proxmox Host | 50 | 10.10.50.20 | Virtualization cluster |
| AP-01..AP-11 | 10 | 10.10.10.20-10.10.10.30 | Predictable mgmt addressing |
| CAM-O1..O5 | 30 | 10.10.30.10-10.10.30.14 | UniFi Protect static mapping |
| FLOOD-O1..O5 | 30 | 10.10.30.20-10.10.30.24 | Flood light automation |
| Doorbell Front | 30 | 10.10.30.40 | Wireless but reserved |
| Doorbell Back | 30 | 10.10.30.41 | Wireless but reserved |

## 4. DHCP Options
- **Option 42 (NTP):** 10.10.50.10 provided to VLANs 20/30/50; guest VLAN uses pool NTP (time.cloudflare.com).
- **Option 43:** Not configured (UniFi APs adopted via Layer 2).
- **Lease duration:** 12 hours for Guest VLAN, 7 days for others.

## 5. Address Management Process
1. Update this document prior to adding new wired drops or IoT devices.
2. Reserve IP in UniFi Network Application (Client > Reserve Static IP) and note in static table.
3. Tag cables and patch panel ports with matching hostnames/IPs using Brady labeler.
4. Quarterly audit: export DHCP lease table, compare to inventory spreadsheet, remediate rogue/unknown devices.


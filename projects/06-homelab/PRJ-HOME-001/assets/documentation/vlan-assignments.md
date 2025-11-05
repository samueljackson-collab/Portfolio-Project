# VLAN Assignments - PRJ-HOME-001

Overview:
- Network CIDR: 10.0.0.0/16

VLANs:
- VLAN 10: Management - 10.0.10.0/24
- VLAN 20: Servers - 10.0.20.0/24
- VLAN 30: IoT - 10.0.30.0/24
- VLAN 40: Guests - 10.0.40.0/24

Firewall rules (examples):
- Allow Management -> Servers: TCP 22, 443, 8443
- Deny Guests -> Management: All
- Allow Servers -> Internet: HTTP/HTTPS via NAT
- Allow IoT -> Cloud Services: HTTP/HTTPS only

Sanitization notes before publishing:
- Remove controller admin credentials
- Replace public IPs with placeholders
- Do not include VPN credentials

How to export UniFi safely:
1. In UniFi controller, go to Settings → System → Export configuration
2. Remove all credentials and external IP entries
3. Replace SSIDs or passphrases with placeholders
# Physical Network Topology Diagram Specification

## Layout Structure
- Orientation: Left-to-right, Internet on far left.
- Grouping by physical location: rack, office, living room.
- Color scheme: red WAN, blue trunks, green access, orange fiber.

## Components
1. ISP cloud labeled "Internet via Comcast" 1Gbps/35Mbps.
2. Arris SB8200 modem connected via red line to UDMP WAN.
3. Rack group: UDMP (top), Switch 24 PoE (below) with blue trunk between, servers beneath (Proxmox1 port9 VLAN40, Proxmox2 port10 VLAN40, TrueNAS port11 VLAN40).
4. APs: Office AP trunk port13, LivingRoom port14, Bedroom port15. SSID mappings shown (HomeNetwork-5G→VLAN10, IoT→VLAN20, Guest→VLAN30).
5. End device clusters by VLAN: Trusted (workstations/phones/TV), IoT (speakers/lights/thermostat), Guest (visitor devices), Cameras (front/back/garage/driveway to NVR in server VLAN).

## Annotations
- Cable types (Cat6 for APs, Cat5e outdoor for cameras), port numbers, IPs for infra, link speeds (1G), PoE draw for APs/cameras, distance notes for long runs.
- Legend: rectangle devices, cloud Internet, line colors as above, dashed for WiFi.

# Logical Network Architecture Diagram Specification

## Layout
- Top-down: Internet -> UDMP -> VLAN clouds -> devices.
- UDMP shown with WAN + VLAN interfaces (IDs and gateways), NAT boundary highlighted, services (DHCP/DNS/Firewall/IDS).

## VLAN Clouds
- Colors: Management dark blue, Trusted green, IoT yellow, Guest red, Servers blue, Cameras orange.
- Each cloud lists VLAN name, ID, subnet, gateway.

## Traffic Flows
- Solid arrows for allowed flows labeled with protocols (e.g., Trusted→Servers HTTP/S, SSH, SMB).
- Dashed with red X for denied flows (e.g., Guest→any RFC1918).
- Example paths numbered for internet access, inter-VLAN allowed and denied cases.

## Security Zones
- Group boxes: Trusted Zone (Management + Trusted), Restricted (IoT + Cameras), Isolated (Guest).
- Note IDS/IPS inspection and DNS hierarchy (UDMP -> OpenDNS -> public resolvers).

# Physical Network Topology Diagram Specification

## Layout Structure
- Orientation left-to-right: Internet -> UDMP -> Switch -> APs/Servers -> End devices.
- Group components by location: rack, office, living room, bedrooms.
- Color scheme: red WAN, blue trunks, green access, orange fiber.

## Components
- ISP cloud labeled "Internet via Comcast 1G/35M" connected by red line to Arris SB8200 modem.
- SB8200 to UDMP WAN (red); UDMP LAN1 trunk (blue) to Switch port 23.
- Rack box containing UDMP (top), Switch (middle), Proxmox/TrueNAS servers (below).
- Switch annotations: ports 1-8 Trusted access (green), 9-12 Servers (green/blue to servers), 13-16 AP trunks (blue), 17-20 Cameras (green), 21 IoT (green), 22 Printer (green), 24 spare trunk (blue dotted).
- APs shown with WiFi callouts listing SSID to VLAN mappings.
- End-device clusters by VLAN: Trusted (green box), IoT (yellow), Guest (red), Servers (blue in rack), Cameras (orange to NVR).
- Include link speeds on lines (1G copper), PoE wattage on AP/camera links, distances for long runs.

## Legend
- Rectangles for physical devices, cloud for WAN, solid lines for wired, dashed for wireless, color-coded per link type.

# Logical Network Architecture Diagram Specification

## Layout
- Top Internet cloud -> UDMP firewall/router -> VLAN clouds for Management, Trusted, IoT, Guest, Servers, Cameras.
- Arrows showing allowed flows (solid) and denied (dashed with red X), labeled with allowed protocols.
- UDMP annotated with NAT boundary, DHCP/DNS services, IDS/IPS.
- Security zones grouped: Trusted (Management+Trusted), Restricted (IoT+Cameras), Isolated (Guest).
- Include DHCP ranges and gateways inside VLAN bubbles.
- Example flows: Trusted -> Servers (HTTP/S, SSH, SMB), IoT -> Internet (HTTP/S), Guest -> Internet only with red X to other VLANs.

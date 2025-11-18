# Physical Network Topology Diagram Specification

## Layout
- Orientation left-to-right: Internet → UDMP → Switch → APs/Servers/Endpoints.
- Grouping by location: rack, office, living room, bedroom, exterior.
- Colors: red=WAN, blue=trunk, green=access, orange=fiber.

## Components
1. ISP cloud labeled "Comcast 1G/35M" → red line to Arris SB8200.
2. SB8200 modem rectangle → red line to UDMP WAN.
3. Rack box containing UDMP (top), Switch 24 PoE (below), servers (Proxmox1/2, TrueNAS).
   - UDMP LAN to Switch via blue trunk, annotated "all VLANs" and port numbers.
   - Switch port annotations: ports 1-8 VLAN10 access, 9-12 VLAN40 access, 13-16 AP trunks (1/10/20/30), 17-20 VLAN50 cameras, 21 IoT, 22 printer, 23 uplink, 24 spare trunk.
4. APs: Office AP on trunk port13; Living Room AP on port14; Bedroom AP on port15. Callouts for SSIDs and VLAN mappings.
5. Endpoints grouped by VLAN color-coded boxes: Trusted (green devices), IoT (yellow), Guest (red), Servers (blue servers), Cameras (orange cameras to NVR).
6. Annotations: cable type (Cat6, outdoor-rated), PoE draw per device, link speeds (1G).
7. Legend: shapes/line styles/colors, NAT boundary at UDMP.

# Logical Network Architecture Diagram Specification
- Top-down layers: Internet → UDMP security edge → services (DNS/DHCP) → VLAN clouds → device groups.
- Each VLAN cloud shows name, ID, subnet, gateway; colors per VLAN list.
- Security zones boxes: Trusted zone (Mgmt+Trusted), Restricted (IoT+Cameras), Isolated (Guest).
- Arrows with allowed traffic: Trusted→Servers (HTTP/S, SSH, SMB), Trusted→Management (SSH/HTTPS), IoT→Internet (HTTP/S), Guest→Internet (HTTP/S).
- Red X dashed lines for denied paths: IoT→Trusted, Guest→LAN, Cameras→Internet.
- Numbered flows: 1) Internet browsing path, 2) Trusted→Server access, 3) Blocked IoT lateral attempt.
- Notes: NAT at UDMP, DNS chain UDMP→Cloudflare/Google, DHCP scopes per VLAN.

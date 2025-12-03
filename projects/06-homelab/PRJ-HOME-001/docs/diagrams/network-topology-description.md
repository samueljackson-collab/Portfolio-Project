# Network Topology Diagram Descriptions

## Physical Network Topology Diagram Specification

### Layout Structure
- **Orientation**: Left-to-right flow, Internet on far left, end devices on far right.
- **Grouping**: By physical location (rack, office, living room, exterior).
- **Color Scheme**: Red = WAN, Blue = trunks, Green = access ports, Orange = fiber (future-ready callouts).

### Components to Include
1. **ISP Cloud** labeled "Internet via Comcast" with note "1 Gbps / 35 Mbps".
2. **Cable Modem (Arris SB8200)** rectangle; red line to ISP cloud; red line to UDMP WAN.
3. **Network Rack** (center-left) boxed with:
   - **UDM-Pro** at top: red WAN from modem; blue trunk from LAN1 to switch; labels for Mgmt IP 192.168.1.1 and WAN DHCP IP.
   - **USW-24-POE** below UDMP: blue trunk from UDMP to port 23; annotations per port:
     - Ports 1-8 green access VLAN10 (Trusted) for workstations/docks.
     - Ports 9-12 green access VLAN40 (Servers) for Proxmox/TrueNAS.
     - Ports 13-16 blue trunks (all VLANs) PoE to APs; PoE wattage labels (15.4/13.2/14.1W) and reserved port 16.
     - Ports 17-20 green access VLAN50 (Cameras) with PoE draws labeled; note 100M links.
     - Port 21 green access VLAN20 (IoT hub).
     - Port 22 green access VLAN10 (Printer).
     - Port 23 blue trunk uplink to UDMP; Port 24 blue trunk spare.
   - **Servers** stacked under switch: Proxmox-01 (Port9 VLAN40), Proxmox-02 (Port10), TrueNAS (Port11).
4. **Wireless APs (center-right)** with PoE blue trunks from switch ports 13/14/15:
   - AP-Office: SSIDs HomeNetwork-5G→VLAN10, IoT→VLAN20, Guest→VLAN30; channel/power notes.
   - AP-LivingRoom: same SSIDs; channel 36 80MHz; power 20 dBm.
   - AP-Bedroom: same SSIDs; channel 149 80MHz; power 18 dBm.
5. **End Devices (far right) grouped by VLAN-colored boxes**:
   - Trusted (green): 3 desktops, 2 laptops, 4 phones, 2 tablets, 1 TV, 1 printer (also shown on port 22 path).
   - IoT (yellow): smart speakers, lights, thermostat, smart plugs; cloud icon for outbound HTTPS.
   - Guest (red): 2-3 generic devices; red isolation note.
   - Servers (blue): Proxmox nodes + TrueNAS already in rack area.
   - Cameras (orange): 4 camera icons linking to VLAN50 ports; arrow to NVR within UDMP/Protect.
6. **Annotations**: cable types (Cat6, outdoor Cat5e), lengths, link speeds (1G or 100M), PoE power, port numbers, distances for long runs.
7. **Legend**: shapes, line colors, line thickness mapping to link speed; dashed lines for WiFi coverage arcs from each AP.

## Logical Network Architecture Diagram Specification

### Layout Structure
- **Orientation**: Top-down hierarchy: Internet → UDMP → VLAN clouds → devices.
- **Layers**:
  1. Internet (top cloud).
  2. Security/Edge: UDMP rectangle with WAN and VLAN interfaces.
  3. Services: DHCP/DNS/NTP/IDS shown inside UDMP box.
  4. VLAN Clouds: Mgmt (1), Trusted (10), IoT (20), Guest (30), Servers (40), Cameras (50) with color coding.
  5. Devices grouped inside respective VLAN clouds.

### VLAN Representation
- Each cloud shows name, ID, subnet, gateway. Colors: Mgmt dark blue, Trusted green, IoT yellow, Guest red, Servers blue, Cameras orange.

### Connections Between VLANs
- Solid black arrows for allowed flows with labels (e.g., Trusted → Servers: "HTTP/S, SSH, SMB, NFS").
- Dashed lines with red X for denied paths (e.g., Guest → any RFC1918, IoT → Trusted).
- NAT boundary drawn on UDMP between LAN and Internet.

### Gateway/Router Details
- UDMP rectangle lists interfaces: VLAN1 192.168.1.1, VLAN10 192.168.10.1, VLAN20 192.168.20.1, VLAN30 192.168.30.1, VLAN40 192.168.40.1, VLAN50 192.168.50.1; WAN DHCP IP.
- Services: DHCP scopes, DNS forwarders (OpenDNS/Cloudflare), IDS/IPS, DPI, VPN (disabled by default), NVR (Protect) linked to Cameras VLAN.

### Security Zones
- Dotted grouping boxes: Trusted Zone (Mgmt + Trusted + Servers), Restricted Zone (IoT + Cameras), Isolated Zone (Guest).

### Traffic Flow Examples
1. Internet access: Trusted device → UDMP → NAT → Internet (arrow sequence).
2. Inter-VLAN allowed: Trusted → Servers (HTTP/S, SSH, SMB) with rule number 200.
3. Inter-VLAN denied: IoT → Trusted with dashed line and red X referencing deny rule 1000.
4. Camera streaming: Cameras → UDMP → Servers (RTSP 554) labeled rule 900/210.

### Annotations
- DHCP ranges per VLAN, DNS hierarchy (UDMP → OpenDNS/Cloudflare), firewall rule references, IDS/IPS mode (block on WAN, alert on LAN), content filtering on Guest, bandwidth limits on Guest (25/10 Mbps).

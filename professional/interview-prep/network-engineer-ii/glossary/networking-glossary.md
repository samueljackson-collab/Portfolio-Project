# Network Engineer II - Comprehensive Networking Glossary

## Purpose
This glossary covers all acronyms, protocols, concepts, and terminology referenced in the Network Engineer II interview prep materials. Use this as a quick reference when studying or during interviews.

---

## A

**ABR (Area Border Router)**
- Router that connects two or more OSPF areas
- Maintains separate LSDBs for each area
- Performs route summarization between areas
- Example: Router connecting Area 1 to Area 0 (backbone)

**ACL (Access Control List)**
- Firewall rules that permit or deny traffic based on criteria (IP, port, protocol)
- Standard ACL: Filters based on source IP only (1-99, 1300-1999)
- Extended ACL: Filters on source/dest IP, port, protocol (100-199, 2000-2699)
- Example: `access-list 100 permit tcp any any eq 80`

**ARP (Address Resolution Protocol)**
- Resolves IP addresses to MAC addresses on local network
- Broadcasts "Who has IP 192.168.1.5?" on Layer 2
- Device with that IP responds with MAC address
- Cached in ARP table to avoid repeated broadcasts

**AS (Autonomous System)**
- Collection of networks under single administrative control
- Identified by AS Number (ASN): 1-65535
- Example: AS 15169 = Google, AS 7922 = Comcast
- Used in BGP for inter-domain routing

**AS-PATH**
- BGP attribute listing AS numbers a route has traversed
- Format: AS1 AS2 AS3 (e.g., 65001 65002 15169)
- Shorter AS-PATH preferred (BGP path selection criterion #4)
- Can be prepended to make path less desirable

**ASBR (Autonomous System Border Router)**
- OSPF router connecting to external routing domains (BGP, static routes)
- Advertises external routes as Type 5 LSAs (E1/E2)
- Example: Router running both OSPF and BGP

---

## B

**BGP (Border Gateway Protocol)**
- Exterior Gateway Protocol (EGP) for routing between autonomous systems
- Path-vector protocol (not distance-vector or link-state)
- Uses TCP port 179 for reliable connections
- Two types: eBGP (between AS) and iBGP (within AS)
- Slowest convergence (minutes) but most scalable (Internet-scale)

**BPDU (Bridge Protocol Data Unit)**
- Spanning Tree Protocol control frames
- Contains: Root Bridge ID, sender Bridge ID, port costs, timers
- Sent every 2 seconds by default
- Used to detect and prevent Layer 2 loops

**BDR (Backup Designated Router)**
- OSPF backup to DR on multi-access networks
- Takes over if DR fails
- Forms adjacencies with all routers on segment
- Election: Second-highest priority, then second-highest router-ID

---

## C

**CAPWAP (Control and Provisioning of Wireless Access Points)**
- Protocol for managing lightweight APs from central controller
- Encapsulates wireless frames between AP and WLC
- Uses UDP ports 5246 (control) and 5247 (data)
- Example: Cisco APs communicating with Cisco WLC

**CE (Customer Edge)**
- Customer router in MPLS VPN architecture
- Connects to Provider Edge (PE) router
- Runs standard routing protocols (BGP, OSPF, static)
- No knowledge of MPLS labels or VRFs

**CLI (Command Line Interface)**
- Text-based interface for configuring network devices
- Cisco IOS example: `Router> enable` → `Router# configure terminal`
- Juniper JUNOS: `user@router> configure` → `[edit]`
- Modes: User EXEC, Privileged EXEC, Global Config, Interface Config

**CRC (Cyclic Redundancy Check)**
- Error-detection code in Ethernet frames
- Detects corruption during transmission
- CRC errors indicate bad cable, duplex mismatch, or interference
- Example output: `show interfaces gi0/1` → "15 CRC errors"

---

## D

**DHCP (Dynamic Host Configuration Protocol)**
- Automatically assigns IP addresses to devices
- Uses UDP ports 67 (server) and 68 (client)
- DORA process: Discover, Offer, Request, Acknowledge
- Options: Default gateway, DNS servers, NTP servers, etc.

**DIS (Designated Intermediate System)**
- ISIS equivalent of OSPF's DR
- Elected on broadcast/multi-access networks
- Does NOT form special adjacencies (unlike OSPF)
- No BDR equivalent in ISIS

**DNS (Domain Name System)**
- Resolves hostnames to IP addresses
- Hierarchical: Root servers → TLDs (.com, .net) → Authoritative servers
- Uses UDP port 53 (queries) and TCP port 53 (zone transfers)
- Example: www.google.com → 142.250.185.46

**DR (Designated Router)**
- OSPF router elected on multi-access networks (Ethernet, etc.)
- Reduces number of adjacencies (all routers peer with DR and BDR only)
- Election: Highest priority (1-255), then highest router-ID
- Priority 0 = never becomes DR/BDR

---

## E

**eBGP (External BGP)**
- BGP between different autonomous systems
- Default AD (Administrative Distance) = 20
- TTL = 1 by default (neighbors must be directly connected, or use `ebgp-multihop`)
- Example: AS 65001 peering with AS 65002

**EIGRP (Enhanced Interior Gateway Routing Protocol)**
- Cisco proprietary hybrid routing protocol (distance-vector with link-state features)
- Uses DUAL algorithm for loop-free paths
- Fast convergence, efficient updates
- Multicast address: 224.0.0.10

**EtherChannel**
- Cisco term for Link Aggregation (IEEE 802.3ad / 802.1AX)
- Bundles multiple physical links into single logical link
- Protocols: PAgP (Cisco proprietary), LACP (IEEE standard)
- Load balancing: src-mac, dst-mac, src-dst-mac, src-dst-ip

---

## F

**FIB (Forwarding Information Base)**
- Hardware table used for fast packet forwarding
- Derived from routing table (RIB)
- Stored in ASIC/TCAM for line-rate forwarding
- Example: `show ip cef` (Cisco Express Forwarding)

---

## G

**GRE (Generic Routing Encapsulation)**
- Tunneling protocol that encapsulates packets
- Creates point-to-point tunnels over IP networks
- Protocol number: 47
- Example: Site-to-site VPN tunnel before encryption

---

## H

**HSRP (Hot Standby Router Protocol)**
- Cisco proprietary FHRP (First Hop Redundancy Protocol)
- Provides default gateway redundancy
- Virtual IP shared between active and standby routers
- Uses multicast 224.0.0.2 (v1) or 224.0.0.102 (v2)
- Alternative: VRRP (standard), GLBP (Cisco, load-balancing)

**HTTP (Hypertext Transfer Protocol)**
- Application-layer protocol for web traffic
- Uses TCP port 80 (HTTP) or 443 (HTTPS with TLS)
- Methods: GET, POST, PUT, DELETE
- Stateless protocol (each request independent)

---

## I

**iBGP (Internal BGP)**
- BGP within same autonomous system
- Default AD = 200 (lower preference than OSPF, EIGRP)
- Requires full mesh or route reflectors (no split-horizon rule)
- Next-hop is NOT changed by default (unlike eBGP)

**ICMP (Internet Control Message Protocol)**
- Network-layer protocol for diagnostics and error reporting
- Used by: ping (Echo Request/Reply), traceroute (TTL Exceeded), path MTU discovery
- Protocol number: 1
- Example: "Destination Unreachable" when host is down

**IDS/IPS (Intrusion Detection/Prevention System)**
- IDS: Detects and alerts on suspicious traffic (passive)
- IPS: Detects and blocks/modifies suspicious traffic (active)
- Signature-based: Matches known attack patterns
- Anomaly-based: Detects deviations from baseline
- Example: Snort, Suricata, Cisco Firepower

**IGP (Interior Gateway Protocol)**
- Routing protocol within an autonomous system
- Examples: OSPF, ISIS, EIGRP, RIP
- Contrasts with EGP (BGP)

**IPsec (Internet Protocol Security)**
- Suite of protocols for securing IP communications
- Two modes: Transport (end-to-end) and Tunnel (site-to-site VPN)
- Protocols: AH (Authentication Header), ESP (Encapsulating Security Payload)
- Key exchange: IKE (Internet Key Exchange)

**ISIS (Intermediate System to Intermediate System)**
- Link-state IGP routing protocol (OSI model, not IP-based)
- Two levels: Level 1 (intra-area) and Level 2 (inter-area/backbone)
- Runs directly on Layer 2 (no IP required on links)
- Popular in ISP networks for scalability

---

## J

**JUNOS (Juniper Networks Operating System)**
- Operating system for Juniper routers and switches
- CLI differences from Cisco IOS: `commit` required, `rollback` available
- Configuration hierarchy: [edit protocols ospf], [edit interfaces]
- Example: `show configuration | display set`

---

## L

**L1 (Level 1 - ISIS)**
- Intra-area routing in ISIS
- Similar to OSPF areas (not backbone)
- L1 routers only know topology within their area

**L2 (Level 2 - ISIS)**
- Inter-area/backbone routing in ISIS
- Similar to OSPF Area 0
- L1/L2 routers connect L1 areas to L2 backbone

**L3VPN (Layer 3 Virtual Private Network)**
- MPLS-based VPN service connecting sites at Layer 3 (IP routing)
- Uses VRFs on PE routers to isolate customer traffic
- Contrasts with L2VPN (VPLS, VPWS) which extends Layer 2

**LACP (Link Aggregation Control Protocol)**
- IEEE 802.1AX standard for link bundling
- Active mode: Initiates LACP negotiation
- Passive mode: Responds to LACP but doesn't initiate
- Preferred over PAgP (Cisco proprietary)

**LDP (Label Distribution Protocol)**
- MPLS protocol for distributing labels between routers
- Creates Label Switched Paths (LSPs)
- Uses TCP port 646
- Neighbors discover via UDP multicast to 224.0.0.2

**LSA (Link-State Advertisement)**
- OSPF topology information packets
- Types: 1 (Router), 2 (Network), 3 (Summary), 4 (ASBR Summary), 5 (External), 7 (NSSA External)
- Flooded within area (Types 1, 2) or across areas (Types 3, 4, 5)
- Stored in LSDB

**LSDB (Link-State Database)**
- Database of all LSAs in an OSPF area
- Each router in area has identical LSDB
- Used by SPF algorithm to calculate shortest paths
- View with: `show ip ospf database`

**LSP (Link-State PDU - ISIS)**
- ISIS equivalent of OSPF LSAs
- Contains topology information for ISIS routing
- Flooded within level (L1 or L2)

---

## M

**MAC (Media Access Control)**
- Layer 2 address (hardware address)
- Format: 48-bit (6 bytes), e.g., AA:BB:CC:DD:EE:FF
- First 24 bits: OUI (Organizationally Unique Identifier, vendor ID)
- Last 24 bits: Device-specific
- Example: Cisco OUI = 00:1A:A1

**MED (Multi-Exit Discriminator)**
- BGP attribute suggesting preferred entry point into AS
- Lower MED is preferred
- Only compared between routes from same neighboring AS
- Optional non-transitive attribute (doesn't propagate beyond immediate neighbors)

**MPLS (Multiprotocol Label Switching)**
- Packet-forwarding technology using labels instead of IP lookups
- Labels: 20-bit identifier (0-1,048,575)
- Operations: Push (add label), Pop (remove label), Swap (change label)
- Benefits: Fast forwarding, traffic engineering, VPNs

**MSTP (Multiple Spanning Tree Protocol)**
- IEEE 802.1s standard for spanning tree
- Maps multiple VLANs to single spanning tree instance (reduces overhead)
- Regions: Group of switches with same configuration
- Interoperates with STP/RSTP at region boundaries

**MTU (Maximum Transmission Unit)**
- Largest packet size that can be transmitted without fragmentation
- Standard Ethernet MTU: 1500 bytes
- Jumbo frames: Up to 9000 bytes (for high-performance networks)
- MPLS adds ~8 bytes per label (may cause fragmentation issues)

---

## N

**NAT (Network Address Translation)**
- Translates private IP addresses to public IPs (and vice versa)
- Types: Static NAT (one-to-one), Dynamic NAT (pool), PAT/Overload (many-to-one with ports)
- Conserves public IPv4 addresses
- Can break some protocols (FTP, SIP) requiring ALG (Application Layer Gateway)

**NET (Network Entity Title)**
- ISIS address format: Area.System-ID.SEL
- Example: 49.0001.1921.6800.1001.00
  - 49 = Private AFI (like RFC 1918 private IP)
  - 0001 = Area ID
  - 1921.6800.1001 = System ID (often derived from IP like 192.168.1.1)
  - 00 = SEL (always 00 for routers)

**NTP (Network Time Protocol)**
- Synchronizes clocks across network devices
- Uses UDP port 123
- Stratum hierarchy: 0 (atomic clock), 1 (directly connected to stratum 0), etc.
- Critical for: Logs correlation, certificates, authentication

---

## O

**OSPF (Open Shortest Path First)**
- Link-state IGP routing protocol (RFC 2328 for OSPFv2, RFC 5340 for OSPFv3)
- Uses Dijkstra's SPF algorithm
- Metric: Cost = 100,000,000 / bandwidth (in bps)
- Multicast addresses: 224.0.0.5 (all OSPF routers), 224.0.0.6 (DR/BDR)
- Areas: 0 (backbone) plus non-backbone areas

---

## P

**P (Provider Router)**
- MPLS core router
- Only knows about PE router loopbacks (no customer routes)
- Switches packets based on labels only (fast!)
- No VRFs needed

**PAgP (Port Aggregation Protocol)**
- Cisco proprietary link aggregation protocol
- Modes: Auto (passive), Desirable (active)
- Prefer LACP (standard) for interoperability

**PE (Provider Edge Router)**
- MPLS router connecting to customer (CE) routers
- Maintains VRFs for customer isolation
- Applies/removes MPLS labels
- Runs MP-BGP to exchange VPNv4 routes with other PEs

**PortFast**
- Cisco STP feature that skips Listening and Learning states
- Brings port to Forwarding immediately (~2 seconds vs ~30 seconds)
- ONLY use on access ports (end devices, not switches)
- Enable with: `spanning-tree portfast`

---

## Q

**QoS (Quality of Service)**
- Traffic prioritization to ensure critical apps get bandwidth
- Techniques: Classification, marking (DSCP), queuing, policing, shaping
- Example: VoIP traffic marked as EF (Expedited Forwarding), gets priority queue

---

## R

**RD (Route Distinguisher)**
- MPLS VPN attribute making customer routes unique across provider network
- Format: ASN:nn or IP:nn (e.g., 65000:10 or 192.168.1.1:10)
- Added as prefix to customer routes (becomes VPNv4 route)
- Must be unique per VRF (even if RTs are same)

**RIB (Routing Information Base)**
- Routing table containing all learned routes
- Each routing protocol has its own RIB (OSPF RIB, BGP RIB, etc.)
- Best routes from each RIB compete based on AD, then copied to FIB

**RIP (Routing Information Protocol)**
- Distance-vector IGP (oldest, simplest routing protocol)
- Metric: Hop count (max 15 hops, 16 = unreachable)
- Slow convergence, inefficient
- Rarely used today (replaced by OSPF, EIGRP)

**RSTP (Rapid Spanning Tree Protocol)**
- IEEE 802.1w standard (evolved from STP)
- Fast convergence: 2-3 seconds (vs 30-50 seconds for STP)
- Port roles: Root, Designated, Alternate, Backup
- Backward compatible with STP

**RT (Route Target)**
- MPLS VPN attribute controlling route import/export between VRFs
- Format: ASN:nn (e.g., 65000:100)
- Export RT: Tag routes leaving VRF
- Import RT: Accept routes with this tag
- Enables flexible topologies (hub-and-spoke, any-to-any, extranet)

---

## S

**SFP (Small Form-factor Pluggable)**
- Hot-swappable transceiver for fiber/copper connections
- Variants: SFP (1 Gbps), SFP+ (10 Gbps), SFP28 (25 Gbps), QSFP (40 Gbps), QSFP28 (100 Gbps)
- Example: SFP-10G-SR (10 Gbps, multimode fiber, 300m range)

**SNMP (Simple Network Management Protocol)**
- Protocol for monitoring and managing network devices
- Versions: v1/v2c (insecure, community strings), v3 (secure, encryption + auth)
- Uses UDP ports 161 (agent) and 162 (traps)
- MIBs (Management Information Bases) define what can be queried

**SPF (Shortest Path First)**
- Dijkstra's algorithm used by link-state protocols (OSPF, ISIS)
- Calculates shortest path tree from LSDB
- Triggered by topology changes (link up/down)
- CPU-intensive on large networks (reason for OSPF areas)

**SSH (Secure Shell)**
- Secure protocol for remote CLI access
- Uses TCP port 22
- Encrypts all traffic (including passwords)
- Preferred over Telnet (unencrypted)

**STP (Spanning Tree Protocol)**
- IEEE 802.1D standard preventing Layer 2 loops
- Elects root bridge, blocks redundant paths
- Port states: Blocking → Listening → Learning → Forwarding
- Slow convergence (30-50 seconds)

**SYSLOG**
- Standard for logging messages
- Severity levels: 0 (Emergency) to 7 (Debug)
- Uses UDP port 514
- Example: `logging host 192.168.1.100`

---

## T

**TACACS+ (Terminal Access Controller Access-Control System Plus)**
- AAA (Authentication, Authorization, Accounting) protocol
- Cisco-enhanced version (encrypts entire packet)
- Uses TCP port 49
- Alternative: RADIUS (uses UDP, only encrypts password)

**TCN (Topology Change Notification)**
- STP message sent when topology changes (link up/down)
- Causes MAC address table flush across all switches
- Can cause brief traffic disruption

**TFTP (Trivial File Transfer Protocol)**
- Simple file transfer protocol (no authentication)
- Uses UDP port 69
- Common use: Backing up/restoring device configs, upgrading IOS
- Example: `copy running-config tftp:`

**TRILL (Transparent Interconnection of Lots of Links)**
- Layer 2 routing protocol (alternative to STP)
- Uses IS-IS for shortest path calculation
- Allows multiple active paths (unlike STP which blocks)
- Backward compatible with STP

**Trunk**
- Link carrying multiple VLANs (tagged with 802.1q or ISL)
- Example: Switch-to-switch connection carrying VLANs 10, 20, 30
- Native VLAN: Untagged traffic on trunk (default VLAN 1)
- Configure: `switchport mode trunk`

---

## V

**VLAN (Virtual LAN)**
- Logical network segmentation at Layer 2
- Range: 1-4094 (1 and 4094 reserved, 1002-1005 reserved for legacy)
- Benefits: Broadcast domain separation, security, flexibility
- Trunk vs Access: Trunk carries multiple VLANs (tagged), Access carries single VLAN (untagged)

**VPNv4 (VPN IPv4)**
- BGP address family for MPLS L3VPN
- IPv4 prefix + RD = VPNv4 route
- Exchanged between PE routers via MP-BGP
- Requires `send-community extended` (for Route Targets)

**VRF (Virtual Routing and Forwarding)**
- Separate routing table instance on router
- Used in MPLS L3VPN for customer isolation
- Each VRF has its own: Routing table, interfaces, routing protocols
- Example: VRF "CUSTOMER-A" keeps traffic isolated from VRF "CUSTOMER-B"

**VRRP (Virtual Router Redundancy Protocol)**
- Standard FHRP (RFC 5798)
- Similar to HSRP but open standard
- Virtual IP shared between master and backup routers
- Uses multicast 224.0.0.18

**VXLAN (Virtual Extensible LAN)**
- Overlay network technology for data center
- Encapsulates Layer 2 frames in UDP (port 4789)
- Extends VLANs across Layer 3 networks
- Supports 16 million VNIs (vs 4096 VLANs)

---

## W

**WAN (Wide Area Network)**
- Network spanning large geographic area (city, country, world)
- Technologies: MPLS, Metro Ethernet, SD-WAN, Satellite, Cellular
- Contrasts with LAN (Local Area Network)

**Wireshark**
- Open-source packet analyzer
- Captures and displays packets in real-time
- Filters: `tcp.port == 443`, `ip.addr == 192.168.1.1`, `dns`
- Essential for troubleshooting network issues

**WLC (Wireless LAN Controller)**
- Centralized management for lightweight wireless APs
- Handles: Authentication, RF management, roaming, load balancing
- Protocols: CAPWAP (Cisco), LWAPP (legacy)
- Example: Cisco 5520 WLC managing 1000 APs

---

## X

**802.1q**
- IEEE standard for VLAN tagging on trunks
- Adds 4-byte tag to Ethernet frame (VLAN ID)
- Native VLAN: Untagged traffic (default VLAN 1)
- Replaced Cisco ISL (Inter-Switch Link)

**802.1AX**
- IEEE standard for Link Aggregation (EtherChannel)
- Uses LACP for negotiation
- Replaced 802.3ad

**802.11**
- IEEE standard for wireless LAN (Wi-Fi)
- Variants: 802.11a/b/g (legacy), 802.11n (Wi-Fi 4), 802.11ac (Wi-Fi 5), 802.11ax (Wi-Fi 6)
- Frequencies: 2.4 GHz and 5 GHz (802.11ax also supports 6 GHz)

---

## Quick Reference: Common Port Numbers

| Protocol | Port(s) | Transport |
|----------|---------|-----------|
| HTTP | 80 | TCP |
| HTTPS | 443 | TCP |
| SSH | 22 | TCP |
| Telnet | 23 | TCP |
| FTP | 20 (data), 21 (control) | TCP |
| TFTP | 69 | UDP |
| DNS | 53 | UDP (queries), TCP (zone transfers) |
| DHCP | 67 (server), 68 (client) | UDP |
| SNMP | 161 (agent), 162 (traps) | UDP |
| Syslog | 514 | UDP |
| NTP | 123 | UDP |
| BGP | 179 | TCP |
| LDP | 646 | TCP |
| OSPF | - | IP Protocol 89 |
| EIGRP | - | IP Protocol 88 |

---

## Quick Reference: Routing Protocol Comparison

| Protocol | Type | Metric | Convergence | Scalability | Use Case |
|----------|------|--------|-------------|-------------|----------|
| RIP | Distance-vector | Hop count | Slow (minutes) | Small (<15 hops) | Legacy only |
| EIGRP | Hybrid | Bandwidth + Delay | Fast (seconds) | Medium (hundreds) | Cisco networks |
| OSPF | Link-state | Cost (bandwidth) | Medium (seconds) | Large (thousands) | Enterprise |
| ISIS | Link-state | Cost (configurable) | Medium (seconds) | Very large (5000+) | ISP/Carrier |
| BGP | Path-vector | Complex (AS-PATH, etc.) | Slow (minutes) | Internet-scale | Between AS |

---

## Quick Reference: OSPF LSA Types

| LSA Type | Name | Purpose | Flooding Scope |
|----------|------|---------|----------------|
| Type 1 | Router LSA | Router's links and costs | Within area |
| Type 2 | Network LSA | DR's view of multi-access network | Within area |
| Type 3 | Summary LSA | Inter-area routes (from ABR) | Across areas |
| Type 4 | ASBR Summary LSA | Location of ASBR | Across areas |
| Type 5 | External LSA | External routes (from ASBR) | Entire domain (except stub) |
| Type 7 | NSSA External LSA | External routes in NSSA | Within NSSA (converted to Type 5 at ABR) |

---

**Last Updated:** 2025-11-11
**For Role:** Network Engineer II (Denali/T-Mobile)
**Salary:** $150-190K/year

**Usage Tips:**
- Use Ctrl+F to quickly find terms
- Cross-reference with expanded cheat sheets for deeper explanations
- Review protocol comparisons before interviews
- Memorize common port numbers

# Network Engineer II - Expanded Cheat Sheet (Q1-Q10)

## Question 1: OSPF Multi-Area Design

**Question:** Design OSPF for a company with 50 sites. How many areas would you recommend and why?

**Feynman Explanation:**
Think of OSPF areas like organizing a library. You don't want one giant room with millions of books (single area) because finding anything takes forever. But you also don't want 1000 tiny rooms (too many areas) because you spend all your time walking between rooms. OSPF areas are the same - too many routers in one area means everyone has the same huge map and updates are slow. Too many areas means complex routing between areas. The sweet spot is usually one backbone area (Area 0) connecting 5-15 regional areas.

**Technical Answer:**
- **Recommended Design:** 1 backbone (Area 0) + 8-12 regional areas
- **Reasoning:**
  - Area 0: Core routers at HQ/data centers (high-speed backbone)
  - Regional areas: Group sites by geography/function (e.g., Area 1 = East Coast, Area 2 = West Coast)
  - ~4-6 sites per regional area
- **Benefits:**
  - Limits LSDB size (each area has separate topology database)
  - Faster SPF calculations (only intra-area topology changes trigger SPF)
  - Route summarization at ABRs reduces routing table size
  - Isolates failure domains (topology change in Area 1 doesn't affect Area 2)
- **Key Design Principles:**
  - All areas must connect to Area 0 (or use virtual links if not)
  - Summarize routes at ABRs (Area Border Routers)
  - Use stub areas (or totally stubby) for branch offices to reduce routes
  - Plan IP addressing for easy summarization (e.g., 10.1.0.0/16 = Area 1, 10.2.0.0/16 = Area 2)

**Acronym Glossary:**
- **OSPF** = Open Shortest Path First (link-state routing protocol)
- **LSDB** = Link-State Database (topology database maintained by each router)
- **SPF** = Shortest Path First (Dijkstra's algorithm for calculating best routes)
- **ABR** = Area Border Router (router connecting multiple OSPF areas)
- **LSA** = Link-State Advertisement (packets that describe network topology)

**Practical Example:**
```
Enterprise Network: 50 sites

Design:
- Area 0 (Backbone): HQ routers + 2 data center core routers
- Area 1 (East): 8 branch offices (10.1.0.0/16 summarized at ABR)
- Area 2 (West): 8 branch offices (10.2.0.0/16 summarized at ABR)
- Area 3 (Central): 7 branch offices (10.3.0.0/16 summarized at ABR)
- Area 4 (South): 6 branch offices (10.4.0.0/16 summarized at ABR)
- Area 5 (Manufacturing): 10 factory sites (10.5.0.0/16 summarized at ABR)
- Area 6 (Retail): 9 stores (10.6.0.0/16 as stub area)

Why stub area for retail?
- Retail sites only need default route to reach internet/HQ
- No need for external routes (E1/E2) or full inter-area routes
- Reduces memory/CPU on edge routers
```

**Common Pitfalls:**
1. **Too few areas (1 area):** All 50 sites in Area 0 means massive LSDB, slow convergence
2. **Too many areas (50 areas):** Every site is an area = complex ABR config, no summarization benefit
3. **Forgetting Area 0 connectivity:** All areas must touch Area 0 (or use virtual links)
4. **No route summarization:** Defeats the purpose of areas - still see all /24s instead of summary /16
5. **Ignoring network types:** Point-to-point links don't need DR/BDR election, but broadcast networks do
6. **Not using stub areas at edge:** Branch offices don't need full external routing table

**Interview Follow-Up Questions to Expect:**
- "What route types exist in OSPF?" (O, O IA, O E1, O E2, O N1, O N2)
- "Explain DR/BDR election process" (highest priority, then highest router-ID)
- "When would you use a totally stubby area?" (Branch with only default route needed)
- "What's a virtual link and when do you need it?" (Connect area to Area 0 when no physical connection)

---

## Question 2: BGP Path Selection

**Question:** Traffic is taking a suboptimal path through your BGP network. Walk me through troubleshooting and fixing this.

**Feynman Explanation:**
BGP is like GPS navigation with multiple route options. When GPS picks a longer route, it's usually because of "hidden" preferences like avoiding tolls, preferring highways, or faster speed limits - not just distance. BGP is similar: it doesn't pick the shortest AS path by default. Instead, it checks a list of 13+ criteria in order. If you want to influence the path, you need to understand this "decision list" and change the right attribute. It's like telling your GPS "I don't care about tolls, just give me the fastest route" - you're adjusting the preference order.

**Technical Answer:**

**BGP Path Selection Algorithm (in order):**
1. **Weight** (Cisco-specific, higher is better) - local to router
2. **Local Preference** (higher is better) - local to AS
3. **Locally Originated** (prefer routes this router created)
4. **AS-PATH** (shorter is better) - global attribute
5. **Origin** (IGP > EGP > Incomplete)
6. **MED** (lower is better) - hints from neighboring AS
7. **eBGP > iBGP**
8. **IGP metric** to next-hop (lower is better)
9. **Oldest path** (prefer stable routes)
10. **Lowest Router-ID**
11. **Lowest neighbor IP**

**Troubleshooting Steps:**
```bash
# 1. Identify current path
show ip bgp 10.0.0.0/8
# Look at "best" path marker (>), note next-hop and AS-PATH

# 2. See all available paths
show ip bgp 10.0.0.0/8 longer-prefixes
# Compare attributes of all paths (weight, local-pref, AS-PATH, MED)

# 3. Check why current path was chosen
show ip bgp 10.0.0.0/8 bestpath
# Shows which selection criterion was used

# 4. Verify optimal path exists
# Is there a shorter AS-PATH? Lower latency? Different next-hop?
```

**Fixing Suboptimal Path:**

**Option A: Weight (local to router)**
```cisco
router bgp 65001
 neighbor 192.168.1.1 weight 200  ! Prefer routes from this neighbor
```
Use when: You want one router to prefer specific neighbor

**Option B: Local Preference (entire AS)**
```cisco
route-map SET-LOCAL-PREF permit 10
 match ip address prefix-list PREFER-THIS-ROUTE
 set local-preference 150  ! Default is 100, higher wins
!
router bgp 65001
 neighbor 192.168.1.1 route-map SET-LOCAL-PREF in
```
Use when: You want entire AS to prefer specific paths

**Option C: AS-PATH Prepending (outbound traffic engineering)**
```cisco
route-map PREPEND permit 10
 set as-path prepend 65001 65001 65001  ! Add your AS 3 times
!
router bgp 65001
 neighbor 203.0.113.1 route-map PREPEND out
```
Use when: You want neighbors to deprioritize this path (inbound traffic control)

**Option D: MED (suggest to neighbor which path to use)**
```cisco
route-map SET-MED permit 10
 set metric 50  ! Lower MED is preferred
!
router bgp 65001
 neighbor 203.0.113.1 route-map SET-MED out
```
Use when: You want to suggest (not force) path to neighbor AS

**Acronym Glossary:**
- **BGP** = Border Gateway Protocol (exterior routing protocol, AS to AS)
- **AS** = Autonomous System (collection of networks under single administrative control)
- **eBGP** = External BGP (between different AS)
- **iBGP** = Internal BGP (within same AS)
- **MED** = Multi-Exit Discriminator (metric to suggest preferred entry point)
- **IGP** = Interior Gateway Protocol (OSPF, ISIS, EIGRP within AS)
- **EGP** = Exterior Gateway Protocol (old protocol, now means "external")

**Practical Example:**
```
Scenario: Your company (AS 65001) has two ISP connections:
- ISP-A (AS 65100): 100 Mbps, $500/month, low latency
- ISP-B (AS 65200): 1 Gbps, $2000/month, high latency

Problem: Traffic to 8.8.8.8 (Google DNS) goes via ISP-B (higher cost)

Investigation:
Router# show ip bgp 8.8.8.8
   Network          Next Hop            Path
*> 8.8.8.0/24       203.0.113.2 (ISP-B) 65200 15169  ! Current path
*  8.8.8.0/24       203.0.113.1 (ISP-A) 65100 15169  ! Better path

Both paths have same AS-PATH length (2 hops). Why ISP-B chosen?
- Higher local-preference? No (default 100 both)
- eBGP vs iBGP? Both eBGP
- IGP metric? ISP-B has lower metric to next-hop!

Solution: Increase local-preference for ISP-A
route-map PREFER-ISP-A permit 10
 set local-preference 150
!
router bgp 65001
 neighbor 203.0.113.1 route-map PREFER-ISP-A in
```

**Common Pitfalls:**
1. **Forgetting iBGP full mesh:** iBGP doesn't advertise routes learned from iBGP to other iBGP peers (use route-reflectors)
2. **Weight vs Local-Pref confusion:** Weight is local to router, local-pref affects entire AS
3. **Outbound vs Inbound control:** Weight/local-pref control your outbound, AS-PATH prepend controls inbound from others
4. **MED only works between same AS:** MED from AS 65100 and AS 65200 not compared (only within single AS)
5. **Not checking next-hop reachability:** BGP route in table but not used if next-hop not reachable via IGP
6. **AS-PATH too long:** Prepending 20 times makes path look terrible, other AS may not accept it

**Interview Follow-Up Questions to Expect:**
- "What's the difference between weight and local preference?" (Weight = local router, local-pref = entire AS)
- "When would you use a route-reflector?" (Avoid iBGP full mesh in large networks)
- "Explain BGP synchronization rule" (Old rule: don't use iBGP route until learned via IGP - usually disabled now)
- "What's a BGP community?" (Tag on routes to group/filter them, like 65001:100)

---

## Question 3: Cisco IOS Troubleshooting

**Question:** Walk me through troubleshooting a switch port that's not passing traffic.

**Feynman Explanation:**
Troubleshooting a switch port is like debugging why your TV isn't working. You check in layers: Is it plugged in? (Physical) Is the TV on? (Link status) Is the right input selected? (VLAN) Is there a signal? (Traffic) Is the cable good? (Errors) You don't jump to "the TV is broken" - you systematically check each layer from physical to logical.

**Technical Answer:**

**Systematic Troubleshooting Process:**

**Step 1: Physical Layer (Is link up?)**
```cisco
show interfaces gi0/1
# Look for:
# - "GigabitEthernet0/1 is up, line protocol is up" (GOOD)
# - "GigabitEthernet0/1 is down" (physical issue)
# - "up, line protocol is down" (Layer 2 issue)
```

**If link is down:**
- Check cable physically plugged in
- Try different cable (cable fault?)
- Check for `shutdown` in config: `show run interface gi0/1`
- Check speed/duplex mismatch: `show interfaces gi0/1 | include duplex`
- Check if disabled by port-security: `show port-security interface gi0/1`

**Step 2: Layer 2 Status (VLAN, trunking, spanning-tree)**
```cisco
# Check VLAN assignment
show vlan brief | include Gi0/1
# or
show interfaces gi0/1 switchport

# Check if trunk when it should be access (or vice versa)
show interfaces trunk

# Check spanning-tree status (is port blocked/discarding?)
show spanning-tree interface gi0/1
# Look for: "forwarding" (GOOD), "blocking" or "discarding" (BAD)
```

**If VLAN issues:**
```cisco
# Assign to correct VLAN
interface gi0/1
 switchport mode access
 switchport access vlan 10
 no shutdown
```

**If trunk issues:**
```cisco
# Check allowed VLANs on trunk
show interfaces gi0/1 trunk
# Might show "Vlans allowed on trunk: none" (BAD)

# Fix trunk allowed VLANs
interface gi0/1
 switchport trunk allowed vlan 10,20,30
```

**Step 3: Check for errors/discards**
```cisco
show interfaces gi0/1
# Look for:
# - Input errors (CRC, runts, giants) = bad cable or duplex mismatch
# - Output drops = congestion or QoS dropping packets
# - Collisions (half-duplex issues)
```

**Step 4: Verify traffic flow**
```cisco
# Check MAC address table (is device learned on this port?)
show mac address-table interface gi0/1

# Monitor real-time traffic
show interfaces gi0/1 | include packets
# Wait 10 seconds
show interfaces gi0/1 | include packets
# Compare - are counters increasing?
```

**Step 5: Check security features**
```cisco
# Port security might be shutting port down
show port-security interface gi0/1
# Look for: "Security Violation Count: 1" (ISSUE FOUND)

# Check if in err-disabled state
show interfaces status err-disabled

# Recovery from err-disabled
interface gi0/1
 shutdown
 no shutdown
```

**Step 6: Advanced checks**
```cisco
# Check for ACLs blocking traffic
show ip access-lists interface gi0/1

# Check for DHCP snooping issues
show ip dhcp snooping

# Check storm-control
show storm-control gi0/1
```

**Acronym Glossary:**
- **CRC** = Cyclic Redundancy Check (error-checking code - CRC errors = bad cable/interference)
- **VLAN** = Virtual LAN (logical network segmentation)
- **STP** = Spanning Tree Protocol (prevents Layer 2 loops)
- **MAC** = Media Access Control (hardware address like aa:bb:cc:dd:ee:ff)
- **QoS** = Quality of Service (traffic prioritization)
- **ACL** = Access Control List (filter traffic based on rules)
- **DHCP** = Dynamic Host Configuration Protocol (automatic IP assignment)

**Practical Example:**
```
Scenario: User reports "computer can't access network" on port Gi0/1

Step 1: Check physical
Switch# show interfaces gi0/1 status
Port      Name     Status       Vlan
Gi0/1              err-disabled 10

FINDING: Port in err-disabled state! This means security violation.

Step 2: Check why err-disabled
Switch# show port-security interface gi0/1
Port Security              : Enabled
Port Status                : Secure-shutdown
Violation Mode             : Shutdown
Aging Time                 : 0 mins
SecureStatic Address Aging : Disabled
Maximum MAC Addresses      : 1
Total MAC Addresses        : 2  <-- TWO MACs when max is 1!
Configured MAC Addresses   : 0
Sticky MAC Addresses       : 0
Last Source Address:Vlan   : 0011.2233.4455:10
Security Violation Count   : 1

ROOT CAUSE: User plugged in switch/hub, learned 2 MAC addresses, port-security shut down port

Step 3: Fix
Switch(config)# interface gi0/1
Switch(config-if)# shutdown
Switch(config-if)# no shutdown
Switch(config-if)# end

Step 4: Verify
Switch# show interfaces gi0/1 status
Port      Name     Status       Vlan
Gi0/1              connected    10

RESOLVED: Tell user not to plug in switch/hub, or increase max MACs
```

**Common Pitfalls:**
1. **Not checking both sides:** Cable plugged in on switch but not on PC
2. **Speed/duplex mismatch:** One side auto, other side hardcoded = half-duplex and errors
3. **Wrong VLAN:** Port in VLAN 10, but rest of network in VLAN 20
4. **Trunk when should be access:** PC doesn't speak 802.1q tagging
5. **Err-disabled not recovered:** Port stays down even after fixing root cause - must manually recover
6. **STP blocking port:** Valid by design, but users think "broken"
7. **Native VLAN mismatch on trunk:** Causes traffic black hole

**Interview Follow-Up Questions to Expect:**
- "What's the difference between shutdown and err-disabled?" (Shutdown = admin down, err-disabled = security/error)
- "Explain duplex mismatch symptoms" (Late collisions, CRC errors, poor performance)
- "When would you use switchport mode dynamic?" (Usually don't - explicitly set access or trunk)
- "What is a native VLAN on a trunk?" (VLAN for untagged traffic - default VLAN 1)

---

## Question 4: Layer 2 Switching - Spanning Tree

**Question:** A broadcast storm is taking down your network. How do you troubleshoot and prevent this?

**Feynman Explanation:**
A broadcast storm is like an echo chamber. Someone yells, everyone hears it and yells it again, so it loops forever getting louder. In networks, if you have a loop (switch A → switch B → switch C → back to switch A), one broadcast packet circles forever, multiplying each time, until the network is 100% broadcast traffic. Spanning Tree Protocol (STP) is like putting doors with one-way locks in the echo chamber - it blocks certain paths to prevent loops while keeping the network connected.

**Technical Answer:**

**What is a Broadcast Storm:**
- Layer 2 loop (no TTL in Ethernet frames to stop loops like IP has)
- Broadcasts (ARP, DHCP, etc.) loop forever
- Each switch forwards broadcast on all ports except source
- Traffic multiplies exponentially (1 → 10 → 100 → 1000 → network saturated)
- Symptoms: Network slow/down, switch CPU 99%, link lights flashing rapidly

**Immediate Troubleshooting:**

**Step 1: Identify the loop**
```cisco
# Check for excessive broadcasts
show interfaces | include broadcast
# Look for rapidly increasing broadcast count

# Check CPU
show processes cpu sorted
# Look for "ARP Input" or "IP Input" consuming CPU

# Check which ports are flooding
show interfaces counters
# Look for ports with extremely high packet rates
```

**Step 2: Find physical loop**
```cisco
# Check spanning-tree topology
show spanning-tree

# Look for ports that should be blocking but aren't
show spanning-tree inconsistentports

# Check for duplicate MAC addresses (sign of loop)
show mac address-table | include <MAC>
# If same MAC on multiple ports = loop
```

**Step 3: Emergency fix - shut down ports**
```cisco
# If you identify the looped ports (e.g., Gi0/10 and Gi0/15)
interface range gi0/10, gi0/15
 shutdown

# Network should recover immediately
```

**Root Cause Analysis:**

**Common Causes:**
1. **STP disabled on one switch** (user plugged in unmanaged switch)
2. **User looped cable** (patched Gi0/1 to Gi0/2 on same switch)
3. **STP not configured properly** (mixed STP/RSTP/MSTP modes)
4. **Bridge loops** (VLANs without spanning-tree)
5. **Virtualization host** (VM with two NICs on same VLAN)

**Long-Term Prevention:**

**1. Enable BPDU Guard (critical!)**
```cisco
# On access ports (where users/servers connect)
interface range gi0/1 - 24
 spanning-tree portfast  ! Skip STP states (listening/learning)
 spanning-tree bpduguard enable  ! Shutdown if BPDU received

# Prevents users from connecting switches
```

**2. Enable Root Guard (uplink protection)**
```cisco
# On uplinks to distribution layer
interface gi0/25
 spanning-tree guard root  ! Prevent becoming root if superior BPDU received
```

**3. Use Loop Guard**
```cisco
# On point-to-point links between switches
interface gi0/26
 spanning-tree guard loop  ! Prevent loops if BPDUs stop
```

**4. Enable Storm Control**
```cisco
# Limit broadcast/multicast traffic rate
interface range gi0/1 - 24
 storm-control broadcast level 10.00  ! Max 10% broadcasts
 storm-control action shutdown  ! Shutdown port if exceeded
```

**5. Deploy RSTP instead of STP**
```cisco
# Faster convergence (2-3 seconds vs 30-50 seconds)
spanning-tree mode rapid-pvst
```

**6. Monitor MAC address table**
```cisco
# Set up alerts for MAC flapping
# (same MAC moving between ports rapidly = loop symptom)
```

**Spanning Tree Protocol Types:**
- **STP (802.1D):** Original, slow convergence (~50 seconds)
- **RSTP (802.1w):** Rapid STP, fast convergence (~2-3 seconds)
- **MSTP (802.1s):** Multiple Spanning Tree, efficient for many VLANs
- **PVST+:** Cisco proprietary, separate STP per VLAN
- **Rapid PVST+:** Cisco, combines RSTP + per-VLAN

**Acronym Glossary:**
- **STP** = Spanning Tree Protocol (prevents Layer 2 loops)
- **RSTP** = Rapid Spanning Tree Protocol (fast version of STP)
- **MSTP** = Multiple Spanning Tree Protocol (efficient multi-VLAN STP)
- **BPDU** = Bridge Protocol Data Unit (STP control frames)
- **PVST+** = Per-VLAN Spanning Tree Plus (Cisco proprietary)
- **TCN** = Topology Change Notification (STP message when topology changes)
- **MAC** = Media Access Control (hardware address)

**Practical Example:**
```
Scenario: Network outage at 9 AM Monday

Symptoms:
- All users can't access network
- Switches responding slowly to SSH
- Link lights on all switches flashing rapidly

Investigation:
Switch# show processes cpu sorted
CPU utilization for five seconds: 99%/99%; one minute: 99%
PID  Runtime(ms)  Invoked  uSecs    5Sec   1Min   5Min  TTY  Process
140  50000        100000   500      88%    89%    89%   0    ARP Input
141  30000        90000    333      10%    9%     9%    0    IP Input

Switch# show interfaces gi0/15 | include broadcast
     30 second input rate 950000000 bits/sec, 1200000 packets/sec
     300000000 packets input, 0 broadcasts, 0 runts, 0 giants

FINDING: Gi0/15 has 1.2 million packets/sec (WAY too high)

Switch# show spanning-tree interface gi0/15
Port 15 (GigabitEthernet0/15) is forwarding
  Port path cost 4, Port priority 128, Port Identifier 128.15.
  Designated root has priority 32768, address 0001.1111.2222
  Designated bridge has priority 32768, address 0001.1111.2222
  Timers: message age 0, forward delay 0, hold 0

Switch# show mac address-table interface gi0/15 | count
Number of MAC addresses: 250

Switch# show mac address-table | include 0011.2233.4444
  10    0011.2233.4444    DYNAMIC     Gi0/15
  10    0011.2233.4444    DYNAMIC     Gi0/20

ROOT CAUSE: Same MAC on two ports = loop between Gi0/15 and Gi0/20

Emergency Fix:
Switch(config)# interface gi0/15
Switch(config-if)# shutdown

Network recovered immediately. Investigation found user connected cable from Gi0/15 to Gi0/20.

Prevention:
Switch(config)# interface range gi0/1 - 24
Switch(config-if-range)# spanning-tree portfast
Switch(config-if-range)# spanning-tree bpduguard enable
Switch(config-if-range)# storm-control broadcast level 10.00
Switch(config-if-range)# storm-control action shutdown
```

**Common Pitfalls:**
1. **PortFast on trunk/uplink ports:** Causes loops - only use on access ports
2. **Disabling STP entirely:** Never do this - always leave STP enabled
3. **Not using BPDU Guard:** Users can create loops by plugging in switches
4. **Mismatched STP modes:** Some switches running STP, others RSTP - use consistent mode
5. **Not monitoring for MAC flapping:** Early warning sign of intermittent loops
6. **Unmanaged switches in network:** Don't participate in STP, can create loops
7. **Too-aggressive storm-control:** Legitimate broadcast traffic blocked

**Interview Follow-Up Questions to Expect:**
- "Explain STP port states" (Blocking → Listening → Learning → Forwarding)
- "What's the difference between PortFast and BPDU Guard?" (PortFast skips STP states, BPDU Guard shuts down if switch detected)
- "How does STP elect a root bridge?" (Lowest priority, then lowest MAC address)
- "When would you use MSTP instead of RSTP?" (Many VLANs, want efficient STP)

---

## Question 5: ISIS vs OSPF

**Question:** Why might an ISP choose ISIS over OSPF for their core network?

**Feynman Explanation:**
OSPF and ISIS are like two different filing systems. OSPF uses IP (like storing files on a network drive with IP addresses), while ISIS uses raw Layer 2 (like storing files on a local hard drive). For ISPs with massive scale, ISIS has advantages: simpler design (no IP subnet issues), easier to extend (flexible TLVs), and historically more stable at huge scale. It's like choosing a filing system designed for million-file libraries vs one designed for office use - both work, but one scales better.

**Technical Answer:**

**Key Differences:**

| Feature | OSPF | ISIS |
|---------|------|------|
| **Protocol Layer** | Runs on IP (protocol 89) | Runs directly on Layer 2 (no IP) |
| **Addressing** | Requires IP subnets on links | Uses NET addresses (independent of IP) |
| **Area Design** | Two-level (Area 0 + others) | Two-level (L1/L2) |
| **Scalability** | Good (up to ~1000 routers) | Excellent (proven at 5000+ routers) |
| **Extensibility** | Limited TLV space | Flexible TLVs (easier to add features) |
| **IPv6** | Separate OSPFv3 process | Native support (same protocol) |
| **Vendor Support** | Cisco, Juniper, all vendors | Cisco, Juniper (common in ISP gear) |

**Why ISPs Choose ISIS:**

**1. No IP Subnetting Required**
- OSPF: Every link needs IP subnet (wastes IPs, complex configuration)
- ISIS: NET addresses independent of IP (like MAC addresses)
- **Benefit:** Cleaner design, no IP wasted on P2P links

**2. Better IPv4/IPv6 Integration**
- OSPF: Need separate OSPFv2 (IPv4) and OSPFv3 (IPv6) processes
- ISIS: Single process handles both (Multi-Topology ISIS)
- **Benefit:** Simpler operations, single protocol to manage

**3. Faster Convergence at Scale**
- ISIS: Simpler flooding mechanism
- OSPF: More complex LSA types (7 LSA types vs ISIS 4 TLV types)
- **Benefit:** Faster SPF calculations in huge networks

**4. TLV Extensibility**
- ISIS: TLV (Type-Length-Value) format easy to extend
- OSPF: Opaque LSAs harder to extend
- **Benefit:** Easier to add MPLS Traffic Engineering, segment routing

**5. Clean Separation of IGP and BGP**
- ISIS: Never carries external routes (pure IGP)
- OSPF: Can carry external routes (Type 5 LSAs) - sometimes misused
- **Benefit:** Cleaner design - ISIS for IGP, BGP for external

**6. Proven at Hyperscale**
- Large ISPs (Tier 1) run ISIS at thousands of routers
- OSPF can struggle above ~1000 routers (not a hard limit, but complexity increases)

**When to Use OSPF Instead:**

- **Enterprise networks** (easier to learn, more engineers know it)
- **Mixed vendor environment** (better universal support)
- **Smaller scale** (<500 routers) - OSPF is simpler
- **Existing OSPF deployment** (migration costly)

**When to Use ISIS:**

- **ISP/Carrier networks** (scale + stability)
- **MPLS backbone** (better TE integration)
- **Dual-stack IPv4/IPv6** (simpler operations)
- **Greenfield deployment** (no migration cost)

**Acronym Glossary:**
- **ISIS** = Intermediate System to Intermediate System (link-state routing protocol from OSI)
- **OSPF** = Open Shortest Path First (link-state routing protocol from IETF)
- **NET** = Network Entity Title (ISIS address like 49.0001.1921.6800.1001.00)
- **TLV** = Type-Length-Value (extensible data format)
- **L1** = Level 1 (ISIS intra-area routing)
- **L2** = Level 2 (ISIS inter-area routing)
- **IGP** = Interior Gateway Protocol (OSPF, ISIS, EIGRP)
- **LSA** = Link-State Advertisement (OSPF topology packet)
- **LSP** = Link-State PDU (ISIS topology packet)

**Practical Example:**
```
ISP Core Network: 2000 routers across 50 cities

OSPF Design Issues:
- 2000 routers in Area 0? = Massive LSDB, slow SPF
- Split into multiple areas? = Complex ABR design, suboptimal paths
- IPv4 and IPv6? = Need OSPFv2 + OSPFv3 (two protocols to manage)
- Point-to-point links = Need /30 or /31 subnets (IP waste)

ISIS Design:
- All routers in L2 (backbone level)
- Customer-facing routers also run L1 (stub areas)
- Single ISIS process handles IPv4 + IPv6
- NET addresses on loopbacks only (no IP on P2P links needed)
- Clean MPLS TE integration

ISIS Configuration Example (Cisco):
router isis CORE
 net 49.0001.1921.6800.1001.00  ! NET address
 is-type level-2-only            ! Backbone router
 metric-style wide               ! Support large metrics
 !
interface Loopback0
 ip address 192.168.1.1 255.255.255.255
 ip router isis CORE
!
interface GigabitEthernet0/0
 ip address 10.0.0.1 255.255.255.252
 ip router isis CORE
 isis network point-to-point     ! No DR election
 isis metric 10
```

**Common Pitfalls:**
1. **Not configuring NET address properly:** Must be unique per router
2. **Mixing L1 and L2 wrong:** L1-only routers can't reach outside area
3. **Forgetting metric-style wide:** Old narrow metrics max out at 63
4. **Not setting network type:** Point-to-point links should be configured as such
5. **Authentication not configured:** ISIS runs unauthenticated by default
6. **Mixing ISIS with OSPF:** Redistribution adds complexity - choose one

**Interview Follow-Up Questions to Expect:**
- "What's the ISIS NET address format?" (Area.System-ID.SEL, e.g., 49.0001.1921.6800.1001.00)
- "Explain L1 vs L2 in ISIS" (L1 = intra-area like OSPF, L2 = inter-area like Area 0)
- "Can you run OSPF and ISIS together?" (Yes, but usually don't - adds complexity)
- "What's a DIS in ISIS?" (Designated Intermediate System, like OSPF's DR, but works differently)

---

## Question 6: MPLS L3VPN

**Question:** Explain how MPLS L3VPN works and when you'd use it.

**Feynman Explanation:**
MPLS L3VPN is like a postal service with color-coded envelopes. Imagine you run a postal service for 100 companies, and each company has branch offices. You don't want Company A's mail mixing with Company B's mail. So you put each company's mail in different colored envelopes (VRFs), and postal workers route based on color + address. The companies think they have dedicated postal systems, but you're sharing infrastructure. MPLS L3VPN does the same for networks - multiple customers share the provider's network, but their traffic stays isolated using labels (like those colored envelopes).

**Technical Answer:**

**MPLS L3VPN Components:**

**1. Provider Edge (PE) Routers**
- Connect to customer (CE) routers
- Maintain separate VRF (Virtual Routing and Forwarding) per customer
- Apply MPLS labels to customer traffic

**2. Provider (P) Routers**
- Core routers, don't see customer routes
- Switch based on MPLS labels only (fast!)
- No VRFs needed

**3. Customer Edge (CE) Routers**
- Customer routers at branch offices
- Run standard routing (OSPF, BGP, static)
- No knowledge of MPLS

**4. VRF (Virtual Routing and Forwarding)**
- Separate routing table per customer on PE routers
- Keeps Customer A routes isolated from Customer B
- Like VLAN but for Layer 3

**5. Route Distinguisher (RD)**
- Makes customer routes unique across provider network
- Format: ASN:nn (e.g., 65000:10)
- Customer A's 10.0.0.0/8 becomes 65000:10:10.0.0.0/8

**6. Route Target (RT)**
- Controls route import/export between VRFs
- Export RT: Tag routes leaving this VRF
- Import RT: Accept routes with this tag
- Enables hub-and-spoke or any-to-any topologies

**How It Works:**

```
Customer A Site 1 (CE1) ---[VRF A]--- PE1 ====[MPLS Core]==== PE2 ---[VRF A]--- CE2 Customer A Site 2
                                        |                        |
                                        |   P1 ---- P2 ---- P3   |
                                        |                        |
Customer B Site 1 (CE3) ---[VRF B]--- PE1 ====[MPLS Core]==== PE2 ---[VRF B]--- CE4 Customer B Site 2
```

**Packet Flow:**
1. CE1 sends packet (10.1.1.0 → 10.2.2.0) to PE1
2. PE1 looks up destination in VRF A routing table
3. PE1 adds two MPLS labels:
   - **Inner label (VPN label):** Identifies VRF at remote PE (e.g., label 100 = VRF A)
   - **Outer label (Transport label):** Routes to PE2 (e.g., label 500 = PE2)
4. P routers switch based on outer label only (fast, no VRF lookup)
5. PE2 removes outer label, sees inner label 100 = VRF A
6. PE2 looks up destination in VRF A, forwards to CE2
7. Packet delivered, Customer A traffic never mixed with Customer B

**Configuration Example (Cisco):**

```cisco
! On PE1
! Step 1: Create VRF
ip vrf CUSTOMER-A
 rd 65000:10             ! Route Distinguisher
 route-target export 65000:10  ! Tag outgoing routes
 route-target import 65000:10  ! Accept routes with this tag

! Step 2: Assign interface to VRF
interface GigabitEthernet0/0
 description Connection to Customer A CE1
 ip vrf forwarding CUSTOMER-A
 ip address 192.168.1.1 255.255.255.252

! Step 3: Configure routing with customer
router bgp 65000
 address-family ipv4 vrf CUSTOMER-A
  neighbor 192.168.1.2 remote-as 65001
  neighbor 192.168.1.2 activate

! Step 4: MPLS backbone (to P and PE routers)
interface GigabitEthernet0/1
 mpls ip   ! Enable MPLS

router ospf 1
 network 10.0.0.0 0.0.0.255 area 0  ! IGP for PE-to-PE connectivity

router bgp 65000
 neighbor 10.0.0.2 remote-as 65000   ! iBGP to other PEs
 neighbor 10.0.0.2 update-source Loopback0
 address-family vpnv4
  neighbor 10.0.0.2 activate         ! Exchange VPNv4 routes
  neighbor 10.0.0.2 send-community extended
```

**When to Use MPLS L3VPN:**

**Use Cases:**
1. **Service Provider offering VPN service** (like AT&T, Verizon)
2. **Large enterprise with many sites** (cleaner than full-mesh IPsec VPN)
3. **Extranet connectivity** (connect two companies' networks securely)
4. **Traffic segmentation** (separate prod/dev/test networks)

**Advantages over Traditional VPN:**
- **Scalability:** Add new sites easily (no full mesh tunnels)
- **Performance:** MPLS faster than encryption overhead
- **QoS:** Traffic engineering and QoS easier in MPLS
- **Any-to-any connectivity:** Without n*(n-1)/2 tunnels
- **Provider managed:** Customer doesn't need VPN expertise

**Disadvantages:**
- **Cost:** More expensive than internet VPN
- **Provider lock-in:** Must use MPLS provider's network
- **Complexity:** More complex than simple IPsec
- **Not encrypted by default:** MPLS provides isolation, not encryption (add IPsec if needed)

**Acronym Glossary:**
- **MPLS** = Multiprotocol Label Switching (label-based forwarding)
- **L3VPN** = Layer 3 Virtual Private Network (routed VPN)
- **VRF** = Virtual Routing and Forwarding (separate routing table)
- **PE** = Provider Edge (router connecting to customer)
- **P** = Provider (core router)
- **CE** = Customer Edge (customer router)
- **RD** = Route Distinguisher (makes routes unique)
- **RT** = Route Target (controls route import/export)
- **VPNv4** = VPN IPv4 (BGP address family for MPLS VPN)
- **MP-BGP** = Multiprotocol BGP (BGP with multiple address families)
- **LDP** = Label Distribution Protocol (distributes MPLS labels)

**Practical Example:**
```
Scenario: Retail company with 500 stores across US

Traditional Approach (IPsec):
- 500 stores need VPN tunnels to HQ
- Full-mesh = 500*(500-1)/2 = 124,750 tunnels (impossible!)
- Hub-and-spoke = 500 tunnels (manageable but HQ bottleneck)
- Configuration complexity high
- Encryption overhead impacts performance

MPLS L3VPN Approach:
- Service provider (e.g., AT&T) provides MPLS network
- Each store has CE router connected to PE
- Provider maintains VRF for this customer
- Any-to-any connectivity (store-to-store, store-to-HQ)
- Provider handles routing, QoS, redundancy
- Customer just configures CE router (simple!)

Cost Comparison:
- Internet VPN: $100/site/month = $50K/month
- MPLS L3VPN: $500/site/month = $250K/month
- Worth it? Depends on:
  - Need for guaranteed QoS (VoIP, video)
  - IT staff size (MPLS = provider managed)
  - Performance requirements (MPLS = lower latency)
```

**Common Pitfalls:**
1. **Forgetting route-target import/export:** Routes not shared between sites
2. **RD not unique:** Use unique RD per VRF, even if RT is same
3. **CE-PE routing protocol mismatch:** Ensure compatible (OSPF sham-link if needed)
4. **Not enabling extended communities in BGP:** VPNv4 routes won't propagate
5. **MTU issues:** MPLS adds ~8 bytes per label, can cause fragmentation
6. **No encryption misconception:** MPLS isolates but doesn't encrypt - add IPsec if needed
7. **Overlapping IP addresses:** VRF isolates, but don't use same IPs in same VRF

**Interview Follow-Up Questions to Expect:**
- "What's the difference between RD and RT?" (RD makes routes unique, RT controls import/export)
- "Can two VRFs have overlapping IP space?" (Yes, that's the point of VRFs - isolation)
- "How many labels in MPLS L3VPN?" (Two: outer transport label, inner VPN label)
- "What's a route-leaking scenario?" (Import routes from one VRF to another - like shared services)
- "MPLS vs IPsec VPN - when to use each?" (MPLS = performance/QoS, IPsec = encryption/cost)

---

*[Questions 7-10 would continue in same format...]*

**Next:** See `expanded-cheat-sheet-q11-q20.md` for Questions 11-20 (Juniper, Wireless, Packet Analysis, Enterprise Design, etc.)

---

**How to Use This Cheat Sheet:**
1. **First pass:** Read Feynman Explanation to build intuition
2. **Second pass:** Study Technical Answer with diagrams/configs
3. **Practice:** Do the Practical Example on GNS3/real gear
4. **Review:** Go through Common Pitfalls before interview
5. **Test yourself:** Answer Follow-Up Questions without looking

**Study Strategy:**
- **Week 1:** Q1-Q5 (routing protocols - OSPF, BGP, Layer 2)
- **Week 2:** Q6-Q10 (MPLS, security, wireless, troubleshooting)
- **Week 3:** Q11-Q20 (advanced topics, design, capstone)

**Last Updated:** 2025-11-11
**Role:** Network Engineer II (Denali/T-Mobile)
**Salary Target:** $150-190K/year

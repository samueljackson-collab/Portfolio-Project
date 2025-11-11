# Network Engineer II - Lab Tracking Sheet

## Purpose
Use this checklist to track your progress through all 12 essential labs. Check off each lab as you complete it and collect evidence for your portfolio.

---

## 3-Week Lab Schedule Overview

| Week | Focus Area | Labs | Total Hours |
|------|------------|------|-------------|
| Week 1 | Routing Foundations | Labs 01-04 | 20 hours |
| Week 2 | Switching & Advanced Routing | Labs 05-07 | 17 hours |
| Week 3 | Security, Wireless, Integration | Labs 08-12 | 24 hours |

**Total Lab Time:** 61 hours across 3 weeks (~3 hours/day)

---

## Week 1: Routing Foundations

### ☐ Lab 01: GNS3/EVE-NG Setup
**Time:** 4 hours
**Priority:** 🔴 CRITICAL (Foundation for all other labs)
**Difficulty:** Easy

**Objectives:**
- [ ] Install GNS3 or EVE-NG on your machine
- [ ] Download Cisco IOS images (IOSv or vIOS)
- [ ] Create simple 3-router topology
- [ ] Verify connectivity between routers (ping test)

**Prerequisites:**
- Computer with 8GB+ RAM, 50GB+ disk space
- Virtualization enabled in BIOS
- VirtualBox or VMware Workstation

**Evidence to Collect:**
- [ ] GNS3 screenshot showing workspace
- [ ] Topology diagram (3 routers connected)
- [ ] Console output showing successful ping between routers
- [ ] Screenshot of `show version` on router

**Troubleshooting Tips:**
- IOS images: Look for "IOSv" or "vIOS" (virtualized IOS)
- Can't get IOS images? Use Packet Tracer as alternative (limited features but free)
- Connection issues? Check adapter settings in GNS3 preferences

**Validation:**
```bash
# Test on each router
Router# ping <neighbor-ip>
Router# show ip interface brief
Router# show version
```

---

### ☐ Lab 02: OSPF Single Area
**Time:** 5 hours
**Priority:** 🔴 CRITICAL (OSPF is core topic)
**Difficulty:** Medium

**Objectives:**
- [ ] Create 4-router topology in single OSPF area
- [ ] Configure OSPF Area 0 on all routers
- [ ] Verify neighbor relationships formed
- [ ] Analyze LSDB and routing table
- [ ] Test failover by shutting down link

**Prerequisites:**
- Lab 01 completed (GNS3 working)
- Basic understanding of OSPF concepts

**Configuration Template:**
```cisco
router ospf 1
 router-id 1.1.1.1
 network 10.0.0.0 0.0.0.255 area 0
```

**Evidence to Collect:**
- [ ] Topology diagram (4 routers, Area 0)
- [ ] Running configs from all routers
- [ ] Output: `show ip ospf neighbor` (all neighbors in FULL state)
- [ ] Output: `show ip ospf database`
- [ ] Output: `show ip route ospf`
- [ ] Screenshot showing failover (before/after link shutdown)

**Validation:**
```cisco
# All routers should show:
Router# show ip ospf neighbor
# State should be FULL/DR or FULL/BDR or FULL/DROTHER

Router# show ip route ospf
# Should see routes learned via OSPF (O)

Router# show ip ospf interface brief
# All OSPF-enabled interfaces listed
```

**Common Pitfalls:**
- Neighbors stuck in INIT: Check ACLs, firewall
- Neighbors stuck in EXSTART: MTU mismatch
- No neighbors at all: Check network statement, verify interfaces up

---

### ☐ Lab 03: OSPF Multi-Area
**Time:** 6 hours
**Priority:** 🔴 CRITICAL (Interview focus)
**Difficulty:** Hard

**Objectives:**
- [ ] Expand to 3 OSPF areas (Area 0 + 2 regular areas)
- [ ] Configure ABRs (Area Border Routers)
- [ ] Implement route summarization at ABRs
- [ ] Verify inter-area routing works
- [ ] Compare route types (O vs O IA)

**Prerequisites:**
- Lab 02 completed
- Understanding of OSPF areas and LSA types

**Topology:**
```
Area 1 --- ABR1 --- Area 0 (Backbone) --- ABR2 --- Area 2
```

**Evidence to Collect:**
- [ ] Multi-area topology diagram with area labels
- [ ] All router configs (especially ABRs)
- [ ] `show ip route` showing O (intra-area) and O IA (inter-area) routes
- [ ] `show ip ospf database` on ABR (should see Type 1, 2, 3 LSAs)
- [ ] Verification of route summarization working

**Validation:**
```cisco
# On ABR:
Router# show ip ospf border-routers
# Should list ABRs

Router# show ip ospf database summary
# Type 3 LSAs (inter-area routes)

# On non-ABR router in Area 1:
Router# show ip route
# Should see "O IA" routes to Area 2 networks
```

**Common Pitfalls:**
- All areas must connect to Area 0 (or use virtual links)
- Summarization at wrong place (must be on ABR)
- Forgetting to enable OSPF on ABR's Area 0 interfaces

---

### ☐ Lab 04: BGP Basics
**Time:** 5 hours
**Priority:** 🔴 CRITICAL
**Difficulty:** Medium

**Objectives:**
- [ ] Create 3 routers in 3 different AS domains
- [ ] Configure eBGP peering between AS
- [ ] Verify BGP table and best path selection
- [ ] Test path manipulation with AS-PATH prepending

**Prerequisites:**
- Lab 01-03 completed
- Understanding of BGP concepts (AS, eBGP, iBGP)
- **Note:** Leverage Kuiper prep materials for BGP review!

**Topology:**
```
AS 65001 (R1) <--eBGP--> AS 65002 (R2) <--eBGP--> AS 65003 (R3)
```

**Configuration Template:**
```cisco
router bgp 65001
 neighbor 10.0.0.2 remote-as 65002
 network 192.168.1.0 mask 255.255.255.0
```

**Evidence to Collect:**
- [ ] Topology diagram with AS numbers labeled
- [ ] BGP configs from all routers
- [ ] `show ip bgp` output (BGP table with best path marked >)
- [ ] `show ip bgp summary` (neighbor status)
- [ ] AS-PATH prepending config and verification

**Validation:**
```cisco
Router# show ip bgp summary
# Neighbors should be in "Established" state

Router# show ip bgp
# Look for > marker (best path)
# Check AS-PATH attribute

Router# show ip route bgp
# BGP routes installed in routing table
```

**Common Pitfalls:**
- Neighbors stuck in Active: Check connectivity, ACLs
- Routes not advertised: Use `network` statement or `redistribute`
- Next-hop not reachable: May need static route or IGP

---

## Week 2: Switching & Advanced Routing

### ☐ Lab 05: Layer 2 Switching
**Time:** 5 hours
**Priority:** 🔴 CRITICAL
**Difficulty:** Medium

**Objectives:**
- [ ] Create 4-switch topology
- [ ] Configure VLANs (10, 20, 30)
- [ ] Set up 802.1q trunks between switches
- [ ] Configure MSTP (Multiple Spanning Tree)
- [ ] Verify root bridge election and port roles

**Prerequisites:**
- Understanding of VLANs, trunking, STP

**Evidence to Collect:**
- [ ] Switch configs (VLANs, trunks, MSTP)
- [ ] `show vlan brief` output
- [ ] `show interfaces trunk` output
- [ ] `show spanning-tree` output showing root bridge and port states

**Validation:**
```cisco
Switch# show vlan brief
# VLANs 10, 20, 30 should exist

Switch# show interfaces trunk
# Should see allowed VLANs on trunk ports

Switch# show spanning-tree
# Identify root bridge, port roles (Root, Designated, Alternate)
```

---

### ☐ Lab 06: ISIS Routing
**Time:** 5 hours
**Priority:** 🟡 HIGH
**Difficulty:** Medium-Hard

**Objectives:**
- [ ] Create 4-router ISIS topology
- [ ] Configure ISIS Level 1 and Level 2
- [ ] Set NET addresses correctly
- [ ] Verify ISIS adjacencies and database
- [ ] Compare ISIS vs OSPF (document differences)

**Prerequisites:**
- OSPF knowledge (for comparison)
- Understanding of NET address format

**Evidence to Collect:**
- [ ] ISIS configs with NET addresses
- [ ] `show isis neighbors` output
- [ ] `show isis database` output
- [ ] Comparison notes (ISIS vs OSPF)

**Validation:**
```cisco
Router# show isis neighbors
# Neighbors should be UP

Router# show clns interface
# Verify ISIS enabled on interfaces
```

---

### ☐ Lab 07: MPLS L3VPN
**Time:** 7 hours
**Priority:** 🟡 HIGH
**Difficulty:** Hard

**Objectives:**
- [ ] Create 6-router topology (2 PE, 2 P, 2 CE)
- [ ] Configure MPLS and LDP on provider routers
- [ ] Set up VRFs on PE routers
- [ ] Configure RD and RT for customer isolation
- [ ] Test L3VPN connectivity between customer sites

**Prerequisites:**
- Strong understanding of MPLS concepts
- BGP knowledge (MP-BGP used for L3VPN)

**Evidence to Collect:**
- [ ] Complete topology diagram with MPLS domain
- [ ] All router configs (PE, P, CE)
- [ ] `show mpls ldp neighbor` output
- [ ] `show ip vrf` output on PE routers
- [ ] Ping test between CE routers (across MPLS VPN)

**Validation:**
```cisco
# On PE router:
PE# show mpls ldp neighbor
# LDP neighbors should be operational

PE# show ip vrf
# VRFs should be configured

PE# show ip bgp vpnv4 all
# VPNv4 routes exchanged

# On CE router:
CE# ping <remote-CE-ip>
# Should succeed (traffic traversing MPLS VPN)
```

---

## Week 3: Security, Wireless, Integration

### ☐ Lab 08: Firewall Configuration
**Time:** 5 hours
**Priority:** 🟡 HIGH
**Difficulty:** Medium

**Objectives:**
- [ ] Install pfSense or use Cisco ASA in GNS3
- [ ] Create security zones (inside, DMZ, outside)
- [ ] Configure firewall rules for each zone
- [ ] Set up site-to-site VPN
- [ ] Test connectivity and verify firewall blocks unwanted traffic

**Prerequisites:**
- Basic understanding of firewall concepts
- VPN concepts (IPsec)

**Evidence to Collect:**
- [ ] Firewall rule configuration
- [ ] Zone diagram
- [ ] VPN configuration
- [ ] Test results (allowed vs blocked traffic)

---

### ☐ Lab 09: Wireless Controller
**Time:** 4 hours
**Priority:** 🟡 MEDIUM
**Difficulty:** Medium

**Objectives:**
- [ ] Set up Cisco WLC emulator (or Aruba if available)
- [ ] Configure wireless APs
- [ ] Create SSIDs mapped to VLANs
- [ ] Test client connectivity and roaming

**Prerequisites:**
- VLAN knowledge
- Wireless concepts (SSIDs, WPA2, controller architecture)

**Evidence to Collect:**
- [ ] WLC configuration screenshots
- [ ] SSID setup (with VLAN mapping)
- [ ] Client connection test results

---

### ☐ Lab 10: Wireshark Deep Dive
**Time:** 4 hours
**Priority:** 🟡 MEDIUM
**Difficulty:** Easy-Medium

**Objectives:**
- [ ] Capture traffic on your homelab/network
- [ ] Analyze TCP 3-way handshake
- [ ] Analyze DNS queries and responses
- [ ] Identify latency issues and retransmissions
- [ ] Practice using capture filters

**Prerequisites:**
- Wireshark installed
- Basic understanding of TCP/IP

**Evidence to Collect:**
- [ ] Packet capture file (.pcap)
- [ ] Annotated screenshots (highlighting TCP handshake, DNS, issues)
- [ ] Analysis notes (what you found, how you diagnosed)

**Useful Filters:**
```
tcp.port == 80
dns
tcp.analysis.retransmission
http.request
```

---

### ☐ Lab 11: Juniper Configuration
**Time:** 5 hours
**Priority:** 🟢 LOW-MEDIUM (Preferred but not required)
**Difficulty:** Medium

**Objectives:**
- [ ] Set up Juniper vMX in GNS3 (or vSRX)
- [ ] Configure OSPF on Juniper
- [ ] Configure BGP on Juniper
- [ ] Compare Juniper CLI with Cisco CLI (document differences)
- [ ] Practice commit and rollback commands

**Prerequisites:**
- OSPF and BGP knowledge from previous labs
- Willingness to learn new CLI syntax

**Evidence to Collect:**
- [ ] Juniper configs (OSPF, BGP)
- [ ] CLI comparison notes (Cisco vs Juniper)
- [ ] Screenshot of `commit` and `rollback` operations

**Key Juniper CLI Differences:**
```juniper
# Cisco:
Router(config)# interface gi0/0
Router(config-if)# ip address 10.0.0.1 255.255.255.0

# Juniper:
user@router> configure
[edit]
user@router# set interfaces ge-0/0/0 unit 0 family inet address 10.0.0.1/24
user@router# commit
```

---

### ☐ Lab 12: Enterprise Network Design (Capstone)
**Time:** 6 hours
**Priority:** 🔴 CRITICAL (Portfolio showcase)
**Difficulty:** Hard

**Objectives:**
- [ ] Design complete enterprise network (HQ + 3 branches)
- [ ] Core: OSPF backbone with BGP connection to ISP
- [ ] Distribution: VLANs and MSTP
- [ ] Access: Edge security and wireless
- [ ] Document entire design with diagrams, IP addressing plan, and all configs

**Prerequisites:**
- All previous labs completed
- Strong understanding of network design principles

**Evidence to Collect:**
- [ ] Full network design document (PDF)
- [ ] Detailed topology diagram (Visio, draw.io, or hand-drawn)
- [ ] IP addressing plan (spreadsheet)
- [ ] All router and switch configurations
- [ ] Test results (connectivity matrix)

**Design Checklist:**
- [ ] IP addressing scheme documented
- [ ] Routing protocols chosen and justified
- [ ] Redundancy implemented (multiple paths, HSRP/VRRP)
- [ ] Security policies defined (ACLs, firewall rules)
- [ ] Wireless coverage planned
- [ ] Scalability considered (room for growth)

---

## Progress Tracking

**Week 1 Progress:** ☐☐☐☐ (0/4 labs completed)
**Week 2 Progress:** ☐☐☐ (0/3 labs completed)
**Week 3 Progress:** ☐☐☐☐☐ (0/5 labs completed)

**Overall Progress:** 0/12 labs (0%)

---

## Lab Completion Checklist

Before marking any lab as "complete," ensure you have:
- [ ] Completed all objectives listed
- [ ] Collected all required evidence (screenshots, configs, outputs)
- [ ] Documented issues encountered and how you solved them
- [ ] Organized evidence in portfolio folder
- [ ] Reviewed relevant cheat sheet section
- [ ] Can explain the lab to someone else (Feynman test)

---

## Portfolio Organization

**Recommended Folder Structure:**
```
network-engineer-ii-labs/
├── lab-01-gns3-setup/
│   ├── screenshots/
│   ├── topology.png
│   └── notes.md
├── lab-02-ospf-single-area/
│   ├── configs/
│   │   ├── R1-config.txt
│   │   ├── R2-config.txt
│   │   ├── R3-config.txt
│   │   └── R4-config.txt
│   ├── show-commands/
│   │   ├── ospf-neighbors.txt
│   │   ├── ospf-database.txt
│   │   └── routes.txt
│   ├── topology.png
│   └── notes.md
...
└── lab-12-enterprise-design/
    ├── design-doc.pdf
    ├── topology-detailed.png
    ├── ip-plan.xlsx
    ├── configs/
    └── test-results/
```

---

## Tips for Success

**Time Management:**
- Don't rush - understanding is more important than speed
- If stuck for >30 minutes, move on and come back later
- Budget 10-15% extra time for troubleshooting

**Documentation:**
- Take screenshots DURING labs (not after)
- Document failures too - shows troubleshooting skills
- Use comments in configs to explain what you did

**Learning:**
- Review relevant cheat sheet sections before starting lab
- Cross-reference with Kuiper prep for BGP/VPN (Labs 4, 8)
- Do NOT copy-paste configs blindly - type and understand

**Interview Prep:**
- After completing lab, practice explaining it verbally
- Prepare 2-minute summary of each major lab for interviews
- Be ready to screen-share and walk through topology

---

## Red Flags to Address

If you can't answer these after completing labs, review:

**After Lab 02 (OSPF):**
- ☐ Can you explain DR/BDR election process?
- ☐ Can you identify OSPF neighbor states and what they mean?
- ☐ Do you know what LSA Type 1, 2, and 3 are?

**After Lab 04 (BGP):**
- ☐ Can you explain BGP path selection algorithm (first 5 steps)?
- ☐ Do you understand AS-PATH prepending and when to use it?
- ☐ Can you differentiate eBGP from iBGP?

**After Lab 07 (MPLS):**
- ☐ Can you explain how MPLS L3VPN provides customer isolation?
- ☐ Do you understand RD vs RT?
- ☐ Can you describe packet flow through MPLS network?

---

## Additional Resources

**GNS3 Basics:**
- Official GNS3 docs: https://docs.gns3.com/
- David Bombal YouTube channel (GNS3 tutorials)

**Cisco IOS Reference:**
- Cisco IOS Command Reference: https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-15-4m-t/products-command-reference-list.html

**Community Help:**
- Reddit: r/ccna, r/ccnp, r/networking
- NetworkEngineering.StackExchange.com

---

**Last Updated:** 2025-11-11
**For Role:** Network Engineer II (Denali/T-Mobile)
**Salary Target:** $150-190K/year

**Remember:** Quality over quantity. One well-understood lab is worth more than 10 rushed labs!

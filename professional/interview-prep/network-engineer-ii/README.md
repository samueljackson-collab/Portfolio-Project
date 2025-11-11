# Network Engineer II
## Denali / T-Mobile Interview Prep (Quick Start Package)

**Company:** Denali Advanced Integration (supporting T-Mobile/Microsoft)
**Compensation:** $150K-190K/year (Salary with full benefits)
**Location:** Redmond, WA (**On-site required**)
**Experience Required:** 5-10 years network engineering

---

## 🎯 Role Overview

Enterprise network engineer responsible for architecture, support, and operations of **5,000+ network devices**. Lead complex projects, mentor junior engineers, provide expert design and troubleshooting. Heavy focus on **Cisco, Juniper, and Foundry equipment** with routing protocols (OSPF, ISIS, BGP, MPLS).

**Key Differentiator:** This is a **senior/lead role**—you need deep protocol knowledge + leadership + project management skills.

---

## 🔥 Top 10 Topics to Master (Priority Order)

### 1. **OSPF (Open Shortest Path First)** (🔴 CRITICAL)
**What:** Link-state routing, areas, LSAs, DR/BDR, cost calculation, network types
**Why:** "Advanced-level knowledge... protocols such as OSPF"
**Study:** Area design, summarization, stub areas, virtual links, authentication
**Lab:** GNS3 topology with OSPF areas, verify routes, troubleshoot neighbor issues

### 2. **BGP (Border Gateway Protocol)** (🔴 CRITICAL)
**What:** AS numbers, eBGP/iBGP, path selection, attributes (AS-PATH, local-pref, MED), communities
**Why:** "Protocols such as... BGP, MPLS" + "Foundry and Juniper Certifications"
**Study:** BGP neighbors, route filtering, traffic engineering, route reflectors
**Lab:** GNS3 with 3 AS domains, configure eBGP peering, traffic engineering with communities
**Leverage:** You already studied this for Kuiper prep! Review kuiper/cheat-sheets Q9-Q10

### 3. **Cisco IOS Configuration & Troubleshooting** (🔴 CRITICAL)
**What:** CLI navigation, show commands, debug, config hierarchy, VLANs, trunking, routing
**Why:** "5 years... with Cisco... equipment"
**Study:** ios configuration mode, running-config vs startup-config, common show/debug commands
**Lab:** Configure Cisco router/switch in GNS3 or Packet Tracer, VLANs + inter-VLAN routing

### 4. **Layer 2 Switching Advanced** (🔴 CRITICAL)
**What:** MSTP (Multiple Spanning Tree), 802.1q (VLAN tagging), 802.1AX (Link Aggregation/LACP), TRILL
**Why:** "Protocols such as MSTP, 802.1q, 802.1AX, TRILL"
**Study:** STP/RSTP/MSTP regions, VLAN pruning, EtherChannel, link aggregation best practices
**Lab:** Configure MSTP with 3 switches, VLANs, verify topology, test failover

### 5. **ISIS (Intermediate System to Intermediate System)** (🟡 HIGH)
**What:** Link-state routing (alternative to OSPF), Level 1/Level 2, NET addresses, wide metrics
**Why:** "Protocols such as... ISIS"
**Study:** ISIS vs OSPF comparison, when ISPs prefer ISIS, configuration basics
**Lab:** GNS3 with ISIS routing, Level 1 and Level 2 areas, verify adjacencies

### 6. **MPLS (Multiprotocol Label Switching)** (🟡 HIGH)
**What:** Label switching, LDP (Label Distribution Protocol), L3VPN, VRFs, RD/RT
**Why:** "Protocols such as... MPLS, LDP"
**Study:** MPLS basics, how labels are distributed, L3VPN architecture, traffic engineering
**Lab:** GNS3 with MPLS backbone, configure PE-CE routing, VRFs, test L3VPN

### 7. **Network Security** (🟡 HIGH)
**What:** Firewalls (Palo Alto, Cisco ASA, Fortinet), IDS/IPS, VPN (site-to-site, remote-access), access control
**Why:** "Advanced understanding of security engineering... firewall rule set construction"
**Study:** Firewall rule design, zone-based policies, NAT, VPN types (IPsec, SSL), IDS signatures
**Lab:** Configure pfSense or Cisco ASA firewall, site-to-site VPN, access rules
**Leverage:** You studied VPN+BGP for Kuiper prep—extend to security context here

### 8. **Wireless Enterprise** (🟡 MEDIUM)
**What:** 802.11 standards (a/b/g/n/ac/ax), controller-based vs autonomous, CAPWAP, roaming, channels
**Why:** "Advanced knowledge and expertise in... wireless communications"
**Study:** Wireless controller architecture (Cisco WLC, Aruba), SSIDs, VLANs, RF site surveys
**Lab:** Set up wireless controller (emulated or physical), configure APs, test client connectivity

### 9. **Packet Analysis & Troubleshooting** (🟡 MEDIUM)
**What:** Wireshark/Netmon, capture filters, protocol analysis, TCP 3-way handshake, retransmissions
**Why:** "Packets captures... network node scanning"
**Study:** Wireshark basics, common filters, identifying issues (packet loss, latency, routing loops)
**Lab:** Capture traffic on your homelab, analyze TCP connections, DNS queries, identify anomalies

### 10. **Juniper (JUNOS) Configuration** (🟢 LOW-MEDIUM - Preferred)
**What:** JUNOS CLI, configuration hierarchy, commit/rollback, routing instances
**Why:** "At least three years of experience with Cisco, Juniper, and Foundry equipment"
**Study:** Juniper vs Cisco CLI differences, configuration mode, show commands
**Lab:** GNS3 with Juniper vMX, configure OSPF/BGP, compare with Cisco approach

---

## 📚 Quick Reference Cheat Sheet

| Topic | Key Concepts | Interview Question Example |
|-------|-------------|---------------------------|
| **OSPF** | Areas, LSAs, DR/BDR, cost, neighbor states, route types (O, O IA, O E1/E2) | "Design OSPF for a multi-site enterprise with 50 locations. How many areas?" |
| **BGP** | AS-PATH, local-pref, MED, communities, eBGP vs iBGP, route reflectors | "Traffic is taking a suboptimal path. How do you use BGP to influence routing?" |
| **Cisco IOS** | Config modes, show run, show ip route, debug, VLANs, trunks, ACLs | "Walk me through troubleshooting a switch port that's not passing traffic." |
| **Layer 2** | STP/RSTP/MSTP, VLANs, trunking, EtherChannel/LACP, MAC tables | "A broadcast storm is taking down your network. How do you troubleshoot?" |
| **ISIS** | Level 1/Level 2, NET addresses, LSPs, wide metrics | "Why might an ISP choose ISIS over OSPF?" |
| **MPLS** | Labels, LDP, PE/CE routers, VRFs, RD/RT, L3VPN | "Explain how MPLS L3VPN works and when you'd use it." |
| **Security** | Firewall zones, ACLs, NAT, VPN (IPsec, SSL), IDS/IPS | "Design firewall rules for a DMZ hosting public web servers." |
| **Wireless** | 802.11ac/ax, channels, WPA2/WPA3, controller architecture, roaming | "Users complain about wireless drops when moving between floors. How do you troubleshoot?" |
| **Packet Analysis** | Wireshark, TCP, DNS, ARP, capture filters, latency, retransmissions | "A user says 'the network is slow.' Use Wireshark to diagnose the issue." |
| **Juniper** | JUNOS CLI, commit, rollback, routing instances, configuration hierarchy | "Compare Juniper and Cisco CLI. What are key differences?" |

---

## 🧪 12 Essential Labs (3-Week Plan)

**Note:** Network Engineer II requires broader/deeper knowledge—budget 3 weeks instead of 2.

### Week 1: Routing Foundations

**Lab 01: GNS3/EVE-NG Setup (4 hours)**
- Install GNS3 or EVE-NG
- Download Cisco IOS images (IOSv or vIOS)
- Create simple topology (3 routers)
- Verify connectivity
**Evidence:** GNS3 screenshot, topology diagram

**Lab 02: OSPF Single Area (5 hours)**
- 4 routers, single area OSPF
- Configure OSPF, verify neighbors
- Analyze LSDB, routing table
- Test failover (shut down link)
**Evidence:** Configs, show commands, OSPF topology

**Lab 03: OSPF Multi-Area (6 hours)**
- Expand to 3 areas (backbone + 2 regular areas)
- Configure ABRs, verify inter-area routing
- Implement route summarization
- Compare routes (O vs O IA)
**Evidence:** Multi-area diagram, configs, routing tables

**Lab 04: BGP Basics (5 hours)**
- 3 routers in 3 AS domains
- Configure eBGP peering
- Verify BGP table, best path selection
- Test path manipulation (AS-PATH prepend)
**Evidence:** BGP configs, show ip bgp output
**Note:** You did this for Kuiper—extend with more complex scenarios here

### Week 2: Switching & Advanced Routing

**Lab 05: Layer 2 Switching (5 hours)**
- 4 switches, create VLANs (10, 20, 30)
- Configure trunks (802.1q)
- Set up MSTP
- Verify root bridge, port roles
**Evidence:** Switch configs, show spanning-tree, VLAN verification

**Lab 06: ISIS Routing (5 hours)**
- 4 routers, ISIS Level 1 and Level 2
- Configure NET addresses
- Verify adjacencies, ISIS database
- Compare with OSPF (when to use each)
**Evidence:** ISIS configs, show isis neighbors, topology notes

**Lab 07: MPLS L3VPN (7 hours)**
- 6 routers (2 PE, 2 P, 2 CE)
- Configure MPLS, LDP
- Set up VRFs, RD/RT
- Test L3VPN connectivity
**Evidence:** MPLS configs, show mpls ldp neighbor, VRF routing tables

### Week 3: Security, Wireless, Integration

**Lab 08: Firewall Configuration (5 hours)**
- Install pfSense or use Cisco ASA (GNS3)
- Create zones (inside, DMZ, outside)
- Configure firewall rules
- Set up site-to-site VPN
**Evidence:** Firewall rules, VPN config, test connectivity

**Lab 09: Wireless Controller (4 hours)**
- Set up Cisco WLC emulator or Aruba (if available)
- Configure APs, SSIDs, VLANs
- Test client connectivity and roaming
**Evidence:** WLC config, SSID setup, client connection test

**Lab 10: Wireshark Deep Dive (4 hours)**
- Capture traffic on your network
- Analyze TCP 3-way handshake, DNS queries
- Identify latency issues, retransmissions
- Use capture filters (tcp.port == 80, dns, etc.)
**Evidence:** Packet captures with annotations, analysis notes

**Lab 11: Juniper Configuration (5 hours)**
- GNS3 with Juniper vMX (or vSRX)
- Configure OSPF, BGP on Juniper
- Compare CLI with Cisco
- Practice commit/rollback
**Evidence:** Juniper configs, CLI comparison notes

**Lab 12: Enterprise Network Design (6 hours)**
- Design complete enterprise network (headquarters + 3 branches)
- Core: OSPF backbone with BGP to ISP
- Distribution: VLANs, MSTP
- Access: Edge security, wireless
- Document design with diagrams, IP plan, configs
**Evidence:** Full network design document, topology, all configs

---

## 📅 3-Week Learning Path (Condensed)

**Week 1: Routing Mastery**
Days 1-2: GNS3 setup + OSPF single area (Labs 01-02)
Days 3-4: OSPF multi-area (Lab 03)
Days 5-6: BGP fundamentals (Lab 04) + review Kuiper BGP materials
Day 7: Review, practice show commands

**Week 2: Switching & Advanced Protocols**
Days 8-9: Layer 2 switching (Lab 05)
Day 10: ISIS routing (Lab 06)
Days 11-13: MPLS L3VPN (Lab 07)
Day 14: Review protocols, study certifications (CCNP material)

**Week 3: Security, Wireless, Leadership Prep**
Days 15-16: Firewall + VPN (Lab 08)
Day 17: Wireless controller (Lab 09)
Day 18: Wireshark analysis (Lab 10)
Day 19: Juniper configuration (Lab 11)
Day 20: Enterprise design capstone (Lab 12)
Day 21: Interview practice, review all labs, polish portfolio

---

## 🎤 Sample Interview Questions

**Easy:**
1. Explain OSPF in simple terms. When would you use it?
2. What's the difference between a Layer 2 switch and a Layer 3 switch?
3. What is BGP and why is it used on the internet?

**Medium:**
4. Design OSPF for a company with 50 sites. How many areas? What's your summarization strategy?
5. A BGP route is taking a suboptimal path. Walk me through troubleshooting.
6. Explain MPLS L3VPN and when you'd use it vs traditional site-to-site VPNs.

**Hard:**
7. Design network architecture for an enterprise with 10,000 employees, 20 branch offices, and hybrid cloud (AWS + Azure). Include routing, security, wireless.
8. A critical router just failed during business hours. Walk me through your immediate response, investigation, and resolution.
9. You're responsible for a network with 5,000 devices. How do you automate configuration management and ensure consistency?

**Leadership:**
10. Tell me about a time you mentored a junior engineer. What was your approach?
11. Describe a project where you were the technical lead. How did you ensure success?

---

## 🎓 Certification Study Integration

**Recommended Path:**
- **CCNA** (if don't have) → Foundation
- **CCNP Enterprise** → Core routing/switching
- **CCNP Security** → Firewall, VPN, IDS
- **JNCIA/JNCIS** → Juniper equivalent

**Study Resources:**
- Official Cert Guides (books)
- INE, CBT Nuggets (video training)
- Boson ExSim (practice exams)
- GNS3 labs (hands-on practice)

**Note:** Certifications aren't required but "CCNA, CCNP, CCIE a plus" → having them differentiates you.

---

## 📂 Your Relevant Portfolio Projects

- `projects/05-networking-datacenter/PRJ-NET-DC-001/` → "I designed and implemented datacenter networking with..."
- `projects/06-homelab/PRJ-HOME-002/` → "In my homelab, I run enterprise-grade network with VLANs, routing..."
- `projects/p03-hybrid-network/` → "I built hybrid network with VPN and BGP..." (from Kuiper prep)
- `projects/03-cybersecurity/PRJ-CYB-OPS-002/` → "I implemented network security operations with..."

---

## ✅ Pre-Interview Checklist

**Technical Depth:**
- [ ] Can draw OSPF multi-area topology from memory
- [ ] Can explain BGP path selection algorithm step-by-step
- [ ] Know STP/RSTP/MSTP differences and use cases
- [ ] Comfortable with Cisco IOS show commands (route, interfaces, protocols)
- [ ] Understand MPLS basics and L3VPN architecture
- [ ] Can configure firewall from scratch
- [ ] Wireless fundamentals clear (channels, roaming, security)
- [ ] Wireshark proficiency (can diagnose common issues)

**Leadership & Communication:**
- [ ] Prepared examples of mentoring junior engineers
- [ ] Can discuss leading technical projects
- [ ] Ready to explain complex topics to non-technical stakeholders
- [ ] Examples of collaborating with security/DevOps teams

**Portfolio:**
- [ ] Homelab fully documented with diagrams
- [ ] GNS3 labs exported and documented
- [ ] Can screen-share and walk through network designs
- [ ] Resume highlights "5,000+ device network experience" (adjust based on your actual scale)

**Logistics:**
- [ ] On-site requirement confirmed (Redmond, WA)
- [ ] Prepared for whiteboard exercises
- [ ] Questions for interviewer (career growth, team structure, typical projects)

---

## 💪 You've Got This!

**Your Strengths for This Role:**
- ✅ Networking fundamentals (homelab, Kuiper BGP/VPN prep)
- ✅ Troubleshooting mindset (cybersecurity background)
- ✅ Documentation skills (all projects well-documented)
- ✅ Learning agility (Kuiper prep shows you can learn complex topics quickly)

**What Sets You Apart:**
- Your homelab shows passion and initiative
- Cross-domain knowledge (networking + security + cloud + DevOps)
- Portfolio demonstrates real work, not just theoretical knowledge

**Interview Focus:**
- Lead with homelab when discussing experience
- Emphasize Kuiper BGP/VPN deep dive (shows advanced routing knowledge)
- Highlight troubleshooting methodology (systematic approach)
- Demonstrate leadership potential (even if past roles weren't "lead"—show initiative)

---

**Next Steps:**
1. **Today:** Set up GNS3, start Lab 01
2. **Week 1:** OSPF mastery + BGP review (leverage Kuiper materials)
3. **Week 2:** Switching + advanced routing (ISIS, MPLS)
4. **Week 3:** Security, wireless, capstone design + interview practice

**Highest Compensation Role—Worth the 3-Week Investment! 🚀**

---

**Last Updated:** 2025-11-10
**Status:** Ready to begin—this is your highest-paying opportunity!

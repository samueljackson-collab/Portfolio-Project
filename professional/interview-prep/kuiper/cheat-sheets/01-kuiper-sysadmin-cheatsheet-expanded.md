# Kuiper System/Network Administrator Interview Cheat Sheet
## Expanded Edition with Feynman Method Explanations

**Purpose:** Deep understanding of Kuiper ground infrastructure, AWS connectivity, and network operations
**Audience:** System/Network Administrator Interview Candidates
**Last Updated:** 2025-11-10

---

## How to Use This Cheat Sheet

1. **Read the Question/Topic** - Understand what's being asked
2. **Study the Core Answer** - Learn the technical facts
3. **Explain It Simply (Feynman)** - Can you teach this to a 5-year-old?
4. **Review Acronyms** - Know every abbreviation
5. **Apply Practical Example** - Connect to real-world scenarios
6. **Avoid Common Pitfalls** - Learn from common mistakes
7. **Map to Your Portfolio** - Reference your actual project work

---

## Q1-20: Core AWS & Kuiper Ground Infrastructure

### Q1: What is Project Kuiper & where does a Sys/NetAdmin fit?

| Column | Content |
|--------|---------|
| **Question/Topic** | What is Project Kuiper and what is the System/Network Administrator's role? |
| **Core Answer** | Kuiper is Amazon's Low Earth Orbit (LEO) satellite broadband network deploying ~3,200 satellites. As a Sys/NetAdmin, you own the **Ground Gateway Infrastructure** and **AWS Edge Connectivity**. Your responsibilities include: operating ground gateways (RF→IP handoff, BGP routing to AWS), managing secure admin planes (VPN, MFA, bastions), building reliable connectivity (TGW/VPN/DirectConnect), automating configuration/monitoring, enforcing PKI/mTLS security, and leading incident response with SLO-based alerting. |
| **Feynman Explanation** | Imagine Kuiper as a giant Wi-Fi network in space with thousands of satellites. Your job is to build and maintain the "ground stations" that catch the internet signals from space and deliver them into Amazon's cloud. You make sure the connection is fast, secure, and never breaks. If something goes wrong, you fix it quickly using your monitoring tools. |
| **All Acronyms Explained** | • **LEO** = Low Earth Orbit (satellites orbiting 340-1,200 km above Earth, closer than traditional satellites for lower latency)<br>• **Sys/NetAdmin** = System and Network Administrator<br>• **RF** = Radio Frequency (the wireless signals satellites use)<br>• **IP** = Internet Protocol (how data travels on the internet)<br>• **BGP** = Border Gateway Protocol (the routing protocol that connects different networks)<br>• **AWS** = Amazon Web Services (Amazon's cloud computing platform)<br>• **TGW** = Transit Gateway (AWS's cloud router for connecting many networks)<br>• **VPN** = Virtual Private Network (encrypted tunnel over the internet)<br>• **MFA** = Multi-Factor Authentication (requires 2+ ways to prove identity)<br>• **PKI** = Public Key Infrastructure (system for managing security certificates)<br>• **mTLS** = Mutual TLS (two-way encrypted authentication)<br>• **SLO** = Service Level Objective (target for system performance/reliability) |
| **Practical Example from Your Portfolio** | **Reference:** `projects/p03-hybrid-network/` - You built a hybrid network connecting on-premises infrastructure to AWS using Transit Gateway and Site-to-Site VPN with BGP routing. This mirrors how Kuiper ground gateways connect to AWS.<br><br>**Reference:** `projects/06-homelab/PRJ-HOME-002/` - Your UniFi homelab demonstrates VLAN segmentation, secure management planes, and monitoring—skills directly applicable to ground gateway operations. |
| **Common Pitfalls to Avoid** | ❌ Thinking the job is only about satellites (it's really about ground infrastructure & AWS networking)<br>❌ Forgetting security—ground gateways are high-value attack targets<br>❌ Not understanding BGP basics (critical for routing between gateway and AWS)<br>❌ Ignoring observability—you can't fix what you can't see<br>❌ Underestimating the importance of automation at scale |
| **Risk Level** | 🟡 **MEDIUM** - Core concept, must understand the big picture |
| **Time to Learn** | ⏱️ **2-3 hours** - Read AWS networking docs, review your hybrid network project |
| **Owner/Accountability** | 👤 **You** - This is foundational knowledge for the interview |

---

### Q2: Data Flow - Terminal → Satellite → Ground → AWS

| Column | Content |
|--------|---------|
| **Question/Topic** | Describe the complete data flow from a customer terminal to AWS services |
| **Core Answer** | **Path:** Customer Terminal → LEO Satellite Mesh (via OISL) → Ground Gateway POP → AWS Edge (via VPN/DX) → Transit Gateway → Application VPC → Services.<br><br>**Details:** Customer terminals uplink via Ka-band phased arrays. Satellites forward traffic through optical inter-satellite links (OISL) to the optimal ground gateway based on geometry, load, and availability. The gateway converts RF signals to IP packets and hands off to the terrestrial network. Traffic enters AWS via Site-to-Site VPN or Direct Connect, routes through Transit Gateway to the appropriate VPC, and reaches backend services (APIs, edge caches, authentication). |
| **Feynman Explanation** | Think of it like mailing a letter: (1) You drop it in a mailbox (customer terminal sends data to satellite), (2) The post office sorts and flies it to another city (satellites pass data through space to ground station), (3) A local post office receives it (ground gateway converts space signal to internet), (4) It goes through a sorting center (AWS Transit Gateway), (5) Finally delivered to the right house (your application server). Each step has to be fast and reliable! |
| **All Acronyms Explained** | • **LEO** = Low Earth Orbit<br>• **OISL** = Optical Inter-Satellite Link (laser beams between satellites for high-speed data transfer)<br>• **POP** = Point of Presence (a physical location where network equipment is housed)<br>• **AWS** = Amazon Web Services<br>• **DX** = Direct Connect (AWS's private, dedicated network connection)<br>• **VPN** = Virtual Private Network<br>• **TGW** = Transit Gateway<br>• **VPC** = Virtual Private Cloud (isolated network in AWS)<br>• **RF** = Radio Frequency<br>• **IP** = Internet Protocol<br>• **Ka-band** = Frequency band (26.5-40 GHz) used for satellite communication (higher frequency = more bandwidth) |
| **Practical Example from Your Portfolio** | **Reference:** `projects/p03-hybrid-network/README.md` - Your hybrid network project shows the flow from on-prem (like ground gateway) → VPN → Transit Gateway → VPC → application.<br><br>**Reference:** `projects/p10-multi-region/README.md` - Demonstrates multi-region routing similar to how Kuiper routes traffic to different ground gateways.<br><br>**Reference:** `projects/02-cloud-architecture/PRJ-CLOUD-001/` - Shows AWS VPC architecture and data flow patterns. |
| **Common Pitfalls to Avoid** | ❌ Forgetting about trust boundaries at each hop (terminal, satellite mesh, gateway, AWS)<br>❌ Not considering failover paths when a gateway or satellite goes down<br>❌ Ignoring encryption requirements at each layer<br>❌ Missing the importance of latency at each hop (LEO orbit minimizes this but it still adds up)<br>❌ Overlooking monitoring points—you need visibility at every stage |
| **Risk Level** | 🔴 **HIGH** - Interviewers will test your understanding of the complete system |
| **Time to Learn** | ⏱️ **3-4 hours** - Study satellite networking basics, review AWS networking architecture |
| **Owner/Accountability** | 👤 **You** - Draw this flow from memory before the interview |

---

### Q3: Satellite Link Constraints & Operations Impact

| Column | Content |
|--------|---------|
| **Question/Topic** | What are the unique constraints of satellite links and how do they impact operations? |
| **Core Answer** | **Constraints:** (1) Variable latency & jitter due to satellite handoffs as terminals move between coverage areas, (2) Weather fade (rain, snow) can degrade Ka-band signals, (3) Variable capacity per beam based on user density and satellite position, (4) Doppler shift affects signal frequency.<br><br>**Operations Impact:** Must implement QoS (Quality of Service) using DSCP classes to prioritize control-plane traffic over user data, tune TCP buffers for high bandwidth-delay product, design robust retry/backoff logic, enable graceful failover between gateways, and set SLOs based on latency percentiles (P95, P99) and packet loss rather than just bandwidth. Monitor BGP stability and convergence time. |
| **Feynman Explanation** | Satellite internet is like having a really long garden hose for your water. Sometimes the water pressure changes (latency varies), sometimes it rains and the hose gets kinked (weather interference), and sometimes lots of neighbors want to use water at the same time (capacity sharing). As the operator, you need to make sure important water (like emergency services) always flows first, you have backup hoses ready, and you know when problems happen before customers complain. |
| **All Acronyms Explained** | • **QoS** = Quality of Service (prioritizing important traffic over less important traffic)<br>• **DSCP** = Differentiated Services Code Point (a field in IP packets that marks traffic priority, 0-63)<br>• **TCP** = Transmission Control Protocol (reliable data delivery over networks)<br>• **SLO** = Service Level Objective (target for system performance)<br>• **BGP** = Border Gateway Protocol<br>• **P95/P99** = 95th/99th Percentile (95% or 99% of measurements are better than this value)<br>• **Ka-band** = 26.5-40 GHz satellite frequency band<br>• **Doppler shift** = Frequency change due to satellite motion relative to ground<br>• **Bandwidth-delay product** = Maximum data "in flight" = bandwidth × round-trip time |
| **Practical Example from Your Portfolio** | **Reference:** `projects/p07-roaming-simulation/README.md` - Your roaming simulation project shows handling variable network conditions and handoffs.<br><br>**Reference:** `projects/p04-ops-monitoring/README.md` - Demonstrates SLO-based monitoring with percentile metrics (P95, P99 latency).<br><br>**Lab to Add:** Use Linux `tc netem` to simulate satellite conditions (delay, jitter, loss) in your homelab and measure impact on applications. Document in `projects/06-homelab/PRJ-HOME-002/experiments/satellite-link-simulation/`. |
| **Common Pitfalls to Avoid** | ❌ Only monitoring bandwidth—latency and jitter matter more for user experience<br>❌ Using average latency instead of percentiles (P95, P99)—averages hide problems<br>❌ Not implementing QoS—control plane traffic must always work<br>❌ Assuming stable latency like terrestrial fiber—satellite links are dynamic<br>❌ Forgetting weather impacts—need monitoring and graceful degradation<br>❌ Over-aggressive TCP timeouts that cause unnecessary retransmissions |
| **Risk Level** | 🔴 **HIGH** - Shows you understand the unique challenges of satellite operations |
| **Time to Learn** | ⏱️ **4-5 hours** - Study RF propagation, QoS basics, high-latency network design |
| **Owner/Accountability** | 👤 **You** - Run a lab simulation to demonstrate practical understanding |

---

### Q4: Simulating Satellite-Like Conditions in a Lab

| Column | Content |
|--------|---------|
| **Question/Topic** | How would you simulate satellite link conditions for testing? |
| **Core Answer** | Use Linux **tc netem** (Traffic Control Network Emulator) to inject realistic impairments: (1) Base delay (20-40ms for LEO), (2) Jitter (5-15ms variation), (3) Packet loss (0.1-1%), (4) Bandwidth shaping with **TBF** (Token Bucket Filter). Drive traffic with **iperf3** for throughput testing and synthetic HTTP probes for application-level validation. Measure application behavior, validate alert thresholds fire correctly, and verify SLO error-budget burn calculations. Document before/after metrics with screenshots. |
| **Feynman Explanation** | It's like practicing driving in bad weather using a simulator before doing it for real. You use a computer tool (tc netem) to make your home internet act like a satellite connection—adding delays, making some packets disappear, and limiting speed. Then you test if your applications and alerts work correctly under these fake satellite conditions. This way, you're prepared when real problems happen. |
| **All Acronyms Explained** | • **tc netem** = Traffic Control Network Emulator (Linux kernel module for network simulation)<br>• **LEO** = Low Earth Orbit<br>• **TBF** = Token Bucket Filter (bandwidth rate limiter)<br>• **iperf3** = Network performance testing tool (measures throughput, jitter, loss)<br>• **SLO** = Service Level Objective<br>• **HTTP** = Hypertext Transfer Protocol (web traffic)<br>• **ms** = milliseconds (1/1000th of a second)<br>• **Mbps** = Megabits per second (bandwidth measurement) |
| **Practical Example from Your Portfolio** | **TO CREATE:** `projects/06-homelab/PRJ-HOME-002/experiments/satellite-link-simulation/`<br>- Script: `apply-satellite-profile.sh` (adds netem rules)<br>- Script: `revert-to-normal.sh` (removes netem rules)<br>- Test: `run-iperf-baseline.sh` (normal conditions)<br>- Test: `run-iperf-satellite.sh` (with netem)<br>- Results: CSV files and Grafana dashboard screenshots showing latency, jitter, throughput before/after<br><br>**Reference:** `projects/p04-ops-monitoring/README.md` - Your monitoring setup can visualize the impact. |
| **Common Pitfalls to Avoid** | ❌ Not testing on a separate interface (netem affects all traffic on the interface)<br>❌ Forgetting to revert netem rules after testing (breaks your network!)<br>❌ Unrealistic values (e.g., 500ms delay for LEO—that's GEO satellite)<br>❌ Only testing bandwidth, ignoring latency spikes and jitter<br>❌ Not documenting baseline performance before applying netem<br>❌ Testing only one direction (need both upload and download impairment) |
| **Risk Level** | 🟢 **LOW-MEDIUM** - Nice-to-have practical demonstration |
| **Time to Learn** | ⏱️ **2-3 hours** - Tutorial + hands-on lab |
| **Owner/Accountability** | 👤 **You** - Build this lab before the interview for a great talking point |

---

### Q5: AWS Services That Matter for Ground Connectivity

| Column | Content |
|--------|---------|
| **Question/Topic** | Which AWS services are critical for Kuiper ground gateway connectivity? |
| **Core Answer** | **Core Services:**<br>1. **VPC** - Network segmentation and isolation<br>2. **Transit Gateway (TGW)** - Regional hub connecting VPCs and on-prem<br>3. **Site-to-Site VPN** - Encrypted tunnels with BGP dynamic routing<br>4. **Direct Connect (DX)** - Private, dedicated network connection<br>5. **Route 53** - Global DNS with latency/geo routing and health checks<br>6. **CloudWatch** - Metrics, alarms, dashboards for monitoring<br>7. **CloudTrail** - Audit logging of all API calls<br>8. **IAM** - Identity and access management with least privilege<br>9. **AWS PrivateLink** - Private connectivity to AWS services<br>10. **Network Firewall** - Managed firewall for VPC protection |
| **Feynman Explanation** | Think of AWS as a big city with different neighborhoods (VPCs). You need: roads between neighborhoods (Transit Gateway), secure tunnels to your home (VPN), a private highway (Direct Connect), traffic signs (Route 53 for routing), security cameras (CloudWatch monitoring), a police log (CloudTrail), door locks (IAM for access control), and security gates (Network Firewall). Each piece keeps your network fast, secure, and organized. |
| **All Acronyms Explained** | • **AWS** = Amazon Web Services<br>• **VPC** = Virtual Private Cloud (isolated network section in AWS)<br>• **TGW** = Transit Gateway (cloud router connecting multiple VPCs and on-prem networks)<br>• **VPN** = Virtual Private Network<br>• **BGP** = Border Gateway Protocol<br>• **DX** = Direct Connect (dedicated physical connection to AWS)<br>• **Route 53** = AWS's DNS service (named after DNS port 53)<br>• **DNS** = Domain Name System (translates names to IP addresses)<br>• **IAM** = Identity and Access Management<br>• **API** = Application Programming Interface<br>• **Geo routing** = Geolocation-based routing (send EU users to EU servers) |
| **Practical Example from Your Portfolio** | **Reference:** `projects/p01-aws-infra/README.md` - Demonstrates VPC architecture and AWS service integration<br><br>**Reference:** `projects/p03-hybrid-network/README.md` - Shows Transit Gateway, Site-to-Site VPN with BGP, and hybrid connectivity<br><br>**Reference:** `projects/p10-multi-region/README.md` - Uses Route 53 for multi-region routing<br><br>**Reference:** `projects/p02-iam-hardening/README.md` - IAM best practices and least privilege<br><br>**Reference:** `projects/p04-ops-monitoring/README.md` - CloudWatch dashboards and alarms |
| **Common Pitfalls to Avoid** | ❌ Using VPC peering instead of Transit Gateway for complex topologies<br>❌ Not enabling VPN tunnel monitoring (TunnelState, BGP session metrics)<br>❌ Forgetting to encrypt Direct Connect with VPN overlay (DX is not encrypted by default)<br>❌ Using public Route 53 zones for internal routing (use Private Hosted Zones)<br>❌ Overly permissive IAM policies (violates least privilege)<br>❌ Not enabling CloudTrail or VPC Flow Logs (blind to attacks/issues)<br>❌ Missing CloudWatch alarms for critical metrics (tunnel down, BGP down) |
| **Risk Level** | 🔴 **CRITICAL** - Core AWS knowledge required for the role |
| **Time to Learn** | ⏱️ **6-8 hours** - Deep dive into each service, hands-on labs |
| **Owner/Accountability** | 👤 **You** - Must be able to discuss each service confidently |

---

### Q6: Securing Control Planes with mTLS + Private CA

| Column | Content |
|--------|---------|
| **Question/Topic** | How do you secure terminal-to-gateway control plane communications? |
| **Core Answer** | Enforce **Mutual TLS (mTLS)** for all control-plane traffic (configuration, telemetry, admin APIs). Use a **Private Certificate Authority** (AWS ACM Private CA or HashiCorp Vault) to issue certificates with strict Subject Alternative Names (SANs) matching device identity. Implement short-lived certificates (30-90 days), automated rotation via orchestration, certificate pinning for critical paths, and least-privilege IAM roles for automation accessing the CA. Isolate control plane on dedicated admin VLAN, require jump host + MFA for human access, and ship immutable logs to centralized logging (CloudWatch Logs or Splunk). |
| **Feynman Explanation** | Imagine your control plane is like the cockpit of an airplane—only trained pilots with special ID badges can enter, and they have to prove who they are in two ways (their badge AND a password). mTLS means both sides prove their identity with digital badges (certificates) that expire regularly so stolen badges don't work forever. A Private CA is like the badge-making machine that only you control—not public, not shared. This keeps attackers out even if they break through your front door. |
| **All Acronyms Explained** | • **mTLS** = Mutual Transport Layer Security (both client and server authenticate with certificates)<br>• **TLS** = Transport Layer Security (encryption protocol for secure communication)<br>• **CA** = Certificate Authority (trusted entity that issues digital certificates)<br>• **ACM** = AWS Certificate Manager<br>• **Private CA** = Certificate Authority that only you control (not publicly trusted)<br>• **SAN** = Subject Alternative Name (list of identities in a certificate: DNS names, IPs)<br>• **IAM** = Identity and Access Management<br>• **VLAN** = Virtual Local Area Network (network segmentation)<br>• **MFA** = Multi-Factor Authentication<br>• **API** = Application Programming Interface<br>• **Certificate pinning** = Hardcoding expected certificate fingerprints to prevent impersonation |
| **Practical Example from Your Portfolio** | **Reference:** `projects/p02-iam-hardening/README.md` - Demonstrates IAM least privilege and security hardening<br><br>**Reference:** `projects/p16-zero-trust/README.md` - Zero-trust architecture with mTLS principles<br><br>**Reference:** `projects/06-homelab/PRJ-HOME-002/` - Shows VLAN segmentation and management plane isolation<br><br>**TO CREATE:** `projects/06-homelab/PRJ-HOME-002/pki-lab/`<br>- Set up a private CA (using easy-rsa or AWS ACM PCA)<br>- Generate short-lived certificates<br>- Configure sample app with mTLS<br>- Document rotation process |
| **Common Pitfalls to Avoid** | ❌ Using self-signed certificates without a CA (hard to rotate, no chain of trust)<br>❌ Long-lived certificates (1+ years)—increases risk window if compromised<br>❌ Not validating SANs—allows certificate reuse attacks<br>❌ Manual certificate rotation—doesn't scale, error-prone<br>❌ Mixing control plane and data plane traffic—compromises isolation<br>❌ Not monitoring certificate expiration—leads to outages<br>❌ Storing CA private keys insecurely—game over if compromised |
| **Risk Level** | 🔴 **CRITICAL** - Security is paramount for satellite ground infrastructure |
| **Time to Learn** | ⏱️ **5-6 hours** - Study PKI, TLS, certificate lifecycle, hands-on mTLS lab |
| **Owner/Accountability** | 👤 **You** - Be ready to discuss certificate management in depth |

---

### Q7: When to Use Transit Gateway (TGW)

| Column | Content |
|--------|---------|
| **Question/Topic** | When should you use AWS Transit Gateway instead of alternatives? |
| **Core Answer** | Use TGW when: (1) Connecting 5+ VPCs (VPC peering becomes O(N²) complexity), (2) Hybrid connectivity to on-premises or ground gateways (centralized VPN/Direct Connect attachment point), (3) Need for transitive routing (A→TGW→B, TGW routes between them), (4) Centralized network inspection (route traffic through firewall appliances), (5) Multi-account AWS Organizations setup (share TGW via Resource Access Manager), (6) Inter-region connectivity (TGW peering between regions). TGW acts as a regional cloud router, simplifying operations and reducing complexity. |
| **Feynman Explanation** | Imagine you have 10 houses (VPCs) and want everyone to talk to each other. Without Transit Gateway, you'd need to build 45 separate roads between every house pair (N×(N-1)/2). That's a nightmare! Transit Gateway is like building one central roundabout—each house builds one road to the roundabout, and the roundabout handles directing traffic. Now you only need 10 roads. Plus, you can put a security checkpoint at the roundabout to inspect all traffic. |
| **All Acronyms Explained** | • **TGW** = Transit Gateway<br>• **VPC** = Virtual Private Cloud<br>• **O(N²)** = Big-O notation meaning complexity grows quadratically with number of items<br>• **VPN** = Virtual Private Network<br>• **Direct Connect (DX)** = AWS's private network connection<br>• **AWS Organizations** = Multi-account management service<br>• **RAM** = Resource Access Manager (share AWS resources across accounts)<br>• **CIDR** = Classless Inter-Domain Routing (IP address range notation) |
| **Practical Example from Your Portfolio** | **Reference:** `projects/p03-hybrid-network/README.md` - Your project uses Transit Gateway to connect on-premises to multiple VPCs<br><br>**Reference:** `projects/p10-multi-region/README.md` - Demonstrates inter-region TGW peering<br><br>**Visual Aid:** Create a diagram comparing:<br>- 5 VPCs with peering: 10 connections<br>- 5 VPCs with TGW: 5 connections<br>- 10 VPCs with peering: 45 connections (!)<br>- 10 VPCs with TGW: 10 connections<br><br>Save to: `docs/diagrams/kuiper/tgw-vs-peering-scale.png` |
| **Common Pitfalls to Avoid** | ❌ Using TGW for just 2-3 VPCs (overkill, costs more than peering)<br>❌ Not understanding TGW attachment costs (charged per attachment + per GB transferred)<br>❌ Forgetting to configure route tables properly (TGW has its own route tables)<br>❌ Assuming automatic routing (must explicitly associate route tables with attachments)<br>❌ Not considering bandwidth limits (TGW has 50 Gbps burst per AZ)<br>❌ Creating too many TGWs (usually one per region is sufficient) |
| **Risk Level** | 🟡 **MEDIUM-HIGH** - Core architectural decision for AWS networking |
| **Time to Learn** | ⏱️ **3-4 hours** - Study TGW concepts, review your hybrid network project |
| **Owner/Accountability** | 👤 **You** - Be able to justify TGW vs alternatives in an interview |

---

### Q8: TGW vs Full-Mesh VPC Peering

| Column | Content |
|--------|---------|
| **Question/Topic** | Compare Transit Gateway to full-mesh VPC peering. When to use each? |
| **Core Answer** | **VPC Peering:**<br>• 1-to-1 connections, non-transitive (A-B and B-C doesn't mean A-C)<br>• No additional hop, slightly lower latency<br>• No per-GB transfer charges between peered VPCs in same region<br>• Scales O(N²): 5 VPCs = 10 connections, 10 VPCs = 45 connections<br>• Max 125 peering connections per VPC<br><br>**Transit Gateway:**<br>• Hub-and-spoke, transitive routing (A→TGW→C works automatically)<br>• Centralized routing control and network inspection<br>• Scales O(N): 100 VPCs = 100 connections<br>• Supports hybrid connectivity (VPN, Direct Connect)<br>• Additional per-attachment and per-GB charges<br><br>**Decision Rule:** Use peering for 2-4 VPCs in simple topology; use TGW for 5+ VPCs or any hybrid/multi-region need. |
| **Feynman Explanation** | VPC peering is like having your friends' phone numbers—you call them directly, but if you want to talk to their friend, you can't call through them; you need their friend's number too. This gets messy fast! Transit Gateway is like a phone operator—you call the operator, tell them who you want to talk to, and they connect you to anyone. It's easier when you have lots of friends, but you pay the operator a small fee for the convenience. |
| **All Acronyms Explained** | • **TGW** = Transit Gateway<br>• **VPC** = Virtual Private Cloud<br>• **O(N²)** = Quadratic growth (connections = N × (N-1) / 2 for full mesh)<br>• **O(N)** = Linear growth (connections = N for hub-and-spoke)<br>• **Gbps** = Gigabits per second<br>• **AZ** = Availability Zone<br>• **VPN** = Virtual Private Network<br>• **DX** = Direct Connect<br>• **Transitive routing** = Ability to route traffic through an intermediary (A→B→C) |
| **Practical Example from Your Portfolio** | **Reference:** `projects/p03-hybrid-network/README.md` - Document your decision to use TGW instead of peering<br><br>**Create Decision Record:** `docs/adr/ADR-0002-tgw-vs-peering.md` with:<br>- Context: Connecting 8 VPCs + on-premises<br>- Peering option: 28 connections, no transitive routing, no on-prem<br>- TGW option: 8 connections, transitive routing, includes on-prem<br>- Decision: TGW<br>- Cost comparison table<br>- Scalability projection (adding 2 VPCs/month) |
| **Common Pitfalls to Avoid** | ❌ Choosing peering for complex topologies because "it's cheaper"—ignores operational complexity<br>❌ Forgetting that peering doesn't connect to on-premises (dead end for hybrid)<br>❌ Not accounting for growth—peering might work today but not in 6 months<br>❌ Mixing peering and TGW haphazardly—creates routing confusion<br>❌ Assuming transitive peering works (it doesn't—this is a common mistake!)<br>❌ Not considering inspection requirements (peering can't force traffic through firewall) |
| **Risk Level** | 🔴 **HIGH** - Common interview question, tests architectural thinking |
| **Time to Learn** | ⏱️ **2-3 hours** - Study AWS docs, create comparison table, write ADR |
| **Owner/Accountability** | 👤 **You** - Memorize the math (N² vs N) and key decision factors |

---

### Q9: BGP over Site-to-Site VPN

| Column | Content |
|--------|---------|
| **Question/Topic** | How do you configure BGP over AWS Site-to-Site VPN? |
| **Core Answer** | **Steps:**<br>1. Create Customer Gateway (CGW) resource in AWS—specify public IP and BGP ASN of your on-prem router<br>2. Create VPN Connection to Transit Gateway or Virtual Private Gateway—enable dynamic routing<br>3. AWS automatically creates 2 IPsec tunnels with 4 BGP peering IPs (169.254.x.x link-local)<br>4. Download configuration file for your router/firewall<br>5. Configure on-prem side: IPsec tunnels, BGP neighbor statements, prefix advertisements<br>6. Apply BGP policies: route-maps, prefix-lists, AS-PATH manipulation, communities for traffic engineering<br>7. Monitor: CloudWatch metrics (TunnelState, BGPConnectionState, TunnelDataIn/Out), BGP route table<br>8. Alert on: tunnel down, BGP session down, route count changes, tunnel asymmetry |
| **Feynman Explanation** | BGP is like having two mail carriers who automatically tell each other which streets they cover. If a street closes, they update each other instantly without you doing anything. You set it up once—configure the secure tunnel (like a locked mail truck route) and tell each side which neighborhoods to advertise. After that, if you add new neighborhoods (networks), they automatically learn about them. This beats manually updating maps (static routes) every time something changes! |
| **All Acronyms Explained** | • **BGP** = Border Gateway Protocol (dynamic routing protocol that exchanges network prefixes)<br>• **VPN** = Virtual Private Network<br>• **CGW** = Customer Gateway (your on-prem VPN device)<br>• **ASN** = Autonomous System Number (unique ID for your network, public or private 64512-65534)<br>• **TGW** = Transit Gateway<br>• **VGW** = Virtual Private Gateway (older, VPC-attached VPN endpoint)<br>• **IPsec** = Internet Protocol Security (VPN encryption protocol)<br>• **Route-map** = BGP policy tool for filtering/modifying routes<br>• **AS-PATH** = BGP attribute showing the path through ASNs (used for path selection)<br>• **Communities** = BGP tags for grouping/signaling routes (e.g., "backup route")<br>• **Link-local** = 169.254.0.0/16 IP range for local network links only |
| **Practical Example from Your Portfolio** | **Reference:** `projects/p03-hybrid-network/README.md` - Your project implements BGP over Site-to-Site VPN<br><br>**Evidence to add:**<br>1. `terraform/aws-vpn-bgp/` - Terraform code for CGW, VPN connection, TGW attachment<br>2. `docs/runbooks/vpn-bgp-setup.md` - Step-by-step configuration guide<br>3. `dashboards/cloudwatch-vpn-bgp.json` - CloudWatch dashboard showing tunnel and BGP status<br>4. `evidence/screenshots/bgp-routes.png` - Screenshot of BGP route table from on-prem router<br>5. `evidence/screenshots/cw-vpn-metrics.png` - CloudWatch metrics showing healthy tunnels |
| **Common Pitfalls to Avoid** | ❌ Mismatched BGP ASNs (AWS side vs your CGW config)<br>❌ Firewall blocking BGP port (TCP 179) or IPsec ports (UDP 500, 4500)<br>❌ Not configuring both tunnels (single point of failure)<br>❌ Advertising too many prefixes (AWS has limits, e.g., 100 routes per VPN)<br>❌ Not setting BGP timers appropriately (too aggressive = flapping, too slow = slow convergence)<br>❌ Forgetting to enable route propagation on TGW route table<br>❌ No monitoring/alerting—tunnel goes down and nobody knows |
| **Risk Level** | 🔴 **CRITICAL** - Core technology for ground gateway connectivity |
| **Time to Learn** | ⏱️ **6-8 hours** - Study BGP basics, IPsec, AWS VPN docs, hands-on lab |
| **Owner/Accountability** | 👤 **You** - Must be able to configure and troubleshoot BGP over VPN |

---

### Q10: Using the Two Tunnels per VPN (ECMP vs Active/Standby)

| Column | Content |
|--------|---------|
| **Question/Topic** | AWS provides two VPN tunnels per connection. How should you use them? |
| **Core Answer** | **ECMP (Equal-Cost Multi-Path) - Recommended:**<br>• Both tunnels active simultaneously<br>• Traffic load-balanced across both (doubles throughput, max ~2.5 Gbps combined)<br>• Higher resilience—failure of one tunnel = 50% capacity remains<br>• Requires BGP configuration with equal AS-PATH length and local-preference<br>• Monitor for asymmetry (unbalanced traffic distribution)<br><br>**Active/Standby:**<br>• One tunnel primary, second is hot backup<br>• Use BGP AS-PATH prepending or lower local-preference on backup<br>• Backup activates only when primary fails<br>• Simpler but wastes backup tunnel capacity<br><br>**Monitoring:** Alert on tunnel state changes, BGP flaps, asymmetric traffic, high packet loss, latency spikes. Document failover runbook. |
| **Feynman Explanation** | Having two VPN tunnels is like having two lanes on a bridge. ECMP is using both lanes all the time—cars (data) split between them, so you get double the traffic flow and if one lane closes, you still have the other working. Active/Standby is keeping one lane closed "just in case"—you only open it if the first lane breaks. ECMP is almost always better because why waste a perfectly good lane? But you need slightly smarter traffic cops (BGP config) to split the traffic evenly. |
| **All Acronyms Explained** | • **ECMP** = Equal-Cost Multi-Path (load balancing across multiple equal-cost routes)<br>• **VPN** = Virtual Private Network<br>• **BGP** = Border Gateway Protocol<br>• **AS-PATH** = Autonomous System Path (list of ASNs a route passed through)<br>• **AS-PATH prepending** = Artificially lengthening AS-PATH to make a route less preferred<br>• **Local-preference** = BGP attribute to prefer routes (higher = more preferred, local to your AS)<br>• **Gbps** = Gigabits per second<br>• **Tunnel state** = UP or DOWN status of VPN tunnel<br>• **BGP flap** = BGP session going up/down repeatedly (bad!) |
| **Practical Example from Your Portfolio** | **Reference:** `projects/p03-hybrid-network/README.md`<br><br>**Evidence to create:**<br>1. `docs/runbooks/vpn-ecmp-failover.md` - Runbook for ECMP configuration and failover testing<br>2. `dashboards/cloudwatch-vpn-ecmp.json` - Dashboard showing both tunnels' traffic, latency, packet loss<br>3. `evidence/tests/vpn-tunnel-failover/` - Document a chaos test:<br>   - Baseline: Both tunnels up, measure throughput<br>   - Scenario 1: Take down tunnel 1, verify traffic shifts to tunnel 2<br>   - Scenario 2: Restore tunnel 1, verify ECMP resumes<br>   - Screenshots of traffic graphs during test<br>4. `terraform/aws-vpn-ecmp/` - Terraform showing BGP configuration for ECMP |
| **Common Pitfalls to Avoid** | ❌ Configuring one tunnel and ignoring the second (wastes redundancy)<br>❌ Assuming ECMP works by default (requires explicit BGP configuration)<br>❌ Not testing failover—first time you find out it doesn't work shouldn't be during an outage<br>❌ Unequal tunnel performance (latency/loss) making ECMP perform poorly<br>❌ No alerting on tunnel asymmetry (traffic only on one tunnel = degraded ECMP)<br>❌ Not monitoring tunnel flapping (sign of instability)<br>❌ Missing BGP hold-time tuning (default 180s is too slow for failover) |
| **Risk Level** | 🟡 **MEDIUM-HIGH** - Important for high availability and performance |
| **Time to Learn** | ⏱️ **3-4 hours** - Study ECMP, BGP attributes, failover testing |
| **Owner/Accountability** | 👤 **You** - Be ready to explain ECMP configuration and show your failover test |

---

*[Continuing with Q11-Q20 in next message due to length...]*

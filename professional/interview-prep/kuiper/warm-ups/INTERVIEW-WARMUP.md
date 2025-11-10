# Kuiper System/Network Administrator - Interview Warm-Up Questions

**Purpose:** Practice questions with progressive difficulty to build interview confidence
**How to Use:** Start with Easy, progress to Hard. Practice answering aloud. Record yourself.
**Last Updated:** 2025-11-10

---

## How to Practice

1. **Read the question**
2. **Think for 30 seconds** (don't blurt out first thought)
3. **Answer aloud** (as if interviewer is listening)
4. **Time yourself** (aim for 2-3 min answers for technical, 3-5 min for behavioral)
5. **Record yourself** (phone video, helps identify verbal fillers, pace, clarity)
6. **Review the suggested answer** (compare to your answer, note gaps)
7. **Try again tomorrow** (repetition builds fluency)

---

## Question Categories

1. **Easy (Warmup):** Foundation concepts, definitions, basic explanations
2. **Medium (Core):** Application of knowledge, trade-off analysis, design choices
3. **Hard (Advanced):** Complex scenarios, troubleshooting, architecture design
4. **Behavioral:** Leadership principles, problem-solving, teamwork

---

## EASY Questions (10-15 min total practice)

### E1: What is Project Kuiper?
**Expected Answer Time:** 1-2 minutes
**Key Points to Hit:**
- Amazon's LEO satellite broadband network
- ~3,200 satellites providing global internet coverage
- Your role: ground gateway infrastructure and AWS connectivity
- Focus on reliability, security, and automation

**Cheat Sheet Reference:** Q1

**Practice Tip:** Use the Feynman explanation—explain like you're talking to a non-technical friend.

---

### E2: What is the difference between a VPC and a subnet?
**Expected Answer Time:** 1-2 minutes
**Key Points:**
- VPC = isolated virtual network in AWS (e.g., 10.0.0.0/16)
- Subnet = subdivision of VPC tied to one Availability Zone (e.g., 10.0.1.0/24)
- Public subnet = has route to Internet Gateway
- Private subnet = no direct internet route, uses NAT Gateway for outbound

**Cheat Sheet Reference:** Q5, Glossary (VPC, Subnet)

**Practice Tip:** Draw the architecture while explaining (on whiteboard or paper during interview).

---

### E3: What is Transit Gateway and when would you use it?
**Expected Answer Time:** 2 minutes
**Key Points:**
- Regional cloud router connecting VPCs, VPN, Direct Connect
- Use when: 5+ VPCs, hybrid connectivity, need transitive routing
- Avoids VPC peering sprawl (O(N²) → O(N))
- Centralized routing and inspection

**Cheat Sheet Reference:** Q7

**Practice Tip:** Mention the O(N²) math—shows you understand scalability.

---

### E4: Explain BGP in simple terms.
**Expected Answer Time:** 2 minutes
**Key Points:**
- Border Gateway Protocol—routing protocol of the internet
- Exchanges network prefixes (routes) between autonomous systems
- Dynamic (auto-updates when networks change) vs static routes (manual)
- Used in Kuiper for ground gateway ↔ AWS routing over VPN

**Cheat Sheet Reference:** Q9, Glossary (BGP)

**Practice Tip:** Use analogy: "Like mail carriers telling each other which streets they cover."

---

### E5: What is mTLS and why is it important?
**Expected Answer Time:** 2 minutes
**Key Points:**
- Mutual TLS = two-way authentication (both client and server present certificates)
- Regular TLS = only server proves identity (like HTTPS)
- mTLS = both sides prove identity (control planes, admin APIs)
- Critical for Kuiper: prevents unauthorized access to ground gateway control plane

**Cheat Sheet Reference:** Q6, Glossary (mTLS)

**Practice Tip:** Use the "ID badge" analogy from Feynman explanation.

---

## MEDIUM Questions (20-30 min total practice)

### M1: You have 8 VPCs that need to communicate. Should you use VPC peering or Transit Gateway? Why?
**Expected Answer Time:** 3-4 minutes
**Key Points:**
- **VPC Peering:** 8 VPCs = 28 connections (N*(N-1)/2), non-transitive, no hybrid connectivity
- **Transit Gateway:** 8 VPCs = 8 connections, transitive routing, supports hybrid, easier to manage
- **Decision:** TGW for this scenario
- **Trade-offs:** TGW costs more per attachment + per GB, but operational simplicity worth it at this scale
- **Future-proofing:** Adding 2 more VPCs: peering = +18 connections, TGW = +2 connections

**Cheat Sheet Reference:** Q7, Q8

**Practice Tip:** Write the math on whiteboard to show your analytical thinking.

---

### M2: AWS Site-to-Site VPN provides two tunnels. How would you use them and why?
**Expected Answer Time:** 3-4 minutes
**Key Points:**
- **ECMP (Recommended):** Both tunnels active, traffic load-balanced, ~2.5 Gbps combined, higher resilience
- **Active/Standby:** One tunnel primary, second backup only, wastes capacity
- **Configuration:** Use BGP with equal AS-PATH and local-preference for ECMP
- **Monitoring:** Alert on tunnel asymmetry (traffic only on one = degraded ECMP)
- **Failover Test:** Must test both tunnel failure and recovery

**Cheat Sheet Reference:** Q10

**Practice Tip:** Mention that you've tested this in your homelab (reference Lab 04).

---

### M3: How would you monitor a VPN connection to ensure it's working properly?
**Expected Answer Time:** 3-4 minutes
**Key Points:**
- **System Metrics (CloudWatch):**
  - TunnelState (UP/DOWN)
  - BGPSessionState (ESTABLISHED/IDLE)
  - TunnelDataIn/Out (bytes)
  - Packet loss %
- **Synthetic Probes:**
  - ICMP ping through tunnel
  - HTTP check to application behind tunnel
  - Validates user-facing functionality, not just tunnel status
- **Alerting:** Page on tunnel down OR synthetic probe fails (need both!)
- **Dashboard:** Real-time visibility for NOC

**Cheat Sheet Reference:** Q19

**Practice Tip:** Reference your Lab 06 monitoring dashboard—offer to show it if virtual interview.

---

### M4: Your BGP session over VPN keeps flapping (going up and down). How do you troubleshoot?
**Expected Answer Time:** 4-5 minutes
**Systematic Approach:**
1. **Check tunnel state:** Is IPsec tunnel stable? (CloudWatch TunnelState)
2. **Check packet loss:** High loss can cause BGP hold-timer expiry (default 180s)
3. **Check BGP timers:** Too aggressive? (e.g., 10s keepalive, 30s hold)—tune to 30s/90s
4. **Check firewall:** Is TCP port 179 allowed bidirectionally?
5. **Check BGP logs:** Look for NOTIFICATION messages (what caused session close?)
6. **Check ISP:** Is public internet path unstable? (traceroute, ping)
7. **Increase hold timer:** Give BGP more tolerance for temporary disruptions
8. **Consider Direct Connect:** If VPN over internet is fundamentally unstable

**Cheat Sheet Reference:** Q9, Glossary (BGP Flap)

**Practice Tip:** Show systematic troubleshooting—interviewers love structured thinking.

---

### M5: Explain the difference between latency-based and geolocation routing in Route 53. When would you use each?
**Expected Answer Time:** 3-4 minutes
**Key Points:**
- **Latency-based:** Route 53 measures latency from user to each endpoint, routes to lowest latency
  - **Use when:** Performance optimization, endpoints distributed across AWS regions
  - **Example:** User in Tokyo gets routed to ap-northeast-1 (lowest latency)
- **Geolocation:** Routes based on user's geographic location (continent/country/state)
  - **Use when:** Data sovereignty (GDPR), licensing restrictions, content localization
  - **Example:** All EU users → eu-west-1, all US users → us-east-1
- **For Kuiper:** Latency-based for user traffic (best performance), geolocation for regulatory compliance if needed
- **Key:** Combine with health checks for automatic failover

**Cheat Sheet Reference:** Q15

**Practice Tip:** Ask clarifying questions: "What's more important—absolute lowest latency or regulatory compliance?"

---

### M6: What goes into a safe network change plan?
**Expected Answer Time:** 3-4 minutes
**Key Points:**
- **Pre-change:**
  - Scope, blast radius, pre-checks (snapshot dashboards, configs)
  - Peer review (2+ engineers)
  - Rollback plan (specific commands)
  - Communication (NOC, stakeholders, on-call)
- **During change:**
  - Follow runbook step-by-step
  - Apply incrementally, test after each step
  - Monitor continuously
- **Post-change:**
  - Verify monitors green (BGP up, tunnels up, routes correct)
  - Run synthetic tests
  - Soak period (15-30 min)
  - Post-change review

**Cheat Sheet Reference:** Q14

**Practice Tip:** Emphasize discipline—"even in my homelab, I document changes" shows professionalism.

---

## HARD Questions (30-40 min total practice)

### H1: Design a highly available ground gateway architecture for Kuiper. Walk me through your design choices.
**Expected Answer Time:** 6-8 minutes
**Structured Answer:**

**Requirements Gathering (30 seconds):**
- "Let me clarify requirements: What's our availability SLO? 99.9%? 99.99%?"
- "What's our throughput requirement? 10 Gbps per gateway?"
- "Are we designing for one region or multi-region?"

**Architecture (3-4 minutes):**
1. **Two Ground Gateways in different geographic locations** (avoid correlated failures)
2. **Each gateway has:**
   - Primary path: 10G Direct Connect to AWS (low latency, high bandwidth)
   - Backup path: Site-to-Site VPN over internet (encrypted, instant failover)
3. **Both connect to same regional Transit Gateway** via DX and VPN attachments
4. **BGP Traffic Engineering:**
   - Use communities to mark primary (65000:100) vs backup (65000:200)
   - Set local-preference to prefer DX (200) over VPN (100)
   - Normal state: 50/50 traffic split between gateways (or 70/30 based on capacity)
5. **User Traffic Steering:**
   - Route 53 latency-based routing with health checks
   - Low TTL (60s) for fast DNS failover
   - Health checks probe gateway application endpoint, not just network reachability
6. **Monitoring:**
   - CloudWatch dashboards: tunnel state, BGP state, traffic throughput, latency
   - Synthetic probes: ICMP + HTTP end-to-end tests
   - Alarms: tunnel down, BGP down, health check fail → page immediately
7. **Failure Modes:**
   - Gateway A fails → BGP converges in 30-60s, DNS fails over in 60-120s (1 TTL + propagation)
   - Total failover time: ~2 minutes, within 99.9% SLO (43.8 min/month budget)

**Trade-offs (1-2 minutes):**
- Cost: ~$4K/month (2 gateways × DX + TGW) vs single gateway $2K/month
- Complexity: More complex operations, need robust monitoring and runbooks
- Resilience: Can lose entire gateway site without service impact—worth the investment

**Cheat Sheet Reference:** Q11, Q12

**Practice Tip:** Draw architecture on whiteboard while talking. This is your Lab 08 showcase!

---

### H2: You're on-call. You get paged at 3 AM: "VPN tunnel down." Walk me through your incident response.
**Expected Answer Time:** 5-7 minutes
**Incident Response (structured):**

**1. Acknowledge and Assess (1 min):**
- Ack page in PagerDuty (stops escalation)
- Check dashboard: Is this a single tunnel or both? One gateway or both?
- Check impact: Is traffic failing over automatically? Are users impacted?
- Severity: Single tunnel down = P2 (degraded), both tunnels down = P1 (outage)

**2. Immediate Mitigation (2 min):**
- If both tunnels down and traffic not failing over: Manual failover to backup gateway
- Open incident bridge if P1
- Post status update: "Investigating VPN tunnel issue, no user impact due to automatic failover" (or "User impact, working mitigation")

**3. Investigation (3-5 min):**
- **Check AWS side:**
  - AWS Health Dashboard—any AWS VPN issues in region?
  - CloudWatch metrics—when did tunnel go down? Was it gradual or sudden?
  - VPN logs—any error messages?
- **Check on-prem side:**
  - SSH to customer gateway—is it reachable?
  - Check IPsec logs—why did tunnel drop? (certificate expired? firewall change? ISP issue?)
  - Check BGP logs—did BGP session close gracefully or timeout?
- **Check network path:**
  - Can customer gateway reach AWS VPN endpoint IPs? (ping, traceroute)
  - Packet loss? ISP issue?

**4. Resolution (varies):**
- **If certificate expired:** Rotate certificate (runbook), restart tunnel
- **If firewall rule changed:** Revert or fix rule (UDP 500, 4500 for IPsec)
- **If ISP issue:** Engage ISP, use backup VPN tunnel over different ISP
- **If unknown:** Restart IPsec daemon (strongswan, libreswan), forces reconnection

**5. Validation (1-2 min):**
- Verify tunnel state UP in CloudWatch
- Verify BGP session ESTABLISHED
- Verify routes being exchanged (show ip bgp, show ip route)
- Run synthetic probes to confirm end-to-end connectivity
- Monitor for 15 min (soak period) to ensure stability

**6. Post-Incident (after resolution):**
- Close incident
- Write postmortem (blameless): What happened, why, how to prevent recurrence
- Action items: Add monitoring if gap found, update runbook, fix root cause

**Cheat Sheet Reference:** Q9, Q14, Q19

**Practice Tip:** Show calm, systematic approach. Interviewers want to see you don't panic under pressure.

---

### H3: How would you scale this architecture globally? What changes for multi-region?
**Expected Answer Time:** 5-6 minutes
**Multi-Region Design:**

**Architecture Changes:**
1. **Regional TGWs:** One TGW per region (us-east-1, us-west-2, eu-west-1)
2. **Regional Gateways:** Each region has 2+ ground gateways (local redundancy)
3. **Inter-Region Connectivity:** TGW Peering between regions (for cross-region traffic if needed)
4. **User Steering:** Route 53 latency or geolocation routing to nearest region
5. **Regional Isolation:** Each region operates independently
   - Regional control plane (Prometheus, Grafana, Alertmanager per region)
   - Regional data plane (user traffic stays in-region when possible)
   - Failure isolation: Region failure doesn't cascade to other regions

**Trade-offs:**
- **Cost:** 3× TGWs, 6× gateways vs single region—but necessary for global scale and resilience
- **Data Transfer:** Cross-region data transfer costs ($0.02/GB)—keep traffic regional when possible
- **Latency:** Regional routing minimizes latency (user in EU → EU gateway → EU TGW → EU VPC)
- **Compliance:** Geolocation routing ensures EU user data stays in EU (GDPR compliance)

**Failure Scenarios:**
- **Gateway failure:** Regional failover (2 gateways per region)
- **Region failure:** Route 53 fails over to next-nearest region
- **Total failover time:** ~2-3 minutes (BGP + DNS propagation)

**Monitoring:**
- **Global dashboard:** Overview of all regions, overall health
- **Regional dashboards:** Deep dive per region (avoid cross-region dependencies)
- **SLO:** 99.99% global availability (allows one region down without violating SLO)

**Cheat Sheet Reference:** Q13

**Practice Tip:** Reference your Lab 12 if you completed it. If not, explain you'd build it the same way as dual-gateway but replicated across regions.

---

### H4: You notice BGP routes are taking a suboptimal path (traffic going from us-east-1 to us-west-2 to reach a destination that's directly connected to us-east-1). How do you troubleshoot and fix this?
**Expected Answer Time:** 5-6 minutes
**Troubleshooting BGP Routing:**

**1. Understand Current State:**
- `show ip bgp` on gateway routers—look at AS-PATH and local-preference for the destination prefix
- `show ip route`—which route is installed in routing table?
- Traceroute from source to destination—confirm the path

**2. Identify Why Path is Suboptimal:**
- **AS-PATH length:** Longer path through us-west-2? (BGP prefers shortest AS-PATH)
- **Local-preference:** Is us-west-2 path marked higher local-pref? (Local-pref overrides AS-PATH)
- **MED (Multi-Exit Discriminator):** Is us-west-2 path preferred due to lower MED?
- **Communities:** Did someone tag the direct path with a deprioritization community?
- **Prefix specificity:** Is us-west-2 advertising a more specific prefix (longer match wins)?

**3. Fix (depends on root cause):**
- **If AS-PATH issue:** Prepend AS-PATH on us-west-2 advertisement to make it less preferred
- **If local-pref issue:** Set higher local-pref on us-east-1 path (e.g., 200 vs 100)
- **If communities:** Update route-map to not lower preference based on community
- **If prefix specificity:** Can't change (longer match always wins)—may need to route accordingly

**4. Apply Change Safely:**
- Test on one router first
- Monitor traffic shift (watch flow logs, CloudWatch metrics)
- Verify no dropped packets or blackholing
- Apply to remaining routers
- Document change in ticket and runbook

**5. Long-term Prevention:**
- Document BGP policy clearly (which paths should be preferred, why)
- Add monitoring for suboptimal paths (alert if traffic exits region unexpectedly)
- Regular BGP route audits (monthly review of routing tables)

**Cheat Sheet Reference:** Q9, Lab 14 (BGP TE)

**Practice Tip:** Show you understand BGP path selection algorithm: (1) Highest local-pref, (2) Shortest AS-PATH, (3) Lowest origin, (4) Lowest MED, (5) eBGP over iBGP, (6) Lowest IGP cost, (7) Lowest router ID.

---

### H5: Walk me through how you would implement SLOs for the Kuiper ground gateway.
**Expected Answer Time:** 6-8 minutes
**SLO Implementation:**

**1. Define SLIs (Service Level Indicators):**
- **Availability:** Successful synthetic probes / total synthetic probes (per minute)
- **Latency:** P95 end-to-end latency for HTTP probes through gateway (target: <50ms)
- **Error Rate:** Failed requests / total requests (target: <0.1%)

**2. Set SLO Targets:**
- **Availability:** 99.9% (43.8 minutes downtime allowed per month)
- **Latency:** P95 <50ms (95% of requests faster than 50ms)
- **Error Rate:** <0.1% (999 successful per 1000 requests)

**3. Calculate Error Budget:**
- 99.9% SLO = 0.1% error budget
- Per month: 43,200 minutes × 0.001 = 43.8 minutes of downtime allowed
- Per day: 1,440 minutes × 0.001 = 1.44 minutes/day
- If we spend error budget too fast (burn rate), page on-call immediately

**4. Implement Measurements:**
- **Synthetic Probes:** Blackbox exporter or Lambda functions probing gateway every 30s
  - ICMP ping (network reachability)
  - HTTP GET /health (application health)
  - Record success/failure, latency
- **Prometheus Recording Rules:**
  ```yaml
  - record: sli:availability:ratio
    expr: sum(rate(probe_success[5m])) / sum(rate(probe_total[5m]))
  - record: sli:latency:p95
    expr: histogram_quantile(0.95, rate(probe_duration_seconds_bucket[5m]))
  ```

**5. Create Burn Rate Alerts:**
- **Fast burn (1 hour window):** If we burn >5% of monthly budget in 1 hour → page (critical)
- **Slow burn (24 hour window):** If we burn >10% of monthly budget in 24 hours → warning
- This catches both sudden outages and gradual degradation

**6. Dashboard:**
- Current SLO status (green/yellow/red)
- Error budget remaining (e.g., "28.3 minutes remaining this month")
- Burn rate graph (are we burning faster than sustainable?)
- SLI measurements (availability %, P95 latency)

**7. Weekly SLO Review:**
- Generate report: Did we meet SLOs? If not, why?
- Postmortem for SLO violations
- Action items to prevent recurrence

**8. Use Error Budget for Decision Making:**
- Error budget healthy (90%+ remaining) → Can take risks, deploy aggressively
- Error budget low (<50% remaining) → Freeze risky changes, focus on reliability
- Error budget exhausted → ONLY reliability fixes, no new features

**Cheat Sheet Reference:** Q20, Lab 15, Glossary (SLI/SLO/SLA)

**Practice Tip:** This shows SRE maturity. Reference Google SRE book if you've read it.

---

## BEHAVIORAL Questions (STAR Method: Situation, Task, Action, Result)

### B1: Tell me about a time you had to troubleshoot a complex technical issue. How did you approach it?
**Expected Answer Time:** 4-5 minutes
**STAR Structure:**

**Situation (30 seconds):**
- "In my homelab, I was building a Site-to-Site VPN with BGP to AWS. The VPN tunnels came up, but BGP sessions wouldn't establish."

**Task (30 seconds):**
- "I needed to diagnose why BGP wasn't working and get the sessions established so routes could be exchanged."

**Action (2-3 minutes):**
- "I took a systematic approach:
  1. First, verified tunnel state was UP in both AWS console and customer gateway logs—confirmed tunnels healthy
  2. Checked if TCP port 179 was allowed in firewall rules—initially found firewall blocking BGP
  3. Added firewall rules allowing TCP 179 bidirectionally
  4. BGP still didn't establish—checked BGP configuration on customer gateway
  5. Found ASN mismatch: I'd configured ASN 65000 on customer gateway but AWS was expecting 65001
  6. Corrected ASN in Terraform code, applied changes, redeployed VPN connection
  7. BGP sessions immediately established, verified with `show ip bgp summary`
  8. Validated routes being exchanged with `show ip bgp` and `show ip route`"

**Result (30 seconds):**
- "BGP sessions came up successfully, routes exchanged, and I could ping across the VPN connection. I documented the troubleshooting steps in my project README so I wouldn't make the same ASN mistake again. The whole process taught me to be methodical: check one layer at a time (tunnel → firewall → configuration → protocol state)."

**Practice Tip:** Use REAL examples from your labs. They're authentic and you can speak confidently about them.

---

### B2: Describe a time when you had to learn a new technology quickly. How did you approach it?
**Expected Answer Time:** 3-4 minutes
**Example Answer:**

**Situation:**
- "I needed to learn AWS networking and BGP for this Kuiper interview prep, and I had limited experience with both."

**Task:**
- "I had 2 weeks to become proficient enough to discuss these topics confidently in an interview."

**Action:**
- "I created a structured learning plan:
  1. Started with fundamentals: AWS documentation, VPC basics, networking concepts
  2. Built hands-on labs progressively: VPC → Transit Gateway → VPN → BGP
  3. Used the Feynman technique: Forced myself to explain each concept simply, which revealed gaps in understanding
  4. Documented everything: Created a cheat sheet, glossary, and lab evidence as I went
  5. Built muscle memory through repetition: Deployed and tore down infrastructure multiple times
  6. Tested myself: Chaos engineering to validate my understanding (intentionally broke things to see if I could troubleshoot)"

**Result:**
- "In 2 weeks, I completed 8 hands-on labs covering VPC, Transit Gateway, VPN with BGP, Route 53, mTLS, monitoring, dual-gateway failover, and chaos testing. I now have a portfolio demonstrating these skills, and I can explain these concepts clearly. The systematic approach worked—I could apply the same method to any new technology."

**Practice Tip:** This is basically describing your 2-week learning path. It shows self-directed learning and discipline.

---

### B3: Tell me about a time you made a mistake. How did you handle it?
**Expected Answer Time:** 3-4 minutes
**Example Answer (from your homelab or adapt):**

**Situation:**
- "While configuring BGP over VPN in my homelab, I accidentally fat-fingered a route-map and prepended AS-PATH way too much (5 times instead of once). This made the backup VPN tunnel path so unattractive that even when I shut down the primary tunnel for testing, traffic still preferred the broken primary path over the healthy backup."

**Task:**
- "I needed to identify my mistake, fix it, and make sure I wouldn't make the same error again."

**Action:**
- "First, I admitted the mistake to myself—easy in a homelab, but important practice for production!
- I reviewed the BGP route table (`show ip bgp`) and immediately saw the issue: AS-PATH was prepended 5 times
- Checked my Terraform code and found the typo: `prepend 5` instead of `prepend 1`
- Fixed the code, applied the change, verified BGP routes corrected
- Tested failover again—this time backup path worked perfectly
- Updated my change process: Now I always `terraform plan` twice and have someone (or at least future me next day) review before applying
- Added comments in code explaining the intent (e.g., `# Prepend once to make backup slightly less preferred`)"

**Result:**
- "The failover worked correctly after the fix. More importantly, I learned to slow down during configuration changes—taking an extra 2 minutes to review prevents hours of troubleshooting. I also implemented a personal peer review process even for homelab changes, which is a habit I'd bring to production environments."

**Practice Tip:** Show you learn from mistakes and implement processes to prevent recurrence. Don't blame others.

---

### B4: Tell me about a time you had to make a decision with incomplete information.
**Expected Answer Time:** 3-4 minutes
**Example Answer:**

**Situation:**
- "When designing my dual-gateway architecture lab, I didn't have real Kuiper ground gateway specifications (hardware, throughput, failover requirements). I had to make design decisions based on limited public information."

**Task:**
- "I needed to create a realistic architecture that would demonstrate understanding of HA principles without knowing exact requirements."

**Action:**
- "I made reasonable assumptions based on industry standards and documented them:
  - Assumed 10 Gbps throughput per gateway (based on typical LEO satellite gateway specs)
  - Assumed 99.9% availability SLO (industry standard for consumer broadband)
  - Assumed failover time budget of 2 minutes (BGP convergence + DNS TTL)
- I designed the architecture to be flexible: parameterized values in Terraform so they could easily change
- I explicitly documented my assumptions in the README and ADR (Architecture Decision Record)
- I asked clarifying questions in the design document: 'If real requirements differ, what would change?'"

**Result:**
- "The architecture I built was sound for the assumed requirements. More importantly, I demonstrated a key skill: making progress despite uncertainty by stating assumptions clearly, documenting decisions, and building flexibility to adapt when more information becomes available. In an interview or real project, I'd ask clarifying questions early to reduce unknowns."

**Practice Tip:** Amazon loves "Bias for Action"—show you don't get paralyzed by lack of perfect information.

---

### B5: How do you prioritize multiple urgent tasks?
**Expected Answer Time:** 2-3 minutes
**Framework-Based Answer:**

**Approach:**
- "I use a combination of impact, urgency, and dependencies to prioritize:
  1. **Critical + Immediate:** User-facing outage → top priority (e.g., both VPN tunnels down, users impacted)
  2. **High Impact + Soon:** Degraded service, automatic failover working but at risk (e.g., one tunnel down, users not impacted yet)
  3. **Low Impact + Urgent:** Monitoring alerts, non-user-facing issues (e.g., certificate expiring in 7 days)
  4. **Low Impact + Not Urgent:** Improvements, optimization (e.g., refactor Terraform modules)

**Example:**
- "If I'm paged for 'VPN tunnel down' (P2—degraded, no user impact) while working on certificate rotation due tomorrow, I'd:
  - Quickly assess VPN tunnel: Is failover working? Users impacted? If no user impact and automatic failover functioning, this is P2
  - Continue certificate rotation (prevents P1 outage tomorrow)—finish it
  - Then address VPN tunnel (root cause fix so we're not running degraded)
- However, if VPN tunnel escalates (second tunnel shows signs of instability, risk of full outage), it immediately becomes P1 and I'd escalate certificate rotation to a colleague or pause it."

**Key Principle:**
- "Always prioritize user impact first, then risk of escalation, then future risk. Communicate trade-offs transparently: 'I'm fixing X first because of Y; Z will be addressed in N hours.'"

**Practice Tip:** Shows you're level-headed and analytical. Amazon's "Deliver Results" + "Customer Obsession."

---

## Practice Schedule

**Week 1 (During Labs):**
- Day 1-3: Easy questions E1-E5 (15 min/day)
- Day 4-6: Medium questions M1-M3 (20 min/day)
- Day 7: Review E1-E5 and M1-M3

**Week 2 (During Labs):**
- Day 8-10: Medium questions M4-M6 (20 min/day)
- Day 11-12: Hard questions H1-H3 (30 min/day)
- Day 13: Hard questions H4-H5 + Behavioral B1-B3 (40 min)
- Day 14: Full mock interview (all question types, 90 minutes)

---

## Mock Interview Structure (Day 14)

**Total Time: 90 minutes**

1. **Introduction (5 min):**
   - "Tell me about yourself"
   - "Why Kuiper? Why this role?"

2. **Technical Deep Dive (40 min):**
   - 2 Easy questions (10 min)
   - 3 Medium questions (20 min)
   - 2 Hard questions (15 min)

3. **Behavioral (30 min):**
   - 4-5 behavioral questions using STAR method

4. **Your Questions for Interviewer (10 min):**
   - Prepare 5-7 thoughtful questions (see below)

5. **Wrap-Up (5 min):**
   - Thank interviewer, timeline, next steps

---

## Questions to Ask the Interviewer

**About the Role:**
1. "What does a typical day look like for a Sys/NetAdmin on the Kuiper ground team?"
2. "What's the biggest technical challenge the team is facing right now?"
3. "How is success measured for this role in the first 6 months?"

**About the Team:**
4. "Can you tell me about the team structure? Who would I work most closely with?"
5. "How does the team handle on-call rotations and incident response?"
6. "What's the team's approach to professional development and learning new technologies?"

**About the Technology:**
7. "What's the ground gateway tech stack? (Vendors, automation tools, monitoring platforms?)"
8. "How mature is the infrastructure? Am I building greenfield or improving existing systems?"
9. "What's the deployment cadence? How often do network changes go out?"

**About the Company/Project:**
10. "What's the timeline for Kuiper's full deployment?"
11. "How does the ground team collaborate with the satellite engineering and AWS teams?"

**Red Flag Checks (ask diplomatically):**
12. "What do people who struggle in this role have in common?" (Tells you what NOT to do)
13. "Why is this position open?" (New headcount = growth, backfill = ask why person left)

---

## Final Tips

**During the Interview:**
- ✅ Think aloud (show your reasoning)
- ✅ Ask clarifying questions (shows you gather requirements)
- ✅ Draw diagrams (visual communication)
- ✅ Admit if you don't know something, then show how you'd figure it out
- ✅ Reference your portfolio/labs naturally ("In my homelab, I built...")
- ✅ Be enthusiastic—show you're excited about the role and technology

**Don't:**
- ❌ Ramble—stay concise (2-5 min answers)
- ❌ Memorize answers word-for-word (sounds robotic)
- ❌ Bad-mouth previous employers or technologies
- ❌ Pretend to know something you don't (gets exposed quickly)
- ❌ Go silent for 30+ seconds (think aloud instead)

---

**You're ready! Remember: The interview is a two-way conversation. They're evaluating you, and you're evaluating them. Be confident in your skills—you've built real things in your portfolio, and that speaks volumes. Good luck! 🚀**

---

**Last Updated:** 2025-11-10
**Document:** professional/interview-prep/kuiper/warm-ups/INTERVIEW-WARMUP.md

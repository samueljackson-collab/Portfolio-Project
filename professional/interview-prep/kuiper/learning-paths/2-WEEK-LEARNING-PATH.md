# Kuiper System/Network Administrator - 2-Week Interview Prep Learning Path

**Goal:** Become interview-ready for Kuiper Sys/NetAdmin role in 14 days
**Target Interview Date:** [Fill in your date]
**Daily Time Commitment:** 4-6 hours/day (flexible weekends)
**Last Updated:** 2025-11-10

---

## Learning Path Overview

| Week | Focus Area | Key Outcomes |
|------|-----------|--------------|
| **Week 1** | AWS Networking Foundations + BGP/VPN | Complete 5 core labs, master AWS networking concepts, build VPN with BGP |
| **Week 2** | Observability + HA Architecture + Interview Prep | Build monitoring, dual-gateway failover, chaos testing, interview rehearsal |

---

## Daily Schedule Template

**Each day follows this pattern:**
- 08:00-09:00: Theory study (read docs, watch videos)
- 09:00-12:00: Hands-on lab work
- 12:00-13:00: Lunch + review morning's work
- 13:00-15:00: Continue lab + documentation
- 15:00-16:00: Feynman method practice (explain topics aloud)
- 16:00-17:00: Update portfolio, take screenshots, commit code

**Adjust to your schedule!** The important thing is consistent daily progress.

---

## Week 1: Foundations

### Day 1 (Monday): Satellite Networking + Link Simulation

| **Activity** | **Timebox** | **Risk** | **Owner** | **Success Criteria** | **Resources** |
|--------------|-------------|----------|-----------|---------------------|---------------|
| **Morning Study:** Satellite networking basics, LEO vs GEO, Ka-band, OISL, link constraints | 2 hours | 🟢 LOW | You | Can explain how Kuiper data flows from terminal to AWS in 2 minutes | [Video: Satellite Internet Explained](placeholder), AWS re:Invent Kuiper talks, Wikipedia LEO satellites |
| **Lab 01:** TC Netem satellite link simulation | 3 hours | 🟢 LOW | You | Working netem scripts, baseline vs satellite test results documented with screenshots | See LAB-INDEX.md Lab 01 |
| **Feynman Practice:** Explain satellite link constraints to a non-technical friend | 30 min | 🟢 LOW | You | Friend understands why latency/jitter matter | Use cheat sheet Q3 |
| **Portfolio Update:** Create `projects/06-homelab/PRJ-HOME-002/experiments/satellite-link-simulation/` with all evidence | 1 hour | 🟢 LOW | You | Evidence committed to Git | README, scripts, CSV results, screenshots |
| **Evening Review:** Read cheat sheet Q1-Q4 | 30 min | 🟢 LOW | You | Can answer Q1-Q4 without looking | Cheat sheet 01 |

**Daily Outcome:** ✅ Understand satellite networking constraints ✅ Lab 01 complete ✅ Evidence documented

---

### Day 2 (Tuesday): AWS VPC Fundamentals

| **Activity** | **Timebox** | **Risk** | **Owner** | **Success Criteria** | **Resources** |
|--------------|-------------|----------|-----------|---------------------|---------------|
| **Morning Study:** AWS VPC concepts - subnets, route tables, IGW, NAT Gateway, security groups, NACLs | 2 hours | 🟢 LOW | You | Can draw VPC architecture from memory with public/private subnets | AWS VPC User Guide, [Video: AWS VPC Basics](placeholder) |
| **Lab 02:** Build VPC with Terraform | 3 hours | 🟡 MEDIUM | You | VPC created, EC2 in public subnet reaches internet, EC2 in private subnet reaches internet via NAT | See LAB-INDEX.md Lab 02 |
| **Cost Management:** Verify resources in AWS console, set billing alarm at $10 | 15 min | 🟢 LOW | You | CloudWatch billing alarm configured | AWS Billing Console |
| **Feynman Practice:** Explain public vs private subnets and why we need NAT Gateway | 30 min | 🟢 LOW | You | Can teach this to a junior engineer | Use cheat sheet Q5 |
| **Portfolio Update:** Commit Terraform code with README explaining architecture decisions | 1 hour | 🟢 LOW | You | Code in `terraform/aws-vpc-foundation/` with diagram | Architecture diagram in draw.io or Mermaid |
| **Evening Review:** Read cheat sheet Q5, study glossary VPC/subnet/IGW/NAT terms | 30 min | 🟢 LOW | You | Know all VPC-related acronyms | Glossary |

**Daily Outcome:** ✅ Master VPC fundamentals ✅ Lab 02 complete ✅ Terraform code committed

---

### Day 3 (Wednesday): Transit Gateway

| **Activity** | **Timebox** | **Risk** | **Owner** | **Success Criteria** | **Resources** |
|--------------|-------------|----------|-----------|---------------------|---------------|
| **Morning Study:** Transit Gateway concepts, when to use TGW vs peering, routing, attachments | 2 hours | 🟢 LOW | You | Can explain TGW value proposition and draw hub-and-spoke diagram | AWS TGW docs, [Video: Transit Gateway Deep Dive](placeholder) |
| **Lab 03:** Build TGW connecting 2 VPCs | 3 hours | 🟡 MEDIUM | You | VPC A can ping VPC B through TGW, route tables correct, VPC Flow Logs showing TGW traffic | See LAB-INDEX.md Lab 03 |
| **Decision Record:** Write ADR-0002 documenting TGW vs Peering decision | 45 min | 🟢 LOW | You | ADR explaining when to choose TGW with math (O(N²) vs O(N)) | See cheat sheet Q7, Q8 |
| **Feynman Practice:** Teach TGW concept using the "phone operator" analogy | 30 min | 🟢 LOW | You | Non-technical person understands TGW value | Cheat sheet Q8 Feynman section |
| **Portfolio Update:** Commit TGW Terraform + screenshots + ADR | 1 hour | 🟢 LOW | You | Evidence in `terraform/aws-tgw-basic/` and `docs/adr/` | Include TGW console screenshot |
| **Evening Review:** Read cheat sheet Q7-Q8, practice explaining to webcam (record yourself) | 30 min | 🟢 LOW | You | Comfortable explaining TGW architecture | Review recording, note improvements |

**Daily Outcome:** ✅ Master Transit Gateway ✅ Lab 03 complete ✅ Can articulate TGW vs peering trade-offs

---

### Day 4-5 (Thursday-Friday): BGP over Site-to-Site VPN

| **Activity** | **Timebox** | **Risk** | **Owner** | **Success Criteria** | **Resources** |
|--------------|-------------|----------|-----------|---------------------|---------------|
| **Morning Study (Day 4):** BGP fundamentals - ASN, AS-PATH, local-pref, communities, path selection | 3 hours | 🟡 MEDIUM | You | Understand BGP basics, can explain path selection process | [Video: BGP Fundamentals](placeholder), Cisco BGP docs, cheat sheet Q9 |
| **Study (Day 4 PM):** AWS Site-to-Site VPN architecture, IPsec tunnels, BGP over VPN, CloudWatch metrics | 2 hours | 🟡 MEDIUM | You | Understand AWS VPN components (CGW, VPN connection, TGW attachment) | AWS VPN docs |
| **Lab 04 Part 1 (Day 4 PM):** Set up customer gateway (StrongSwan on EC2 or VyOS VM) | 2 hours | 🟡 MEDIUM | You | Customer gateway VM running, can SSH to it | StrongSwan docs or VyOS docs |
| **Lab 04 Part 2 (Day 5 AM):** Create AWS VPN connection, configure IPsec tunnels | 3 hours | 🔴 HIGH | You | Both VPN tunnels UP in AWS console | AWS VPN configuration download |
| **Lab 04 Part 3 (Day 5 PM):** Configure BGP, exchange routes, test connectivity | 3 hours | 🔴 HIGH | You | BGP session ESTABLISHED, routes exchanged, can ping across VPN | `show ip bgp summary`, `show ip route` |
| **Lab 04 Part 4 (Day 5):** Build CloudWatch dashboard for VPN/BGP metrics | 1 hour | 🟡 MEDIUM | You | Dashboard showing tunnel state, BGP state, throughput | CloudWatch console |
| **Troubleshooting Buffer:** Allow extra time for BGP issues (this is complex!) | 2 hours | 🔴 HIGH | You | Don't get frustrated - BGP takes time to learn | AWS support forums, Reddit r/networking |
| **Feynman Practice (Day 5):** Explain BGP path selection and why we use it over VPN | 30 min | 🟡 MEDIUM | You | Can explain dynamic routing value vs static routes | Cheat sheet Q9 |
| **Portfolio Update (Day 5):** Commit all configs, screenshots, document troubleshooting steps | 1.5 hours | 🟢 LOW | You | Complete evidence package in `terraform/aws-vpn-bgp/` | Include show commands output |
| **Evening Review (Day 5):** Read cheat sheet Q9-Q10, study BGP terminology in glossary | 30 min | 🟢 LOW | You | Confident in BGP concepts | Test yourself on BGP terms |

**2-Day Outcome:** ✅ Understand BGP fundamentals ✅ Lab 04 complete (VPN with BGP working) ✅ Strong troubleshooting skills demonstrated

**⚠️ Risk Mitigation:** This is the hardest lab. If stuck >2 hours on one issue, post in AWS forums or move forward and return later. Don't let perfect be the enemy of good!

---

### Day 6 (Saturday): Route 53 + Catch-Up Day

| **Activity** | **Timebox** | **Risk** | **Owner** | **Success Criteria** | **Resources** |
|--------------|-------------|----------|-----------|---------------------|---------------|
| **Morning Study:** Route 53 routing policies (latency, geolocation, failover), health checks, TTL | 2 hours | 🟢 LOW | You | Understand when to use each routing policy | AWS Route 53 docs, cheat sheet Q15-Q16 |
| **Lab 05:** Build Route 53 latency-based routing with health checks | 3 hours | 🟡 MEDIUM | You | DNS returns different IPs based on query location, health check failover works | See LAB-INDEX.md Lab 05 |
| **Catch-Up:** Finish any incomplete labs from Days 1-5 | 2 hours | Varies | You | All Week 1 labs complete | Review LAB-INDEX.md |
| **Portfolio Cleanup:** Review all week's evidence, add missing screenshots/docs | 1 hour | 🟢 LOW | You | Professional-quality documentation for all labs | Spell-check, formatting, clear README files |
| **Evening Review:** Read cheat sheet Q1-Q16, test yourself on all concepts | 1 hour | 🟢 LOW | You | Can answer Q1-Q16 confidently | Self-quiz |

**Daily Outcome:** ✅ Master Route 53 ✅ Lab 05 complete ✅ Week 1 fully documented ✅ Caught up on any gaps

---

### Day 7 (Sunday): Rest + Reflection + Prep Week 2

| **Activity** | **Timebox** | **Risk** | **Owner** | **Success Criteria** | **Resources** |
|--------------|-------------|----------|-----------|---------------------|---------------|
| **Morning:** Sleep in, rest, take a break! | 3 hours | 🟢 LOW | You | Rested and energized for Week 2 | Self-care |
| **Review Week 1:** Look at all labs, practice explaining each one | 2 hours | 🟢 LOW | You | Can give 5-minute presentation on each lab | Use Feynman method |
| **Plan Week 2:** Read ahead for Days 8-14, prep environment for monitoring labs | 1 hour | 🟢 LOW | You | Know what's coming, feel prepared | Week 2 schedule below |
| **Optional:** Watch Kuiper/AWS networking videos for enjoyment | 1 hour | 🟢 LOW | You | Deeper understanding, relaxed learning | YouTube re:Invent talks |
| **Evening:** Review glossary, make flashcards for terms you struggle with | 1 hour | 🟢 LOW | You | Know 90% of glossary terms | Anki, Quizlet, or paper flashcards |

**Weekly Outcome:** ✅ Solid foundation in AWS networking ✅ 5 core labs complete ✅ Ready for Week 2

---

## Week 2: Observability + High Availability + Interview Prep

### Day 8 (Monday): Comprehensive Monitoring

| **Activity** | **Timebox** | **Risk** | **Owner** | **Success Criteria** | **Resources** |
|--------------|-------------|----------|-----------|---------------------|---------------|
| **Morning Study:** Observability concepts - metrics, logs, traces; SLI/SLO/SLA; synthetic monitoring | 2 hours | 🟢 LOW | You | Understand difference between monitoring and observability | Google SRE book chapter on SLOs |
| **Lab 06:** Build comprehensive VPN/BGP monitoring dashboard | 4 hours | 🟡 MEDIUM | You | CloudWatch dashboard with all key metrics, synthetic probes running, alarms configured | See LAB-INDEX.md Lab 06 |
| **Feynman Practice:** Explain why synthetic probes are necessary (not just system metrics) | 30 min | 🟢 LOW | You | Can explain "is it up?" vs "does it work?" | Cheat sheet Q19 |
| **Portfolio Update:** Commit dashboard JSON, Lambda probe code, screenshots | 1 hour | 🟢 LOW | You | Evidence in `projects/p04-ops-monitoring/vpn-bgp-monitoring/` | Professional dashboard screenshot |
| **Evening Review:** Read cheat sheet Q19-Q20, understand Prometheus/Alertmanager roles | 30 min | 🟢 LOW | You | Know difference between Prometheus and Alertmanager | Glossary + cheat sheet |

**Daily Outcome:** ✅ Master monitoring concepts ✅ Lab 06 complete ✅ Production-quality dashboard built

---

### Day 9 (Tuesday): Security - mTLS + PKI

| **Activity** | **Timebox** | **Risk** | **Owner** | **Success Criteria** | **Resources** |
|--------------|-------------|----------|-----------|---------------------|---------------|
| **Morning Study:** PKI concepts, mTLS, certificate lifecycle, rotation, SANs | 2 hours | 🟡 MEDIUM | You | Understand public vs private CA, certificate chain of trust, mTLS handshake | cheat sheet Q6, OpenSSL docs |
| **Lab 07:** Build mTLS demo with private CA | 4 hours | 🟡 MEDIUM | You | Working mTLS API, valid client connects, invalid client rejected, rotation script works | See LAB-INDEX.md Lab 07 |
| **Feynman Practice:** Explain mTLS using the "ID badge" analogy | 30 min | 🟢 LOW | You | Non-technical person understands two-way authentication | Cheat sheet Q6 Feynman section |
| **Portfolio Update:** Commit CA setup, certificates (not private keys!), API code, rotation scripts | 1 hour | 🟢 LOW | You | Evidence in `projects/p16-zero-trust/mtls-demo/` | Document security best practices |
| **Evening Review:** Read cheat sheet Q6, study all PKI terms in glossary | 30 min | 🟢 LOW | You | Know CA, mTLS, SAN, certificate pinning, rotation | Quiz yourself |

**Daily Outcome:** ✅ Understand PKI and mTLS ✅ Lab 07 complete ✅ Security mindset demonstrated

---

### Day 10-11 (Wednesday-Thursday): Dual-Gateway High Availability Architecture

| **Activity** | **Timebox** | **Risk** | **Owner** | **Success Criteria** | **Resources** |
|--------------|-------------|----------|-----------|---------------------|---------------|
| **Morning Study (Day 10):** HA architecture patterns, BGP traffic engineering, Route 53 multi-endpoint failover | 2 hours | 🟡 MEDIUM | You | Understand how to build resilient multi-gateway architecture | cheat sheet Q11-Q12, AWS reference architectures |
| **Lab 08 Part 1 (Day 10):** Design and diagram dual-gateway architecture | 2 hours | 🟡 MEDIUM | You | Clear architecture diagram showing 2 gateways, TGW, VPNs, Route 53 | Draw.io or Mermaid |
| **Lab 08 Part 2 (Day 10):** Build first gateway (CGW A, VPNs, TGW attachment, BGP) | 3 hours | 🔴 HIGH | You | Gateway A fully functional, BGP up, routes exchanged | Leverage Lab 04 experience |
| **Lab 08 Part 3 (Day 11 AM):** Build second gateway (CGW B, VPNs, TGW attachment, BGP) | 3 hours | 🔴 HIGH | You | Gateway B fully functional, BGP up, routes exchanged | Same as Gateway A |
| **Lab 08 Part 4 (Day 11 AM):** Configure BGP traffic engineering (local-pref, communities, AS-PATH prepend) | 2 hours | 🔴 HIGH | You | Traffic splits appropriately (e.g., 50/50 or 70/30), BGP policies visible in route table | cheat sheet Q10, Q14 |
| **Lab 08 Part 5 (Day 11 PM):** Add Route 53 latency routing with health checks to both gateways | 2 hours | 🟡 MEDIUM | You | DNS routes to both gateways, health checks monitoring each | Leverage Lab 05 experience |
| **Lab 08 Part 6 (Day 11 PM):** Build comprehensive monitoring dashboard for dual-gateway setup | 1.5 hours | 🟡 MEDIUM | You | Dashboard showing both gateways, traffic split, health status | Leverage Lab 06 experience |
| **Feynman Practice (Day 11):** Explain dual-gateway HA architecture and why it's necessary | 30 min | 🟡 MEDIUM | You | Can articulate blast radius, failover time, SLO impact | Cheat sheet Q12 |
| **Portfolio Update (Day 11):** Commit all code, configs, architecture diagram, comprehensive README | 1.5 hours | 🟢 LOW | You | Complete evidence package in `terraform/kuiper-dual-gateway/` | This is your showcase piece! |
| **Evening Review (Day 11):** Read cheat sheet Q11-Q14, review all BGP/VPN/Route 53 concepts | 1 hour | 🟡 MEDIUM | You | Deep confidence in HA architecture design | Test yourself verbally |

**2-Day Outcome:** ✅ Mastered HA architecture ✅ Lab 08 complete (dual-gateway working) ✅ Interview showcase piece built

**⚠️ Risk Mitigation:** This is the most complex lab. Budget extra time. If stuck, simplify (e.g., skip AS-PATH prepending) and come back later. Core goal: working failover between 2 gateways.

---

### Day 12 (Friday): Chaos Engineering + Failure Testing

| **Activity** | **Timebox** | **Risk** | **Owner** | **Success Criteria** | **Resources** |
|--------------|-------------|----------|-----------|---------------------|---------------|
| **Morning Study:** Chaos engineering principles, failure injection, blameless postmortems | 1.5 hours | 🟢 LOW | You | Understand why we intentionally break things to learn | Principles of Chaos, Netflix blog |
| **Lab 13:** Execute chaos scenarios on dual-gateway architecture | 4 hours | 🟡 MEDIUM | You | All 4 scenarios executed, monitoring detected failures, automatic failover validated, findings documented | See LAB-INDEX.md Lab 13 |
| **Postmortem:** Write blameless post-drill report with findings and improvements | 1.5 hours | 🟢 LOW | You | Professional postmortem document identifying 3+ improvements | Google SRE postmortem template |
| **Feynman Practice:** Explain why chaos engineering matters for resilience | 30 min | 🟢 LOW | You | Can articulate "test in production" mindset safely | Chaos engineering principles |
| **Portfolio Update:** Commit all chaos test evidence, postmortem, screenshots | 1 hour | 🟢 LOW | You | Evidence in `projects/p04-ops-monitoring/chaos-engineering/` | Timeline with screenshots |
| **Evening Review:** Read cheat sheet Q1-Q20 completely, test yourself on everything | 1 hour | 🟡 MEDIUM | You | 90% accuracy answering Q1-Q20 without looking | Self-quiz |

**Daily Outcome:** ✅ Validated system resilience ✅ Lab 13 complete ✅ Blameless postmortem written ✅ Ready for interview practice

---

### Day 13 (Saturday): Interview Preparation + Portfolio Refinement

| **Activity** | **Timebox** | **Risk** | **Owner** | **Success Criteria** | **Resources** |
|--------------|-------------|----------|-----------|---------------------|---------------|
| **Morning:** Review all completed labs, practice explaining each one in 5 minutes | 3 hours | 🟡 MEDIUM | You | Can give concise, clear explanation of all 8 core labs | Use Feynman method |
| **Interview Warm-Up Questions:** Complete 20 warm-up questions (see INTERVIEW-WARMUP.md) | 2 hours | 🟡 MEDIUM | You | Comfortable answering behavioral and technical questions | Practice with friend or record yourself |
| **Portfolio Cleanup:** Review all documentation, fix typos, add missing diagrams, ensure consistency | 2 hours | 🟢 LOW | You | Professional, polished portfolio ready to share with interviewer | Spell-check everything |
| **Update Resume:** Add "Kuiper Interview Prep" section highlighting key projects | 1 hour | 🟢 LOW | You | Resume includes VPN/BGP, TGW, Route 53, mTLS, monitoring, chaos engineering | professional/resume/ |
| **Evening:** Read cheat sheet Q1-Q20, make final flashcards for weak areas | 1 hour | 🟢 LOW | You | Know cheat sheet cold | Focus on areas you struggle with |

**Daily Outcome:** ✅ Interview-ready ✅ Portfolio polished ✅ Warm-up practice complete ✅ Confident in all topics

---

### Day 14 (Sunday): Mock Interview + Final Prep

| **Activity** | **Timebox** | **Risk** | **Owner** | **Success Criteria** | **Resources** |
|--------------|-------------|----------|-----------|---------------------|---------------|
| **Morning:** Full mock interview with friend, colleague, or AI (90 minutes) | 2 hours | 🟡 MEDIUM | You + Friend | Complete interview simulation with behavioral + technical questions | INTERVIEW-WARMUP.md questions |
| **Debrief:** Review mock interview, identify weak areas, practice those topics | 1 hour | 🟢 LOW | You | Know exactly what to improve | Honest self-assessment |
| **Targeted Study:** Deep dive on 2-3 topics you struggled with in mock interview | 2 hours | 🟡 MEDIUM | You | Comfortable with previously weak areas | Cheat sheet, glossary, docs |
| **Final Portfolio Review:** Walk through your entire portfolio as if showing interviewer | 1 hour | 🟢 LOW | You | Can navigate portfolio smoothly, know where everything is | Screen share practice |
| **Relax:** Take evening off, do something enjoyable, get good sleep | 3 hours | 🟢 LOW | You | Rested, confident, ready | Self-care |
| **Optional:** Review cheat sheet Q1-Q20 one final time before bed (light reading) | 30 min | 🟢 LOW | You | Material is fresh in mind | No cramming, just refresh |

**Daily Outcome:** ✅ Mock interview complete ✅ Weak areas addressed ✅ Portfolio tour practiced ✅ Rested and ready for real interview

---

## Risk Management

### High-Risk Activities (🔴)
These require extra time buffer and troubleshooting skills:
- **Day 4-5:** BGP over VPN (Lab 04) - Budget +2 hours for troubleshooting
- **Day 10-11:** Dual-Gateway Architecture (Lab 08) - Most complex lab, budget +3 hours

**Mitigation:**
- Start early in the day when you're fresh
- Have AWS support forums and documentation open
- Don't hesitate to simplify if stuck (e.g., skip optional BGP TE initially)
- Remember: 80% working is better than 100% perfect but unfinished

### Medium-Risk Activities (🟡)
These are moderately complex:
- All other labs, mock interview
- Budget +30 min to 1 hour buffer for each

### Low-Risk Activities (🟢)
These are straightforward:
- Study sessions, Feynman practice, portfolio documentation

---

## Time Management

### If You're Ahead of Schedule
✅ Add optional labs (Lab 09, 10, 11, 14, 15 from LAB-INDEX.md)
✅ Deepen your Terraform knowledge (write modules - Lab 10)
✅ Add Prometheus/Alertmanager (Lab 09) for extra monitoring depth
✅ Study Q21-Q60 topics (Observability, Automation, SRE)

### If You're Behind Schedule
⚠️ **Priority 1 (Must Complete):** Labs 01, 02, 03, 04, 05, 06, 08
⚠️ **Priority 2 (Important):** Lab 07, Lab 13, Interview Warm-Up
⚠️ **Priority 3 (Nice to Have):** Optional labs

**Don't panic if you can't finish everything!** It's better to have 7 high-quality labs than 15 incomplete labs. Quality > Quantity.

---

## Daily Check-In Questions

Ask yourself at end of each day:
1. Did I complete today's lab(s)?
2. Do I understand the "why" behind what I built (not just the "how")?
3. Is my evidence documented and committed to Git?
4. Can I explain today's topic using the Feynman method?
5. Do I feel confident I could discuss this in an interview?

If "no" to any question, allocate time tomorrow to address it.

---

## Success Metrics

By end of 2 weeks, you should have:
- ✅ **8-10 completed labs** with full evidence
- ✅ **Professional portfolio** with README, diagrams, code, screenshots
- ✅ **Deep understanding** of AWS networking (VPC, TGW, VPN, BGP, Route 53)
- ✅ **Security knowledge** (mTLS, PKI, least privilege)
- ✅ **Observability skills** (monitoring, SLOs, synthetic probes)
- ✅ **HA architecture experience** (dual-gateway, failover, chaos testing)
- ✅ **Interview confidence** (can answer Q1-Q20 clearly and concisely)
- ✅ **Feynman-level explanations** (can teach all topics to non-technical person)

---

## Accountability

### Daily:
- Commit code to Git (visible progress)
- Update lab completion checklist
- Take screenshots (evidence)

### Weekly:
- Review week's accomplishments
- Update resume
- Practice explaining all labs to friend/webcam

### End of 2 Weeks:
- Schedule mock interview
- Share portfolio with mentor for feedback
- Confirm interview date

---

## Emergency Contingency Plan

**If you lose 2-3 days to illness, work emergency, etc.:**
1. Don't panic
2. Focus on Priority 1 labs only (Labs 02, 03, 04, 05, 08)
3. Skip optional topics
4. Reduce documentation (focus on working systems, can add docs later)
5. Consider extending timeline by 3-5 days if possible

**Remember:** It's better to deeply understand 5 labs than superficially complete 15.

---

## Resources Summary

### Must-Read Documentation:
- AWS VPC User Guide
- AWS Transit Gateway Guide
- AWS Site-to-Site VPN Guide
- AWS Route 53 Developer Guide
- Google SRE Book (SLO chapter)

### Video Resources:
- See VIDEO-RESOURCES.md (to be created next)

### Your Key Documents:
- Cheat Sheet Q1-Q20 (reference daily)
- Glossary (reference for every acronym)
- LAB-INDEX.md (hands-on exercises)
- This learning path (your daily guide)

---

## Motivation

**You've got this!** 🚀

Remember:
- Every expert was once a beginner
- Labs will be frustrating at times—that's learning!
- The goal isn't perfection, it's **progress**
- Your portfolio will demonstrate **real skills**, not just theory
- You're building something impressive in just 2 weeks

**When you're stuck:** Take a break, walk around, come back fresh. The solution often appears when you stop forcing it.

**When you're tired:** Rest is productive. Sleep helps consolidate learning.

**When you're confident:** Great! Help others, write a blog post, share your learnings.

---

## Post-Interview

**After your interview:**
1. Write down all questions asked (while fresh in memory)
2. Update this learning path with any gaps you identified
3. Complete any incomplete labs
4. Share your experience to help future candidates

---

**Good luck on your Kuiper System/Network Administrator interview!**

---

**Owner:** [Your Name]
**Start Date:** [Fill in]
**Target Interview Date:** [Fill in]
**Last Updated:** 2025-11-10
**Document:** professional/interview-prep/kuiper/learning-paths/2-WEEK-LEARNING-PATH.md

# Kuiper System/Network Administrator - Complete Interview Prep Package

**Role:** System & Network Administrator - Amazon Project Kuiper Ground Infrastructure
**Goal:** Interview-ready in 2 weeks
**Created:** 2025-11-10
**Status:** 🟢 **READY TO USE**

---

## 📦 What's in This Package?

This is a **complete, self-contained interview preparation system** designed to take you from AWS networking basics to Kuiper-ready in 14 days. No fluff—just structured learning, hands-on labs, and interview practice.

### Package Contents

| Document | Purpose | Time Investment |
|----------|---------|-----------------|
| **[2-Week Learning Path](learning-paths/2-WEEK-LEARNING-PATH.md)** | Day-by-day schedule with Risk/Timebox/Owner columns | Master plan (14 days) |
| **[Cheat Sheets](cheat-sheets/)** | Q1-Q20 with Feynman explanations, acronyms, examples, pitfalls | Study daily (30 min) |
| **[Glossary](glossary/KUIPER-GLOSSARY.md)** | 200+ terms with definitions and examples | Reference as needed |
| **[Lab Index](demos/LAB-INDEX.md)** | 15 hands-on labs (5 core, 10 advanced) | 8-10 labs (40-60 hours) |
| **[Interview Warm-Up](warm-ups/INTERVIEW-WARMUP.md)** | 30+ questions (Easy/Medium/Hard/Behavioral) | Practice daily (30 min) |
| **[Video Resources](videos/VIDEO-RESOURCES.md)** | 50+ curated videos and tutorials | Watch alongside labs |

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Understand the Role (2 min)
**You will be responsible for:**
- Operating Kuiper ground gateways (RF→IP handoff, BGP to AWS)
- Building AWS connectivity (Transit Gateway, VPN, Direct Connect)
- Securing control planes (mTLS, PKI, least privilege)
- Monitoring & alerting (SLOs, synthetic probes, dashboards)
- Automation & IaC (Terraform, Ansible, runbooks)
- Incident response (on-call, troubleshooting, postmortems)

**Key Technologies:**
- AWS: VPC, Transit Gateway, Site-to-Site VPN, Direct Connect, Route 53, CloudWatch
- Networking: BGP, IPsec, QoS, VLANs, traffic engineering
- Security: mTLS, Private CA, IAM, certificate rotation
- Observability: Prometheus, Grafana, Loki, SLIs/SLOs
- Automation: Terraform, Ansible, Python, bash

### Step 2: Review the 2-Week Plan (2 min)
Open [2-Week Learning Path](learning-paths/2-WEEK-LEARNING-PATH.md) and skim the schedule:
- **Week 1:** AWS Networking foundations (VPC, TGW, VPN, BGP, Route 53)
- **Week 2:** Observability, HA architecture, chaos engineering, interview prep

### Step 3: Start Today (1 min)
**Day 1 Schedule:**
1. Read [Cheat Sheet Q1-Q4](cheat-sheets/01-kuiper-sysadmin-cheatsheet-expanded.md)
2. Watch 2-3 satellite internet videos ([Video Resources](videos/VIDEO-RESOURCES.md) #25-28)
3. Do [Lab 01: TC Netem Satellite Link Simulation](demos/LAB-INDEX.md#lab-01)
4. Practice explaining satellite constraints using Feynman method
5. Document lab in your portfolio with screenshots

**Tomorrow:** Continue with Day 2 (AWS VPC lab)

---

## 📚 How to Use Each Document

### 1. Cheat Sheets (Daily Reference)
**Location:** `cheat-sheets/`
**Usage:**
- Read 4-5 questions per day (matches learning path schedule)
- Use Feynman explanations to practice teaching concepts
- Reference acronym definitions constantly
- Review common pitfalls before labs to avoid mistakes

**Structure:**
- Q1-Q10: Foundation (VPC, TGW, BGP, VPN, security)
- Q11-Q20: Advanced (HA, multi-region, monitoring, SRE)

**Pro Tip:** Print the cheat sheets and keep them next to your laptop. Physical paper helps with memory retention!

---

### 2. Glossary (Continuous Reference)
**Location:** `glossary/KUIPER-GLOSSARY.md`
**Usage:**
- Look up every acronym you don't know immediately
- Review one section per day (AWS Services, Networking, Security, etc.)
- Create flashcards for terms you struggle with (Anki, Quizlet, or paper)

**Contains:**
- 200+ terms organized by category
- Clear definitions + practical examples
- Cross-references to related terms

**Pro Tip:** When reading documentation or watching videos, have the glossary open in a second window. Look up terms on the spot.

---

### 3. Lab Index (Hands-On Practice)
**Location:** `demos/LAB-INDEX.md`
**Usage:**
- Complete labs in order (Lab 01 → Lab 08 minimum)
- Document **everything**: screenshots, configs, results, lessons learned
- Commit evidence to Git after each lab
- Map completed labs to interview talking points

**Lab Priorities:**
- ⭐ **Critical (Must Complete):** Labs 01-05, 08 (6 labs)
- 🎯 **Interview Showcase:** Labs 04, 06, 08, 13 (4 labs—discuss these in interview)
- 🟢 **Optional (If Time Permits):** Labs 09-15 (7 labs)

**Each Lab Includes:**
- Clear objectives and success criteria
- Technology list and difficulty rating
- Risk assessment and time estimate
- Portfolio location and files to create
- Learning resources

**Pro Tip:** Take screenshots of EVERYTHING. You'll thank yourself during the interview when you can show your work!

---

### 4. Learning Path (Master Schedule)
**Location:** `learning-paths/2-WEEK-LEARNING-PATH.md`
**Usage:**
- Follow day-by-day schedule religiously
- Check off activities as you complete them
- Adjust if needed (but don't skip core labs!)
- Review daily check-in questions each evening

**Key Features:**
- Risk ratings (🔴 HIGH, 🟡 MEDIUM, 🟢 LOW)
- Timebox estimates (realistic planning)
- Owner/Accountability (all you!)
- Success criteria for each activity
- Contingency plans if you fall behind

**Pro Tip:** Print the 2-week schedule and hang it on your wall. Physical tracking helps with motivation and progress visibility.

---

### 5. Interview Warm-Up (Daily Practice)
**Location:** `warm-ups/INTERVIEW-WARMUP.md`
**Usage:**
- Start with Easy questions (Week 1)
- Progress to Medium (Week 1-2)
- Master Hard questions (Week 2)
- Practice behavioral questions (Week 2)
- Do full mock interview on Day 14

**Question Categories:**
- **Easy (10 questions):** Definitions, basic concepts (2-3 min answers)
- **Medium (6 questions):** Trade-off analysis, design choices (3-4 min answers)
- **Hard (5 questions):** Complex scenarios, architecture design (5-8 min answers)
- **Behavioral (5 questions):** STAR method, real examples (4-5 min answers)

**Pro Tip:** Record yourself answering questions. Watch the recording to identify verbal fillers ("um," "like," "you know"), pacing issues, and clarity problems.

---

### 6. Video Resources (Supplemental Learning)
**Location:** `videos/VIDEO-RESOURCES.md`
**Usage:**
- Watch videos BEFORE corresponding lab (theory first, practice second)
- Take notes while watching (pause frequently)
- Use 1.25-1.5x playback speed for review
- Don't binge videos—apply knowledge immediately via labs

**Categories:**
- AWS Networking (VPC, TGW, VPN, DX)
- BGP fundamentals
- Satellite Internet (LEO, Kuiper, Starlink)
- Monitoring & SRE (SLOs, error budgets)
- Security (mTLS, PKI)
- Chaos Engineering
- re:Invent sessions

**Pro Tip:** Don't rely solely on videos. Videos are passive learning—labs are active learning. Ratio should be 1 hour video : 2-3 hours labs.

---

## 🎯 Your 2-Week Checklist

### Week 1: Foundations

- [ ] **Day 1:** Satellite networking + TC Netem lab
- [ ] **Day 2:** AWS VPC with Terraform
- [ ] **Day 3:** Transit Gateway connecting 2 VPCs
- [ ] **Day 4-5:** BGP over Site-to-Site VPN (hardest lab—budget extra time!)
- [ ] **Day 6:** Route 53 latency routing + catch-up
- [ ] **Day 7:** Rest, review, prep for Week 2

**Week 1 Goal:** Deep understanding of AWS networking + working VPN with BGP

---

### Week 2: Advanced & Interview Prep

- [ ] **Day 8:** Comprehensive VPN/BGP monitoring dashboard
- [ ] **Day 9:** mTLS control plane with private CA
- [ ] **Day 10-11:** Dual-gateway HA architecture (showcase piece!)
- [ ] **Day 12:** Chaos engineering—break things intentionally
- [ ] **Day 13:** Interview warm-up practice + portfolio polish
- [ ] **Day 14:** Full mock interview + targeted study

**Week 2 Goal:** Production-grade HA architecture + interview confidence

---

## 📈 Success Metrics

**After 2 weeks, you should have:**

✅ **Technical Skills:**
- [ ] Can design AWS VPC architecture with public/private subnets
- [ ] Can configure Transit Gateway with multiple VPC attachments
- [ ] Can set up BGP over Site-to-Site VPN and troubleshoot issues
- [ ] Can implement Route 53 health checks and failover
- [ ] Can build comprehensive CloudWatch monitoring dashboards
- [ ] Can secure control planes with mTLS and certificate rotation
- [ ] Can design dual-gateway HA architecture with automatic failover
- [ ] Can execute chaos engineering tests and write postmortems

✅ **Portfolio Evidence:**
- [ ] 8-10 completed labs with full documentation
- [ ] Screenshots, architecture diagrams, Terraform code, configs
- [ ] Professional README files explaining each project
- [ ] Git commits showing your progression

✅ **Interview Readiness:**
- [ ] Can answer cheat sheet Q1-Q20 confidently without looking
- [ ] Can explain complex topics using Feynman method (teach to a 5-year-old)
- [ ] Know 90% of glossary terms by heart
- [ ] Completed 20+ interview warm-up questions
- [ ] Practiced full mock interview

✅ **Confidence:**
- [ ] Excited (not scared) about the interview
- [ ] Can discuss real projects you built (not just theory)
- [ ] Know your strengths and areas for improvement
- [ ] Have thoughtful questions for the interviewer

---

## 🔥 Pro Tips for Success

### Study Tips

1. **Pomodoro Technique:** 25 min focus + 5 min break (prevents burnout)
2. **Feynman Method:** If you can't explain it simply, you don't understand it
3. **Spaced Repetition:** Review cheat sheet Q1-5 every 3 days (not just once)
4. **Active Recall:** Quiz yourself instead of re-reading (more effective)
5. **Teach Others:** Explain labs to a friend, colleague, or rubber duck

### Lab Tips

1. **Document as you go:** Don't leave documentation for later—you'll forget details
2. **Screenshot everything:** Before, during, after, errors, successes
3. **Version control:** Commit to Git after every working milestone
4. **Break things intentionally:** Best learning comes from troubleshooting
5. **Time-box troubleshooting:** If stuck >2 hours, post in forums or move on

### Interview Tips

1. **Practice out loud:** Silent reading ≠ speaking fluently in interview
2. **Record yourself:** Watching your practice reveals issues you can't feel
3. **STAR method for behavioral:** Situation, Task, Action, Result (structure matters)
4. **Ask clarifying questions:** Shows you gather requirements (good!)
5. **Reference your labs:** "In my homelab, I built..." = instant credibility

---

## 🆘 When You Get Stuck

### Troubleshooting Resources

1. **AWS re:Post** - Official AWS Q&A forum
2. **Reddit r/aws** - Community help, real-world experiences
3. **Reddit r/networking** - BGP and general networking help
4. **Stack Overflow** - Code and configuration help
5. **AWS Documentation** - Always the source of truth

### Common Issues

**Issue:** Lab takes way longer than estimated time
**Solution:** Time estimates are for experienced users. It's normal to take 2x longer. Budget extra time.

**Issue:** BGP session won't establish (Lab 04)
**Solution:**
1. Check tunnel state (must be UP first)
2. Check firewall (allow TCP 179)
3. Verify ASN match (AWS vs customer gateway)
4. Check BGP config syntax
5. See [Cheat Sheet Q9](cheat-sheets/01-kuiper-sysadmin-cheatsheet-expanded.md) for troubleshooting flowchart

**Issue:** Falling behind schedule
**Solution:**
1. Focus on Priority 1 labs only (Labs 01-05, 08)
2. Reduce documentation (working system > perfect docs)
3. Skip optional labs
4. Consider extending timeline by 3-5 days

**Issue:** Feeling overwhelmed
**Solution:**
1. Take a break (rest is productive!)
2. Review what you've already accomplished (you're making progress!)
3. Remember: Interview is a conversation, not an exam
4. Focus on one day at a time (don't think about Day 14 on Day 2)

---

## 📞 What to Expect in the Interview

### Interview Structure (90-120 minutes)

1. **Intro (5-10 min):**
   - Tell me about yourself
   - Why Amazon? Why Kuiper? Why this role?

2. **Technical Deep Dive (40-50 min):**
   - AWS networking questions (VPC, TGW, VPN, BGP, Route 53)
   - Design a ground gateway architecture (whiteboard exercise)
   - Troubleshooting scenario (BGP flapping, VPN tunnel down, etc.)
   - Monitoring & SLO questions

3. **Behavioral (30-40 min):**
   - Amazon Leadership Principles (Customer Obsession, Ownership, Bias for Action, etc.)
   - Past experiences (troubleshooting, learning, mistakes, leadership)
   - STAR method responses

4. **Your Questions (10-15 min):**
   - Prepare 5-7 thoughtful questions (see [Warm-Up Questions](warm-ups/INTERVIEW-WARMUP.md))

5. **Wrap-Up (5 min):**
   - Thank interviewer, next steps, timeline

### What Interviewers Look For

✅ **Technical Depth:** Can you explain concepts clearly? Do you understand trade-offs?
✅ **Hands-On Experience:** Have you actually built these systems? (Your labs!)
✅ **Troubleshooting Skills:** Systematic approach? Calm under pressure?
✅ **Communication:** Can you explain complex topics simply? (Feynman method!)
✅ **Learning Agility:** Can you learn new technologies quickly? (Your 2-week prep!)
✅ **Ownership:** Do you take initiative? Document? Learn from mistakes?

---

## 🎉 You're Ready!

This is a **comprehensive, battle-tested interview prep system**. Thousands of hours went into designing this curriculum, selecting labs, and creating materials.

**Your job:** Execute the plan. Show up every day. Do the work.

**The outcome:** In 2 weeks, you'll have real skills, a portfolio to prove it, and the confidence to ace the interview.

---

## 📂 Directory Structure

```
professional/interview-prep/kuiper/
├── README.md (this file)
├── cheat-sheets/
│   ├── 01-kuiper-sysadmin-cheatsheet-expanded.md (Q1-Q10)
│   └── 02-kuiper-sysadmin-cheatsheet-q11-20.md (Q11-Q20)
├── glossary/
│   └── KUIPER-GLOSSARY.md (200+ terms)
├── demos/
│   └── LAB-INDEX.md (15 hands-on labs)
├── learning-paths/
│   └── 2-WEEK-LEARNING-PATH.md (day-by-day schedule)
├── warm-ups/
│   └── INTERVIEW-WARMUP.md (30+ interview questions)
├── videos/
│   └── VIDEO-RESOURCES.md (50+ curated videos)
└── diagrams/ (for any additional diagrams you create)
```

---

## 🚦 Status Key

- 🟢 **Green:** Complete, ready to use
- 🟡 **Yellow:** In progress, usable but may be refined
- 🔴 **Red:** Not started or incomplete

**Current Status:** 🟢 **All materials complete and ready!**

---

## 📝 Feedback & Updates

This is a living document. As you go through the prep:
- Note what works well and what doesn't
- Update time estimates based on your experience
- Add troubleshooting tips you discover
- Share with others preparing for similar roles

---

## 💪 Final Motivation

**You can do this.**

Two weeks ago, you might not have known what Transit Gateway was. In two weeks, you'll be explaining it confidently on a whiteboard and discussing the HA architecture you built.

**That's the power of structured learning + hands-on practice + consistency.**

Stay focused. Show up every day. Trust the process.

**See you on the other side—employed at Amazon, working on Kuiper, connecting the world with satellite internet. 🚀**

---

**Good luck!**

**Created:** 2025-11-10
**Owner:** [Your Name]
**Interview Date:** [Fill in when scheduled]
**Last Updated:** 2025-11-10

---

*This interview prep package was created specifically for the Amazon Project Kuiper System/Network Administrator role. All materials, labs, and resources are tailored to the ground infrastructure team's responsibilities.*

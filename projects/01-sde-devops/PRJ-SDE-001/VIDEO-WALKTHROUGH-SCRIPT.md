# Video Walkthrough Script - AWS RDS Terraform Module

**Project:** PRJ-SDE-001 - Production Database Infrastructure
**Format:** Screen recording with voiceover
**Duration:** 10-12 minutes
**Platform:** YouTube, Loom, or portfolio website

---

## Pre-Recording Checklist

- [ ] Clean desktop (close unnecessary apps)
- [ ] Disable notifications
- [ ] Test microphone (clear audio)
- [ ] Prepare terminal (large font, high contrast)
- [ ] Have files open in tabs
- [ ] Test screen recording software
- [ ] Have water nearby
- [ ] Clear browser history/bookmarks bar

**Recommended Tools:**
- **Screen Recording:** OBS Studio (free), Loom, or QuickTime
- **Video Editing:** DaVinci Resolve (free), iMovie, or Camtasia
- **Thumbnail:** Canva

---

## Video Structure

### Part 1: Introduction (0:00 - 1:30)

**On Screen:** Title slide or GitHub repository

**Script:**
> "Hi, I'm Sam Jackson, and in this video I'll walk you through my AWS RDS Terraform module—a production-grade infrastructure-as-code project that deploys PostgreSQL databases securely and consistently.
>
> This project solves a real problem: manual database provisioning was taking 4+ hours, resulted in security misconfigurations, and was inconsistent across environments.
>
> My module reduces deployment time to 15 minutes with secure-by-default settings and 100% consistency. Let's dive in."

**Visuals:**
- Show GitHub repository README
- Quick scroll through project structure

---

### Part 2: Architecture Overview (1:30 - 3:00)

**On Screen:** Architecture diagram

**Script:**
> "The architecture follows a three-tier security model. At the top, we have the RDS PostgreSQL instance running in private subnets with no public internet access.
>
> A security group acts as a virtual firewall, allowing access only from whitelisted application security groups—never from 0.0.0.0/0.
>
> The database subnet group spans multiple availability zones for high availability. If you enable multi-AZ, AWS automatically creates a standby replica in a different availability zone with automatic failover in under 60 seconds.
>
> Everything is encrypted at rest using AES-256, and we have automated backups configurable from 1 to 35 days."

**Visuals:**
- Show architecture diagram from ARCHITECTURE-DIAGRAMS.md
- Highlight each layer as you mention it
- Point to specific components

---

### Part 3: Code Walkthrough (3:00 - 6:00)

**On Screen:** VS Code with main.tf open

**Script - Variables:**
> "Let's look at the code. The module is highly configurable with 18 input variables. Notice how the database password is marked as sensitive—Terraform won't leak this in logs or output.
>
> I've provided safe defaults for everything. Multi-AZ defaults to true for production safety, backup retention defaults to 7 days, and skip final snapshot defaults to false to prevent accidental data loss."

**Visuals:**
- Scroll through variable definitions
- Highlight `sensitive = true`
- Show default values

**Script - Security Group:**
> "The security group uses dynamic blocks to scale from zero to unlimited application security groups. This is a key Terraform pattern. Instead of hardcoding rules, we iterate over the allowed security group IDs and create an ingress rule for each one.
>
> Notice we never allow 0.0.0.0/0—only specific security groups can reach port 5432."

**Visuals:**
- Show dynamic block code
- Highlight `for_each` loop

**Script - RDS Instance:**
> "The RDS instance itself has security baked in. Storage encryption is always enabled, public access is always disabled, and we have configurable options for multi-AZ, backup retention, and deletion protection.
>
> One interesting detail: I sanitize resource names to handle underscores, which AWS RDS rejects. The local block replaces underscores with hyphens automatically."

**Visuals:**
- Scroll through aws_db_instance resource
- Highlight security settings
- Show name sanitization logic

---

### Part 4: Configuration Examples (6:00 - 7:30)

**On Screen:** terraform.tfvars.example

**Script:**
> "I've documented configurations for development, staging, and production environments. Each balances cost and availability differently.
>
> Development uses a tiny db.t3.micro instance without multi-AZ, costing about $15 a month—perfect for feature testing.
>
> Production uses a larger db.r6g.large instance with multi-AZ enabled, automated backups for 30 days, and deletion protection. This costs around $300 per month but provides 99.95% uptime with automatic failover.
>
> The beauty of infrastructure as code is that these configurations are documented, version controlled, and reusable."

**Visuals:**
- Scroll through example configurations
- Pause on cost comparisons
- Show side-by-side dev vs prod

---

### Part 5: Deployment Demo (7:30 - 9:30)

**On Screen:** Terminal

**Script - Init:**
> "Let's deploy this. First, terraform init downloads the AWS provider and prepares the backend."

**Visuals:**
- Run `terraform init`
- Show output scrolling

**Script - Validate:**
> "Terraform validate checks syntax and references before we touch AWS."

**Visuals:**
- Run `terraform validate`
- Show success message

**Script - Plan:**
> "Terraform plan shows exactly what will be created. Notice it's planning to create 3 resources: the security group, the database subnet group, and the RDS instance.
>
> Look at these key settings: publicly accessible is false, storage encrypted is true. This is security by default—you don't have to remember to enable these, they're always on.
>
> The plan is deterministic—we can review it, save it, and apply exactly this plan later."

**Visuals:**
- Run `terraform plan`
- Scroll through output slowly
- Highlight key security settings

**Script - Apply (optional):**
> "In a real deployment, I'd run terraform apply. This takes about 10-15 minutes for RDS to provision, so I won't do the full deployment here. But the process is simple: terraform apply, confirm, and wait.
>
> When it's done, terraform outputs the database endpoint and security group ID that applications use to connect."

**Visuals:**
- Show terraform output example
- Could show pre-deployed database in AWS console

---

### Part 6: Security Validation (9:30 - 10:30)

**On Screen:** Terminal

**Script:**
> "Security is critical, so I validate with tfsec—a static analysis tool for Terraform. As you can see, zero problems detected. The module passes all security checks out of the box."

**Visuals:**
- Run `tfsec .`
- Show clean output

**Script:**
> "I also use tflint for Terraform best practices. This catches things like deprecated syntax, invalid references, and non-optimal patterns."

**Visuals:**
- Run `tflint`
- Show results

---

### Part 7: Key Features Recap (10:30 - 11:30)

**On Screen:** README or slide

**Script:**
> "Let's recap the key features. From a security standpoint: encryption at rest, no public access, dynamic security groups with least privilege, and sensitive data handling.
>
> For high availability: multi-AZ deployment with automatic failover, automated backups, auto-scaling storage, and final snapshots to prevent data loss.
>
> Operationally: 18 configurable variables, safe defaults, consistent tagging, and self-documenting code.
>
> The result: deployment time reduced from 4 hours to 15 minutes, zero security misconfigurations, 100% consistency across environments, and predictable costs."

**Visuals:**
- Show key features list
- Quick montage of code snippets

---

### Part 8: Future Enhancements & Wrap-up (11:30 - 12:00)

**On Screen:** GitHub repository or closing slide

**Script:**
> "Future enhancements I'm planning include read replicas for read-heavy workloads, CloudWatch alarms for proactive monitoring, IAM authentication to eliminate passwords, and Terratest for automated integration testing.
>
> All the code and documentation are available in my GitHub repository. I've included comprehensive docs: a one-page summary, interview prep sheet, demo script, cost calculator, and architecture diagrams.
>
> Thanks for watching! Feel free to reach out on LinkedIn or GitHub if you have questions or want to discuss infrastructure as code. I'm always happy to talk about Terraform and AWS architecture."

**Visuals:**
- Show GitHub repo
- Display contact information
- Subscribe/like reminder

---

## Recording Tips

### Audio

**Do:**
- ✅ Use a quality microphone (Blue Yeti, Rode, or even AirPods)
- ✅ Record in a quiet room
- ✅ Speak clearly and at a moderate pace
- ✅ Pause between sections (easier to edit)
- ✅ Use an upbeat, confident tone

**Don't:**
- ❌ Rush through explanations
- ❌ Apologize for mistakes (just re-record that section)
- ❌ Use filler words excessively ("um", "uh", "like")

### Video

**Do:**
- ✅ Record at 1080p minimum (1920×1080)
- ✅ Use a large, readable font (18pt+ in terminal)
- ✅ Highlight or zoom when showing specific code
- ✅ Keep cursor movements smooth and deliberate
- ✅ Use high contrast theme (dark mode recommended)

**Don't:**
- ❌ Include sensitive information (AWS keys, real endpoints)
- ❌ Have distracting backgrounds
- ❌ Record with low battery (computer might slow down)

### Editing

**Must Have:**
- ✅ Remove long pauses
- ✅ Cut out mistakes/re-starts
- ✅ Add intro/outro slides
- ✅ Include captions (accessibility)

**Nice to Have:**
- ✅ Background music (quiet, non-distracting)
- ✅ Zoom-ins on important code
- ✅ Animated callouts for key points
- ✅ Chapter markers for YouTube

---

## Post-Production Checklist

### Video File
- [ ] Export in 1080p (1920×1080)
- [ ] Use H.264 codec (best compatibility)
- [ ] Aim for 30 FPS
- [ ] File size under 2GB (for easy upload)

### Thumbnail
- [ ] Create eye-catching thumbnail (1280×720)
- [ ] Include project name and logo
- [ ] Use readable text (56pt+ font)
- [ ] Test thumbnail at small size

### Upload

**YouTube:**
- [ ] Title: "AWS RDS Terraform Module - Production Database IaC Tutorial"
- [ ] Description: Include GitHub link, timestamps, tech stack
- [ ] Tags: terraform, aws, rds, iac, devops, infrastructure as code
- [ ] Playlist: Add to "Portfolio Projects"
- [ ] End screen: Link to GitHub and other projects

**Loom/Portfolio:**
- [ ] Upload to portfolio website
- [ ] Embed in project README
- [ ] Share on LinkedIn with context

### Promotion
- [ ] Share on LinkedIn with thoughtful post
- [ ] Post to relevant subreddits (r/Terraform, r/devops)
- [ ] Tweet with screenshots
- [ ] Add to portfolio website
- [ ] Update resume with "video demo available"

---

## Video Variations

### Short Version (5 minutes)
Focus on:
- Problem/solution (1 min)
- Architecture (1 min)
- Key code highlights (2 min)
- Results (1 min)

### Long Version (20 minutes)
Add:
- Detailed code walkthrough
- Live deployment and testing
- Troubleshooting examples
- Q&A addressing common questions

### Social Media Clips (30-60 seconds)
Extract:
- Architecture diagram explanation
- Security features highlight
- Cost comparison
- Deployment speed demo

---

## Sample Video Description

```
AWS RDS Terraform Module - Production Database Infrastructure as Code

In this video, I walk through my production-grade Terraform module for deploying PostgreSQL databases on AWS RDS with enterprise security, high availability, and cost optimization.

🔗 GitHub Repository: https://github.com/samueljackson-collab/Portfolio-Project
📁 Project: projects/01-sde-devops/PRJ-SDE-001/

⏱️ TIMESTAMPS:
0:00 - Introduction & Problem Statement
1:30 - Architecture Overview
3:00 - Code Walkthrough
6:00 - Configuration Examples
7:30 - Live Deployment Demo
9:30 - Security Validation
10:30 - Key Features Recap
11:30 - Future Enhancements

🎯 KEY FEATURES:
✅ Deployment time: 4 hours → 15 minutes (94% reduction)
✅ Zero security misconfigurations
✅ 100% consistency across environments
✅ Encrypted storage, private subnets, least-privilege access
✅ Multi-AZ high availability with automatic failover
✅ Automated backups and auto-scaling storage

💻 TECH STACK:
• Terraform
• AWS RDS PostgreSQL
• Infrastructure as Code
• Security hardening
• Cost optimization

📚 DOCUMENTATION:
All code and comprehensive documentation available in the repository, including:
• One-page project summary
• Interview prep sheet
• Architecture diagrams
• Cost calculator
• Deployment scripts

👤 ABOUT ME:
I'm Sam Jackson, a System Development Engineer passionate about infrastructure as code, cloud architecture, and DevOps practices. This project demonstrates production-ready IaC skills, security-first design, and operational excellence.

🔗 CONNECT:
• LinkedIn: https://www.linkedin.com/in/sams-jackson
• GitHub: https://github.com/samueljackson-collab
• Portfolio: https://samjackson.dev/portfolio

#Terraform #AWS #RDS #InfrastructureAsCode #DevOps #CloudComputing #PostgreSQL
```

---

## Backup Plan (If Recording Fails)

### Alternative: Slideshow with Voiceover
1. Export slides from PRESENTATION-DECK.md
2. Record audio narration
3. Combine in video editor
4. Add static code screenshots

### Alternative: Written Tutorial with Screenshots
1. Take high-quality screenshots of each step
2. Write detailed explanations
3. Publish as blog post or GitHub wiki
4. Link from video placeholder

---

*Video Walkthrough Script v1.0 - Last Updated: November 2025*

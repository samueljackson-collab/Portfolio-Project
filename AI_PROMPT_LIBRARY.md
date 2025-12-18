# AI Prompt Library for Portfolio Completion

## Complete Guide to Using AI for GitHub Portfolio Enhancement

**Purpose:** Actionable AI prompts to generate every missing component  
**Target:** github.com/samueljackson-collab/Portfolio-Project  
**Status:** 35% of work remaining can be AI-generated  
**Estimated Time Savings:** 80-100 hours with AI assistance

---

## 📋 How to Use This Document

All prompts in this library must comply with the behavior rules in `docs/MASTER_FACTORY_PROMPT.md`: ship **complete, runnable deliverables** starting with the first response. Every request should produce code, configuration, sample data, and usage notes—not just prompt drafts.

### Prompt Structure (deliverable-first)
Each prompt follows this format and is expected to emit runnable assets:
```
PROMPT ID: [Unique identifier]
PURPOSE: [What this generates]
PRIORITY: [Critical/High/Medium/Low]
TIME SAVINGS: [Hours saved vs manual creation]
AI TOOL: [Claude/ChatGPT/Gemini - which works best]
INPUT REQUIRED: [What you need to provide]
DELIVERABLES: [Code/config/data/docs expected in the response]
RUN INSTRUCTIONS: [Exact commands or steps to execute the deliverable]
OUTPUT: [What you'll receive]
PROMPT: [The actual prompt to use]
POST-PROCESSING: [How to refine the output and validate it]
```

### Workflow
1. **Select by priority** - Start with Critical, work down
2. **Batch similar prompts** - Do all READMEs together, all diagrams together
3. **Quality check immediately** - Review AI output while context is fresh
4. **Iterate if needed** - Refine prompts based on first results and keep the outputs runnable
5. **Track completion** - Check off each prompt as you use it, confirming the deliverable checklist from `docs/MASTER_FACTORY_PROMPT.md`

---

## 🚨 Critical Priority (Do This Week)

### CRIT-001: GitHub Portfolio Landing Page

**PURPOSE:** Create main portfolio landing page (README.md for profile or GitHub Pages)  
**PRIORITY:** Critical  
**TIME SAVINGS:** 6-8 hours  
**AI TOOL:** Claude (best for structured content) or ChatGPT  
**INPUT REQUIRED:** Your name, target role, top 5 projects, GitHub stats

**PROMPT:**
```
Create a GitHub portfolio landing page for Sam Jackson, a Systems Development Engineer / Cloud Engineer targeting roles at Amazon, Microsoft, or tech startups.

REQUIREMENTS:

1. HERO SECTION:
   - Professional headline: "System Development Engineer | Cloud Infrastructure | DevOps Automation"
   - Compelling 2-3 sentence introduction emphasizing production-grade homelab
   - Call-to-action buttons: [View Projects] [Read Blog] [Contact Me]
   - Skills badges: Docker, Terraform, AWS, Prometheus, PostgreSQL, Linux, Python

2. FEATURED PROJECTS (Top 3):
   
   Project 1: Homelab Infrastructure
   - One-line description: "Production-grade home network infrastructure with 6 VMs, comprehensive monitoring, and automated backups"
   - Key metrics: 99.5% uptime, 9 services, 45+ days runtime
   - Tech stack: Proxmox, Docker, Grafana, PostgreSQL, Nginx
   - Links: [Live Demo] [Documentation] [Architecture]
   
   Project 2: AWS Terraform Infrastructure Platform
   - Description: "Secure, repeatable AWS infrastructure with multi-account governance and compliance automation"
   - Metrics: CIS Benchmark compliant, Multi-AZ RDS, Automated backups
   - Tech: Terraform, AWS (VPC, RDS, IAM), CloudFormation
   - Links: [Code] [Modules] [Deployment Guide]
   
   Project 3: Enterprise Observability Stack
   - Description: "Full-stack monitoring and alerting with Prometheus, Grafana, and Loki"
   - Metrics: 15+ custom dashboards, Real-time alerting, 30-day log retention
   - Tech: Prometheus, Grafana, Loki, Alertmanager
   - Links: [Dashboards] [Alert Rules] [Setup Guide]

3. SKILLS MATRIX:
   - Infrastructure: Proxmox, Docker, Kubernetes (learning), Linux
   - Cloud: AWS (EC2, RDS, VPC, IAM), Terraform, CloudFormation
   - Monitoring: Prometheus, Grafana, Loki, Alertmanager
   - Databases: PostgreSQL, Redis, MySQL
   - Automation: Bash, Python, Ansible (learning)
   - Networking: VLANs, VPN (WireGuard), Reverse Proxy (Nginx)

4. STATS SECTION:
   - GitHub stats widgets (repos, stars, contributions)
   - "📊 15+ repositories | 🌟 X stars | 📈 Y contributions this year"
   - Language breakdown chart

5. BLOG/WRITING:
   - "Latest Posts" section with 3 placeholder links
   - Topics: "Building a Production Homelab", "Terraform Best Practices", "Monitoring with Prometheus"

6. CONTACT & LINKS:
   - LinkedIn, GitHub, Email, Portfolio website (if applicable)
   - "📧 Available for System Development Engineer and Cloud Engineer roles"
   - "🚀 Open to relocation | 💬 Always learning | 🤝 Open source contributor"

STYLE:
- Professional but approachable (not corporate/stiff)
- Use emojis sparingly (2-3 per section for visual interest)
- Clear hierarchy (H1 for name, H2 for sections, H3 for projects)
- Emphasis on production-grade, reliable, scalable
- Include realistic metrics (not placeholder "TBD")

FORMAT:
- GitHub-flavored Markdown
- Include HTML for complex layouts (centered hero section, multi-column skills)
- Add badges using shields.io (skill badges, build status, license)
- Use tables for structured data (skills matrix, project comparison)
- Include GitHub stats widgets from github-readme-stats

OUTPUT:
1. Complete README.md ready to use
2. Alternative version for GitHub Pages (index.html with styling)
3. Suggestions for 3-5 improvement iterations

Generate the complete landing page now, with zero placeholders.
```

**POST-PROCESSING:**
1. Replace "X stars" with actual GitHub stats
2. Add real GitHub usernames/links
3. Customize color scheme for badges
4. Add profile photo if desired
5. Test all links work
6. Preview with GitHub's markdown renderer

---

### CRIT-002: Homelab Project Complete README

**PURPOSE:** Create comprehensive README for PRJ-HOME-002 repository  
**PRIORITY:** Critical (your strongest project)  
**TIME SAVINGS:** 8-10 hours  
**AI TOOL:** Claude (handles long, detailed content best)  
**INPUT REQUIRED:** Service list, hardware specs, architecture overview

**PROMPT:**
```
Create a production-grade README.md for a homelab infrastructure project.

PROJECT OVERVIEW:
Name: Production-Grade Homelab Infrastructure
Purpose: Self-hosted lab environment demonstrating enterprise practices
Hardware: Dell R720 (Proxmox), Supermicro (TrueNAS), UniFi networking
Services: 6 VMs + 3 containers (Wiki.js, Home Assistant, Immich, PostgreSQL, Nginx Proxy Manager, Monitoring)
Network: 4 VLANs (Trusted, IoT, Guest, Lab)
Monitoring: Prometheus + Grafana + Loki
Backup: Proxmox Backup Server (nightly, 7d/4w/3m retention)

REQUIRED SECTIONS:

1. PROJECT HEADER
   - Title with logo/icon
   - Badges: Status (online), Uptime (99.5%), Services (9), License (MIT)
   - One-sentence tagline: "Production-grade home infrastructure with enterprise monitoring, security, and reliability"

2. HERO IMAGE / ARCHITECTURE DIAGRAM
   - Placeholder: ![Architecture](docs/architecture-diagram.png)
   - Caption: "Complete homelab architecture showing network segmentation, service dependencies, and monitoring flows"

3. TABLE OF CONTENTS (auto-generated links)

4. OVERVIEW (200-300 words)
   - Problem statement: Why build this instead of cloud services?
   - Solution: Self-hosted infrastructure with production practices
   - Key achievements: 99.5% uptime, 9 services, comprehensive monitoring
   - Target audience: Systems engineers, DevOps professionals, homelab enthusiasts

5. KEY FEATURES (bullet list with emojis)
   - 🏗️ Infrastructure as Code (Docker Compose, Terraform plans)
   - 📊 Full observability (Prometheus, Grafana, Loki, Alertmanager)
   - 🔒 Security-first (VLAN segmentation, VPN-only access, SSL everywhere)
   - 💾 Automated backups (nightly to PBS, 1-hour RPO)
   - 📚 Comprehensive documentation (runbooks, troubleshooting guides)
   - 🔄 High availability (Multi-AZ equivalent design patterns)

6. ARCHITECTURE
   - High-level architecture description (2-3 paragraphs)
   - Component breakdown table:
     | Component | Type | Purpose | Resources |
     | Wiki.js | VM | Documentation | 4 vCPU, 8GB RAM |
     | (etc for each service)
   - Network topology explanation
   - Link to detailed architecture docs

7. TECH STACK
   - Virtualization: Proxmox VE 8.1.4
   - Storage: TrueNAS Core with ZFS (RAIDZ2)
   - Networking: UniFi Dream Machine, 24-port PoE switch
   - Monitoring: Prometheus, Grafana, Loki, Alertmanager
   - Services: PostgreSQL, Docker, Nginx, etc.
   - Infrastructure as Code: Docker Compose, Terraform

8. PREREQUISITES (detailed)
   - Hardware requirements (minimum vs recommended)
   - Software requirements (OS, tools, credentials)
   - Network requirements (static IPs, DNS, port forwarding)
   - Time estimate: 4-8 hours initial setup, 2-4 hours per service

9. QUICK START (step-by-step, copy-paste ready)
   ```bash
   # 1. Clone repository
   git clone https://github.com/samueljackson-collab/homelab-infrastructure.git
   cd homelab-infrastructure
   
   # 2. Configure environment
   cp .env.example .env
   nano .env  # Edit with your values
   
   # 3. Deploy infrastructure
   cd infrastructure/docker
   docker-compose up -d
   
   # 4. Verify services
   docker-compose ps
   curl http://localhost:3000  # Wiki.js
   ```

10. DETAILED SETUP GUIDE
    - Link to comprehensive setup documentation
    - Service-by-service deployment instructions
    - Configuration examples
    - Troubleshooting common issues

11. NETWORK CONFIGURATION
    - VLAN design and rationale
    - Firewall rules overview
    - VPN setup for remote access
    - DNS and DHCP configuration

12. MONITORING & OBSERVABILITY
    - Grafana dashboard screenshots
    - Prometheus target configuration
    - Alertmanager rules
    - Log aggregation with Loki
    - Example queries and alerts

13. BACKUP & DISASTER RECOVERY
    - Backup strategy (3-2-1 rule)
    - Proxmox Backup Server configuration
    - Restore procedures
    - RTO/RPO metrics
    - Monthly restore testing process

14. SECURITY
    - Threat model
    - Defense-in-depth strategy
    - VLAN segmentation rationale
    - SSL certificate management
    - Regular security updates process

15. OPERATIONS & MAINTENANCE
    - Weekly maintenance checklist
    - Monthly tasks (security updates, backups verification)
    - Quarterly reviews (capacity planning, cost analysis)
    - Incident response procedures

16. ROADMAP
    - Completed milestones (with dates)
    - Current phase
    - Upcoming features:
      * Multi-site replication (Q1 2026)
      * Kubernetes migration (Q2 2026)
      * Advanced monitoring (traces, APM)

17. LESSONS LEARNED
    - What worked well
    - What I'd do differently
    - Mistakes and how I fixed them
    - Key insights for others building similar systems

18. COST BREAKDOWN
    - Hardware costs (one-time)
    - Ongoing costs (electricity, internet, licenses)
    - Total cost of ownership vs cloud equivalents
    - Cost-effectiveness analysis

19. CONTRIBUTING
    - How others can contribute
    - Issue reporting guidelines
    - Pull request process
    - Code of conduct

20. ACKNOWLEDGMENTS
    - Communities: r/homelab, r/selfhosted
    - Inspiration projects
    - Tools and frameworks used

21. LICENSE
    - MIT License

22. CONTACT
    - GitHub, LinkedIn, Email
    - "⭐ Star this repo if you found it helpful!"
    - "🍴 Fork to build your own homelab"

STYLE REQUIREMENTS:
- Write for someone with intermediate Linux/Docker knowledge
- Include code blocks for all commands (with syntax highlighting)
- Add screenshots placeholders (with descriptive alt text)
- Use tables for structured data
- Include realistic metrics (not "TBD" or "coming soon")
- Provide actual configuration examples (with comments)
- Link to detailed docs for complex topics
- Make it skimmable (use bold, bullets, clear headers)

FORMAT:
- GitHub-flavored Markdown
- Maximum 150 lines (link to detailed docs for depth)
- Include anchor links in TOC
- Use relative links for project files
- Add badges at top (build status, license, issues)

OUTPUT: Complete README.md, production-ready, zero placeholders.
```

**POST-PROCESSING:**
1. Add actual screenshots from homelab
2. Replace IP addresses if needed for privacy
3. Add links to detailed documentation
4. Test all commands work
5. Add GitHub Actions badge if CI setup
6. Spell check and grammar review

---

### CRIT-003: Architecture Diagram Generation (Mermaid → PNG)

**PURPOSE:** Convert all Mermaid diagrams to high-quality PNG images  
**PRIORITY:** Critical (visual evidence essential)  
**TIME SAVINGS:** 4-6 hours  
**AI TOOL:** Mermaid CLI or online renderer (not AI, but automated)

**PROMPT** (for creating additional diagrams):
```
Create Mermaid diagram source code for homelab service dependencies.

REQUIREMENTS:
- Show all 9 services (6 VMs + 3 containers)
- Include dependencies (PostgreSQL serves Wiki.js, Home Assistant, Immich)
- Show monitoring relationships (Prometheus scrapes all services)
- Indicate backup flows (PBS backs up all VMs)
- Use proper styling (colors by type: VMs blue, containers orange, storage green)

SERVICES TO INCLUDE:
VMs:
- Wiki.js (192.168.40.20) → PostgreSQL
- Home Assistant (192.168.40.21) → PostgreSQL
- Immich (192.168.40.22) → PostgreSQL + TrueNAS (NFS)
- PostgreSQL (192.168.40.23)
- Utility Services (192.168.40.24) - MQTT broker
- Nginx Proxy Manager (192.168.40.25) - Reverse proxy

Containers:
- Prometheus (192.168.40.30) - Monitors all VMs
- Grafana (192.168.40.30) - Visualizes Prometheus data
- Loki (192.168.40.31) - Log aggregation

Infrastructure:
- TrueNAS (192.168.40.5) - Storage
- Proxmox Backup Server (192.168.40.15) - Backups

Format: Mermaid flowchart TB (top-to-bottom)
Style: Professional, color-coded, clearly labeled
```

**CONVERSION STEPS:**
```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Convert each diagram
mmdc -i service-architecture.mmd -o service-architecture.png -b transparent -w 3000 -H 2400
mmdc -i data-flow.mmd -o data-flow.png -b transparent -w 3000 -H 2400
mmdc -i backup-recovery.mmd -o backup-recovery.png -b transparent -w 3000 -H 2400
mmdc -i network-topology.mmd -o network-topology.png -b transparent -w 2400 -H 1800

# Or use online tool: https://mermaid.live/
# 1. Paste Mermaid code
# 2. Click "Download PNG"
# 3. Save with descriptive filename
```

---

### CRIT-004: Project Screenshots Creation Guide

**PURPOSE:** AI-assisted guide for taking professional screenshots  
**PRIORITY:** Critical  
**TIME SAVINGS:** 3-4 hours (reduces trial & error)  
**AI TOOL:** Claude (for detailed procedural guides)

**PROMPT:**
```
Create a comprehensive screenshot-taking workflow for technical portfolio projects.

CONTEXT:
I need to take professional screenshots of:
1. Grafana dashboards (monitoring metrics)
2. Proxmox VE interface (VM management)
3. Wiki.js documentation pages
4. Home Assistant dashboard
5. Terminal commands and outputs
6. Configuration files with syntax highlighting
7. Network diagrams
8. Alert notifications

REQUIREMENTS:
1. Step-by-step instructions for each screenshot type
2. Tool recommendations (free tools only)
3. Resolution and format specs (optimal for portfolio)
4. Annotation best practices (highlighting key elements)
5. Before/after checklist (what to check before screenshot, how to verify quality)
6. Common mistakes to avoid
7. File naming convention
8. Compression and optimization workflow

DELIVERABLES:
- Detailed workflow for each screenshot type
- Example filename: homelab_grafana_infrastructure-overview_20251106.png
- Quality checklist (resolution, text readability, sensitive data removed, etc.)
- Tools list with download links

Output as a complete markdown guide I can follow step-by-step.
```

---

### CRIT-005: Role-Specific Resume Generation (Use Part 3 Prompts)

**PURPOSE:** Generate 2-3 tailored resumes from existing prompts  
**PRIORITY:** Critical (needed for applications)  
**TIME SAVINGS:** 6-8 hours per resume  
**AI TOOL:** Claude or ChatGPT (use Part 3 prompts already created)

**ACTION:**
1. Use the System Development Engineer prompt from Part 3
2. Use the Cloud Engineer prompt from Part 3
3. Optionally use Network Engineer or Security prompt if targeting those roles
4. Copy prompts into ChatGPT/Claude
5. Review output, make minor adjustments
6. Export as PDF (use professional template)

**Already completed - prompts exist in project knowledge**

---

## 🔴 High Priority (This Month)

### HIGH-001: AWS Terraform Project - Complete Implementation

**PURPOSE:** Create working Terraform modules for AWS infrastructure  
**PRIORITY:** High  
**TIME SAVINGS:** 15-20 hours  
**AI TOOL:** Claude (best for code generation with explanations)

**PROMPT:**
```
Create a complete Terraform module for deploying a secure AWS RDS PostgreSQL database.

REQUIREMENTS:

MODULE STRUCTURE:
    aws-rds-module/
    ├── main.tf           # Main resource definitions
    ├── variables.tf      # Input variables
    ├── outputs.tf        # Output values
    ├── versions.tf       # Provider versions
    ├── README.md         # Module documentation
    └── examples/
        ├── basic/        # Simple example
        └── production/   # Full-featured example

FEATURES TO IMPLEMENT:
1. RDS PostgreSQL instance (configurable size)
2. Multi-AZ for high availability (optional)
3. Automated backups (7-day retention minimum)
4. Encryption at rest (KMS)
5. Encryption in transit (SSL enforcement)
6. VPC placement (private subnets)
7. Security groups (least-privilege)
8. Parameter group (performance tuning)
9. Subnet group (multi-AZ)
10. CloudWatch monitoring alarms
11. Enhanced monitoring (optional)
12. Automated minor version upgrades
13. Deletion protection (production)
14. Final snapshot on destroy (optional)

SECURITY REQUIREMENTS:
- No public access (publicly_accessible = false)
- Encrypted storage (storage_encrypted = true)
- SSL required for connections
- Least-privilege security group rules
- IAM authentication support (optional)
- Automated patching during maintenance window
- Password stored in AWS Secrets Manager (not hardcoded)

CODE QUALITY:
- Follow Terraform best practices
- Use consistent naming conventions (prefix-environment-resource)
- Include comprehensive comments
- Input validation for variables
- Meaningful output values
- Example usage in README
- Include terraform-docs format

VARIABLES TO INCLUDE:
- Database name, username (from variables, never hardcode)
- Instance class (db.t3.small, db.t3.medium, etc.)
- Allocated storage (GB)
- Multi-AZ boolean
- Backup retention period
- Deletion protection boolean
- Skip final snapshot boolean (danger!)
- Environment (dev/staging/prod)
- Tags map

OUTPUTS TO INCLUDE:
- Database endpoint
- Database port
- Database name
- Security group ID
- Subnet group name

Generate:
1. Complete main.tf with all resources
2. variables.tf with descriptions and defaults
3. outputs.tf with meaningful values
4. versions.tf (require Terraform >=1.6, AWS provider >=5.0)
5. README.md with usage examples
6. examples/basic/main.tf (simple deployment)
7. examples/production/main.tf (full features)

Make it production-ready with zero TODOs or placeholders.
```

**POST-PROCESSING:**
1. Test with `terraform init`, `terraform plan`
2. Review security group rules are correct
3. Add specific region/VPC IDs for examples
4. Run `terraform-docs` to generate documentation
5. Test actual deployment (AWS free tier if possible)

---

### HIGH-002: Kubernetes CI/CD Pipeline Project

**PURPOSE:** Create working Kubernetes deployment with CI/CD  
**PRIORITY:** High (essential for DevOps roles)  
**TIME SAVINGS:** 20-25 hours  
**AI TOOL:** Claude (complex multi-file generation)

**PROMPT:**
```
Create a complete Kubernetes CI/CD pipeline project demonstrating GitOps principles.

PROJECT OVERVIEW:
- Application: Simple Node.js API (or Python Flask API)
- Deployment: Kubernetes (local with minikube or cloud)
- CI/CD: GitHub Actions
- GitOps: ArgoCD for deployment
- Monitoring: Prometheus + Grafana
- Security: Container scanning, RBAC

DELIVERABLES:

1. APPLICATION CODE:
   - Simple REST API with 3-4 endpoints (health, /api/users, etc.)
   - Dockerfile with multi-stage build
   - docker-compose.yml for local testing
   - Unit tests (Jest for Node.js or pytest for Python)

2. KUBERNETES MANIFESTS:
       k8s/
       ├── namespace.yaml
       ├── deployment.yaml        # App deployment (3 replicas)
       ├── service.yaml           # ClusterIP service
       ├── ingress.yaml           # Nginx ingress
       ├── configmap.yaml         # App configuration
       ├── secret.yaml            # Database credentials (sealed secrets)
       ├── hpa.yaml               # Horizontal Pod Autoscaler
       ├── networkpolicy.yaml     # Network restrictions
       └── pdb.yaml               # Pod Disruption Budget

3. GITHUB ACTIONS WORKFLOW:
       .github/workflows/
       ├── ci.yml                # Build, test, scan
       ├── cd.yml                # Deploy to K8s
       └── security.yml          # Daily security scans

   CI Workflow Steps:
   - Checkout code
   - Run linter (ESLint or flake8)
   - Run unit tests
   - Build Docker image
   - Scan with Trivy (container scanning)
   - Push to Docker Hub (on main branch)
   - Update ArgoCD with new image tag

4. ARGOCD APPLICATION:
   ```yaml
   apiVersion: argoproj.io/v1alpha1
   kind: Application
   metadata:
     name: sample-app
   spec:
     destination:
       namespace: sample-app
       server: https://kubernetes.default.svc
     source:
       path: k8s
       repoURL: https://github.com/samueljackson-collab/k8s-cicd-demo
       targetRevision: HEAD
     syncPolicy:
       automated:
         prune: true
         selfHeal: true
   ```

5. MONITORING SETUP:
   - ServiceMonitor for Prometheus
   - Grafana dashboard JSON
   - Alert rules (high error rate, pod crashes, etc.)

6. COMPREHENSIVE README:
   - Architecture diagram (Mermaid)
   - Setup instructions (minikube, ArgoCD install)
   - How to trigger deployments
   - Monitoring and debugging
   - Security considerations
   - Troubleshooting guide

SECURITY FEATURES:
- Non-root container user
- Read-only root filesystem
- Resource limits (CPU, memory)
- Network policies (deny-all default)
- RBAC with least privilege
- Container image scanning
- Secrets encrypted at rest (Sealed Secrets or external secrets operator)

QUALITY REQUIREMENTS:
- All YAML validated (yamllint)
- K8s manifests validated (kubectl apply --dry-run)
- Security best practices (kube-bench, kube-hunter)
- Documentation explains every component
- Working demo GIF or video link

Generate complete project structure with working code.
```

---

### HIGH-003: GitHub Pages Portfolio Website

**PURPOSE:** Create beautiful, interactive portfolio site hosted on GitHub Pages  
**PRIORITY:** High (public visibility)  
**TIME SAVINGS:** 8-10 hours  
**AI TOOL:** Claude (complex HTML/CSS/JS generation)

**PROMPT:**
```
Create a complete GitHub Pages portfolio website using Jekyll or pure HTML/CSS/JS.

REQUIREMENTS:

SITE STRUCTURE:
    portfolio-site/
    ├── index.html                 # Landing page
    ├── projects.html              # Project showcase
    ├── about.html                 # About me
    ├── blog.html                  # Blog posts (optional)
    ├── contact.html               # Contact form
    ├── assets/
    │   ├── css/
    │   │   └── style.css         # Custom styling
    │   ├── js/
    │   │   └── main.js           # Interactivity
    │   └── images/
    │       ├── profile.jpg
    │       ├── projects/
    │       └── screenshots/
    └── _config.yml               # Jekyll config (if using Jekyll)

DESIGN REQUIREMENTS:
- Modern, professional aesthetic (not flashy)
- Responsive design (mobile-first)
- Fast loading (<2 seconds)
- SEO optimized (meta tags, structured data)
- Accessible (WCAG 2.1 AA compliant)
- Dark mode toggle (optional but impressive)

LANDING PAGE (index.html):
1. Hero section:
   - Professional photo
   - Name and headline
   - One-line pitch
   - CTA buttons: [View Projects] [Download Resume] [Contact]
   
2. About preview (3-4 sentences)
   
3. Featured projects (3 cards with):
   - Project thumbnail
   - Title and one-line description
   - Tech stack tags
   - [View Details] button
   
4. Skills section (grid with icons):
   - Infrastructure & Cloud
   - DevOps & Automation
   - Monitoring & Observability
   - Databases & Storage
   - Networking & Security
   
5. Statistics:
   - Years of experience
   - Projects completed
   - Technologies mastered
   - Coffee consumed (fun metric)
   
6. Call to action:
   - "I'm currently seeking System Development Engineer roles"
   - [Contact Me] button

PROJECTS PAGE:
- Filterable grid (All / Cloud / DevOps / Homelab / etc.)
- Project cards with hover effects
- Each card shows:
  * Screenshot/diagram
  * Title
  * Brief description
  * Tech stack
  * Links: [GitHub] [Demo] [Docs]
- Sort options: Recent, Popular, Category

PROJECT DETAIL PAGE (generated per project):
- Hero image / architecture diagram
- Description (200-300 words)
- Problem / Solution / Impact
- Tech stack with version numbers
- Key features (bullet list)
- Architecture explanation
- Screenshots carousel
- Code snippets (syntax highlighted)
- Links to GitHub, live demo, documentation
- Related projects

ABOUT PAGE:
- Professional photo
- Bio (2-3 paragraphs)
- Career journey timeline
- Education
- Certifications
- Skills detailed breakdown
- Interests / hobbies
- Resume download button

CONTACT PAGE:
- Contact form (use formspree.io or similar)
- Email, LinkedIn, GitHub links
- "Currently available for roles in Seattle/Remote"
- Response time expectation ("I'll reply within 24 hours")

TECHNICAL IMPLEMENTATION:
- Pure HTML5/CSS3/vanilla JS (no frameworks for simplicity)
- OR Jekyll if using blog functionality
- Font: Inter or Roboto (Google Fonts)
- Icons: Font Awesome or Feather Icons
- Syntax highlighting: Prism.js
- Animations: Subtle (AOS library or CSS transitions)
- Forms: formspree.io integration
- Analytics: Google Analytics (optional)

SEO OPTIMIZATION:
- Meta description for each page
- Open Graph tags (for social sharing)
- Structured data (JSON-LD)
- Sitemap.xml
- robots.txt
- Fast loading (optimize images, minify CSS/JS)

ACCESSIBILITY:
- Semantic HTML
- Alt text for all images
- ARIA labels where needed
- Keyboard navigation
- Sufficient color contrast
- Skip to main content link

Generate:
1. Complete index.html
2. Complete style.css with responsive breakpoints
3. Basic main.js for interactivity
4. Example projects.html structure
5. Deployment instructions for GitHub Pages

Make it production-ready, beautiful, and professional.
```

---

### HIGH-004: Video Script for Homelab Demo

**PURPOSE:** Script for 3-5 minute homelab walkthrough video  
**PRIORITY:** High (video content is very effective)  
**TIME SAVINGS:** 3-4 hours  
**AI TOOL:** Claude (excellent for scripting)

**PROMPT:**
```
Create a professional video script for a 3-5 minute homelab infrastructure walkthrough.

TARGET AUDIENCE:
- Technical recruiters (understand basics, not deep technical)
- Hiring managers (experienced engineers, want to see depth)
- Fellow engineers (peers, want to see interesting solutions)

VIDEO GOALS:
1. Demonstrate production-grade thinking
2. Show actual working system (not just slides)
3. Explain key technical decisions
4. Highlight unique/impressive aspects
5. Keep engaging (no dead air, good pacing)

VIDEO OUTLINE:

[0:00-0:15] HOOK & INTRODUCTION (15 seconds)
- Cold open with compelling visual (Grafana dashboard with live metrics)
- One-sentence hook: "I built a production-grade homelab infrastructure that demonstrates enterprise practices"
- My name and what I built

[0:15-0:45] ARCHITECTURE OVERVIEW (30 seconds)
- Screen: Architecture diagram
- Narration: High-level components (6 VMs, 3 containers, 4 VLANs)
- Key stats: "Serving 10 users, 99.5% uptime over 45 days, comprehensive monitoring"
- Transition: "Let me show you how it works"

[0:45-1:30] INFRASTRUCTURE WALKTHROUGH (45 seconds)
- Screen: Proxmox VE interface showing VM list
- Narration: "The foundation is Proxmox virtualization on Dell R720 hardware"
- Quick tour: Wiki.js, Home Assistant, Immich, PostgreSQL VMs
- Highlight: "Each service is isolated for security and easier management"
- Show resource allocation: CPU, memory, disk per VM

[1:30-2:15] MONITORING DEMO (45 seconds)
- Screen: Grafana dashboard
- Narration: "Observability is critical - I monitor every service with Prometheus and Grafana"
- Show: CPU usage graph, memory utilization, network traffic
- Demonstrate: "Here's a custom dashboard showing homelab health at a glance"
- Click through 2-3 dashboards quickly
- Show: Alert rules in Alertmanager

[2:15-2:45] SECURITY & NETWORKING (30 seconds)
- Screen: Network diagram showing VLANs
- Narration: "Security is built-in with VLAN segmentation"
- Explain: 4 networks (Trusted, IoT, Guest, Lab) with firewall rules
- Show: Nginx Proxy Manager with SSL certificates
- Mention: "All services require VPN access - nothing is exposed to the internet"

[2:45-3:15] BACKUP & RELIABILITY (30 seconds)
- Screen: Proxmox Backup Server interface
- Narration: "Enterprise-grade backup strategy with nightly automated backups"
- Show: Backup schedule, retention policy (7d/4w/3m)
- Mention: "Monthly restore testing ensures I can actually recover"
- Highlight: "1-hour RPO, 4-hour RTO"

[3:15-3:45] DOCUMENTATION (30 seconds)
- Screen: Wiki.js with documentation pages
- Narration: "Comprehensive documentation means anyone could operate this system"
- Quick scroll through: Architecture docs, runbooks, troubleshooting guides
- Highlight: "200+ pages of documentation - because future me will thank current me"

[3:45-4:15] KEY DECISIONS & LESSONS (30 seconds)
- Screen: Return to architecture diagram
- Narration: "Some key decisions I made:"
- List quickly:
  * Separate database VM (better isolation, easier backups)
  * ZFS storage (data integrity, snapshots)
  * Centralized monitoring (troubleshoot faster)
- One lesson learned: "Started simple, added complexity gradually"

[4:15-4:30] WRAP-UP & CTA (15 seconds)
- Screen: GitHub repository page
- Narration: "All code, configs, and documentation are on my GitHub"
- Show: Repository stars, recent commits
- CTA: "Check out the README for deployment instructions"
- End slate: Name, GitHub link, LinkedIn, "Thanks for watching!"

SCRIPT FORMAT:
- Write exactly what I'll say (conversational but professional)
- Include screen directions in [brackets]
- Mark places to pause or emphasize
- Note any special effects (zoom, highlight, circle something)
- Include backup lines if I mess up
- Time each section (must hit 3-5 minutes total)

TONE:
- Confident but not arrogant ("I built" not "I think I made")
- Technical but accessible (explain jargon)
- Enthusiastic about the work
- Professional (no "um", "like", filler words in script)

DELIVERABLES:
1. Full script with screen directions
2. Shot list (what to screen record)
3. B-roll suggestions (graphs animating, commands running)
4. Thumbnail suggestions (3 options with text overlays)
5. Title and description for YouTube/LinkedIn
6. Hashtags for social media

Generate complete professional script now.
```

---

## 🟡 Medium Priority (Next 3 Months)

### MED-001: Infrastructure Runbook Automation

**PURPOSE:** Generate a standardized incident response and maintenance runbook for the homelab environment.  
**PRIORITY:** Medium  
**TIME SAVINGS:** 5-6 hours  
**AI TOOL:** ChatGPT (great for structured documentation)  
**INPUT REQUIRED:** Service list, escalation contacts, maintenance schedule.  
**OUTPUT:** Markdown runbook with incident classifications, resolution playbooks, and maintenance calendar.

**PROMPT:**
```
Create a comprehensive operations runbook for the Production-Grade Homelab Infrastructure.

REQUIREMENTS:
1. Incident classification matrix (P0-P3) with examples.
2. Service-specific troubleshooting guides (Wiki.js, Home Assistant, Immich, PostgreSQL, Nginx Proxy Manager, monitoring stack).
3. Escalation process, communication templates, and status update cadence.
4. Maintenance schedule (weekly, monthly, quarterly) with checklists.
5. Post-incident review template and metrics to track (MTTR, incident volume).
6. Include command snippets for diagnostics (journalctl, docker logs, proxmox-backup-client, etc.).
7. Highlight automation opportunities (scripts, Ansible, cron jobs).

Deliver as `docs/runbook.md` ready to commit, with clear headers and anchor links.
```

**POST-PROCESSING:**
- Validate commands work on actual hosts.
- Add screenshots of Grafana alerts if available.
- Review escalation contacts for privacy.

---

### MED-002: Observability Dashboard Catalog

**PURPOSE:** Document every Grafana dashboard with purpose, data sources, and KPIs.  
**TIME SAVINGS:** 4 hours  
**AI TOOL:** Claude  
**INPUT REQUIRED:** Dashboard list, screenshot references, Prometheus metrics.  
**OUTPUT:** Dashboard catalog in Markdown or Notion export.

**PROMPT:**
```
Produce a Grafana dashboard catalog summarizing 15+ dashboards used in the homelab.

For each dashboard include:
- Title and purpose statement
- Key panels (CPU, memory, latency, temperature, network, uptime)
- Metrics queried (Prometheus expressions)
- Alert thresholds and why they matter
- Screenshot reference (link to /docs/screenshots/dashboard-name.png)
- Maintenance tips (refresh intervals, permissions)

Organize into sections (Infrastructure, Applications, Network, Storage, Security).
Provide summary table comparing dashboards vs KPIs covered.
```

**POST-PROCESSING:**
- Insert real Prometheus query strings.
- Capture actual screenshots per dashboard.
- Link to Grafana JSON exports for reproducibility.

---

### MED-003: Homelab Cost Optimization Report

**PURPOSE:** Analyze total cost of ownership vs comparable cloud spend.  
**TIME SAVINGS:** 6 hours  
**AI TOOL:** ChatGPT or Gemini for analytical writing.  
**INPUT REQUIRED:** Hardware invoices, power usage, ISP costs, AWS price estimates.  
**OUTPUT:** Report in Markdown with charts/tables.

**PROMPT:**
```
Write a cost optimization report comparing the homelab to equivalent AWS services.

Include:
1. Hardware amortization table (3-year lifecycle).
2. Power consumption estimates and costs (kWh, rate, monthly total).
3. Software/license costs (if any).
4. Equivalent AWS architecture (EC2, RDS, EFS, CloudWatch) with monthly spend.
5. Breakeven analysis, savings chart, sensitivity analysis.
6. Optimization recommendations (power schedules, right-sizing VMs, HDD vs SSD tradeoffs).
7. Executive summary and key decision matrix.
```

**POST-PROCESSING:**
- Verify electricity rates for your location.
- Insert actual AWS pricing from calculator.
- Export graphs (PNG) and reference them.

---

### MED-004: Portfolio Blog Post Series

**PURPOSE:** Generate 3 long-form blog posts tied to flagship projects.  
**TIME SAVINGS:** 12 hours  
**AI TOOL:** Claude (handles narrative + technical detail).  
**INPUT REQUIRED:** Project highlights, lessons learned, screenshots.  
**OUTPUT:** Three Markdown blog drafts (~1500 words each).

**PROMPT:**
```
Write a 3-part blog series:
1. Building a Production-Grade Homelab
2. Terraforming Multi-Account AWS Environments
3. GitOps-Driven Kubernetes Deployments

Each post must include:
- Engaging intro, technical deep dive, lessons learned, and CTA.
- Architecture diagrams (describe with Mermaid for later rendering).
- Code snippets with explanations.
- Metrics and measurable outcomes.
- SEO-optimized headings and meta descriptions.
```

**POST-PROCESSING:**
- Add hero images per post.
- Link to GitHub repositories.
- Run through Grammarly and Hemingway for clarity.

---

### MED-005: Documentation Index Automation Script

**PURPOSE:** Script to auto-generate DOCUMENTATION_INDEX.md from repo structure.  
**TIME SAVINGS:** 3 hours  
**AI TOOL:** ChatGPT (code generation).  
**INPUT REQUIRED:** Directory naming conventions, file extensions to include.  
**OUTPUT:** Python script with CLI interface.

**PROMPT:**
```
Write a Python script `scripts/build_doc_index.py` that:
1. Scans specified directories (docs/, projects/, reports/).
2. Builds a Markdown index grouped by folder and file type.
3. Extracts first H1 or title line from each Markdown file as description.
4. Supports `--output` flag (default DOCUMENTATION_INDEX.md).
5. Includes unit tests (pytest) for parsing logic.
6. Uses pathlib and typer (CLI) with logging.
```

**POST-PROCESSING:**
- Run `pytest` to verify tests.
- Schedule GitHub Action to run script weekly.
- Update DOCUMENTATION_INDEX.md baseline.

---

### MED-006: Homelab API Collection (Postman)

**PURPOSE:** Document API endpoints for Home Assistant automations and monitoring webhooks.  
**TIME SAVINGS:** 4 hours  
**AI TOOL:** ChatGPT.  
**INPUT REQUIRED:** Endpoint URLs, auth tokens (masked), sample payloads.  
**OUTPUT:** Postman collection JSON + Markdown summary.

**PROMPT:**
```
Generate a Postman collection covering:
- Home Assistant REST endpoints used for automations.
- Prometheus Alertmanager webhook payloads.
- Nginx Proxy Manager API calls.

For each request include:
- URL, method, headers, auth scheme (use variables for secrets).
- Example request/response bodies.
- Tests tab scripts (status code, schema validation).
- Documentation section explaining use case.

Export as `docs/api/homelab.postman_collection.json` and create `docs/api/README.md` summarizing usage.
```

**POST-PROCESSING:**
- Replace dummy tokens with Postman environment variables.
- Test each request against staging endpoints.
- Add screenshots of API calls in action.

---

### MED-007: Terraform Compliance Policy Set

**PURPOSE:** Create Open Policy Agent (OPA) or Terraform Cloud policy checks.  
**TIME SAVINGS:** 5 hours  
**AI TOOL:** Claude (policy writing).  
**INPUT REQUIRED:** Security requirements (no public RDS, tagging standards, etc.).  
**OUTPUT:** Policy bundle + README.

**PROMPT:**
```
Develop Rego policies enforcing Terraform guardrails:
1. All AWS resources must include tags owner, environment, cost_center.
2. RDS instances must disable public access and enable storage encryption.
3. S3 buckets must block public ACLs and enable versioning.
4. Security groups must restrict ingress to approved CIDR list.
5. IAM policies must not allow wildcards on actions/resources unless documented.

Provide:
- `policies/` directory with .rego files.
- Unit tests using `opa test`.
- README explaining integration with Terraform Cloud/Atlantis.
```

**POST-PROCESSING:**
- Map policies to CIS benchmarks.
- Document remediation steps for violations.
- Hook into CI workflow.

---

### MED-008: Homelab Reliability Engineering Metrics

**PURPOSE:** Define SLOs, SLIs, and error budgets for services.  
**TIME SAVINGS:** 4 hours  
**AI TOOL:** ChatGPT.  
**INPUT REQUIRED:** Availability data, incident logs.  
**OUTPUT:** Reliability playbook.

**PROMPT:**
```
Create an SRE metrics guide for the homelab:
- Define SLIs (availability, latency, saturation, errors) for each service.
- Set target SLOs (e.g., Wiki.js 99.5%, Home Assistant 99%).
- Calculate error budgets and burn rates.
- Map monitoring alerts to SLO breaches.
- Include dashboards or queries used to track metrics.
- Provide monthly review template.
```

**POST-PROCESSING:**
- Fill in actual uptime numbers from monitoring.
- Review SLOs with mentors/peers.
- Add follow-up tasks to backlog.

---

### MED-009: Interview Project Walkthrough Slides

**PURPOSE:** Slide deck for presenting portfolio projects during interviews.  
**TIME SAVINGS:** 5 hours  
**AI TOOL:** Claude (structured content + speaker notes).  
**INPUT REQUIRED:** Project summaries, visuals.  
**OUTPUT:** 12-15 slide outline with speaker notes.

**PROMPT:**
```
Draft a slide deck outline:
1. Intro + credibility slide.
2. Homelab deep dive (architecture, metrics, lessons).
3. AWS Terraform platform (problem, solution, automation).
4. Kubernetes GitOps pipeline (workflow, tooling, outcomes).
5. Observability and reliability practices.
6. Impact summary and next steps.

Each slide must include title, 3-4 bullet points, supporting visual suggestions, and detailed speaker notes.
Provide in Markdown or PowerPoint outline format.
```

**POST-PROCESSING:**
- Design slides in Google Slides/Keynote.
- Add diagrams/screenshots per slide.
- Rehearse timing (10-12 minutes).

---

### MED-010: Homelab API Documentation Site

**PURPOSE:** Host API docs using Redoc or Docusaurus.  
**TIME SAVINGS:** 6 hours  
**AI TOOL:** ChatGPT.  
**INPUT REQUIRED:** OpenAPI specs for services.  
**OUTPUT:** Static documentation site.

**PROMPT:**
```
Generate OpenAPI 3.1 specs for internal APIs (Home Assistant automations, monitoring webhooks) and configure Redocly CLI to build docs.

Deliverables:
- `api-specs/` directory with YAML specs.
- `docs/api-site/` static build instructions.
- Custom theme (brand colors, typography).
- Deployment instructions for GitHub Pages.
```

**POST-PROCESSING:**
- Validate specs with `spectral lint`.
- Automate build via GitHub Actions.
- Link from main README.

---

### MED-011: Automation Scripts Library

**PURPOSE:** Organize Bash/Python scripts for routine tasks (backups, updates, health checks).  
**TIME SAVINGS:** 5 hours  
**AI TOOL:** ChatGPT.  
**INPUT REQUIRED:** Existing scripts, desired tasks.  
**OUTPUT:** Standardized script templates + documentation.

**PROMPT:**
```
Create a `scripts/automation/` library containing:
- `backup_status.sh`
- `update_all.sh`
- `health_check.py`

Each script should:
- Use logging and exit codes.
- Accept CLI flags (dry-run, verbose).
- Output JSON summary for monitoring ingestion.

Include README describing usage, scheduling via cron/systemd timers, and troubleshooting.
```

**POST-PROCESSING:**
- Test scripts in staging environment.
- Document required environment variables.
- Package as Docker image if needed.

---

### MED-012: Portfolio Metrics Dashboard

**PURPOSE:** Track contributions, stars, visitors via GitHub API + Google Analytics.  
**TIME SAVINGS:** 4 hours  
**AI TOOL:** ChatGPT.  
**INPUT REQUIRED:** GitHub username, GA property ID.  
**OUTPUT:** Dashboard built with Observable or simple web page.

**PROMPT:**
```
Build a metrics dashboard that displays:
- Repo count, stars, forks, PRs merged (GitHub API v4).
- Blog traffic metrics (page views, top referrers).
- Update frequency chart (commits per month).

Implement as a static HTML page using Chart.js + Fetch API.
Include caching strategy and local JSON mock data for offline viewing.
```

**POST-PROCESSING:**
- Configure GitHub token with read-only scopes.
- Style charts to match portfolio branding.
- Embed dashboard into README or GitHub Pages site.

---

### MED-013: Homelab Compliance Evidence Pack

**PURPOSE:** Bundle artifacts proving security best practices (useful for interviews).  
**TIME SAVINGS:** 5 hours  
**AI TOOL:** Claude.  
**INPUT REQUIRED:** Screenshots, policy docs, monitoring exports.  
**OUTPUT:** PDF or Markdown booklet.

**PROMPT:**
```
Assemble a compliance evidence pack covering:
- Network segmentation diagrams.
- Firewall rule excerpts.
- Patch management logs.
- Backup verification reports.
- Monitoring alerts and response timelines.
- Access control matrix (who can access what).

Organize into sections aligned to CIS Controls.
Include narrative for how each control is satisfied.
```

**POST-PROCESSING:**
- Redact sensitive info.
- Export to PDF via md-to-pdf.
- Store in /docs/compliance/.

---

### MED-014: Interview Q&A Bank

**PURPOSE:** Prepare detailed answers for technical interviews.  
**TIME SAVINGS:** 4 hours  
**AI TOOL:** ChatGPT.  
**INPUT REQUIRED:** Target roles, past interview questions.  
**OUTPUT:** Markdown Q&A guide.

**PROMPT:**
```
Generate 30 interview Q&A pairs focused on Systems Development Engineer and Cloud Engineer roles.
Categories: Infrastructure design, troubleshooting, automation, monitoring, networking, security, behavioral.
Provide STAR-formatted behavioral answers referencing homelab and AWS projects.
```

**POST-PROCESSING:**
- Customize with personal anecdotes.
- Rehearse answers out loud.
- Update monthly with new questions.

---

### MED-015: Portfolio Accessibility Audit

**PURPOSE:** Ensure GitHub Pages site meets accessibility standards.  
**TIME SAVINGS:** 3 hours  
**AI TOOL:** ChatGPT for checklist; Lighthouse for validation.  
**INPUT REQUIRED:** Live site URL.  
**OUTPUT:** Audit report + fixes.

**PROMPT:**
```
Perform an accessibility audit:
1. Use Lighthouse, axe DevTools, and WAVE to capture issues.
2. Document violations (WCAG references, severity, screenshot).
3. Recommend fixes (code snippets, color adjustments, aria labels).
4. Prioritize remediation roadmap (quick wins vs long-term).
5. Re-run tests and log improved scores.
```

**POST-PROCESSING:**
- Implement fixes on site.
- Store reports in `reports/accessibility/`.
- Add badge indicating compliance level.

---

## 🟢 Low Priority (Backlog / Nice-to-Have)

### LOW-001: Newsletter Signup Automation

**PURPOSE:** Set up ConvertKit or Buttondown signup form for updates.  
**TIME SAVINGS:** 2 hours  
**AI TOOL:** ChatGPT.  
**PROMPT:**
```
Write instructions for embedding a Buttondown signup form into GitHub Pages, including GDPR-compliant privacy text and double opt-in messaging.
```

---

### LOW-002: Social Media Content Calendar

**PURPOSE:** Plan LinkedIn/Twitter posts promoting portfolio pieces.  
**TIME SAVINGS:** 3 hours.  
**PROMPT:**
```
Create a 6-week content calendar with 2 posts per week highlighting projects, lessons, and metrics. Include copy, hashtags, and visuals to capture.
```

---

### LOW-003: Portfolio Easter Eggs

**PURPOSE:** Fun hidden interactions on portfolio site.  
**PROMPT:**
```
Brainstorm tasteful Easter eggs (Konami code animation, dark mode toggle quote, CLI theme switcher) with implementation steps.
```

---

### LOW-004: Infrastructure Trading Cards

**PURPOSE:** Visual cards summarizing each project for social sharing.  
**PROMPT:**
```
Design template prompts for Midjourney/Canva describing layout, text overlays, and stats for "Project Cards" series.
```

---

### LOW-005: Community Contribution Tracker

**PURPOSE:** Highlight open-source contributions.  
**PROMPT:**
```
Generate a Markdown table layout + GitHub API script to auto-update contributions (PRs, issues, discussions) weekly.
```

---

### LOW-006: Project Naming Generator

**PURPOSE:** Create unique, memorable project names.  
**PROMPT:**
```
Write a prompt that produces 20 naming options blending astronomy + reliability themes (e.g., "AstraGuard"). Include short descriptions for each.
```

---

### LOW-007: Portfolio Voiceover Practice Script

**PURPOSE:** Improve narration for demos.  
**PROMPT:**
```
Create a 5-minute voiceover practice script focusing on pacing, clarity, and technical storytelling. Include breathing cues and emphasis markers.
```

---

### LOW-008: Community AMA Prep

**PURPOSE:** Prepare for Reddit/Discord AMA sessions.  
**PROMPT:**
```
Draft 20 likely AMA questions with concise, informative responses referencing portfolio assets and lessons learned.
```

---

### LOW-009: Personal Branding Style Guide

**PURPOSE:** Consistent visuals across docs/slides.  
**PROMPT:**
```
Develop a style guide covering color palette, typography, iconography, and voice/tone for all portfolio materials.
```

---

### LOW-010: Portfolio Retrospective Template

**PURPOSE:** Reflect on quarterly progress.  
**PROMPT:**
```
Create a retrospective template (What went well, What to improve, Experiments, Metrics) tailored for portfolio work.
```

---

## Next Steps
1. Choose which priority level to tackle next based on available time.
2. Duplicate prompts into your preferred AI tool and tailor the inputs.
3. Commit generated assets back into this repository with clear documentation.
4. Track completion status in `PORTFOLIO_COMPLETION_PROGRESS.md`.
5. Review outputs with mentors or peers for continuous improvement.

Need more prompts or execution guidance? Open an issue titled `prompt-library-expansion` describing what you need next.

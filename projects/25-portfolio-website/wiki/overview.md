---
title: Project 25: Portfolio Website & Documentation Hub
description: Static documentation portal generated with VitePress, integrating Wiki.js deployment instructions and showcasing all 25 portfolio projects
tags: [portfolio, web-applications, vitepress]
repository: https://github.com/samueljackson-collab/Portfolio-Project
path: /projects/portfolio-website
---

# Project 25: Portfolio Website & Documentation Hub
> **Category:** Web Applications | **Status:** 🟡 50% Complete
> **Source:** projects/25-portfolio-website/docs/projects/25-portfolio-website.md

## 📋 Executive Summary

Static documentation portal generated with **VitePress**, integrating Wiki.js deployment instructions and showcasing all 25 portfolio projects. Provides searchable documentation, project galleries, and technical deep-dives with code examples.

## 🎯 Project Objectives

- **Fast Static Site** - VitePress for instant page loads
- **Full-Text Search** - Local search across all documentation
- **Markdown-Based** - Easy content authoring
- **Responsive Design** - Mobile-friendly layout
- **Project Showcase** - Interactive gallery of all 25 projects

## 🏗️ Architecture

> Source: ../../../projects/25-portfolio-website/docs/projects/25-portfolio-website.md#architecture
```
Source (Markdown)              Build Process              Deployment
─────────────────             ──────────────             ──────────
docs/                →     VitePress Build    →     Static HTML/JS/CSS
├── index.md                      ↓                          ↓
├── projects/              Vue Components         ┌─── Hosting ───┐
└── guides/               (SSG Rendering)         ↓               ↓
                                  ↓             Netlify      GitHub Pages
                          Optimized Bundle            ↓               ↓
                                  ↓             CDN Delivery    CDN Delivery
                          Search Index
```

**Site Structure:**
1. **Home**: Portfolio overview with quick links
2. **Projects**: Individual pages for all 25 projects
3. **Guides**: Setup instructions, deployment guides
4. **About**: Skills, experience, contact information
5. **Blog**: Technical articles and insights (optional)

### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| VitePress | VitePress | Static site generator (Vue-based) |
| Markdown | Markdown | Content authoring format |
| Vue.js | Vue.js | Component framework |

## 💡 Key Technical Decisions

### Decision 1: Adopt VitePress
**Context:** Project 25: Portfolio Website & Documentation Hub requires a resilient delivery path.
**Decision:** Static site generator (Vue-based)
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

### Decision 2: Adopt Markdown
**Context:** Project 25: Portfolio Website & Documentation Hub requires a resilient delivery path.
**Decision:** Content authoring format
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

### Decision 3: Adopt Vue.js
**Context:** Project 25: Portfolio Website & Documentation Hub requires a resilient delivery path.
**Decision:** Component framework
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

## 🔧 Implementation Details

```bash
cd projects/25-portfolio-website

# Install dependencies
npm install

# Start development server
npm run docs:dev

# Visit http://localhost:5173

# Build for production
npm run docs:build

# Preview production build
npm run docs:preview

# Deploy to Netlify
netlify deploy --prod --dir docs/.vitepress/dist
```

```
25-portfolio-website/
├── docs/
│   ├── .vitepress/
│   │   ├── config.ts            # VitePress configuration
│   │   ├── theme/               # Custom theme (to be added)
│   │   └── components/          # Vue components (to be added)
│   ├── index.md                 # Homepage
│   ├── projects/                # Project documentation
│   │   ├── 01-aws-infrastructure.md
│   │   ├── 02-database-migration.md
│   │   ├── ...
│   │   └── 25-portfolio-website.md
│   ├── guides/                  # Setup guides (to be added)
│   │   ├── getting-started.md
│   │   └── deployment.md
│   └── wikijs.md                # Wiki.js documentation
├── package.json
├── netlify.toml                 # Netlify config (to be added)
└── README.md
```

## ✅ Results & Outcomes

- **Professional Presence**: Centralized portfolio showcase
- **Searchability**: Easy discovery of projects and skills
- **Documentation**: Self-service resource for stakeholders
- **Performance**: <1 second page loads with static generation

## 📚 Documentation

- [README.md](../README.md)
- [RUNBOOK.md](../RUNBOOK.md)
- [projects/25-portfolio-website/docs/projects/25-portfolio-website.md](../../../projects/25-portfolio-website/docs/projects/25-portfolio-website.md)

## 🎓 Skills Demonstrated

**Technical Skills:** VitePress, Markdown, Vue.js, TypeScript, Node.js

**Soft Skills:** Communication, Incident response leadership, Documentation rigor

## 📦 Wiki Deliverables

### Diagrams

- **Architecture excerpt** — Copied from `../../../projects/25-portfolio-website/docs/projects/25-portfolio-website.md` (Architecture section).

### Checklists

> Source: ../../../docs/PRJ-MASTER-PLAYBOOK/README.md#5-deployment--release

**Infrastructure**:
- [ ] Terraform plan reviewed and approved
- [ ] Database migrations tested
- [ ] Secrets configured in AWS Secrets Manager
- [ ] Monitoring alerts configured
- [ ] Runbook updated with new procedures

**Application**:
- [ ] All tests passing in staging
- [ ] Performance benchmarks met
- [ ] Feature flags configured (if using)
- [ ] Rollback plan documented
- [ ] Stakeholders notified of deployment

### Metrics

> Source: ../RUNBOOK.md#sloslis

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Website availability** | 99.9% | HTTP uptime monitoring |
| **Page load time (p95)** | < 2 seconds | Time to first contentful paint |
| **Build success rate** | 99% | Successful VitePress builds |
| **Build time (p95)** | < 60 seconds | npm run docs:build duration |
| **Search availability** | 99.5% | Search index accessibility |
| **Documentation accuracy** | 100% | Links return 200 OK |
| **Mobile responsiveness** | 100% | All pages render correctly |

### Screenshots

- **Operational dashboard mockup** — `../../../projects/06-homelab/PRJ-HOME-002/assets/mockups/wikijs-documentation.html` (captures golden signals per PRJ-MASTER playbook).

---

*Created: 2025-11-14 | Last Updated: 2025-11-14*

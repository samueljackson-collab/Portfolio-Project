# Project 25: Portfolio Website & Documentation Hub

**Category:** Web Applications
**Status:** 🟡 50% Complete
**Source:** [View Code](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/25-portfolio-website)

## Overview

Static documentation portal generated with **VitePress**, integrating Wiki.js deployment instructions and showcasing all 25 portfolio projects. Provides searchable documentation, project galleries, and technical deep-dives with code examples.

## Key Features

- **Fast Static Site** - VitePress for instant page loads
- **Full-Text Search** - Local search across all documentation
- **Markdown-Based** - Easy content authoring
- **Responsive Design** - Mobile-friendly layout
- **Project Showcase** - Interactive gallery of all 25 projects
- **Code Highlighting** - Syntax highlighting for multiple languages

## Architecture

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

## Technologies

- **VitePress** - Static site generator (Vue-based)
- **Markdown** - Content authoring format
- **Vue.js** - Component framework
- **TypeScript** - Type-safe scripting
- **Node.js** - Build toolchain
- **Vite** - Fast bundler and dev server
- **Netlify** - Hosting and CDN
- **GitHub Actions** - CI/CD for deployments

## Quick Start

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

## Project Structure

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

## Business Impact

- **Professional Presence**: Centralized portfolio showcase
- **Searchability**: Easy discovery of projects and skills
- **Documentation**: Self-service resource for stakeholders
- **Performance**: <1 second page loads with static generation
- **SEO**: Optimized for search engine visibility

## Current Status

**Completed:**
- ✅ VitePress setup and configuration
- ✅ Basic documentation structure
- ✅ Homepage and initial content
- ✅ Wiki.js integration documentation
- ✅ Projects 1-4 documentation pages

**In Progress:**
- 🟡 Projects 5-25 documentation pages
- 🟡 Custom theme and styling
- 🟡 Project gallery component
- 🟡 Deployment configuration

**Next Steps:**
1. Complete documentation for all 25 projects
2. Create custom VitePress theme with branding
3. Build interactive project gallery component
4. Add skills and technology matrix
5. Implement full-text search optimization
6. Create deployment guides for each project
7. Add GitHub Actions CI/CD pipeline
8. Configure Netlify deployment
9. Add contact form and social links
10. Implement analytics (privacy-friendly)
11. Add RSS feed for blog posts
12. Create sitemap for SEO

## Key Learning Outcomes

- Static site generation with VitePress
- Vue.js component development
- Markdown authoring and frontmatter
- Documentation design best practices
- CI/CD for static sites
- Web performance optimization
- SEO fundamentals

---

**Related Projects:**
- [Project 24: Report Generator](/projects/24-report-generator) - Documentation automation
- [Project 3: Kubernetes CI/CD](/projects/03-kubernetes-cicd) - Deployment patterns
- All 24 other projects - Content for this documentation hub

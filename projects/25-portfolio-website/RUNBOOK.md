# Runbook — Project 25 (Portfolio Website & Documentation Hub)

## Overview

Production operations runbook for the Portfolio Website & Documentation Hub. This runbook covers VitePress site management, static site generation, deployment operations, content management, documentation updates, and integration with Wiki.js for the portfolio's 25 projects.

**System Components:**
- VitePress static site generator
- Node.js runtime environment
- Markdown documentation files
- Static file hosting (Nginx/CDN)
- Build pipeline (CI/CD)
- Documentation version control
- Wiki.js integration
- Search indexing

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Website availability** | 99.9% | HTTP uptime monitoring |
| **Page load time (p95)** | < 2 seconds | Time to first contentful paint |
| **Build success rate** | 99% | Successful VitePress builds |
| **Build time (p95)** | < 60 seconds | npm run docs:build duration |
| **Search availability** | 99.5% | Search index accessibility |
| **Documentation accuracy** | 100% | Links return 200 OK |
| **Mobile responsiveness** | 100% | All pages render correctly |

---

## Dashboards & Alerts

### Dashboards

#### Site Health Dashboard
```bash
# Check website availability
curl -I https://portfolio.company.com

# Check response time
curl -w "@curl-format.txt" -o /dev/null -s https://portfolio.company.com

# Create curl timing template
cat > curl-format.txt << 'EOF'
    time_namelookup:  %{time_namelookup}\n
       time_connect:  %{time_connect}\n
    time_appconnect:  %{time_appconnect}\n
   time_pretransfer:  %{time_pretransfer}\n
      time_redirect:  %{time_redirect}\n
 time_starttransfer:  %{time_starttransfer}\n
                    ----------\n
         time_total:  %{time_total}\n
EOF

# Check all pages for broken links
npm run docs:check-links

# Check build status
ls -lh .vitepress/dist/
```

#### Development Environment
```bash
# Check Node.js version
node --version

# Check npm version
npm --version

# Check dependencies
npm list --depth=0

# Check for outdated packages
npm outdated

# Run local dev server
npm run docs:dev
```

#### Build and Deployment Dashboard
```bash
# Check recent builds
ls -lt .vitepress/dist/ | head -10

# Check build logs
cat build.log | tail -50

# Check deployed version
curl -s https://portfolio.company.com/version.json | jq .

# Check CDN cache status
curl -I https://portfolio.company.com | grep -i cache
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Website completely down | Immediate | Emergency rollback, restore service |
| **P0** | All pages returning 404 | Immediate | Restore deployment, check hosting |
| **P1** | Build pipeline failing | 30 minutes | Fix build errors, investigate changes |
| **P1** | Page load time > 5 seconds | 1 hour | Optimize assets, check CDN |
| **P1** | Search functionality broken | 1 hour | Rebuild index, check search service |
| **P2** | Broken links detected (>10) | 4 hours | Fix links, update documentation |
| **P2** | Build time > 2 minutes | 8 hours | Optimize build, review content |
| **P3** | Individual page 404 | 24 hours | Update link, add redirect |
| **P3** | Documentation outdated | 48 hours | Update content, commit changes |

#### Alert Queries

```bash
# Check website availability
if ! curl -sf https://portfolio.company.com > /dev/null; then
  echo "ALERT: Portfolio website is down"
  exit 1
fi

# Check response time
RESPONSE_TIME=$(curl -w "%{time_total}" -o /dev/null -s https://portfolio.company.com)
if (( $(echo "$RESPONSE_TIME > 2.0" | bc -l) )); then
  echo "ALERT: Page load time is ${RESPONSE_TIME}s (threshold: 2s)"
fi

# Check for broken links
BROKEN_LINKS=$(npm run docs:check-links 2>&1 | grep -c "404\|broken")
if [ $BROKEN_LINKS -gt 10 ]; then
  echo "ALERT: $BROKEN_LINKS broken links detected"
fi

# Check build health
if ! npm run docs:build > /dev/null 2>&1; then
  echo "ALERT: VitePress build failing"
  exit 1
fi
```

---

## Standard Operations

### Local Development

#### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/org/Portfolio-Project.git
cd Portfolio-Project/projects/25-portfolio-website

# Install Node.js (if not installed)
# Recommended: Use nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# Install dependencies
npm install

# Verify installation
node --version
npm --version
npm list vitepress
```

#### Run Development Server
```bash
# Start dev server
npm run docs:dev

# Dev server will start at http://localhost:5173

# Start with custom port
npm run docs:dev -- --port 3000

# Start with custom host
npm run docs:dev -- --host 0.0.0.0

# View in browser
open http://localhost:5173
```

#### Hot Reload Development
```bash
# Start dev server (supports hot reload)
npm run docs:dev

# Edit markdown files
vim docs/projects/project-21.md

# Changes automatically reload in browser

# Edit VitePress config
vim docs/.vitepress/config.js

# Server restarts automatically
```

### Content Management

#### Create New Documentation Page
```bash
# Create new project documentation
cat > docs/projects/project-26.md << 'EOF'
# Project 26: Example Project

## Overview
Brief description of the project.

## Architecture
System architecture details.

## Getting Started
```bash
npm install
npm start
```

## Configuration
Configuration details.

## Operations
Operational procedures.
EOF

# Add to sidebar navigation
vim docs/.vitepress/config.js
# Update themeConfig.sidebar

# Preview changes
npm run docs:dev
```

#### Update Existing Documentation
```bash
# Edit documentation
vim docs/projects/project-25.md

# Check for broken links
npm run docs:check-links

# Preview changes locally
npm run docs:dev

# Commit changes
git add docs/
git commit -m "docs: update project 25 documentation"
git push
```

#### Add Images and Assets
```bash
# Create assets directory
mkdir -p docs/public/images/projects/

# Add image
cp ~/screenshots/project-25-dashboard.png docs/public/images/projects/

# Reference in markdown
cat >> docs/projects/project-25.md << 'EOF'

## Dashboard Screenshot
![Project 25 Dashboard](/images/projects/project-25-dashboard.png)
EOF

# Optimize images (optional)
npm install -g sharp-cli
sharp -i docs/public/images/projects/*.png -o docs/public/images/projects/ -f webp

# Preview
npm run docs:dev
```

#### Manage Navigation and Sidebar
```bash
# Edit VitePress configuration
vim docs/.vitepress/config.js

# Example sidebar configuration:
export default {
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Projects', link: '/projects/' },
      { text: 'Guide', link: '/guide/' }
    ],
    sidebar: {
      '/projects/': [
        {
          text: 'Infrastructure Projects',
          items: [
            { text: 'Project 21: Quantum Crypto', link: '/projects/project-21' },
            { text: 'Project 22: Autonomous DevOps', link: '/projects/project-22' },
            { text: 'Project 23: Monitoring', link: '/projects/project-23' },
            { text: 'Project 24: Report Generator', link: '/projects/project-24' },
            { text: 'Project 25: Portfolio Website', link: '/projects/project-25' }
          ]
        }
      ]
    }
  }
}

# Reload and test
npm run docs:dev
```

### Build and Deployment

#### Build Static Site
```bash
# Clean previous build
rm -rf docs/.vitepress/dist

# Build production site
npm run docs:build

# Check build output
ls -lh docs/.vitepress/dist/

# Verify critical files
ls docs/.vitepress/dist/index.html
ls docs/.vitepress/dist/assets/
ls docs/.vitepress/dist/projects/

# Test built site locally
npx serve docs/.vitepress/dist
# Open http://localhost:3000
```

#### Preview Production Build
```bash
# Build site
npm run docs:build

# Preview built site
npm run docs:preview

# Preview starts at http://localhost:4173

# Test production build
curl http://localhost:4173
curl http://localhost:4173/projects/project-25.html
```

#### Deploy to Production
```bash
# Build for production
npm run docs:build

# Deploy to static hosting (example: S3)
aws s3 sync docs/.vitepress/dist/ s3://portfolio-website-prod/ \
  --delete \
  --cache-control "public, max-age=3600"

# Deploy to Netlify
netlify deploy --prod --dir=docs/.vitepress/dist

# Deploy to Vercel
vercel --prod

# Deploy to GitHub Pages
npm run docs:build
git add docs/.vitepress/dist -f
git commit -m "deploy: update website"
git subtree push --prefix docs/.vitepress/dist origin gh-pages

# Verify deployment
curl -I https://portfolio.company.com
```

#### Rollback Deployment
```bash
# Rollback to previous S3 version
aws s3api list-object-versions --bucket portfolio-website-prod --prefix index.html
PREVIOUS_VERSION_ID="abc123"
aws s3api copy-object \
  --bucket portfolio-website-prod \
  --copy-source portfolio-website-prod/index.html?versionId=$PREVIOUS_VERSION_ID \
  --key index.html

# Rollback Netlify deployment
netlify rollback

# Rollback Vercel deployment
vercel rollback

# Verify rollback
curl https://portfolio.company.com
```

### Search Management

#### Configure Search
```bash
# Install search plugin
npm install -D @vitepress/plugin-search

# Configure in .vitepress/config.js
import { defineConfig } from 'vitepress'
import { SearchPlugin } from '@vitepress/plugin-search'

export default defineConfig({
  vite: {
    plugins: [SearchPlugin()]
  }
})

# Rebuild site
npm run docs:build
```

#### Rebuild Search Index
```bash
# Clear search cache
rm -rf docs/.vitepress/cache

# Rebuild site with fresh index
npm run docs:build

# Verify search works
npm run docs:preview
# Test search functionality at http://localhost:4173
```

### Performance Optimization

#### Optimize Build Performance
```bash
# Enable build cache
export VITE_BUILD_CACHE=true
npm run docs:build

# Parallel build (if supported)
npm run docs:build -- --parallel

# Check build time
time npm run docs:build

# Analyze bundle size
npm run docs:build -- --analyze
```

#### Optimize Assets
```bash
# Compress images
npm install -g sharp-cli
sharp -i docs/public/**/*.{png,jpg,jpeg} -o docs/public/ -f webp

# Minify CSS/JS (done automatically by VitePress)

# Enable gzip/brotli compression (server-side)
# For Nginx:
# gzip on;
# gzip_types text/plain text/css application/json application/javascript;

# For S3 CloudFront:
# Enable automatic compression in CloudFront settings
```

#### Monitor Performance
```bash
# Lighthouse audit
npm install -g lighthouse
lighthouse https://portfolio.company.com --output html --output-path ./lighthouse-report.html

# WebPageTest
# Visit https://www.webpagetest.org
# Enter: https://portfolio.company.com

# Check Core Web Vitals
# Use Google PageSpeed Insights
# https://pagespeed.web.dev/?url=https://portfolio.company.com
```

---

## Incident Response

### Detection

**Automated Detection:**
- Website uptime monitoring alerts
- Build pipeline failure notifications
- Performance degradation alerts
- Broken link detection
- Search functionality failures

**Manual Detection:**
```bash
# Check website availability
curl -I https://portfolio.company.com

# Check for errors
curl -s https://portfolio.company.com | grep -i "error\|404\|500"

# Test critical pages
curl -I https://portfolio.company.com/projects/project-21.html
curl -I https://portfolio.company.com/guide/

# Check build status
git log -1 --pretty=format:"%h - %an: %s" --abbrev-commit
ls -lh docs/.vitepress/dist/

# Test search
curl -s https://portfolio.company.com/search?q=kubernetes | grep -q "results"
```

### Triage

#### Severity Classification

### P0: Complete Site Outage
- Website completely inaccessible
- All pages returning 5xx errors
- DNS resolution failure
- Hosting service down

### P1: Major Functionality Loss
- Build pipeline completely broken
- All pages returning 404
- Search functionality broken
- Critical pages unavailable

### P2: Degraded Performance
- Slow page load times (>5s)
- Individual pages broken
- Build warnings/errors
- Multiple broken links (>10)

### P3: Minor Issues
- Individual broken link
- Documentation typos
- Image loading slow
- Build time elevated

### Incident Response Procedures

#### P0: Website Completely Down

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check website status
curl -I https://portfolio.company.com

# 2. Check DNS resolution
nslookup portfolio.company.com
dig portfolio.company.com

# 3. Check hosting service status
# For S3: Check AWS Console or CLI
aws s3 ls s3://portfolio-website-prod/

# For Netlify: Check status
netlify status

# For Vercel: Check deployment
vercel ls

# 4. Check recent deployments
git log --oneline -n 5
```

**Investigation (5-20 minutes):**
```bash
# Check deployment logs
netlify logs  # For Netlify
vercel logs   # For Vercel

# Check S3 bucket permissions
aws s3api get-bucket-policy --bucket portfolio-website-prod

# Check CloudFront distribution (if using)
aws cloudfront get-distribution --id DISTRIBUTION_ID

# Check for recent changes
git diff HEAD~1 HEAD docs/

# Check build logs
cat build.log
```

**Recovery:**
```bash
# Quick rollback to last known good deployment
git revert HEAD
npm run docs:build
netlify deploy --prod

# Or restore from backup
aws s3 sync s3://portfolio-website-backup/latest/ s3://portfolio-website-prod/ --delete

# Or redeploy last known good commit
git checkout <last-good-commit>
npm run docs:build
netlify deploy --prod

# Verify recovery
curl -I https://portfolio.company.com
curl https://portfolio.company.com | grep -q "Portfolio"

# Return to main branch
git checkout main
```

#### P0: All Pages Returning 404

**Investigation:**
```bash
# Check deployment directory
ls -la docs/.vitepress/dist/

# Check if files were deployed
aws s3 ls s3://portfolio-website-prod/

# Check web server configuration
# For Nginx:
sudo nginx -t
cat /etc/nginx/sites-enabled/portfolio

# Check for routing issues
curl -I https://portfolio.company.com/index.html
curl -I https://portfolio.company.com/projects/project-25.html
```

**Recovery:**
```bash
# Rebuild and redeploy
rm -rf docs/.vitepress/dist
npm run docs:build
aws s3 sync docs/.vitepress/dist/ s3://portfolio-website-prod/ --delete

# Or fix routing configuration
# For S3 static website hosting:
aws s3 website s3://portfolio-website-prod/ \
  --index-document index.html \
  --error-document 404.html

# For Nginx, fix rewrite rules:
# location / {
#   try_files $uri $uri/ /index.html;
# }

# Reload Nginx
sudo nginx -s reload

# Verify fix
curl https://portfolio.company.com/projects/project-25.html
```

#### P1: Build Pipeline Failing

**Investigation:**
```bash
# Check build errors
npm run docs:build 2>&1 | tee build-error.log

# Check Node version
node --version

# Check dependencies
npm list
npm outdated

# Check for syntax errors in config
cat docs/.vitepress/config.js | npx prettier --check

# Check for markdown errors
find docs/ -name "*.md" -exec npx markdownlint {} \;
```

**Recovery:**
```bash
# Fix dependency issues
rm -rf node_modules package-lock.json
npm install

# Fix Node version mismatch
nvm install 18
nvm use 18
npm install

# Fix configuration errors
vim docs/.vitepress/config.js
# Fix syntax errors

# Fix markdown errors
vim docs/problematic-file.md

# Retry build
npm run docs:build

# If successful, deploy
npm run docs:deploy
```

#### P1: Search Functionality Broken

**Investigation:**
```bash
# Test search endpoint
curl -s "https://portfolio.company.com/search?q=test"

# Check search index
ls -lh docs/.vitepress/dist/search-index.json

# Check search plugin
npm list | grep search

# Check browser console for errors
# Open https://portfolio.company.com in browser
# Open DevTools → Console
```

**Recovery:**
```bash
# Rebuild search index
rm -rf docs/.vitepress/cache
npm run docs:build

# Reinstall search plugin
npm install -D @vitepress/plugin-search
npm run docs:build

# Deploy updated site
npm run docs:deploy

# Verify search works
curl -s "https://portfolio.company.com/search?q=kubernetes" | grep -q "results"
```

#### P2: Slow Page Load Times

**Investigation:**
```bash
# Measure load time
curl -w "@curl-format.txt" -o /dev/null -s https://portfolio.company.com

# Check asset sizes
du -sh docs/.vitepress/dist/*
find docs/.vitepress/dist -name "*.js" -exec du -h {} \; | sort -rh | head -10

# Check image sizes
find docs/public/images -type f -exec du -h {} \; | sort -rh | head -10

# Run Lighthouse audit
lighthouse https://portfolio.company.com --output json --output-path ./lighthouse.json
cat lighthouse.json | jq '.audits."speed-index".score'
```

**Optimization:**
```bash
# Compress images
npm install -g sharp-cli
find docs/public/images -name "*.png" -exec sharp -i {} -o {} -f webp \;

# Enable CDN caching
# For CloudFront:
aws cloudfront create-invalidation --distribution-id DISTRIBUTION_ID --paths "/*"

# Optimize JavaScript bundles
# Update vite.config.js
vim docs/.vitepress/config.js
# Add build optimizations:
# export default {
#   vite: {
#     build: {
#       minify: 'terser',
#       rollupOptions: {
#         output: {
#           manualChunks: { /* split chunks */ }
#         }
#       }
#     }
#   }
# }

# Rebuild and deploy
npm run docs:build
npm run docs:deploy

# Verify improvement
lighthouse https://portfolio.company.com
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/website-incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Portfolio Website Incident Report

**Date:** $(date)
**Severity:** P1
**Duration:** 30 minutes
**Component:** Build Pipeline

## Timeline
- 14:00: Build pipeline failure detected
- 14:05: Investigation started
- 14:10: Identified outdated Node.js version
- 14:20: Updated Node.js and dependencies
- 14:25: Successful rebuild
- 14:30: Site deployed and verified

## Root Cause
Node.js version mismatch after system update

## Mitigation
- Updated Node.js to v18 LTS
- Locked Node version in .nvmrc
- Rebuilt and deployed site

## Action Items
- [ ] Add Node.js version check to CI/CD
- [ ] Pin Node.js version in Docker image
- [ ] Add pre-build validation
- [ ] Update documentation
- [ ] Add automated build health checks

EOF

# Update documentation
git add docs/
git commit -m "docs: add incident resolution notes"
git push
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: "npm run docs:dev" fails

**Symptoms:**
```bash
$ npm run docs:dev
Error: Cannot find module 'vitepress'
```

**Diagnosis:**
```bash
# Check Node.js version
node --version

# Check npm installation
npm --version

# Check dependencies
npm list vitepress
```

**Solution:**
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Or update Node.js
nvm install 18
nvm use 18
npm install

# Retry
npm run docs:dev
```

---

#### Issue: Broken links in documentation

**Symptoms:**
- Links return 404
- Relative links not working

**Diagnosis:**
```bash
# Check for broken links
npm run docs:check-links

# Or manually
find docs/ -name "*.md" -exec grep -H "\[.*\](.*)" {} \;

# Test specific link
curl -I https://portfolio.company.com/projects/missing-page.html
```

**Solution:**
```bash
# Fix broken links
vim docs/projects/project-25.md
# Update: [Link](/old-path) → [Link](/new-path)

# Or add redirect
# In docs/.vitepress/config.js:
# export default {
#   rewrites: {
#     'old-path.md': 'new-path.md'
#   }
# }

# Rebuild
npm run docs:build

# Verify
npm run docs:check-links
```

---

#### Issue: Images not loading

**Symptoms:**
- Images show broken icon
- 404 for image paths

**Diagnosis:**
```bash
# Check image exists
ls docs/public/images/project-25.png

# Check image path in markdown
grep -r "project-25.png" docs/

# Check deployed image
curl -I https://portfolio.company.com/images/project-25.png
```

**Solution:**
```bash
# Fix image path
# Correct: ![Image](/images/project-25.png)
# NOT: ![Image](../public/images/project-25.png)

# Or copy image to correct location
cp ~/image.png docs/public/images/

# Rebuild and redeploy
npm run docs:build
npm run docs:deploy
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 1 hour (Git commits)
- **RTO** (Recovery Time Objective): 15 minutes (redeploy from Git)

### Backup Strategy

**Source Code Backup:**
```bash
# All source in Git
git remote -v
git log --oneline -n 5

# Automated Git backups
# Ensure regular commits and pushes

# Mirror repository
git clone --mirror https://github.com/org/Portfolio-Project.git
```

**Deployed Site Backup:**
```bash
# Backup deployed S3 site
aws s3 sync s3://portfolio-website-prod/ s3://portfolio-website-backup/$(date +%Y%m%d)/

# Automated daily backup
cat > /etc/cron.daily/portfolio-website-backup << 'EOF'
#!/bin/bash
aws s3 sync s3://portfolio-website-prod/ s3://portfolio-website-backup/latest/
find /backup/portfolio-website/ -type d -mtime +30 -exec rm -rf {} +
EOF
chmod +x /etc/cron.daily/portfolio-website-backup
```

### Disaster Recovery Procedures

**Complete Loss of Hosting:**
```bash
# 1. Clone repository
git clone https://github.com/org/Portfolio-Project.git
cd Portfolio-Project/projects/25-portfolio-website

# 2. Install dependencies
nvm use 18
npm install

# 3. Build site
npm run docs:build

# 4. Deploy to new hosting
# Option 1: Deploy to S3
aws s3 sync docs/.vitepress/dist/ s3://portfolio-website-new/ --delete
aws s3 website s3://portfolio-website-new/ \
  --index-document index.html \
  --error-document 404.html

# Option 2: Deploy to Netlify
netlify deploy --prod --dir=docs/.vitepress/dist

# Option 3: Deploy to Vercel
vercel --prod

# 5. Update DNS
# Point portfolio.company.com to new hosting

# 6. Verify
curl https://portfolio.company.com
```

---

## Maintenance Procedures

### Daily Tasks
```bash
# Check website availability
curl -I https://portfolio.company.com

# Check for broken links (automated)
npm run docs:check-links

# Review analytics (if configured)
# Check visitor counts, popular pages, errors
```

### Weekly Tasks
```bash
# Update dependencies
npm outdated
npm update

# Run security audit
npm audit
npm audit fix

# Review and update documentation
git pull
# Review recent changes

# Test build
npm run docs:build
```

### Monthly Tasks
```bash
# Update Node.js
nvm install --lts
nvm use --lts
npm install

# Performance audit
lighthouse https://portfolio.company.com

# Review and archive old content
# Update project statuses
# Add new projects

# Test disaster recovery
# Follow DR drill procedures

# Update this runbook
git pull
vim RUNBOOK.md
```

---

## Quick Reference

### Most Common Operations
```bash
# Start dev server
npm run docs:dev

# Build site
npm run docs:build

# Preview production build
npm run docs:preview

# Check for broken links
npm run docs:check-links

# Deploy to production
npm run docs:deploy

# View logs
npm run docs:build 2>&1 | tee build.log
```

### Emergency Response
```bash
# P0: Website down
curl -I https://portfolio.company.com
git checkout <last-good-commit>
npm run docs:build
npm run docs:deploy

# P1: Build failing
npm run docs:build 2>&1 | tee error.log
rm -rf node_modules && npm install
npm run docs:build

# P1: Search broken
rm -rf docs/.vitepress/cache
npm run docs:build
npm run docs:deploy

# P2: Slow performance
lighthouse https://portfolio.company.com --output html
# Review and optimize based on report
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Platform Engineering Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates

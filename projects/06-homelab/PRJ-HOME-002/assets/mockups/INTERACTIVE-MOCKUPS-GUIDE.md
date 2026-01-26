# INTERACTIVE MOCKUPS GUIDE
## How to Use Your Portfolio Visual Evidence

**Created:** November 6, 2025
**Author:** Claude
**Purpose:** Instructions for screenshotting and using the HTML mockups

---

## 📋 What You Have

I've created 5 production-quality interactive HTML mockups:

1. **grafana-dashboard.html** - Infrastructure monitoring dashboard
2. **wikijs-documentation.html** - Documentation platform interface
3. **homeassistant-dashboard.html** - Smart home control panel
4. **proxmox-datacenter.html** - Virtualization management interface
5. **nginx-proxy-manager.html** - Reverse proxy configuration

All files are saved in: `projects/06-homelab/PRJ-HOME-002/assets/mockups/`

---

## 🖥️ How to Take Screenshots

### Method 1: Browser Built-in Tools (Recommended)

**Chrome/Edge:**
1. Open the HTML file in browser (File → Open)
2. Press F12 to open DevTools
3. Press Ctrl+Shift+P (Cmd+Shift+P on Mac)
4. Type "screenshot" and select "Capture full size screenshot"
5. Image saves to Downloads folder

**Firefox:**
1. Open the HTML file
2. Press F12
3. Click the "..." menu in DevTools
4. Select "Take a screenshot of the entire page"

### Method 2: Online Tools

**Easiest Option: LambdaTest Screenshot Tool**
- URL: https://www.lambdatest.com/free-online-tools/screenshot
- Upload your HTML file
- Select resolution: 1920x1080
- Download PNG

**Alternative: Screely.com**
- URL: https://www.screely.com/
- Upload screenshot from Method 1
- Adds browser chrome and background
- Makes it look more professional

---

## 📐 Recommended Screenshot Specs

For portfolio presentation:
- **Resolution:** 1920x1080 (Full HD)
- **Format:** PNG (better quality than JPG)
- **File size:** Under 2MB (use TinyPNG to compress if needed)
- **Naming:** Use descriptive names:
  - `homelab-grafana-monitoring-dashboard.png`
  - `homelab-wikijs-documentation-page.png`
  - `homelab-homeassistant-smart-home.png`
  - `homelab-proxmox-vm-management.png`
  - `homelab-nginx-reverse-proxy.png`

---

## ✨ Enhancement Tips

### Add Browser Chrome (makes it look real)

1. Take basic screenshot first
2. Go to https://browserframe.com/
3. Upload your screenshot
4. Select browser type (Chrome recommended)
5. Download with browser frame

### Add Annotations (for presentations)

Use tools like:
- **Snagit** (paid, best quality)
- **Greenshot** (free, Windows)
- **Skitch** (free, Mac)
- **draw.io** (free, web-based)

Add annotations for:
- Callouts highlighting key features
- Arrows showing data flow
- Labels explaining metrics
- Circles emphasizing important elements

---

## 📊 How to Use in Portfolio

### 1. GitHub Portfolio README

```markdown
## Homelab Infrastructure

### Monitoring & Observability
![Grafana Dashboard](images/homelab-grafana-monitoring-dashboard.png)
*Real-time monitoring of 6 VMs and 3 containers using Prometheus + Grafana*

### Documentation
![Wiki.js Platform](images/homelab-wikijs-documentation-page.png)
*Internal documentation platform with 234 pages covering infrastructure, runbooks, and procedures*

### Infrastructure Management
![Proxmox VE](images/homelab-proxmox-vm-management.png)
*Proxmox hypervisor managing 48GB RAM, 32 cores, running production services*
```

### 2. LinkedIn Portfolio Section

**Upload Process:**
1. LinkedIn Profile → Featured section → Add Media
2. Upload each screenshot
3. Add title and description

**Sample Description:**
```
Homelab Monitoring Dashboard

Built comprehensive observability stack using:
• Prometheus for metrics collection
• Grafana for visualization
• 6 VMs + 3 containers monitored
• Custom dashboards for CPU, memory, disk I/O
• Alertmanager integration for Slack notifications

This infrastructure supports my learning and demonstration of:
- Systems administration
- Infrastructure as code
- Production reliability practices
- Monitoring and observability
```

### 3. Resume Portfolio Link

Add to resume:
```
PROJECTS
Homelab Infrastructure (2023-Present)
• Built production-grade home network from scratch
• View portfolio: github.com/yourusername/homelab-portfolio
  [QR code linking to portfolio]
```

### 4. Interview Presentations

**Create PowerPoint/Google Slides:**

Slide 1: Title
- "Production Homelab Infrastructure"
- "System Development Portfolio"

Slide 2: Architecture Overview
- Network diagram (from Part 2)
- VLAN segmentation
- Service architecture

Slide 3: Monitoring (Grafana screenshot)
- "Real-time observability across 9 services"
- Key metrics highlighted

Slide 4: Documentation (Wiki.js screenshot)
- "Comprehensive runbooks and procedures"
- 200+ pages of technical documentation

Slide 5: Smart Home Integration (Home Assistant)
- "IoT automation with 20+ devices"
- Demonstrates API integration skills

Slide 6: Virtualization (Proxmox)
- "Resource management and optimization"
- Shows infrastructure management skills

Slide 7: Security (Nginx Proxy Manager)
- "Reverse proxy with SSL termination"
- Automated certificate management

Slide 8: Outcomes
- "99.5% uptime over 45 days"
- "Automated backups with 1-hour RPO"
- "Zero data loss incidents"

---

## 🎨 Making Screenshots Look Professional

### Before Taking Screenshot:

1. **Full screen the browser** (F11 in most browsers)
2. **Zoom to 100%** (Ctrl+0)
3. **Wait for animations** to complete
4. **Remove distractions** (close unnecessary tabs shown in browser)

### After Taking Screenshot:

1. **Crop appropriately**
   - Remove unnecessary white space
   - Keep aspect ratio reasonable
   - Focus on content, not empty areas

2. **Compress file size**
   - Use TinyPNG.com
   - Target: Under 500KB for web
   - Under 2MB for print

3. **Add context if needed**
   - Subtle drop shadow (Photoshop/GIMP)
   - Light border (1px #e0e0e0)
   - Background gradient (for presentations)

---

## 🔄 Interactive Demo Option

**Instead of static screenshots, you can:**

1. Host HTML files on GitHub Pages:
   ```bash
   # In your portfolio repo
   mkdir demos
   cp *.html demos/
   git add demos/
   git commit -m "Add interactive demos"
   git push
   ```

2. Enable GitHub Pages in repo settings

3. Access at: `https://yourusername.github.io/portfolio/demos/grafana-dashboard.html`

4. Add to resume as QR code or link:
   ```
   Interactive Demo: yourusername.github.io/portfolio/demos
   ```

**Advantages:**
- Interviewers can click around
- Shows attention to detail
- Demonstrates web development skills
- More impressive than static images

---

## 📱 Mobile Screenshot Option

For Home Assistant dashboard specifically:

1. Open in browser
2. Press F12 (DevTools)
3. Click "Toggle device toolbar" (Ctrl+Shift+M)
4. Select "iPhone 14 Pro" or "Pixel 7"
5. Take screenshot
6. Shows mobile app interface design

---

## ✅ Screenshot Checklist

Before finalizing your portfolio:

- [ ] All screenshots taken at 1920x1080
- [ ] File sizes optimized (< 2MB each)
- [ ] Consistent naming convention used
- [ ] No sensitive information visible (passwords, real IPs if confidential)
- [ ] Browser chrome added for realism (optional)
- [ ] Annotations added where helpful
- [ ] Images look sharp (not blurry)
- [ ] Colors render correctly
- [ ] Text is readable at portfolio size
- [ ] Aspect ratios maintained (no squishing)

---

## 🎯 Portfolio Impact Metrics

Use these screenshots to demonstrate:

**Systems Administration:**
- Proxmox screenshot shows: VM management, resource allocation
- Metric: "Managing 6 VMs with 48GB RAM allocation"

**Monitoring/Observability:**
- Grafana screenshot shows: Custom dashboards, real-time metrics
- Metric: "Monitoring 9 services with 99.8% uptime"

**Documentation:**
- Wiki.js screenshot shows: Technical writing, knowledge management
- Metric: "Created 200+ pages of runbooks and procedures"

**Automation:**
- Home Assistant screenshot shows: IoT integration, automation
- Metric: "Automated 15+ home devices with custom workflows"

**Security:**
- Nginx screenshot shows: SSL management, reverse proxy
- Metric: "Secured 5 services with automated SSL certificates"

---

## 🚀 Next Steps

1. **Take all 5 screenshots** using Chrome full-page capture
2. **Compress images** using TinyPNG
3. **Upload to GitHub** in portfolio repo `/images` folder
4. **Update README** with embedded images
5. **Create LinkedIn post** featuring one screenshot
6. **Add to resume** as portfolio link
7. **Prepare demo** for interviews (bookmark HTML files)

---

## 💡 Pro Tips

1. **Consistency is key**: Use same browser, same resolution for all screenshots
2. **Quality over quantity**: 5 great screenshots > 20 mediocre ones
3. **Tell a story**: Arrange screenshots to show full infrastructure stack
4. **Add metrics**: Every screenshot should have quantifiable achievements
5. **Keep originals**: Save high-res versions separately
6. **Version control**: Name files with dates if iterating (v2, v3, etc.)
7. **Test on mobile**: View portfolio on phone to ensure images scale
8. **Get feedback**: Show to peers before finalizing

---

## 📧 Portfolio Presentation Template

Subject: System Development Engineer Application - Sam Jackson

```
Hi [Hiring Manager],

I'm excited to apply for the System Development Engineer position. I've built
a production-grade homelab infrastructure that demonstrates my skills in:

• Infrastructure management (Proxmox, 6 VMs, 3 containers)
• Monitoring & observability (Prometheus, Grafana, Loki)
• Automation & IaC (Terraform, Docker Compose)
• Database administration (PostgreSQL, high availability)

Interactive portfolio: github.com/yourusername/homelab-portfolio
[Include your best screenshot as inline image]

Key achievements:
- 99.5% uptime across 9 services over 45 days
- Automated backup strategy with 1-hour RPO
- Comprehensive monitoring with custom Grafana dashboards
- Documentation platform with 200+ technical pages

I'd love to discuss how my experience building and operating production
infrastructure translates to the SDE role at [Company].

Best regards,
Sam Jackson
```

---

## 🎬 Demo Video Script (Optional)

If creating a video walkthrough:

```
[0:00-0:15] Introduction
"Hi, I'm Sam. Today I'll show you my homelab infrastructure that I built
to learn production operations."

[0:15-0:45] Architecture Overview
[Show network diagram]
"The infrastructure includes 6 VMs running on Proxmox, with services
including Wiki.js, Home Assistant, Immich photo management, and a
centralized PostgreSQL database."

[0:45-1:30] Monitoring Demo
[Open Grafana dashboard]
"I've implemented comprehensive monitoring using Prometheus and Grafana.
You can see real-time CPU, memory, and network metrics across all services."

[1:30-2:15] Management Demo
[Open Proxmox interface]
"Proxmox manages all virtualization, with resource allocation optimized
per workload. Each VM is backed up nightly to a dedicated backup server."

[2:15-2:45] Documentation
[Open Wiki.js]
"I maintain detailed documentation covering architecture, runbooks,
troubleshooting procedures, and operational notes."

[2:45-3:00] Closing
"This infrastructure demonstrates my ability to design, build, and operate
production systems. Thanks for watching!"
```

---

## 📊 Success Metrics

Track portfolio effectiveness:
- GitHub stars/forks: Indicates interest from community
- LinkedIn post engagement: Likes, comments, shares
- Interview requests mentioning portfolio: Direct attribution
- Questions asked about infrastructure: Shows depth perceived

Aim for:
- 50+ GitHub stars in first month
- 100+ LinkedIn post views
- 3+ interview requests mentioning portfolio
- 2+ technical deep-dive conversations

---

**Remember:** The goal is not just to show pretty pictures, but to demonstrate
your ability to build, operate, and document production infrastructure. Each
screenshot should tell a story of technical capability and professional maturity.

Good luck with your job search! 🚀

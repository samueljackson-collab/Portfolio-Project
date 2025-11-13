# Quick Start Guide: Adding Your Code to GitHub

**Purpose:** Fast reference for uploading code from local zip folders to this portfolio repository

---

## 🎯 What You Need

Your portfolio needs these missing assets directories:

```
projects/06-homelab/PRJ-HOME-001/assets/  ← Network diagrams, configs
projects/06-homelab/PRJ-HOME-002/assets/  ← Service configs, backups
projects/01-sde-devops/PRJ-SDE-002/assets/ ← Dashboards, monitoring configs
projects/08-web-data/PRJ-WEB-001/assets/  ← Code samples, diagrams
professional/resume/                      ← Resume PDFs
```

📖 **Detailed breakdown:** See `MISSING_DOCUMENTS_ANALYSIS.md`

> 🆕 **Enterprise templates (P01–P20)** are located in `projects-new/`. See [`projects-new/QUICK_START_GUIDE.md`](./projects-new/QUICK_START_GUIDE.md) for a deep dive, or jump directly with `cd projects-new/P01-aws-infra`.

---

## 🚀 Three Methods (Pick One)

### Method 1: GitHub Web Interface (Easiest)
**Best for:** Small files, quick uploads

1. Go to https://github.com/samueljackson-collab/Portfolio-Project
2. Navigate to desired directory
3. Click "Add file" → "Upload files"
4. Drag your files, add commit message
5. Click "Commit changes"

**Limitations:** 100 files max, 25MB per file

---

### Method 2: GitHub Desktop (User-Friendly)
**Best for:** Non-technical users, visual interface

1. **Install:** Download from https://desktop.github.com/
2. **Clone:** File → Clone Repository → Select this repo
3. **Add Files:** 
   - Extract your zip
   - Copy files to the cloned folder
   - GitHub Desktop auto-detects changes
4. **Commit & Push:**
   - Review changes
   - Enter commit message
   - Click "Commit to main"
   - Click "Push origin"

---

### Method 3: Git Command Line (Most Powerful)
**Best for:** Large uploads, power users

#### One-Time Setup
```bash
# Install Git (if not already installed)
# Windows: https://git-scm.com/
# Mac: brew install git
# Linux: sudo apt-get install git

# Configure Git
git config --global user.name "Sam Jackson"
git config --global user.email "your-email@example.com"

# Clone repository
cd ~/Documents
git clone https://github.com/samueljackson-collab/Portfolio-Project.git
cd Portfolio-Project
```

#### Every Time You Add Files

```bash
# 1. Create missing directories (first time only)
mkdir -p projects/06-homelab/PRJ-HOME-001/assets/{diagrams,configs,docs}
mkdir -p projects/06-homelab/PRJ-HOME-002/assets/{diagrams,configs,screenshots}
mkdir -p projects/01-sde-devops/PRJ-SDE-002/assets/{dashboards,configs,screenshots}

# 2. Extract your zip and copy files
unzip ~/Downloads/my-files.zip -d /tmp/extracted
cp -r /tmp/extracted/* projects/06-homelab/PRJ-HOME-001/assets/diagrams/

# 3. Check what you're adding
git status
git diff

# 4. Add files
git add projects/06-homelab/PRJ-HOME-001/assets/

# 5. Commit with descriptive message
git commit -m "Add network diagrams for PRJ-HOME-001"

# 6. Push to GitHub
git push origin main

# 7. Verify on GitHub
# Visit: https://github.com/samueljackson-collab/Portfolio-Project
```

---

## 📁 Where to Put Your Files

### Homelab Network (PRJ-HOME-001)
```
projects/06-homelab/PRJ-HOME-001/assets/
├── diagrams/
│   ├── network-topology.png         ← Physical/logical network
│   └── vlan-layout.png              ← VLAN design
├── configs/
│   ├── unifi-export.json            ← UniFi config (sanitized)
│   └── firewall-rules.md            ← Firewall documentation
└── docs/
    └── setup-guide.md               ← How you built it
```

### Virtualization (PRJ-HOME-002)
```
projects/06-homelab/PRJ-HOME-002/assets/
├── diagrams/
│   └── service-architecture.png     ← VM/container layout
├── configs/
│   ├── docker-compose-*.yml         ← Service configs
│   └── nginx-proxy.json             ← Reverse proxy setup
└── screenshots/
    └── dashboard.png                ← Proxmox/services
```

### Observability (PRJ-SDE-002)
```
projects/01-sde-devops/PRJ-SDE-002/assets/
├── dashboards/
│   └── *.json                       ← Grafana dashboards
├── configs/
│   ├── prometheus.yml               ← Monitoring config
│   └── alertmanager.yml             ← Alert rules
└── screenshots/
    └── dashboard-*.png              ← Live dashboard views
```

### E-commerce Recovery (PRJ-WEB-001)
```
projects/08-web-data/PRJ-WEB-001/assets/
├── code/
│   ├── sql/*.sql                    ← SQL scripts (sanitized)
│   └── php/*.php                    ← Code excerpts
├── diagrams/
│   └── architecture.png             ← System design
└── docs/
    └── runbooks/*.md                ← Operational guides
```

### Resumes
```
professional/resume/
├── 2025-11-04_Jackson_Sam_SystemDevelopmentEngineer.pdf
├── 2025-11-04_Jackson_Sam_CloudEngineer.pdf
└── 2025-11-04_Jackson_Sam_QAEngineer.pdf
```

---

## ⚠️ Before You Upload - Security Checklist

**MUST sanitize these in all files:**

- [ ] Real IP addresses → Use 10.0.0.0, 192.168.0.0, or example.com
- [ ] Passwords/API keys → Remove or use placeholders: `YOUR_PASSWORD_HERE`
- [ ] Real domain names → Use example.com
- [ ] Email addresses → Use example@example.com
- [ ] Client names → Remove or anonymize
- [ ] Personal photos → Remove or blur
- [ ] Screenshot sensitive data → Crop or blur

**Files to NEVER commit:**
- `terraform.tfvars` (has secrets)
- `.env` files (has secrets)
- Private keys (`.pem`, `.key`)
- Large binaries (>100MB - use Git LFS)

---

## 🔧 Common Commands

```bash
# Check status
git status

# See what changed
git diff

# Add specific file
git add path/to/file.txt

# Add entire directory
git add projects/06-homelab/

# Add everything (careful!)
git add .

# Undo staging (before commit)
git reset path/to/file.txt

# Commit with message
git commit -m "Add diagrams for homelab project"

# Push to GitHub
git push origin main

# Pull latest changes
git pull origin main

# Create new branch
git checkout -b my-feature-branch

# Switch branches
git checkout main
```

---

## 🐛 Troubleshooting

### "Authentication failed"
```bash
# Use personal access token instead of password
# Create token at: https://github.com/settings/tokens
# Use token as password when prompted
```

### "File too large" (>100MB)
```bash
# Use Git LFS
git lfs install
git lfs track "*.zip"
git add .gitattributes
git commit -m "Configure Git LFS"
git add large-file.zip
git commit -m "Add large file"
git push
```

### "Merge conflict"
```bash
# Pull first, then push
git pull origin main
# Resolve conflicts if any
git add .
git commit -m "Resolve merge conflict"
git push origin main
```

### "Permission denied"
```bash
# Check SSH keys or use HTTPS with token
git remote set-url origin https://github.com/samueljackson-collab/Portfolio-Project.git
```

---

## 📞 Need More Help?

1. **Detailed guide:** Read `MISSING_DOCUMENTS_ANALYSIS.md`
2. **Git documentation:** https://git-scm.com/doc
3. **GitHub guides:** https://guides.github.com/
4. **GitHub Desktop help:** https://docs.github.com/en/desktop

---

## ✅ Quick Checklist

Before you finish:

- [ ] All asset directories created
- [ ] Files copied to correct locations
- [ ] Sensitive data sanitized
- [ ] Files committed and pushed
- [ ] Verified on GitHub web interface
- [ ] Updated README if needed (remove "being prepared" notes)

---

**Last Updated:** November 4, 2025

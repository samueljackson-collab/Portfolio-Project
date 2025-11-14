# 📁 Portfolio Assets

Visual assets and supporting materials for the portfolio.

## 📂 Directory Structure

```
assets/
├── diagrams/           # Architecture diagrams (Mermaid, PNG)
├── screenshots/        # Project screenshots
│   ├── homelab/       # Homelab infrastructure
│   ├── aws/           # AWS cloud projects
│   ├── monitoring/    # Monitoring dashboards
│   ├── kubernetes/    # Kubernetes deployments
│   ├── database/      # Database projects
│   └── demos/         # Demo application screenshots
├── videos/            # Demo videos and recordings
└── exports/           # Generated reports and exports
```

## 🎨 Asset Guidelines

### Screenshots
- **Resolution**: 1920x1080 minimum
- **Format**: PNG (optimized)
- **Naming**: descriptive-kebab-case.png
- **Privacy**: Redact sensitive information

### Diagrams
- **Source**: Mermaid (.mmd files)
- **Export**: PNG and SVG
- **Style**: Consistent color scheme
- **Labels**: Clear and professional

### Videos
- **Format**: MP4 (H.264)
- **Resolution**: 1080p
- **Length**: 2-5 minutes max
- **Audio**: Optional narration

## 🚀 Quick Commands

```bash
# Generate diagrams
python3 ../scripts/generate-diagrams.py

# Optimize screenshots
find screenshots/ -name "*.png" -exec optipng -o2 {} \; 2>/dev/null || true

# Count assets
find . -type f | wc -l

# View diagram in browser (Mermaid Live)
# Copy .mmd file content and paste at https://mermaid.live
```

## 📊 Current Asset Inventory

Run the metrics script to get current counts:
```bash
python3 ../scripts/portfolio-metrics.py
```

## 📸 Screenshot Organization

Screenshots are organized by project category:

- **homelab/** - Proxmox, VMs, networking, storage
- **aws/** - VPC, EC2, RDS, CloudWatch, Terraform
- **monitoring/** - Prometheus, Grafana, Loki, Alertmanager
- **kubernetes/** - Clusters, deployments, services, ArgoCD
- **database/** - PostgreSQL, backups, replication
- **demos/** - Interactive HTML mockups and demos

## 🎨 Architecture Diagrams

Current diagrams available in `diagrams/`:

1. **homelab-architecture.mmd** - Complete homelab infrastructure
2. **aws-vpc-architecture.mmd** - AWS VPC multi-AZ design
3. **monitoring-stack.mmd** - Observability infrastructure
4. **kubernetes-cicd.mmd** - K8s CI/CD pipeline
5. **postgresql-ha.mmd** - PostgreSQL high availability

### Viewing Diagrams

**Option 1: Mermaid Live Editor**
```bash
# Copy diagram content and paste at https://mermaid.live
cat diagrams/homelab-architecture.mmd
```

**Option 2: Convert to PNG**
```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Convert diagrams
mmdc -i diagrams/homelab-architecture.mmd -o diagrams/homelab-architecture.png
```

**Option 3: VS Code**
```bash
# Install Mermaid Preview extension
# Open .mmd file and press Ctrl+Shift+V
```

## 📋 Asset Checklist

Use this checklist when adding new project assets:

- [ ] Screenshots captured at 1920x1080+
- [ ] Personal/sensitive info redacted
- [ ] Images optimized (PNG compression)
- [ ] Files named descriptively
- [ ] Organized in appropriate category folder
- [ ] Architecture diagram created (if applicable)
- [ ] README updated with asset references

---

*Managed assets for the enterprise portfolio project*

#!/bin/bash
###############################################################################
# Portfolio Infrastructure Setup Script
# Sets up complete portfolio directory structure and automation
###############################################################################

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

###############################################################################
# Setup Functions
###############################################################################

setup_directories() {
    print_header "Setting Up Directory Structure"

    # Create main directories
    mkdir -p {assets,demos,docs,scripts}/{diagrams,screenshots,html-mockups}
    mkdir -p assets/{diagrams,screenshots,videos,exports}
    mkdir -p demos/{html-mockups,live-demos,recordings}
    mkdir -p docs/{guides,architecture,templates,business-cases}

    # Create project-specific asset directories
    mkdir -p assets/screenshots/{homelab,aws,monitoring,kubernetes,database,demos}

    print_success "Directory structure created"
    tree -L 2 -d assets demos docs 2>/dev/null || ls -la assets/ demos/ docs/
}

generate_diagrams() {
    print_header "Generating Architecture Diagrams"

    if [ -f "scripts/generate-diagrams.py" ]; then
        python3 scripts/generate-diagrams.py
        print_success "Diagrams generated"
    else
        print_info "Diagram generator not found, skipping"
    fi
}

create_documentation_index() {
    print_header "Creating Documentation Index"

    cat > docs/README.md << 'EOF'
# 📚 Portfolio Documentation Hub

## Quick Navigation

### 🎯 Getting Started
- [Quick Start Guide](../QUICK_START_GUIDE.md)
- [Portfolio Overview](../README.md)
- [Project Structure](./architecture/project-structure.md)

### 📖 Technical Guides
- [Homelab Setup Guide](./guides/homelab-setup.md)
- [AWS Infrastructure Guide](./guides/aws-infrastructure.md)
- [Monitoring Stack Guide](./guides/monitoring-setup.md)
- [Kubernetes Deployment Guide](./guides/kubernetes-deployment.md)

### 🏗️ Architecture Documentation
- [System Architecture Overview](./architecture/system-overview.md)
- [Network Design](./architecture/network-design.md)
- [Security Architecture](./architecture/security-design.md)
- [High Availability Design](./architecture/ha-design.md)

### 💼 Business & Career
- [Business Case Studies](./business-cases/)
- [Resume Templates](../professional/resume/)
- [Portfolio Presentation](./templates/portfolio-presentation.md)

### 🔧 Implementation Guides
- [Docker Compose Setup](./guides/docker-compose.md)
- [Terraform Deployment](./guides/terraform-deployment.md)
- [CI/CD Pipeline Setup](./guides/cicd-setup.md)
- [Backup & Recovery](./guides/backup-recovery.md)

## 📊 Documentation Statistics

- Total Documents: 600+ pages
- Technical Guides: 50+
- Architecture Diagrams: 20+
- Code Examples: 100+

## 🚀 Quick Actions

```bash
# Generate all diagrams
python3 scripts/generate-diagrams.py

# Take screenshots
bash scripts/take-screenshots.sh

# Run metrics analysis
python3 scripts/portfolio-metrics.py

# Build documentation site
mkdocs build  # if using MkDocs
```

## 📞 Support

For questions or issues, please refer to the main [README](../README.md) or create an issue in the repository.

---

*Last updated: $(date +%Y-%m-%d)*
EOF

    print_success "Documentation index created"
}

create_assets_readme() {
    print_header "Creating Assets README"

    cat > assets/README.md << 'EOF'
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
find screenshots/ -name "*.png" -exec optipng -o2 {} \;

# Count assets
find . -type f | wc -l
```

## 📊 Asset Inventory

Run the metrics script to get current counts:
```bash
python3 ../scripts/portfolio-metrics.py
```

---

*Managed assets for the portfolio project*
EOF

    print_success "Assets README created"
}

create_master_setup_readme() {
    print_header "Creating Scripts README"

    cat > scripts/README.md << 'EOF'
# 🛠️ Portfolio Automation Scripts

Automation tools for managing and building the portfolio.

## 📜 Available Scripts

### Core Scripts

#### `generate-diagrams.py`
Generate architecture diagrams from Mermaid definitions.

```bash
python3 generate-diagrams.py
```

**Generates**:
- Homelab architecture
- AWS VPC design
- Monitoring stack
- Kubernetes CI/CD
- PostgreSQL HA

**Output**: `assets/diagrams/*.mmd`

#### `take-screenshots.sh`
Interactive guide for capturing project screenshots.

```bash
bash take-screenshots.sh
```

**Features**:
- Step-by-step screenshot guide
- Category organization
- Verification tools
- Image optimization

#### `portfolio-metrics.py`
Analyze portfolio completion and generate metrics.

```bash
python3 portfolio-metrics.py
```

**Reports**:
- Overall completion percentage
- Project status breakdown
- Documentation statistics
- Infrastructure inventory

**Output**: `portfolio-metrics.json`, `portfolio-badge.json`

#### `setup-portfolio-infrastructure.sh`
One-command setup for complete portfolio infrastructure.

```bash
bash setup-portfolio-infrastructure.sh
```

**Actions**:
- Create directory structure
- Generate diagrams
- Create documentation indexes
- Run initial metrics scan

## 🚀 Quick Start

```bash
# Run complete setup
bash setup-portfolio-infrastructure.sh

# Generate all assets
python3 generate-diagrams.py
bash take-screenshots.sh

# Check progress
python3 portfolio-metrics.py
```

## 📋 Prerequisites

### Python 3.8+
```bash
python3 --version
```

### Optional Tools
```bash
# For screenshot optimization
sudo apt install optipng pngquant

# For diagram conversion (optional)
npm install -g @mermaid-js/mermaid-cli
```

## 🔧 Configuration

Scripts use these directory conventions:
- `assets/` - Visual assets
- `demos/` - Demo applications
- `docs/` - Documentation
- `projects/` - Project code

## 📊 Metrics Output

The metrics script generates:

**portfolio-metrics.json**
```json
{
  "overall_completion": 65,
  "projects": {
    "total": 22,
    "completed": 8,
    "in_progress": 6
  }
}
```

**portfolio-badge.json** (for shields.io)
```json
{
  "label": "portfolio completion",
  "message": "65%",
  "color": "yellow"
}
```

## 🎯 Best Practices

1. **Run metrics regularly** to track progress
2. **Generate diagrams** before documentation updates
3. **Optimize screenshots** before committing
4. **Verify assets** with metrics script

## 📞 Support

For issues or questions, see the main [README](../README.md).

---

*Portfolio automation toolkit*
EOF

    print_success "Scripts README created"
}

run_initial_metrics() {
    print_header "Running Initial Metrics Scan"

    if [ -f "scripts/portfolio-metrics.py" ]; then
        python3 scripts/portfolio-metrics.py
    else
        print_info "Metrics script not found, skipping"
    fi
}

create_quick_start_guide() {
    print_header "Creating Quick Start Guide"

    cat > PORTFOLIO_INFRASTRUCTURE_GUIDE.md << 'EOF'
# 🚀 Portfolio Infrastructure Quick Start

## Overview

This portfolio includes comprehensive automation tools for:
- 📊 Progress tracking and metrics
- 🎨 Architecture diagram generation
- 📸 Screenshot organization
- 📚 Documentation management
- 🏗️ Infrastructure as Code

## Initial Setup

### 1. Run Infrastructure Setup

```bash
bash scripts/setup-portfolio-infrastructure.sh
```

This creates:
- Complete directory structure
- Documentation indexes
- Initial metrics baseline
- Architecture diagrams

### 2. Generate Visual Assets

```bash
# Generate all architecture diagrams
python3 scripts/generate-diagrams.py

# Interactive screenshot guide
bash scripts/take-screenshots.sh
```

### 3. Track Progress

```bash
# Run metrics analysis
python3 scripts/portfolio-metrics.py

# View metrics
cat portfolio-metrics.json
```

## Directory Structure

```
Portfolio-Project/
├── portfolio-website/      # GitHub Pages landing site
├── assets/                # Visual assets
│   ├── diagrams/         # Architecture diagrams
│   ├── screenshots/      # Project screenshots
│   └── videos/          # Demo recordings
├── demos/                # Demo applications
├── docs/                 # Technical documentation
├── projects/             # Project implementations
└── scripts/              # Automation tools
```

## Daily Workflow

### Adding a New Project

1. Create project directory in `projects/`
2. Add README.md with status indicators
3. Implement code and documentation
4. Take screenshots: `bash scripts/take-screenshots.sh`
5. Update metrics: `python3 scripts/portfolio-metrics.py`

### Updating Documentation

1. Edit markdown files in `docs/`
2. Generate diagrams if needed
3. Update architecture docs
4. Commit and push changes

### Preparing for Review

1. **Generate all assets**:
   ```bash
   python3 scripts/generate-diagrams.py
   bash scripts/take-screenshots.sh
   ```

2. **Run quality checks**:
   ```bash
   python3 scripts/portfolio-metrics.py
   ```

3. **Optimize images**:
   ```bash
   find assets/screenshots -name "*.png" -exec optipng -o2 {} \;
   ```

4. **Review metrics**:
   ```bash
   cat portfolio-metrics.json
   ```

## Deployment

### GitHub Pages

The portfolio website auto-deploys via GitHub Actions:

1. Push to `main` branch
2. GitHub Actions runs
3. Site deploys to: `https://samueljackson-collab.github.io/Portfolio-Project/`

### Enable GitHub Pages

1. Go to: Repository Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main` or `gh-pages`
4. Folder: `/portfolio-website` or root

## Metrics & Reporting

### Available Metrics

- **Overall completion** percentage
- **Project counts** by status
- **Implementation status** (code, docs, tests)
- **Documentation** statistics
- **Infrastructure** inventory

### Generate Reports

```bash
# Full analysis
python3 scripts/portfolio-metrics.py

# Output files
ls -l portfolio-metrics.json
ls -l portfolio-badge.json
```

### Use Metrics in README

Add completion badge:
```markdown
![Completion](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/samueljackson-collab/Portfolio-Project/main/portfolio-badge.json)
```

## Troubleshooting

### Scripts Not Executable

```bash
chmod +x scripts/*.sh scripts/*.py
```

### Python Dependencies

```bash
pip install -r requirements.txt
```

### Directory Not Found

```bash
bash scripts/setup-portfolio-infrastructure.sh
```

## Next Steps

1. ✅ Run initial setup
2. ✅ Generate diagrams
3. ✅ Take screenshots
4. ✅ Review metrics
5. ⬜ Complete high-priority projects
6. ⬜ Deploy to GitHub Pages
7. ⬜ Share with recruiters

## Resources

- [Main README](./README.md)
- [Scripts Documentation](./scripts/README.md)
- [Documentation Hub](./docs/README.md)
- [Project Templates](./docs/templates/)

---

*Infrastructure guide for portfolio automation*
EOF

    print_success "Quick start guide created"
}

###############################################################################
# Main Execution
###############################################################################

main() {
    clear
    cat << 'EOF'
╔═══════════════════════════════════════════════════════════╗
║     Portfolio Infrastructure Setup                        ║
║     Comprehensive automation and structure                ║
╚═══════════════════════════════════════════════════════════╝
EOF

    setup_directories
    create_documentation_index
    create_assets_readme
    create_master_setup_readme
    create_quick_start_guide
    generate_diagrams
    run_initial_metrics

    print_header "Setup Complete!"

    cat << EOF

${GREEN}✨ Portfolio infrastructure is ready!${NC}

📁 Created:
   - Complete directory structure
   - Documentation indexes
   - Asset organization
   - Automation scripts

🚀 Next Steps:

   1. Generate diagrams:
      ${BLUE}python3 scripts/generate-diagrams.py${NC}

   2. Capture screenshots:
      ${BLUE}bash scripts/take-screenshots.sh${NC}

   3. Track progress:
      ${BLUE}python3 scripts/portfolio-metrics.py${NC}

   4. View the quick start guide:
      ${BLUE}cat PORTFOLIO_INFRASTRUCTURE_GUIDE.md${NC}

   5. Deploy to GitHub Pages:
      ${BLUE}git add . && git commit -m "feat: Add portfolio infrastructure" && git push${NC}

📚 Documentation:
   - Setup Guide: PORTFOLIO_INFRASTRUCTURE_GUIDE.md
   - Scripts: scripts/README.md
   - Docs Hub: docs/README.md

EOF
}

# Run main function
main

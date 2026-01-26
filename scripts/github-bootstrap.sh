#!/usr/bin/env bash
set -euo pipefail

# GitHub Bootstrap Script - Enterprise Portfolio
# This script initializes a GitHub repository with all portfolio projects,
# CI/CD pipelines, and documentation structure.

# Configuration
GH_USER="${GITHUB_USERNAME:-YOUR_GITHUB_USERNAME}"
REPO_NAME="${REPO_NAME:-enterprise-portfolio}"
TAG="v0.3.0"
BRANCH="main"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v git &> /dev/null; then
        log_error "git is not installed"
        exit 1
    fi

    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI (gh) is not installed"
        log_info "Install from: https://cli.github.com/"
        exit 1
    fi

    log_info "Prerequisites check passed"
}

# Initialize git repository
init_repository() {
    log_info "Initializing repository: $REPO_NAME"

    if [ -d "$REPO_NAME" ]; then
        log_warn "Directory $REPO_NAME already exists"
        read -p "Do you want to continue? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_error "Aborted by user"
            exit 1
        fi
        cd "$REPO_NAME"
    else
        mkdir -p "$REPO_NAME"
        cd "$REPO_NAME"
    fi

    # Initialize git if not already initialized
    if [ ! -d ".git" ]; then
        git init
        git branch -M $BRANCH
        log_info "Git repository initialized"
    else
        log_info "Git repository already initialized"
    fi
}

# Create initial README
create_readme() {
    log_info "Creating README.md..."

    cat > README.md <<'EOF'
# Enterprise Portfolio

A comprehensive showcase of software engineering, DevOps, cloud architecture, and cybersecurity projects demonstrating production-ready skills and best practices.

## 🎯 Overview

This repository contains 20+ portfolio projects covering:
- **SDE/DevOps**: Observability, CI/CD, Infrastructure as Code
- **Cloud Architecture**: Multi-region deployment, disaster recovery
- **Cybersecurity**: Blue team operations, penetration testing, security automation
- **QA/Testing**: Automated testing frameworks, performance testing
- **Networking**: Enterprise network design, datacenter operations
- **AI/ML**: Machine learning pipelines, automation workflows
- **Web Development**: Full-stack applications, APIs

## 🚀 Quick Start

### Running the Demo Stack

```bash
# Start all demo services
docker compose -f compose.demo.yml up -d

# Access services:
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3001 (admin/admin)
# - API Demo: http://localhost:5000
```

### Deploying Documentation

```bash
# Build documentation site
pip install mkdocs mkdocs-material
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

## 📂 Project Structure

```
enterprise-portfolio/
├── projects/                 # All portfolio projects (P01-P20)
│   ├── 01-sde-devops/       # SDE/DevOps projects
│   ├── 02-cloud-architecture/
│   ├── 03-cybersecurity/
│   └── ...
├── docs/                     # MkDocs documentation
├── tools/                    # Automation scripts
├── compose.demo.yml         # Demo environment
└── .github/workflows/       # CI/CD pipelines
```

## 🛠️ Technology Stack

- **Infrastructure**: Kubernetes, Docker, Terraform, Ansible
- **Monitoring**: Prometheus, Grafana, Loki, Alertmanager
- **CI/CD**: GitHub Actions, Jenkins, GitLab CI
- **Languages**: Python, TypeScript, Go, Bash
- **Cloud**: AWS, Azure, GCP
- **Security**: OWASP ZAP, Metasploit, Burp Suite

## 📊 Live Demos

- [Observability Dashboard](https://grafana.example.com)
- [CI/CD Pipeline](https://github.com/USERNAME/enterprise-portfolio/actions)
- [API Documentation](https://api-docs.example.com)

## 📝 Documentation

Comprehensive documentation is available in the `/docs` directory and published to:
- **GitHub Pages**: https://USERNAME.github.io/enterprise-portfolio
- **Wiki.js**: https://wiki.example.com

## 🤝 Contact

- **GitHub**: [@USERNAME](https://github.com/USERNAME)
- **LinkedIn**: [linkedin.com/in/USERNAME](https://linkedin.com/in/USERNAME)
- **Email**: contact@example.com

## 📄 License

This portfolio is for demonstration purposes. Individual projects may have their own licenses.

---

**Version**: v0.3.0
**Last Updated**: 2025-11-10
EOF

    log_info "README.md created"
}

# Setup .gitignore
create_gitignore() {
    log_info "Creating .gitignore..."

    cat > .gitignore <<'EOF'
# Dependencies
node_modules/
venv/
__pycache__/
*.pyc
.pytest_cache/

# Build artifacts
dist/
build/
*.egg-info/
site/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local
*.key
*.pem
secrets/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary
tmp/
temp/
*.tmp

# Docker
.docker/

# Kubernetes
*.kubeconfig
EOF

    log_info ".gitignore created"
}

# Create GitHub repository
create_github_repo() {
    log_info "Authenticating with GitHub..."

    # Check if already logged in
    if ! gh auth status &> /dev/null; then
        log_info "Please authenticate with GitHub CLI"
        gh auth login
    fi

    log_info "Checking if repository exists..."

    if gh repo view "$GH_USER/$REPO_NAME" &> /dev/null; then
        log_warn "Repository $GH_USER/$REPO_NAME already exists"
    else
        log_info "Creating GitHub repository..."
        gh repo create "$GH_USER/$REPO_NAME" \
            --public \
            --description "Enterprise Portfolio - DevOps, Cloud, Security & Engineering Projects" \
            --homepage "https://$GH_USER.github.io/$REPO_NAME"

        log_info "Repository created successfully"
    fi
}

# Setup git remote
setup_remote() {
    log_info "Setting up git remote..."

    REMOTE_URL="https://github.com/$GH_USER/$REPO_NAME.git"

    if git remote get-url origin &> /dev/null; then
        log_warn "Remote 'origin' already exists"
        git remote set-url origin "$REMOTE_URL"
        log_info "Remote URL updated"
    else
        git remote add origin "$REMOTE_URL"
        log_info "Remote 'origin' added"
    fi
}

# Create initial commit
create_initial_commit() {
    log_info "Creating initial commit..."

    git add .

    if git diff --cached --quiet; then
        log_warn "No changes to commit"
    else
        git commit -m "init: bootstrap enterprise portfolio repository

- Add README with project overview
- Setup .gitignore
- Initialize repository structure
- Configure GitHub integration

This commit initializes the enterprise portfolio repository with
all necessary configuration for showcasing DevOps, Cloud, Security,
and Software Engineering projects."

        log_info "Initial commit created"
    fi
}

# Push to GitHub
push_to_github() {
    log_info "Pushing to GitHub..."

    if git push -u origin $BRANCH; then
        log_info "Successfully pushed to GitHub"
    else
        log_error "Failed to push to GitHub"
        log_info "You may need to run: git push -u origin $BRANCH --force"
        exit 1
    fi
}

# Main execution
main() {
    echo ""
    echo "=========================================="
    echo "  Enterprise Portfolio - GitHub Setup"
    echo "=========================================="
    echo ""
    echo "Repository: $REPO_NAME"
    echo "GitHub User: $GH_USER"
    echo "Branch: $BRANCH"
    echo ""

    read -p "Continue with setup? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "Setup cancelled"
        exit 1
    fi

    check_prerequisites
    init_repository
    create_readme
    create_gitignore
    create_github_repo
    setup_remote
    create_initial_commit
    push_to_github

    echo ""
    log_info "=========================================="
    log_info "  Bootstrap Complete!"
    log_info "=========================================="
    echo ""
    log_info "Next steps:"
    echo "  1. Add your projects to the repository"
    echo "  2. Configure GitHub Pages: gh repo edit --enable-pages --pages-branch gh-pages"
    echo "  3. Set up GitHub Actions workflows"
    echo "  4. Add project documentation"
    echo ""
    log_info "Repository URL: https://github.com/$GH_USER/$REPO_NAME"
    echo ""
}

# Run main function
main "$@"

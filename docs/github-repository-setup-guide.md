# GitHub Repository Setup Guide – Complete Implementation

> **Purpose:** Create professional, recruiter-ready GitHub repositories with strong documentation, CI/CD, and automation for portfolio projects.
>
> **Version:** 1.0  
> **Last Updated:** October 11, 2025  
> **Estimated Time:** 3–5 hours per portfolio suite  
> **Skill Level:** Beginner-Friendly

---

## 📋 Table of Contents

1. [Why GitHub for Portfolio Projects](#-why-github-for-portfolio-projects)
2. [Prerequisites](#-prerequisites)
3. [Account Setup](#-account-setup)
4. [Creating Your First Repository](#-creating-your-first-repository)
5. [Repository Structure Best Practices](#-repository-structure-best-practices)
6. [README.md Creation](#-readmemd-creation)
7. [Branch Protection Rules](#-branch-protection-rules)
8. [GitHub Actions CI/CD Setup](#-github-actions-cicd-setup)
9. [Secrets Management](#-secrets-management)
10. [GitHub Pages Deployment](#-github-pages-deployment)
11. [Repository Settings & Optimization](#-repository-settings--optimization)
12. [Creating an Organization (Optional)](#-creating-an-organization-optional)
13. [Best Practices & Tips](#-best-practices--tips)
14. [Troubleshooting](#-troubleshooting)

---

## 🎯 Why GitHub for Portfolio Projects

### What GitHub Provides

**For Recruiters**
- ✅ Instant access to code and documentation
- ✅ Proof of consistent technical activity
- ✅ Visibility into version control habits
- ✅ Evidence of mature engineering workflows (CI/CD, testing, docs)

**For You**
- ✅ Free hosting for code and documentation
- ✅ Branching, reviews, and collaboration tooling
- ✅ Automated CI/CD with GitHub Actions
- ✅ GitHub Pages for static documentation sites
- ✅ Built-in issue tracking and project boards
- ✅ Professional public presence

### What This Guide Delivers

By following the steps you will have:
- ✅ Professional, standardized repositories for each portfolio project
- ✅ Compelling READMEs tailored for recruiters
- ✅ Branch protection to prevent accidental regressions
- ✅ Automated CI/CD pipelines with Terraform validation and security scans
- ✅ Secure secret management practices
- ✅ Optional documentation microsite via GitHub Pages

---

## ✅ Prerequisites

### Required Knowledge
- [ ] Basic Git commands (`git init`, `git add`, `git commit`, `git push`)
- [ ] Command-line familiarity (navigation, editing, running scripts)

If you are new to Git, complete the [Git Basics tutorial](https://git-scm.com/book/en/v2/Getting-Started-Git-Basics).

### Required Software

Install Git on your workstation.

**Windows (Chocolatey)**
```powershell
choco install git
```

**macOS (Homebrew)**
```bash
brew install git
```

**Ubuntu/Debian**
```bash
sudo apt-get update
sudo apt-get install git
```

**Verify**
```bash
git --version
# git version 2.x.x
```

### Optional but Recommended

- [ ] **GitHub CLI (`gh`)** – simplified auth, repo creation, PRs. Install from [cli.github.com](https://cli.github.com/).
- [ ] **Visual Studio Code** – excellent Git integration. Download from [code.visualstudio.com](https://code.visualstudio.com/).

---

## 🔐 Account Setup

### Step 1: Create a GitHub Account

1. Visit [github.com/signup](https://github.com/signup).
2. Provide a professional email, strong password, and memorable username.
   - ✅ `jane-doe-dev`
   - ✅ `john-smith-engineer`
   - ❌ `coolguy123`
3. Verify your email and select the free plan (plenty for portfolios).

### Step 2: Configure Git Locally

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# Set main as the default branch
git config --global init.defaultBranch main

# Windows: normalize line endings
git config --global core.autocrlf input
```

### Step 3: Set Up SSH Keys (Recommended)

```bash
ssh-keygen -t ed25519 -C "you@example.com"
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

Copy the public key (`~/.ssh/id_ed25519.pub`) and add it to GitHub under **Settings → SSH and GPG keys**. Test with:

```bash
ssh -T git@github.com
# Hi username! You've successfully authenticated...
```

---

## 📦 Creating Your First Repository

### Step 1: Choose a Structure

Prefer one repository per flagship project. It keeps history focused and lets you tailor documentation for each audience.

### Step 2: Create a Repository (Web UI)

1. Visit [github.com/new](https://github.com/new).
2. Name the repo `aws-multi-tier-architecture` (kebab-case, descriptive).
3. Add a short description highlighting scope and impact.
4. Set visibility to **Public** (recommended for portfolios).
5. Initialize with a README, Terraform `.gitignore`, and MIT license.

**GitHub CLI equivalent**
```bash
gh repo create aws-multi-tier-architecture \
  --public \
  --description "Production-grade 3-tier AWS architecture" \
  --gitignore Terraform \
  --license mit
```

### Step 3: Clone Locally

```bash
mkdir -p ~/github-projects
cd ~/github-projects

git clone git@github.com:your-username/aws-multi-tier-architecture.git
cd aws-multi-tier-architecture

git remote -v
```

You now have a local working copy.

---

## 📁 Repository Structure Best Practices

Use a clean, predictable layout like the structure below (already scaffolded in this repository).

```
aws-multi-tier-architecture/
├── README.md
├── LICENSE
├── .gitignore
├── docs/
│   ├── architecture.md
│   ├── deployment.md
│   ├── troubleshooting.md
│   ├── cost-analysis.md
│   ├── security.md
│   └── adr/
│       ├── 001-multi-az.md
│       └── 002-database-choice.md
├── infrastructure/
│   └── terraform/
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── modules/
│           ├── vpc/
│           ├── compute/
│           └── database/
├── scripts/
│   ├── deploy.sh
│   ├── destroy.sh
│   └── validate.sh
├── tests/
│   ├── unit/
│   └── integration/
├── .github/
│   └── workflows/
│       ├── terraform-validate.yml
│       └── security-scan.yml
├── docs-site/
│   └── index.html
└── examples/
    └── terraform.tfvars.example
```

---

## 📝 README.md Creation

Your README is the first impression. Treat it like a project landing page.

### Professional README Template

```markdown
# AWS Multi-Tier Architecture with Terraform

> Production-grade 3-tier architecture demonstrating infrastructure as code, high availability, and security best practices.

[![Terraform](https://img.shields.io/badge/Terraform-1.6%2B-623CE4?logo=terraform&logoColor=white)](https://www.terraform.io/)
[![AWS](https://img.shields.io/badge/AWS-Cloud-orange?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Architecture Diagram](docs/images/architecture.png)
```

Continue the README with:
- Table of contents
- Overview and business impact
- Architecture diagram and explanation
- Features, prerequisites, quick start, cost, security, contributing, license, contact

Update badges to match your GitHub Actions workflow URLs:

```markdown
[![Terraform Validation](https://github.com/your-username/aws-multi-tier-architecture/actions/workflows/terraform-validate.yml/badge.svg)](https://github.com/your-username/aws-multi-tier-architecture/actions/workflows/terraform-validate.yml)
[![Security Scan](https://github.com/your-username/aws-multi-tier-architecture/actions/workflows/security-scan.yml/badge.svg)](https://github.com/your-username/aws-multi-tier-architecture/actions/workflows/security-scan.yml)
```

---

## 🔒 Branch Protection Rules

1. Navigate to **Settings → Branches → Add rule**.
2. Target branch pattern `main`.
3. Recommended options:
   - ✅ Require pull request reviews (1 approval suffices for solo projects).
   - ✅ Dismiss stale approvals when new commits land.
   - ✅ Require status checks to pass (`terraform-validate`, `security-scan`).
   - ✅ Require branches to be up to date before merging.
   - ✅ Require conversation resolution.
   - ✅ Enforce linear history.
4. Save the rule. Main is now protected from force pushes and unreviewed merges.

---

## 🔄 GitHub Actions CI/CD Setup

Two workflows are included:

### Terraform Validation
- Triggers on pushes to `main` and `develop`, PRs into `main`, or manual runs.
- Runs `terraform fmt`, `init` (local backend), `validate`, and `tflint`.

### Security Scan
- Runs on pushes/PRs to `main` plus a weekly cron.
- Executes Trivy (filesystem scan) and Checkov (Terraform misconfiguration scan).
- Uploads SARIF results to the repository's Security tab.

Review `.github/workflows/*.yml` to customize Terraform versions or add additional checks.

---

## 🔐 Secrets Management

Never commit credentials or `.tfvars` with secrets. Instead:

1. Navigate to **Settings → Secrets and variables → Actions → New repository secret**.
2. Add the following at minimum:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`
3. Reference secrets in workflows using `${{ secrets.AWS_ACCESS_KEY_ID }}`.

Local safety nets:
- `.gitignore` already excludes `.env`, `*.tfvars`, `*.pem`, etc.
- Use `.example` suffixes for sample configs (see `examples/terraform.tfvars.example`).

---

## 🌐 GitHub Pages Deployment

1. Create a lightweight docs site (see `docs-site/index.html`).
2. Go to **Settings → Pages** and set source to `main` branch, `/docs-site` folder.
3. Optionally map a custom domain and enable HTTPS.

Link to the published site from the README so recruiters can browse documentation quickly.

---

## ⚙️ Repository Settings & Optimization

- **About panel:** Add a succinct description, project website, and tags (e.g., `terraform`, `aws`, `devops`).
- **Features:** Enable Issues and Projects; disable Wiki/Discussions if unused.
- **Merge options:** Allow squash merging, disable merge commits/rebase to maintain linear history.
- **Automatically delete head branches** after merging PRs.
- **Community health:** Add `CONTRIBUTING.md` and `SECURITY.md` if you invite feedback.

---

## 🏢 Creating an Organization (Optional)

Separate personal tinkering from polished portfolio work:

1. Profile → **Your organizations** → **New organization**.
2. Choose the free plan and name it `your-name-portfolio`.
3. Transfer project repositories to the organization (Settings → Danger Zone → Transfer ownership).
4. Update README links to reflect new URLs.

---

## 💡 Best Practices & Tips

### Commit Hygiene

Use descriptive commit messages following `<type>: <summary>`.

- ✅ `feat: add compute module with autoscaling group`
- ✅ `docs: expand troubleshooting with GitHub Pages section`
- ❌ `update`
- ❌ `misc fixes`

Common prefixes: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.

### Keep the Repo Clean

Commit:
- Source code, infrastructure definitions, docs, tests
- Configuration examples (`.example` files)

Ignore:
- Secrets, `.tfvars`, `.env`
- Large binaries and build outputs
- IDE-specific metadata (covered by `.gitignore`)

### Maintenance Cadence

- Weekly: triage issues, merge PRs, refresh README if needed.
- Monthly: update dependencies, review CI results, rotate secrets, prune branches.

### Portfolio Presentation Tips

- Pin top repositories to your GitHub profile.
- Cross-link live demos, case studies, and LinkedIn posts.
- Keep commit history active; recruiters often check the contribution graph.
- Respond to issues professionally, even if the project is solo.

---

## 🔧 Troubleshooting

### Cannot Push to Repository
- Check remote URL (`git remote -v`).
- Pull latest changes with `git pull --rebase origin main`.
- Confirm SSH key is loaded (`ssh -T git@github.com`).
- For protected branches, push to a feature branch and open a PR.

### GitHub Actions Fail
- Inspect workflow logs under the **Actions** tab.
- Ensure Terraform files are formatted (`terraform fmt`).
- Confirm secrets exist for AWS credentials.
- Re-run the job after fixing issues.

### GitHub Pages 404
- Verify `docs-site/index.html` exists on `main`.
- Confirm Pages source is set to `/docs-site`.
- Wait a few minutes for deployment and check the Pages build log if enabled.

---

## 📋 Next Steps Checklist

- [ ] Duplicate this structure for each flagship project.
- [ ] Customize README and documentation per project.
- [ ] Configure branch protection rules.
- [ ] Set up GitHub Actions secrets and monitor workflow runs.
- [ ] Enable GitHub Pages and link from README.
- [ ] Pin repositories on your profile and share the polished GitHub URL with recruiters.

---

## 📚 Additional Resources

- [GitHub Docs](https://docs.github.com/)
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Actions Guide](https://docs.github.com/en/actions)
- [Terraform + GitHub Actions Tutorial](https://learn.hashicorp.com/tutorials/terraform/github-actions)
- [Markdown Guide](https://www.markdownguide.org/)

---

**Guide Version:** 1.0  
**Last Updated:** October 11, 2025  
**Maintained by:** Your Name

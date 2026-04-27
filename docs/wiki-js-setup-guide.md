# Wiki.js Setup Guide - Complete Implementation

> **Purpose:** Step-by-step guide to deploy Wiki.js for your portfolio documentation. This guide covers everything from installation to content migration.
>
> **Version:** 1.0  
> **Last Updated:** October 11, 2025  
> **Estimated Time:** 2-4 hours  
> **Skill Level:** Beginner-Friendly

---

## 📋 Table of Contents

1. [What is Wiki.js and Why Use It](#what-is-wikijs-and-why-use-it)
2. [Prerequisites](#prerequisites)
3. [Quickstart: Deploy Wiki.js in 10 Steps](#quickstart-deploy-wikijs-in-10-steps)
4. [Quickstart: GitHub & Documentation Workflow](#quickstart-github-and-documentation-workflow)
5. [Deployment Options Overview](#deployment-options-overview)
6. [Method 1: Docker Compose Deployment (Recommended)](#method-1-docker-compose-deployment)
7. [Method 2: Node.js + PM2 Service Installation](#method-2-nodejs-pm2-installation)
8. [Method 3: Kubernetes Deployment (Production Scale)](#method-3-kubernetes-deployment)
9. [Initial Configuration](#initial-configuration)
10. [Content Organization Strategy](#content-organization-strategy)
11. [Migrating Portfolio Documentation](#migrating-portfolio-documentation)
12. [User Management & Access Control](#user-management-access-control)
13. [Backup & Recovery](#backup-and-recovery)
14. [Customization & Theming](#customization-and-theming)
15. [Troubleshooting](#troubleshooting)

---

<a id="what-is-wikijs-and-why-use-it"></a>
## 🎯 What is Wiki.js and Why Use It

### What is Wiki.js?

**Simple Explanation:**
> Wiki.js is a modern, open-source wiki platform that lets you organize and share documentation in a beautiful, searchable format. Think of it as Wikipedia for your personal or team documentation.

**Technical Description:**
> Wiki.js is a NodeJS-based wiki engine with built-in Markdown support, Git synchronization, multiple authentication providers, and a modern API. It's designed for creating documentation sites with minimal configuration.

### Why Use Wiki.js for Your Portfolio?

**Benefits:**

1. **Professional Presentation**
   - Clean, modern interface impresses recruiters
   - Mobile-responsive design
   - Professional appearance vs. raw markdown files

2. **Easy Navigation**
   - Built-in search functionality
   - Hierarchical page organization
   - Tag-based categorization

3. **Content Management**
   - Version control integrated with Git
   - Multiple editors (Markdown, WYSIWYG)
   - Media management for images/diagrams

4. **Collaboration Ready**
   - Multi-user support
   - Access control per page
   - Comment system (optional)

5. **Portfolio Showcase**
   - Demonstrates ability to deploy web applications
   - Shows system administration skills
   - Proves documentation best practices

**What You'll Have After This Guide:**
- ✅ Fully functional Wiki.js instance
- ✅ Portfolio documentation migrated and organized
- ✅ Professional documentation site to share with recruiters
- ✅ Automated backups configured
- ✅ SSL/TLS security enabled

---

<a id="prerequisites"></a>
## ✅ Prerequisites

### Required Knowledge
- [ ] **Basic command line usage**
  - Navigate directories (`cd`, `ls`)
  - Edit files (`nano`, `vim`)
  - Run commands with sudo

- [ ] **Basic understanding of web servers**
  - What a domain/subdomain is
  - What ports are (80, 443)
  - Basic HTTP concepts

### Required Software

**For Docker Compose Setup (Easiest):**
- [ ] Docker Desktop or Docker Engine installed
- [ ] Docker Compose installed (v2.0+)
- [ ] Text editor (VS Code, nano, etc.)
- [ ] Web browser

**System Requirements:**
- **Minimum:**
  - 1 CPU core
  - 1 GB RAM
  - 5 GB disk space
  - Internet connection

- **Recommended:**
  - 2 CPU cores
  - 2 GB RAM
  - 10 GB disk space
  - Fast internet connection

### Optional (But Recommended)

- [ ] **Domain name** (for public access)
  - Free option: Use DuckDNS or NoIP for subdomain
  - Paid option: Purchase domain from Namecheap, Google Domains, etc.

- [ ] **SSL Certificate** (for HTTPS)
  - Free: Let's Encrypt (automated)
  - Included in this guide

- [ ] **Cloud server** (if not using localhost)
  - AWS EC2 t3.micro (free tier eligible)
  - DigitalOcean Droplet ($6/month)
  - Linode Nanode ($5/month)

---

<a id="quickstart-deploy-wikijs-in-10-steps"></a>
## 🚀 Quickstart: Deploy Wiki.js in 10 Steps

> **Use this section when you need Wiki.js running fast.** Each step links back to the in-depth method for deeper context.

| Step | What to Do | Why it Matters | Command / Reference |
|------|------------|----------------|---------------------|
| 1 | **Provision a host and point your domain** (`wiki.example.com`) | Guarantees TLS readiness and clean URLs | Cloud console + [Prerequisites](#prerequisites) |
| 2 | **Install Docker & Docker Compose** (or Docker Desktop) | Provides the container runtime used throughout the guide | [`setup-prerequisites.sh`](#method-1-docker-compose-deployment) |
| 3 | **Clone the portfolio repo & create the Wiki workspace** | Keeps infrastructure-as-docs alongside project code | `git clone <repo>` → `mkdir -p wiki-portfolio/{data,config,logs,backups}` |
| 4 | **Generate secrets and create `.env`** | Stores credentials outside of version control | [`setup-environment.sh`](#method-1-docker-compose-deployment) |
| 5 | **Drop in `docker-compose.yml`** from Method 1 | Defines Wiki.js, PostgreSQL, and networking in one declarative file | [Docker Compose stack](#method-1-docker-compose-deployment) |
| 6 | **Configure HTTPS with Nginx + Certbot** | Delivers production TLS and security headers from day one | [`config/nginx.conf`](#method-1-docker-compose-deployment) + `certbot --nginx` |
| 7 | **Launch the stack** | Brings the containers online | `docker-compose up -d` |
| 8 | **Run the health script** | Confirms the app, database, and certificate are functioning | [`health-check.sh`](#method-1-docker-compose-deployment) |
| 9 | **Complete the web installer** (`/setup`) | Creates the admin account and seeds the schema | Browser → `https://wiki.example.com/setup` |
| 10 | **Schedule backups & document baseline** | Ensures recovery and captures the first state of the wiki | [`backup-wiki.sh`](#backup-and-recovery) + initial home page draft |

✅ **Outcome:** Wiki.js served over HTTPS with monitored containers, ready for portfolio content.

🛠 **Need a different runtime?** Jump to [Node.js + PM2](#method-2-nodejs-pm2-installation) or [Kubernetes](#method-3-kubernetes-deployment) after completing Step 1 for alternative infrastructures.

---

<a id="quickstart-github-and-documentation-workflow"></a>
## 📦 Quickstart: GitHub & Documentation Workflow

> **Follow these repeatable steps for each of the 25 portfolio projects.** The flow keeps code, automation, and knowledge in sync.

1. **Standardize your local project folder**
   - Use the `portfolio/projects/<project-number>-<name>/` pattern so docs and code line up.
   - Include `README.md`, `docs/`, `infrastructure/`, and `scripts/` directories in every project.

2. **Initialize Git and capture the baseline**
   ```bash
   cd portfolio/projects/1-aws-infrastructure
   git init
   git add .
   git commit -m "feat: bootstrap AWS infrastructure automation"
   ```

3. **Create the GitHub repository** (web UI or CLI)
   ```bash
   gh repo create portfolio-1-aws-infrastructure --public --source=. --remote=origin --push
   ```
   > If you prefer manual setup: `git remote add origin https://github.com/<org>/portfolio-1-aws-infrastructure.git` then `git push -u origin main`.

4. **Define CI/CD early**
   - Add a workflow in `.github/workflows/ci.yml` that runs linting, tests, Terraform plans, etc.
   - Use status badges in each project `README.md` so the wiki can display build health.

5. **Document the project in Wiki.js**
   - Create `/projects/<project-slug>` using the [Project Template](#content-organization-strategy).
   - Embed diagrams, architecture decisions, and link to GitHub repo + CI badge.

6. **Link code and docs through Git sync**
   - In the Wiki.js Admin area → **Storage**, configure Git with a dedicated private repo (e.g., `portfolio-wiki-content`).
   - Enable **Auto Push** and **Auto Pull** so wiki edits track in Git history.

7. **Automate wiki updates from GitHub**
   - Generate a Wiki.js API key (Admin → API).
   - Add a GitHub Actions step that calls the Wiki.js GraphQL API after successful deployments to refresh status tables or changelogs.

8. **Capture operational runbooks**
   - For each CI/CD pipeline, include `/operations/<project>/deployment` and `/operations/<project>/rollback` pages.
   - Reference the scripts stored under `scripts/deployment/` in your repositories.

9. **Verify everything end-to-end**
   - Run the CI pipeline, confirm GitHub shows a green check, and refresh the wiki page to ensure badges + status updates render correctly.
   - Execute `health-check.sh` plus the validation scripts in [`validation/`](#backup-and-recovery) after major releases.

10. **Establish a weekly maintenance cadence**
    - Monday: review open PRs and sync wiki change log.
    - Wednesday: rotate secrets & review backup logs.
    - Friday: export wiki content (`git pull` on the content repo) and archive release notes in `/operations/weekly-reports`.

📚 **Deliverable:** Every project has a GitHub repository, automated pipeline, and a matching Wiki.js knowledge space that stays up to date automatically.

---

<a id="deployment-options-overview"></a>
## 🔀 Deployment Options Overview

### Option 1: Docker Compose (⭐ Recommended)

**Best For:** Beginners, quick setup, local development

**Pros:**
- ✅ Fastest setup (15-20 minutes)
- ✅ Easy to upgrade
- ✅ Isolated environment
- ✅ Easy backup/restore
- ✅ Cross-platform (Windows, Mac, Linux)

**Cons:**
- ❌ Requires Docker knowledge
- ❌ Extra layer of abstraction

**Choose this if:** You want the easiest path to a working Wiki.js

---

<a id="method-2-overview"></a>
### Method 2: Node.js + PM2 Service Installation

**Best For:** Administrators who want fine-grained control over the Node.js runtime, plan to co-locate Wiki.js with other services, or need to integrate with existing Linux service management standards.

**Pros:**
- ✅ Maximum flexibility over Node.js, reverse proxies, and database placement
- ✅ Works on bare-metal or minimal VPS instances without container overhead
- ✅ PM2 restarts the app automatically and captures structured logs
- ✅ Easy to extend with custom build or backup scripts

**Cons:**
- ❌ Manual dependency and OS patch management
- ❌ Requires comfort with systemd, firewalls, and Node.js toolchains
- ❌ Upgrades demand change control (stop service, install, restart)
- ❌ Must harden file permissions and secrets manually

**Choose this if:** You need to demonstrate mastery over Linux service management or deploy Wiki.js on hosts where Docker is not permitted.

---

<a id="method-3-overview"></a>
### Method 3: Kubernetes Deployment (Production Scale)

**Best For:** Teams operating an existing Kubernetes cluster who require high availability, GitOps workflows, and self-healing infrastructure for enterprise documentation.

**Pros:**
- ✅ Horizontal scaling with ReplicaSets and StatefulSets
- ✅ Rolling updates and zero-downtime upgrades via Deployments
- ✅ Secrets, ConfigMaps, and Ingress controllers centralize operations
- ✅ Native integration with GitOps tools (Argo CD, Flux) for automation

**Cons:**
- ❌ Requires Kubernetes expertise and cluster access
- ❌ Higher resource footprint (control plane + worker nodes)
- ❌ Certificate, ingress, and storage classes must already exist
- ❌ Debugging spans multiple layers (Pods, Services, PersistentVolumes)

**Choose this if:** You want to showcase platform engineering skills and run Wiki.js as part of a larger microservice ecosystem.

---

<a id="method-1-docker-compose-deployment"></a>
## 🐳 Method 1: Docker Compose Deployment (Recommended)

### Why choose this method
- **What:** Run Wiki.js and PostgreSQL as containers managed by Docker Compose.
- **Why:** Containers provide isolated, reproducible environments that are easy to back up, migrate, and scale horizontally.
- **When:** Ideal for local workstations, single-node servers, or cloud VMs where you want a production-grade deployment without managing packages manually.

### Architecture overview
```
┌──────────────┐      ┌─────────────────┐      ┌────────────────────┐
│   Nginx      │◀────▶│  Wiki.js (Node) │◀────▶│ PostgreSQL Database │
│ (reverse     │      │  Container      │      │   Container        │
│  proxy + SSL)│      │  Port 3000      │      │   Port 5432        │
└──────────────┘      └─────────────────┘      └────────────────────┘
        ▲                    ▲                           ▲
        │                    │                           │
        └────── shared Docker network & persistent volumes ────────┘
```

### Step 1 — Prepare the host environment
- **What:** Install Docker Engine, Docker Compose, and create the base directory structure.
- **Why:** Ensures every deployment starts from a known-good baseline with the correct dependencies and filesystem layout.
- **How:** Run the following script (or execute the commands manually) on Ubuntu/Debian. Adapt package managers accordingly for macOS (`brew`) or Windows (Docker Desktop).

```bash
#!/bin/bash
# setup-prerequisites.sh — install Docker, Docker Compose, and create folders
set -euo pipefail

echo "🔧 Updating system packages"
sudo apt update && sudo apt upgrade -y

echo "🐳 Installing Docker Engine"
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker "$USER"

echo "🧩 Installing Docker Compose v2"
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)"   -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "📁 Creating Wiki.js project directories"
mkdir -p ~/wikijs/{config,data,logs,backups}

echo "✅ Host preparation complete. Log out/in to refresh Docker group membership."
```

After re-login, confirm the installation:

```bash
docker --version
docker-compose --version
docker ps
```

### Step 2 — Lay out persistent storage
- **What:** Create dedicated folders that will be mounted into the containers.
- **Why:** Keeps uploads, configuration, and database data safe across container restarts or upgrades.
- **How:**

```bash
cd ~/wikijs
mkdir -p data/{uploads,storage} config/nginx logs/nginx backups/database
tree -L 2 .
```

Expected structure:

```
wikijs/
├── backups/
│   └── database/
├── config/
│   └── nginx/
├── data/
│   ├── storage/
│   └── uploads/
├── logs/
│   └── nginx/
└── docker-compose.yml   # created in the next step
```

### Step 3 — Generate secrets and environment configuration
- **What:** Store sensitive values (database password, JWT secret, admin email) in a `.env` file that Docker Compose can load automatically.
- **Why:** Separates code from secrets, simplifies rotation, and prevents secrets from being hard-coded into version control.
- **How:**

```bash
cat <<'EOF' > ~/wikijs/generate-env.sh
#!/bin/bash
set -euo pipefail

generate_secret() {
  openssl rand -base64 48 | tr -dc 'A-Za-z0-9' | head -c 32
}

cat > .env <<ENV
# Wiki.js environment (generated $(date -u +"%Y-%m-%dT%H:%M:%SZ"))
DB_PASSWORD=$(generate_secret)
JWT_SECRET=$(generate_secret)
ADMIN_EMAIL=admin@portfolio.local
SITE_URL=https://wiki.example.com
ENABLE_REGISTRATION=false
ENV

chmod 600 .env
echo "✅ .env file created with fresh secrets"
}

generate_secret
EOF

cd ~/wikijs
bash generate-env.sh
```

The resulting `.env` file will be automatically consumed by Docker Compose.

### Step 4 — Author `docker-compose.yml`
- **What:** Define services for Wiki.js (`wiki`), PostgreSQL (`postgres`), and an optional Nginx reverse proxy.
- **Why:** Compose orchestrates dependent services, health checks, and shared networks in a single declarative file.
- **How:**

```yaml
version: "3.9"

services:
  wiki:
    image: requarks/wiki:2.5
    container_name: wikijs-app
    restart: unless-stopped
    env_file: .env
    environment:
      DB_TYPE: postgres
      DB_HOST: postgres
      DB_PORT: 5432
      DB_USER: wikijs
      DB_PASS: ${DB_PASSWORD}
      DB_NAME: wiki
      NODE_ENV: production
      HOST: 0.0.0.0
      PORT: 3000
      LOG_LEVEL: info
    depends_on:
      postgres:
        condition: service_healthy
    ports:
      - "3000:3000"
    volumes:
      - ./data/uploads:/var/wiki/uploads
      - ./data/storage:/var/wiki/storage
      - ./config:/var/wiki/config
      - ./logs:/var/wiki/logs
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 40s

  postgres:
    image: postgres:15
    container_name: wikijs-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: wiki
      POSTGRES_USER: wikijs
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - ./data/database:/var/lib/postgresql/data
      - ./backups/database:/backups
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U wikijs"]
      interval: 30s
      timeout: 10s
      retries: 5

  nginx:
    image: nginx:alpine
    container_name: wikijs-proxy
    restart: unless-stopped
    depends_on:
      wiki:
        condition: service_healthy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./config/ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx

networks:
  default:
    name: wikijs-network
    driver: bridge
```

> **Security reminder:** Rotate `DB_PASSWORD` and `JWT_SECRET` periodically. Update the `.env` file, then restart the containers.

### Step 5 — Configure Nginx for TLS and reverse proxying
- **What:** Terminate HTTPS traffic, enforce security headers, and forward requests to the Wiki.js container.
- **Why:** Wiki.js does not ship with built-in TLS termination. A reverse proxy provides SSL, caching, and request logging.
- **How:** Place the following in `config/nginx/nginx.conf` and add certificates to `config/ssl/` (use Let's Encrypt or the provided self-signed example).

```nginx
events { worker_connections 1024; }

http {
  upstream wikijs {
    server wiki:3000;
  }

  server {
    listen 80;
    server_name wiki.example.com;
    return 301 https://$server_name$request_uri;
  }

  server {
    listen 443 ssl http2;
    server_name wiki.example.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header Strict-Transport-Security "max-age=63072000" always;

    location / {
      proxy_pass http://wikijs;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_read_timeout 300;
    }

    location /health {
      proxy_pass http://wikijs/health;
      access_log off;
    }
  }
}
```

### Step 6 — Deploy and validate
- **What:** Bring up the stack, ensure every service is healthy, and confirm that the application responds.
- **Why:** Early validation catches configuration drift or permission issues before you invest time curating content.
- **How:**

```bash
cd ~/wikijs
docker-compose pull
docker-compose up -d

watch docker-compose ps
```

When each service reports `Up (healthy)`, run health checks:

```bash
curl -I http://localhost:3000/health
docker-compose logs --tail=50 wiki
docker-compose exec postgres pg_isready -U wikijs
```

Optional automation: save the following as `deploy-wiki.sh` to standardize deployments with backups and rollback hooks.

```bash
#!/bin/bash
set -euo pipefail

log() { printf '\e[32m[INFO]\e[0m %s\n' "$1"; }
fail() { printf '\e[31m[ERROR]\e[0m %s\n' "$1"; exit 1; }

[ -f .env ] || fail "Missing .env file"
source .env

log "Validating Docker availability"
command -v docker >/dev/null || fail "Docker not installed"
command -v docker-compose >/dev/null || fail "Docker Compose not installed"

log "Backing up PostgreSQL data"
timestamp=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U wikijs wiki > "backups/database/${timestamp}.sql"

log "Applying compose stack"
docker-compose pull
docker-compose up -d

log "Waiting for health checks"
docker-compose ps
curl -fsS http://localhost:3000/health >/dev/null || fail "Wiki.js health check failed"

log "Deployment complete — visit https://wiki.example.com"
```

Save a lightweight health script alongside your compose file to re-run checks quickly:

```bash
#!/bin/bash
# health-check.sh — verify Wiki.js, PostgreSQL, and TLS endpoints
set -euo pipefail

BASE_URL="https://wiki.example.com"
HOST=${BASE_URL#https://}
HOST=${HOST%%/*}

echo "🔍 Checking container status"
docker-compose ps

echo "🩺 Hitting Wiki.js health endpoint"
curl -fsS "$BASE_URL/health" >/dev/null && echo "Wiki.js OK"

echo "🗄  Verifying PostgreSQL availability"
docker-compose exec -T postgres pg_isready -U wikijs

echo "🔐 Inspecting TLS certificate expiry"
openssl s_client -connect "$HOST:443" -servername "$HOST" < /dev/null 2>/dev/null \
  | openssl x509 -noout -dates

echo "✅ Health check completed"
```

Make it executable with `chmod +x health-check.sh` and run it after upgrades or incident response drills.

### Step 7 — Plan for maintenance and fail-safes
- **Backups:** Schedule the included database dump command via cron; copy `/var/wiki/uploads` and `/var/wiki/storage` regularly.
- **Updates:** Run `docker-compose pull` followed by `docker-compose up -d` during maintenance windows. Always take a backup first.
- **Disaster recovery:** Restore by re-creating the directory structure, placing backups in `backups/database`, and importing them with `psql` before starting the stack.
- **Monitoring:** Use `docker stats`, `docker-compose logs -f`, and Nginx access logs to track performance and detect anomalies early.

<a id="method-2-nodejs-pm2-installation"></a>
## ⚙️ Method 2: Node.js + PM2 Service Installation

### Why choose this method
- **What:** Install Wiki.js directly on the host operating system, manage the process with PM2, and connect to a locally managed PostgreSQL instance.
- **Why:** Provides absolute control over the runtime, makes it easy to integrate with existing backup tooling, and works well on lightweight VPS or environments where containers are restricted.
- **When:** Use this for environments that mandate traditional service management (systemd), or when you want to demonstrate deep Linux administration skills.

### Prerequisites checklist
| Requirement | Recommended Value | Purpose |
|-------------|-------------------|---------|
| Operating System | Ubuntu 22.04 LTS (or similar) | Stable base with long-term support |
| Node.js | 18 LTS (Wiki.js 2.x supports ≥ 16; 18 LTS recommended) | Runs the application server |
| PM2 | Latest | Manages the Node.js process and restarts on failure |
| PostgreSQL | 13+ | Stores wiki content and metadata |
| Firewall access | Ports 80/443 for HTTP/S, 5432 restricted to localhost | Secure external access |

### Step 1 — Prepare the host and service account
- **What:** Update the OS, create a dedicated non-root user, and harden basic permissions.
- **Why:** Running applications as dedicated users limits blast radius and aligns with least-privilege practices.
- **How:**

```bash
sudo apt update && sudo apt upgrade -y
sudo adduser --system --group --home /opt/wiki wikijs
sudo mkdir -p /opt/wiki/{app,logs,config,uploads}
sudo chown -R wikijs:wikijs /opt/wiki
```

### Step 2 — Install Node.js, Yarn, and PM2
- **What:** Set up the JavaScript runtime and process manager.
- **Why:** Wiki.js ships as a Node application that is deployed via compiled assets; Yarn installs dependencies efficiently and PM2 keeps the service running.
- **How:**

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs build-essential
sudo npm install --global yarn pm2

node --version
pm2 --version
```

### Step 3 — Install and configure PostgreSQL
- **What:** Provision the database server and create credentials dedicated to Wiki.js.
- **Why:** Segregating database users simplifies auditing and revocation.
- **How:**

```bash
sudo apt install -y postgresql postgresql-contrib

sudo -u postgres psql <<'SQL'
CREATE DATABASE wiki;
CREATE USER wikijs WITH ENCRYPTED PASSWORD 'ChangeMeNOW!';
ALTER DATABASE wiki OWNER TO wikijs;
GRANT ALL PRIVILEGES ON DATABASE wiki TO wikijs;
SQL
```

> 🔒 Replace `ChangeMeNOW!` with a unique, strong password. Save it in your password manager.

### Step 4 — Download Wiki.js and stage configuration
- **What:** Fetch the official release bundle and configure runtime settings.
- **Why:** Running from `/opt/wiki/app` keeps application binaries separate from data directories such as `/opt/wiki/uploads`.
- **How:**

```bash
cd /opt/wiki
sudo -u wikijs wget https://github.com/Requarks/wiki/releases/download/2.5.300/wiki-js.tar.gz
sudo -u wikijs tar -xzf wiki-js.tar.gz -C app --strip-components=1
sudo -u wikijs rm wiki-js.tar.gz
```

Create the main configuration file at `/opt/wiki/config/config.yml`:

```yaml
port: 3000
bindIP: 0.0.0.0
db:
  type: postgres
  host: 127.0.0.1
  port: 5432
  user: wikijs
  pass: ChangeMeNOW!
  db: wiki
  ssl: false
logLevel: info
uploads:
  path: /opt/wiki/uploads

features:
  # Disable telemetry for privacy-conscious deployments
  telemetry: false
  # Disallow public registration unless explicitly required
  allowPublicRegistration: false
```

Set secure permissions so only the `wikijs` user can read the configuration and uploads:

```bash
sudo chown -R wikijs:wikijs /opt/wiki
sudo chmod 750 /opt/wiki
sudo chmod 640 /opt/wiki/config/config.yml
```

### Step 5 — Launch Wiki.js with PM2
- **What:** Register the Wiki.js process with PM2, configure log retention, and ensure startup on boot.
- **Why:** PM2 restarts services automatically on crashes or server reboots and centralizes stdout/stderr logs.
- **How:**

```bash
cd /opt/wiki/app
sudo -u wikijs pm2 start server --name wikijs -- -c /opt/wiki/config/config.yml

pm2 status wikijs
pm2 logs wikijs --lines 50
```

Persist PM2 across reboots:

```bash
pm2 startup systemd -u wikijs --hp /opt/wiki
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u wikijs --hp /opt/wiki
pm2 save
```

### Step 6 — Expose Wiki.js securely
- **What:** Configure a reverse proxy (Nginx or Apache) and optionally enable HTTPS via Let's Encrypt.
- **Why:** Terminating TLS at the proxy keeps the Node.js process simple and supports future load balancing.
- **How:**

```nginx
server {
  listen 80;
  server_name wiki.example.com;
  return 301 https://$server_name$request_uri;
}

server {
  listen 443 ssl http2;
  server_name wiki.example.com;

  ssl_certificate /etc/letsencrypt/live/wiki.example.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/wiki.example.com/privkey.pem;

  location / {
    proxy_pass http://127.0.0.1:3000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}
```

Reload the proxy and verify that `https://wiki.example.com/health` returns `200`.

### Step 7 — Operational runbook
- **Upgrades:**
  1. `pm2 stop wikijs`
  2. Backup `/opt/wiki/app` and `/opt/wiki/uploads`
  3. Download the new release tarball to `/opt/wiki/app`
  4. `pm2 start wikijs` and verify logs
- **Backups:** Use `pg_dump` for database exports and archive `/opt/wiki/uploads`. Automate with cron and store in off-site storage.
- **Monitoring:** Hook PM2 into monitoring by exporting metrics (`pm2 ls`, `pm2 monit`) or shipping logs from `/home/wikijs/.pm2/logs/` to your logging stack.
- **Troubleshooting:** Run `pm2 logs wikijs` for real-time output and `journalctl -u nginx` (or equivalent) for proxy errors.

<a id="method-3-kubernetes-deployment"></a>
## ☸️ Method 3: Kubernetes Deployment (Production Scale)

### Why choose this method
- **What:** Deploy Wiki.js and PostgreSQL as Kubernetes workloads backed by persistent volumes, exposed through an Ingress controller.
- **Why:** Kubernetes provides orchestration, rolling updates, and self-healing to support enterprise-grade uptime requirements.
- **When:** Use when you already operate a cluster or need to showcase GitOps, Helm, and infrastructure-as-code capabilities.

### Cluster prerequisites
| Component | Recommendation | Purpose |
|-----------|----------------|---------|
| Kubernetes version | 1.24+ | Ensures compatibility with modern API resources |
| StorageClass | e.g., `gp2`, `standard`, or `rook-ceph-block` | Provides persistent storage for PostgreSQL |
| Ingress Controller | Nginx Ingress, Traefik, or AWS ALB | Exposes Wiki.js over HTTP/S |
| Certificate management | cert-manager or external TLS termination | Automates TLS issuance |
| Secrets management | Kubernetes Secrets, sealed-secrets, or external vault | Stores database credentials |

### Step 1 — Create namespace and secrets
- **What:** Isolate resources and provide credentials for the database.
- **Why:** Namespaces scope RBAC policies and keep documentation workloads separate from the rest of the cluster.
- **How:**

```bash
kubectl create namespace wikijs
kubectl create secret generic wikijs-db-credentials   --namespace=wikijs   --from-literal=postgres-password=$(openssl rand -base64 24)   --from-literal=postgres-user=wikijs   --from-literal=postgres-database=wiki
```

### Step 2 — Author Helm values (recommended)
- **What:** Use the official Wiki.js Helm chart (or Bitnami community chart) with custom values.
- **Why:** Helm packages templates for Deployments, Services, Secrets, and PersistentVolumeClaims, reducing YAML boilerplate.
- **How:** Create `wikijs-values.yaml`:

```yaml
global:
  postgresql:
    auth:
      username: wikijs
      existingSecret: wikijs-db-credentials
      database: wiki
      password: ""
    primary:
      persistence:
        enabled: true
        size: 20Gi
        storageClass: standard

wikijs:
  replicaCount: 2
  image:
    repository: requarks/wiki
    tag: "2.5"
  service:
    type: ClusterIP
    port: 3000
  resources:
    requests:
      cpu: 250m
      memory: 512Mi
    limits:
      cpu: 1
      memory: 1Gi
  ingress:
    enabled: true
    className: nginx
    hosts:
      - host: wiki.example.com
        paths:
          - path: /
            pathType: Prefix
    tls:
      - secretName: wikijs-tls
        hosts:
          - wiki.example.com
```

If you manage PostgreSQL externally, disable the bundled database and point `wikijs.db` values at your managed service.

### Step 3 — Deploy with Helm
- **What:** Install or upgrade the release inside the `wikijs` namespace.
- **Why:** Helm keeps a history of revisions, enabling rollbacks.
- **How:**

```bash
helm repo add requarks https://charts.js.wiki
helm repo update
helm upgrade --install wikijs requarks/wiki \
  --namespace wikijs \
  --values wikijs-values.yaml
```

Watch rollout status:

```bash
kubectl rollout status deployment/wikijs --namespace=wikijs
kubectl get pods --namespace=wikijs
```

### Step 4 — Validate ingress and TLS
- **What:** Confirm external access to the Wiki.js UI and health endpoint.
- **Why:** Ensures DNS, ingress, and certificate automation are working end-to-end.
- **How:**

```bash
kubectl get ingress wikijs -n wikijs
curl -I https://wiki.example.com/health
```

If you use cert-manager, create a `Certificate` resource referencing the ingress host to trigger automatic certificate issuance.

### Step 5 — Configure backups and lifecycle policies
- **Database backups:** Use `kubectl exec` with `pg_dump`, a Kubernetes `CronJob`, or cloud-native snapshots (e.g., AWS EBS snapshots for the PVC).
- **Application assets:** Mount uploads to a PersistentVolume backed by durable storage (NFS, object storage via CSI). Sync to off-cluster storage with `rclone` or Velero.
- **Rollbacks:** `helm rollback wikijs <revision>` reverts to a known-good release. Always test rollbacks in staging before production.

### Step 6 — Scaling and resilience
- **Horizontal Pod Autoscaler:**
  ```bash
  kubectl autoscale deployment wikijs \
    --namespace=wikijs \
    --min=2 --max=5 \
    --cpu-percent=60
  ```
- **Pod disruption budgets:** Protect against voluntary disruptions removing all replicas simultaneously.
  ```yaml
  apiVersion: policy/v1
  kind: PodDisruptionBudget
  metadata:
    name: wikijs-pdb
    namespace: wikijs
  spec:
    minAvailable: 1
    selector:
      matchLabels:
        app.kubernetes.io/name: wikijs
  ```
- **Monitoring:** Scrape application metrics via Prometheus sidecars or use the built-in Kubernetes dashboard. Tail logs with `kubectl logs -f deployment/wikijs -n wikijs`.

### Step 7 — GitOps and CI/CD integration (optional but recommended)
- Store `wikijs-values.yaml` in Git. Use Argo CD or Flux to sync the chart automatically.
- Enforce code reviews on configuration changes to align with change management policies.
- Automate smoke tests (e.g., `curl` health endpoint, login checks) after each deployment using Kubernetes Jobs or your CI pipeline.

With Kubernetes in place, you now have an enterprise-ready Wiki.js platform that can ride alongside other workloads, inherits cluster-level security controls, and scales on demand.

<a id="initial-configuration"></a>
### Step 5: Access Wiki.js Initial Setup

1. **Open browser** and navigate to: `http://localhost:3000`

   **If on cloud server:**
   - Replace `localhost` with your server's IP address
   - Example: `http://192.168.1.100:3000`
   - Or use your domain: `http://wiki.example.com:3000`

2. **First-time setup wizard will appear:**

   **Administrator Account Setup**
   - Email: Enter your email (will be admin account)
   - Password: Create strong password (8+ characters)
   - Confirm Password: Re-enter password
   - Click **"Install"**

3. **Wait for installation** (30-60 seconds)
   - Database initialization
   - Default content creation
   - System configuration

4. **Setup Complete!**
   - You'll be redirected to login page
   - Login with credentials you just created

**✅ Checkpoint:** You should now see the Wiki.js home page!

---

### Step 6: Basic Configuration

#### Configure General Settings

1. **Navigate to Administration**
   - Click your profile (top right)
   - Click **"Administration"**

2. **Site Settings**
   - Go to: **General → Site**
   - **Site Title:** "Portfolio Documentation" (or your preferred name)
   - **Description:** "Comprehensive portfolio and project documentation"
   - **Logo:** Upload your logo (optional)
   - Click **"Apply"**

3. **Locale Settings**
   - Go to: **General → Locale**
   - **Timezone:** Select your timezone
   - **Date Format:** Choose preferred format
   - Click **"Apply"**

#### Enable Search

1. **Go to: Search Engines**
   - Administration → Search Engines
   - **Select:** "Database - PostgreSQL/MySQL" (already enabled)
   - **Or enable:** "Elasticsearch" for better performance (advanced)
   - Click **"Apply"**

2. **Rebuild Search Index**
   - Administration → Utilities → Search Engine
   - Click **"Rebuild Index"**
   - Wait for completion

---

### Step 7: Create Folder Structure

**Plan your documentation hierarchy:**

```
Home
├── Projects
│   ├── 1. AWS Multi-Tier Architecture
│   ├── 2. Kubernetes CI/CD Pipeline
│   ├── 3. IAM Security Hardening
│   ├── 4. Enterprise Monitoring Stack
│   └── 5. Incident Response Runbooks
├── Guides
│   ├── Getting Started
│   ├── Best Practices
│   └── Troubleshooting
├── Architecture
│   ├── Diagrams
│   └── Decision Records
└── About
    ├── Resume
    └── Contact
```

**Create pages:**

1. **Click "New Page" (top right)**
2. **Select path:** `/projects`
3. **Enter title:** "Projects"
4. **Choose editor:** Markdown (recommended)
5. **Create content:**
   ```markdown
   # Portfolio Projects
   
   This section contains detailed documentation for my 5 elite portfolio projects.
   
   ## Projects
   
   1. [AWS Multi-Tier Architecture](/projects/aws-multi-tier)
   2. [Kubernetes CI/CD Pipeline](/projects/kubernetes-cicd)
   3. [IAM Security Hardening](/projects/iam-security)
   4. [Enterprise Monitoring Stack](/projects/monitoring-stack)
   5. [Incident Response Runbooks](/projects/incident-response)
   ```
6. **Click "Create"**

**Repeat for other main sections** (Guides, Architecture, About)

---

### Step 8: Configure SSL/TLS (Production)

**For Production Deployment with Domain:**

#### Option A: Using Nginx Reverse Proxy with Let's Encrypt

**Install Nginx and Certbot:**

```bash
# Install Nginx
sudo apt-get install -y nginx

# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx
```

**Create Nginx configuration:**

```bash
sudo nano /etc/nginx/sites-available/wikijs
```

Add:

```nginx
server {
    listen 80;
    server_name wiki.yourdomain.com;  # Change this!
    
    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name wiki.yourdomain.com;  # Change this!
    
    # SSL will be configured by Certbot
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        
        # Additional headers
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable site and get certificate:**

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/wikijs /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d wiki.yourdomain.com

# Follow prompts:
# - Enter email
# - Agree to terms
# - Choose redirect option (recommended)
```

**Test SSL:**
- Visit `https://wiki.yourdomain.com`
- Should show secure padlock icon

**Auto-renewal:**
```bash
# Certbot automatically configures renewal
# Test renewal process:
sudo certbot renew --dry-run
```

---

<a id="backup-and-recovery"></a>
### Step 9: Configure Backups

#### Automated Backup Script

Create backup script:

```bash
mkdir -p ~/wikijs-backups
nano ~/wikijs-backups/backup.sh
```

Add:

```bash
#!/bin/bash

# Wiki.js Backup Script
# Backs up database and data directory

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$HOME/wikijs-backups"
WIKI_DIR="$HOME/wikijs"

echo "Starting Wiki.js backup at $DATE..."

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

# Backup database
echo "Backing up database..."
docker exec wikijs-db pg_dump -U wikijs wiki | gzip > "$BACKUP_DIR/$DATE/database.sql.gz"

# Backup data directory
echo "Backing up data directory..."
tar -czf "$BACKUP_DIR/$DATE/wiki-data.tar.gz" -C "$WIKI_DIR" data

# Backup docker-compose.yml (configuration)
echo "Backing up configuration..."
cp "$WIKI_DIR/docker-compose.yml" "$BACKUP_DIR/$DATE/"

# Calculate sizes
DB_SIZE=$(du -sh "$BACKUP_DIR/$DATE/database.sql.gz" | cut -f1)
DATA_SIZE=$(du -sh "$BACKUP_DIR/$DATE/wiki-data.tar.gz" | cut -f1)

echo "Backup complete!"
echo "Database backup: $DB_SIZE"
echo "Data backup: $DATA_SIZE"
echo "Location: $BACKUP_DIR/$DATE"

# Optional: Keep only last 7 backups
find "$BACKUP_DIR" -maxdepth 1 -type d -mtime +7 -exec rm -rf {} \;

echo "Old backups cleaned up (kept last 7)"
```

**Make executable:**
```bash
chmod +x ~/wikijs-backups/backup.sh
```

**Test backup:**
```bash
~/wikijs-backups/backup.sh
```

**Schedule automatic backups (daily at 2 AM):**
```bash
# Open crontab
crontab -e

# Add line:
0 2 * * * ~/wikijs-backups/backup.sh >> ~/wikijs-backups/backup.log 2>&1
```

#### Restore from Backup

```bash
#!/bin/bash
# Restore script

BACKUP_DATE=$1  # Format: 20250101_020000
BACKUP_DIR="$HOME/wikijs-backups/$BACKUP_DATE"

if [ -z "$BACKUP_DATE" ]; then
    echo "Usage: ./restore.sh <backup_date>"
    echo "Example: ./restore.sh 20250101_020000"
    exit 1
fi

echo "Restoring from backup: $BACKUP_DATE"

# Stop containers
cd ~/wikijs
docker compose down

# Restore database
echo "Restoring database..."
gunzip -c "$BACKUP_DIR/database.sql.gz" | docker exec -i wikijs-db psql -U wikijs wiki

# Restore data
echo "Restoring data directory..."
tar -xzf "$BACKUP_DIR/wiki-data.tar.gz" -C ~/wikijs

# Start containers
docker compose up -d

echo "Restore complete!"
```

#### Validation toolkit (`validation/`)

Create a reusable validation harness to standardize smoke tests after deployments and restores. Save the file as `validation/validate-deployment.sh` inside your wiki project directory:

```bash
#!/bin/bash
# validation/validate-deployment.sh — orchestrate post-deploy checks
set -euo pipefail

echo "🔍 Validating Wiki.js deployment..."

echo "1. Checking container health"
docker-compose ps

echo "2. Running application health check"
curl -fsS http://localhost:3000/health >/dev/null && echo "   - Wiki.js responded with 200"

echo "3. Testing database connectivity"
docker-compose exec -T postgres pg_isready -U wikijs

echo "4. Inspecting recent logs for errors"
docker-compose logs --tail=50 wiki | grep -i "error" && {
  echo "   ! Found errors in Wiki.js logs";
  exit 1;
} || echo "   - No error entries detected"

echo "5. Verifying SSL certificate status"
DOMAIN=${DOMAIN:-wiki.example.com}
openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" < /dev/null 2>/dev/null \
  | openssl x509 -noout -checkend $((7*24*3600))

echo "✅ Deployment validation finished"
```

Run with `bash validation/validate-deployment.sh`. Integrate it into cron, CI pipelines, or post-restore runbooks to keep production hygiene consistent.

---

<a id="content-organization-strategy"></a>
## 📚 Content Organization Strategy

### Recommended Page Structure

#### 1. Create Homepage

**Path:** `/home`  
**Content:**

```markdown
# Welcome to My Portfolio Documentation

## About This Wiki

This wiki contains comprehensive documentation for my portfolio projects, demonstrating technical expertise and professional practices in:

- Cloud infrastructure (AWS)
- DevOps and CI/CD
- Security and compliance
- Monitoring and observability
- Incident response

## Featured Projects

### 1. [AWS Multi-Tier Architecture](/projects/aws-multi-tier)
Production-grade 3-tier architecture with VPC, Auto Scaling, RDS, and CloudFront.

**Skills Demonstrated:** Terraform, AWS, Infrastructure as Code, High Availability

### 2. [Kubernetes CI/CD Pipeline](/projects/kubernetes-cicd)
End-to-end CI/CD with GitHub Actions, ArgoCD, and Kubernetes deployment.

**Skills Demonstrated:** Kubernetes, CI/CD, GitOps, Containerization

[View All Projects →](/projects)

## Quick Links

- [Architecture Diagrams](/architecture)
- [Runbooks & Playbooks](/runbooks)
- [Resume](/about/resume)
- [Contact](/about/contact)

---

*Last Updated: [Current Date]*
```

#### 2. Create Project Template

**Use this template for each project page:**

```markdown
# [Project Name]

> **Project Type:** [Infrastructure / DevOps / Security / Monitoring / SRE]  
> **Completion Date:** [Date]  
> **GitHub:** [Link]

## 📋 Executive Summary

[2-3 sentences describing project value and business impact]

## 🎯 Project Objectives

- Objective 1
- Objective 2
- Objective 3

## 🏗️ Architecture

[Architecture diagram - upload to Wiki.js]

### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| [Name] | [Tech] | [Purpose] |

## 💡 Key Technical Decisions

### Decision 1: [Title]
**Context:** [Why decision needed]  
**Decision:** [What was decided]  
**Alternatives:** [What else was considered]  
**Outcome:** [Result]

## 🔧 Implementation Details

[Link to detailed implementation guide]

## ✅ Results & Outcomes

- **Metric 1:** [Value]
- **Metric 2:** [Value]
- **Impact:** [Description]

## 📚 Documentation

- [Deployment Guide](/guides/[project]/deployment)
- [Runbook](/runbooks/[project])
- [Troubleshooting](/guides/[project]/troubleshooting)

## 🎓 Skills Demonstrated

**Technical Skills:**
- Skill 1
- Skill 2

**Soft Skills:**
- Communication (comprehensive documentation)
- Strategic thinking (architecture decisions)
- Project management (organized delivery)

---

*Created: [Date] | Last Updated: [Date]*
```

#### 3. Organize with Tags

**Create tags for easy navigation:**

1. **Go to:** Administration → Tags
2. **Create tags:**
   - `aws`
   - `kubernetes`
   - `security`
   - `monitoring`
   - `devops`
   - `terraform`
   - `ci-cd`
   - `elite-project`

3. **Apply tags to pages** as you create them

### 4. 25-Project Coverage Matrix (Required Wiki Pages)

> **Goal:** Every portfolio repository below must have a corresponding Wiki.js page that uses the standard project template (Executive Summary → Objectives → Architecture → Decisions → Implementation → Results → Documentation → Skills) plus the "Wiki Deliverables" column.

| # | Project | GitHub Path | Wiki Path | Status | Wiki Deliverables |
|---|---------|-------------|-----------|--------|-------------------|
| 1 | AWS Infrastructure Automation | `projects/1-aws-infrastructure-automation` | `/projects/aws-infrastructure-automation` | Partial | Multi-AZ network + IaC comparison table (Terraform vs CDK vs Pulumi) and `scripts/validate.sh` output embedded. |
| 2 | Database Migration Platform | `projects/2-database-migration` | `/projects/database-migration-platform` | Minimal | Debezium topology diagram, cutover/rollback timeline, and CDC health checklist. |
| 3 | Kubernetes CI/CD Pipeline | `projects/3-kubernetes-cicd` | `/projects/kubernetes-cicd` | Minimal | GitHub Actions badge, ArgoCD app-of-apps diagram, progressive delivery stages. |
| 4 | DevSecOps Pipeline | `projects/4-devsecops` | `/projects/devsecops-pipeline` | Minimal | SBOM sample, container scanning report screenshots, policy-as-code snippet. |
| 5 | Real-time Data Streaming | `projects/5-real-time-data-streaming` | `/projects/real-time-data-streaming` | Minimal | Kafka/Flink event flow, exactly-once validation script, throughput metrics table. |
| 6 | MLOps Platform | `projects/6-mlops-platform` | `/projects/mlops-platform` | Partial | ML lifecycle diagram, feature pipeline breakdown, MLflow experiment summary. |
| 7 | Serverless Data Processing | `projects/7-serverless-data-processing` | `/projects/serverless-data-processing` | Partial | Event-driven architecture (Step Functions + Lambda), cost model, deployment checklist. |
| 8 | Advanced AI Chatbot | `projects/8-advanced-ai-chatbot` | `/projects/advanced-ai-chatbot` | Partial | Conversation flow, prompt safety guardrails, evaluation rubric. |
| 9 | Multi-Region Disaster Recovery | `projects/9-multi-region-disaster-recovery` | `/projects/multi-region-disaster-recovery` | Partial | Failover topology, RPO/RTO matrix, last chaos drill evidence. |
| 10 | Blockchain Smart Contract Platform | `projects/10-blockchain-smart-contract-platform` | `/projects/blockchain-smart-contract-platform` | Partial | Contract architecture, Hardhat test summary, network deployment steps. |
| 11 | IoT Data Analytics | `projects/11-iot-data-analytics` | `/projects/iot-data-analytics` | Minimal | Device ingestion flow, time-series storage plan, anomaly detection results. |
| 12 | Quantum Computing Integration | `projects/12-quantum-computing` | `/projects/quantum-computing-integration` | Minimal | Hybrid workflow diagram (classical + quantum), Qiskit job sample, benchmarking notes. |
| 13 | Advanced Cybersecurity Platform | `projects/13-advanced-cybersecurity` | `/projects/advanced-cybersecurity-platform` | Minimal | Detection coverage map, SOC automation steps, MITRE ATT&CK alignment table. |
| 14 | Edge AI Inference Platform | `projects/14-edge-ai-inference` | `/projects/edge-ai-inference-platform` | Minimal | Edge deployment diagram, ONNX optimization checklist, latency measurements. |
| 15 | Real-time Collaboration Platform | `projects/15-real-time-collaboration` | `/projects/real-time-collaboration-platform` | Minimal | WebRTC topology, scaling/HA notes, synthetic monitoring screenshot. |
| 16 | Advanced Data Lake | `projects/16-advanced-data-lake` | `/projects/advanced-data-lake` | Minimal | Bronze/Silver/Gold layer diagram, data catalog references, Glue/Athena query samples. |
| 17 | Multi-Cloud Service Mesh | `projects/17-multi-cloud-service-mesh` | `/projects/multi-cloud-service-mesh` | Minimal | Mesh topology (Istio/Linkerd), traffic policies, zero-trust references. |
| 18 | GPU-Accelerated Computing | `projects/18-gpu-accelerated-computing` | `/projects/gpu-accelerated-computing` | Minimal | Cluster layout, scheduler/quotas table, CUDA benchmark excerpts. |
| 19 | Advanced Kubernetes Operators | `projects/19-advanced-kubernetes-operators` | `/projects/advanced-kubernetes-operators` | Minimal | CRD definitions, reconciliation flow diagram, failure-handling runbook. |
| 20 | Blockchain Oracle Service | `projects/20-blockchain-oracle-service` | `/projects/blockchain-oracle-service` | Minimal | Oracle data path (off-chain→on-chain), signing process, SLA matrix. |
| 21 | Quantum-Safe Cryptography | `projects/21-quantum-safe-cryptography` | `/projects/quantum-safe-cryptography` | Minimal | Algorithm comparison chart, key rotation schedule, compliance checklist. |
| 22 | Autonomous DevOps Platform | `projects/22-autonomous-devops-platform` | `/projects/autonomous-devops-platform` | Minimal | Workflow automation diagram, runbook generator screenshots, AI-assist guardrails. |
| 23 | Advanced Monitoring & Observability | `projects/23-advanced-monitoring` | `/projects/advanced-monitoring-observability` | Minimal | End-to-end telemetry map, alert routing matrix, Grafana dashboard embeds. |
| 24 | Report Generator | `projects/24-report-generator` | `/projects/report-generator` | Minimal | Data source inventory, templating pipeline diagram, PDF export evidence. |
| 25 | Portfolio Website | `projects/25-portfolio-website` | `/projects/portfolio-website` | Partial | Site map + navigation screenshot, VitePress build/CI badge, deployment commands. |

**How to use the matrix:**

1. **Create/verify each page path** exactly as listed so automation (Git sync + `tools/wikijs_push.py`) can target predictable URLs.
2. **Apply required tags** from the previous step plus any domain-specific tags (e.g., `ai`, `blockchain`, `data-platform`).
3. **Embed evidence** called out in "Wiki Deliverables"—upload diagrams/screenshots under Assets → Media, then reference them inside the template sections.
4. **Link to GitHub** using the repository path shown so readers can jump from the wiki to source code and CI badges.

### 5. Coverage Automation & QA

1. **Author content locally** in `docs/wiki/` or within each project (`projects/<id>/docs/wiki/`).
2. **Use `tools/wikijs_push.py`** to publish Markdown in bulk:
   ```bash
   python tools/wikijs_push.py \
     --content-root projects \
     --glob "*/wiki/*.md" \
     --base-path /projects \
     --api-url https://wiki.example.com/graphql \
     --api-token $WIKI_TOKEN
   ```
3. **Run a validation pass** after publishing by following the [validation script](#backup-and-recovery) and visually confirming that navigation shows all 25 entries.
4. **Update the wiki changelog** (`/operations/weekly-reports`) whenever a project page is added or materially changed.

---

### 4. 25-Project Coverage Matrix (Required Wiki Pages)

> **Goal:** Every portfolio repository below must have a corresponding Wiki.js page that uses the standard project template (Executive Summary → Objectives → Architecture → Decisions → Implementation → Results → Documentation → Skills) plus the "Wiki Deliverables" column.

| # | Project | GitHub Path | Wiki Path | Status | Wiki Deliverables |
|---|---------|-------------|-----------|--------|-------------------|
| 1 | AWS Infrastructure Automation | `projects/1-aws-infrastructure-automation` | `/projects/aws-infrastructure-automation` | Partial | Multi-AZ network + IaC comparison table (Terraform vs CDK vs Pulumi) and `scripts/validate.sh` output embedded. |
| 2 | Database Migration Platform | `projects/2-database-migration` | `/projects/database-migration-platform` | Minimal | Debezium topology diagram, cutover/rollback timeline, and CDC health checklist. |
| 3 | Kubernetes CI/CD Pipeline | `projects/3-kubernetes-cicd` | `/projects/kubernetes-cicd` | Minimal | GitHub Actions badge, ArgoCD app-of-apps diagram, progressive delivery stages. |
| 4 | DevSecOps Pipeline | `projects/4-devsecops` | `/projects/devsecops-pipeline` | Minimal | SBOM sample, container scanning report screenshots, policy-as-code snippet. |
| 5 | Real-time Data Streaming | `projects/5-real-time-data-streaming` | `/projects/real-time-data-streaming` | Minimal | Kafka/Flink event flow, exactly-once validation script, throughput metrics table. |
| 6 | MLOps Platform | `projects/6-mlops-platform` | `/projects/mlops-platform` | Partial | ML lifecycle diagram, feature pipeline breakdown, MLflow experiment summary. |
| 7 | Serverless Data Processing | `projects/7-serverless-data-processing` | `/projects/serverless-data-processing` | Partial | Event-driven architecture (Step Functions + Lambda), cost model, deployment checklist. |
| 8 | Advanced AI Chatbot | `projects/8-advanced-ai-chatbot` | `/projects/advanced-ai-chatbot` | Partial | Conversation flow, prompt safety guardrails, evaluation rubric. |
| 9 | Multi-Region Disaster Recovery | `projects/9-multi-region-disaster-recovery` | `/projects/multi-region-disaster-recovery` | Partial | Failover topology, RPO/RTO matrix, last chaos drill evidence. |
| 10 | Blockchain Smart Contract Platform | `projects/10-blockchain-smart-contract-platform` | `/projects/blockchain-smart-contract-platform` | Partial | Contract architecture, Hardhat test summary, network deployment steps. |
| 11 | IoT Data Analytics | `projects/11-iot-data-analytics` | `/projects/iot-data-analytics` | Minimal | Device ingestion flow, time-series storage plan, anomaly detection results. |
| 12 | Quantum Computing Integration | `projects/12-quantum-computing` | `/projects/quantum-computing-integration` | Minimal | Hybrid workflow diagram (classical + quantum), Qiskit job sample, benchmarking notes. |
| 13 | Advanced Cybersecurity Platform | `projects/13-advanced-cybersecurity` | `/projects/advanced-cybersecurity-platform` | Minimal | Detection coverage map, SOC automation steps, MITRE ATT&CK alignment table. |
| 14 | Edge AI Inference Platform | `projects/14-edge-ai-inference` | `/projects/edge-ai-inference-platform` | Minimal | Edge deployment diagram, ONNX optimization checklist, latency measurements. |
| 15 | Real-time Collaboration Platform | `projects/15-real-time-collaboration` | `/projects/real-time-collaboration-platform` | Minimal | WebRTC topology, scaling/HA notes, synthetic monitoring screenshot. |
| 16 | Advanced Data Lake | `projects/16-advanced-data-lake` | `/projects/advanced-data-lake` | Minimal | Bronze/Silver/Gold layer diagram, data catalog references, Glue/Athena query samples. |
| 17 | Multi-Cloud Service Mesh | `projects/17-multi-cloud-service-mesh` | `/projects/multi-cloud-service-mesh` | Minimal | Mesh topology (Istio/Linkerd), traffic policies, zero-trust references. |
| 18 | GPU-Accelerated Computing | `projects/18-gpu-accelerated-computing` | `/projects/gpu-accelerated-computing` | Minimal | Cluster layout, scheduler/quotas table, CUDA benchmark excerpts. |
| 19 | Advanced Kubernetes Operators | `projects/19-advanced-kubernetes-operators` | `/projects/advanced-kubernetes-operators` | Minimal | CRD definitions, reconciliation flow diagram, failure-handling runbook. |
| 20 | Blockchain Oracle Service | `projects/20-blockchain-oracle-service` | `/projects/blockchain-oracle-service` | Minimal | Oracle data path (off-chain→on-chain), signing process, SLA matrix. |
| 21 | Quantum-Safe Cryptography | `projects/21-quantum-safe-cryptography` | `/projects/quantum-safe-cryptography` | Minimal | Algorithm comparison chart, key rotation schedule, compliance checklist. |
| 22 | Autonomous DevOps Platform | `projects/22-autonomous-devops-platform` | `/projects/autonomous-devops-platform` | Minimal | Workflow automation diagram, runbook generator screenshots, AI-assist guardrails. |
| 23 | Advanced Monitoring & Observability | `projects/23-advanced-monitoring` | `/projects/advanced-monitoring-observability` | Minimal | End-to-end telemetry map, alert routing matrix, Grafana dashboard embeds. |
| 24 | Report Generator | `projects/24-report-generator` | `/projects/report-generator` | Minimal | Data source inventory, templating pipeline diagram, PDF export evidence. |
| 25 | Portfolio Website | `projects/25-portfolio-website` | `/projects/portfolio-website` | Partial | Site map + navigation screenshot, VitePress build/CI badge, deployment commands. |

**How to use the matrix:**

1. **Create/verify each page path** exactly as listed so automation (Git sync + `tools/wikijs_push.py`) can target predictable URLs.
2. **Apply required tags** from the previous step plus any domain-specific tags (e.g., `ai`, `blockchain`, `data-platform`).
3. **Embed evidence** called out in "Wiki Deliverables"—upload diagrams/screenshots under Assets → Media, then reference them inside the template sections.
4. **Link to GitHub** using the repository path shown so readers can jump from the wiki to source code and CI badges.

### 5. Coverage Automation & QA

1. **Author content locally** in `docs/wiki/` or within each project (`projects/<id>/docs/wiki/`).
2. **Use `tools/wikijs_push.py`** to publish Markdown in bulk:
   ```bash
   python tools/wikijs_push.py \
     --content-root projects \
     --glob "*/wiki/*.md" \
     --base-path /projects \
     --api-url https://wiki.example.com/graphql \
     --api-token $WIKI_TOKEN
   ```
3. **Run a validation pass** after publishing by following the [validation script](#backup-and-recovery) and visually confirming that navigation shows all 25 entries.
4. **Update the wiki changelog** (`/operations/weekly-reports`) whenever a project page is added or materially changed.

---

<a id="migrating-portfolio-documentation"></a>
## 📦 Migrating Portfolio Documentation

### Step 1: Prepare Your Content

**Inventory your documentation:**

```bash
# Assuming documentation is in ~/portfolio_materials
cd ~/portfolio_materials

# Find all markdown files
find . -name "*.md" -type f > markdown_files.txt

# Review list
cat markdown_files.txt
```

### Step 2: Migration Strategy

**For each document:**

1. **Determine appropriate location** in Wiki.js hierarchy
2. **Convert if necessary** (PDF to Markdown, etc.)
3. **Upload assets** (images, diagrams)
4. **Create page** in Wiki.js
5. **Update internal links**

### Step 3: Automated Migration (Optional)

**Create migration script:**

```bash
nano ~/wikijs/migrate.sh
```

```bash
#!/bin/bash

# Wiki.js Content Migration Script

SOURCE_DIR="$HOME/portfolio_materials"
WIKI_API="http://localhost:3000/graphql"
API_KEY="your-api-key-here"  # Get from Wiki.js Admin → API

# Function to create page
create_page() {
    local path=$1
    local title=$2
    local content=$3
    
    curl -X POST "$WIKI_API" \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"query\": \"mutation {
                pages {
                    create(
                        content: \\\"$content\\\",
                        description: \\\"\\\",
                        editor: \\\"markdown\\\",
                        isPublished: true,
                        isPrivate: false,
                        locale: \\\"en\\\",
                        path: \\\"$path\\\",
                        tags: [],
                        title: \\\"$title\\\"
                    ) {
                        responseResult {
                            succeeded
                            errorCode
                            slug
                            message
                        }
                    }
                }
            }\"
        }"
}

# Migrate markdown files
find "$SOURCE_DIR" -name "*.md" | while read file; do
    echo "Migrating: $file"
    # Extract title, create path, migrate content
    # ... (customize based on your structure)
done
```

### Step 4: Manual Migration Workflow

**For most users, manual is easier:**

1. **Open source document** in editor
2. **Copy content**
3. **Create new page** in Wiki.js
4. **Paste and format**
5. **Upload referenced images**
6. **Update links**
7. **Add tags**
8. **Publish**

**Repeat for all documents**

---

<a id="user-management-access-control"></a>
## 👥 User Management & Access Control

### Create User Accounts

1. **Go to:** Administration → Users
2. **Click "New User"**
3. **Fill in:**
   - Email
   - Name
   - Password
   - Provider: Local
   - Group: Choose appropriate group
4. **Click "Create"**

### Configure Groups & Permissions

1. **Go to:** Administration → Groups
2. **Default groups:**
   - **Administrators:** Full access
   - **Users:** Read and edit
   - **Guests:** Read-only

3. **Create custom groups** (if needed):
   - Click "New Group"
   - Name: "Recruiters"
   - Permissions: Read-only
   - Apply to: All pages

### Configure Page Rules

**Set permissions per page/section:**

1. **Edit page**
2. **Click "Page Actions" (top right)**
3. **Select "Access"**
4. **Set rules:**
   - Allow: [Group] - [Permission Level]
   - Deny: [Group] - [No access]

---

<a id="customization-and-theming"></a>
## 🔧 Customization & Theming

### Change Theme

1. **Go to:** Administration → Theme
2. **Select theme:**
   - Default
   - Dark
   - Light (clean)
3. **Primary Color:** Choose brand color
4. **Click "Apply"**

### Custom CSS (Advanced)

1. **Go to:** Administration → Theme → Custom CSS
2. **Add custom styles:**

```css
/* Example: Custom header styling */
.v-toolbar {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
}

/* Custom font */
body {
    font-family: 'Roboto', sans-serif;
}

/* Adjust spacing */
.contents {
    max-width: 1200px;
    margin: 0 auto;
}
```

### Add Logo

1. **Go to:** Administration → General → Site
2. **Upload logo image**
3. **Set dimensions**
4. **Click "Apply"**

---

<a id="troubleshooting"></a>
## 🔍 Troubleshooting

### Common Issues

#### Issue 1: Can't Access Wiki.js

**Symptoms:**
- Browser shows "This site can't be reached"
- Connection refused error

**Solutions:**

1. **Check containers are running:**
   ```bash
   docker compose ps
   # Both containers should show "Up"
   ```

2. **Check logs:**
   ```bash
   docker compose logs wiki
   # Look for errors
   ```

3. **Verify port not in use:**
   ```bash
   sudo lsof -i :3000
   # Should show docker process or nothing
   ```

4. **Restart containers:**
   ```bash
   cd ~/wikijs
   docker compose restart
   ```

---

#### Issue 2: Database Connection Error

**Symptoms:**
- Wiki.js shows database error on startup
- Logs show "could not connect to server"

**Solutions:**

1. **Check database is running:**
   ```bash
   docker compose ps db
   ```

2. **Verify database credentials match:**
   ```bash
   # Check docker-compose.yml
   cat ~/wikijs/docker-compose.yml | grep -A 5 POSTGRES
   ```

3. **Check database logs:**
   ```bash
   docker compose logs db
   ```

4. **Restart database:**
   ```bash
   docker compose restart db
   # Wait 30 seconds
   docker compose restart wiki
   ```

---

#### Issue 3: Can't Login

**Symptoms:**
- Credentials not accepted
- "Invalid credentials" error

**Solutions:**

1. **Reset admin password:**
   ```bash
   # Access database
   docker exec -it wikijs-db psql -U wikijs wiki
   
   # Find user ID
   SELECT id, email FROM users;
   
   # Update password (hash will be regenerated on login)
   UPDATE users SET password = '$2a$10$...' WHERE id = 1;
   
   # Exit
   \q
   ```

2. **Create new admin account:**
   ```bash
   # Access Wiki.js container
   docker exec -it wikijs-app sh
   
   # Run admin reset tool (if available)
   node server reset-admin
   
   # Exit
   exit
   ```

---

#### Issue 4: Slow Performance

**Symptoms:**
- Pages load slowly
- Search is slow

**Solutions:**

1. **Check resource usage:**
   ```bash
   docker stats
   # Look for high CPU/memory usage
   ```

2. **Increase container resources:**
   Edit `docker-compose.yml`:
   ```yaml
   wiki:
     # ... other config ...
     deploy:
       resources:
         limits:
           memory: 2G
         reservations:
           memory: 1G
   ```

3. **Rebuild search index:**
   - Administration → Utilities → Search Engine
   - Click "Rebuild Index"

4. **Enable caching:**
   - Administration → Rendering → Cache
   - Enable page caching

---

### Getting Help

**Resources:**
- Official Docs: https://docs.requarks.io/
- GitHub Issues: https://github.com/requarks/wiki/issues
- Community Forum: https://github.com/requarks/wiki/discussions

**Before asking for help, collect:**
- Wiki.js version: Check Administration → System Info
- Error logs: `docker compose logs wiki`
- Browser console errors: F12 → Console tab

---

## 📋 Next Steps

After completing this setup:

1. ✅ **Migrate your portfolio documentation**
2. ✅ **Customize theme and branding**
3. ✅ **Set up SSL for production**
4. ✅ **Configure automated backups**
5. ✅ **Share with recruiters**

**Make it stand out:**
- Add professional cover pages for each project
- Include architecture diagrams
- Link to GitHub repositories
- Add screenshots and demos
- Keep content updated

---

## 📚 Additional Resources

- [Wiki.js Official Documentation](https://docs.requarks.io/)
- [Markdown Guide](https://www.markdownguide.org/)
- [Mermaid Diagrams](https://mermaid-js.github.io/) (for architecture diagrams)

---

**Guide Version:** 1.0  
**Last Updated:** October 11, 2025  
**Questions?** Check the troubleshooting section or official docs

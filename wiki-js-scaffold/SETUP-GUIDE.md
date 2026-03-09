# Wiki.js Setup Guide - Step-by-Step Examples

This guide provides specific, copy-paste examples for different deployment scenarios.

## 🎯 Scenario 1: Local Development (5 minutes)

**Use case:** Quick testing and content development

```bash
# Step 1: Start Wiki.js with SQLite (no database setup needed)
docker run -d \
  --name wikijs-dev \
  -p 3000:3000 \
  -e "DB_TYPE=sqlite" \
  -e "DB_FILEPATH=/var/wiki/data/db.sqlite" \
  -v $(pwd)/content:/var/wiki/content \
  -v $(pwd)/assets:/var/wiki/assets \
  ghcr.io/requarks/wiki:2

# Step 2: Access and complete setup wizard
open http://localhost:3000

# Step 3: Get API token (after setup)
# Admin → API Access → Create New Token

# Step 4: Import content
export WIKIJS_URL=http://localhost:3000
export WIKIJS_TOKEN=your-token-here
npm install
node scripts/import-to-wikijs.js

# Optional: Import portfolio wiki content from ../wiki
export CONTENT_DIRS=content,../wiki
export DEFAULT_TAGS=portfolio
node scripts/import-to-wikijs.js

# Done! Wiki is ready at http://localhost:3000
```

**Cleanup:**

```bash
docker stop wikijs-dev
docker rm wikijs-dev
```

---

## 🌐 Scenario 2: Production Deployment with SSL (15 minutes)

**Use case:** Public-facing wiki with custom domain

### Prerequisites

- Domain name pointing to your server (A record)
- Server with Docker installed
- Ports 80, 443, and 3000 open

```bash
# Step 1: Clone and configure
git clone <repository-url>
cd wiki-js-scaffold

# Step 2: Configure environment
cp .env.example .env
nano .env

# Update these values:
DOMAIN=wiki.yourcompany.com
CERTBOT_EMAIL=admin@yourcompany.com
DB_PASSWORD=$(openssl rand -base64 32)

# Step 3: Start services
cd docker
docker-compose up -d

# Step 4: Watch initialization
docker-compose logs -f wiki

# Wait for: "✔️ HTTP Server on port 3000: OK"

# Step 5: Complete setup wizard
open https://wiki.yourcompany.com

# Step 6: Import content
cd ..
npm install

# Get API token from Wiki.js admin panel
export WIKIJS_TOKEN=your-production-token
npm run import

# Step 7: Configure automated backups
crontab -e
# Add line:
0 2 * * * /path/to/wiki-js-scaffold/scripts/backup-wiki.sh

# Done! Production wiki ready at https://wiki.yourcompany.com
```

---

## 🏢 Scenario 3: Enterprise Setup with Active Directory (30 minutes)

**Use case:** Company wiki with SSO authentication

```bash
# Step 1: Standard setup
cd wiki-js-scaffold/docker
docker-compose up -d

# Step 2: Access admin panel
open http://localhost:3000

# Step 3: Configure LDAP/Active Directory
# Admin → Authentication → LDAP / Active Directory

# LDAP Configuration:
URL: ldap://your-ad-server.company.com
Port: 389
Use TLS: Yes

Bind DN: CN=WikiJS Service Account,OU=Service Accounts,DC=company,DC=com
Bind Credentials: [service account password]

Search Base: OU=Users,DC=company,DC=com
Search Filter: (sAMAccountName={{username}})

# User Mapping:
Unique ID Field: objectGUID
Display Name: displayName
Email Field: mail

# Step 4: Configure groups
# Admin → Groups → Create from LDAP
# Map AD groups to Wiki.js roles

# Step 5: Test authentication
# Logout and login with AD credentials

# Step 6: Configure audit logging
# Admin → Utilities → Audit Log
# Enable and configure retention

# Step 7: Setup monitoring
# NOTE: docker-compose.monitoring.yml needs to be created (see Scenario 7 below for example)
# docker-compose -f docker-compose.monitoring.yml up -d
# open http://localhost:9090  # Prometheus
# open http://localhost:3001  # Grafana

# Done! Enterprise wiki with SSO and monitoring
```

---

## 🔄 Scenario 4: Git-Based Content Workflow (20 minutes)

**Use case:** Team collaboration with version control

```bash
# Step 1: Create content repository
git init wiki-content
cd wiki-content
git remote add origin https://github.com/yourorg/wiki-content.git

# Step 2: Structure content
mkdir -p pages/{setup,git,documentation,projects,github,advanced}
cp -r ../wiki-js-scaffold/content/* pages/

# Step 3: Create Git storage config
cat > config.yml <<EOF
storage:
  git:
    url: https://github.com/yourorg/wiki-content.git
    branch: main
    auth:
      type: ssh
      privateKey: /path/to/ssh/key
    localPath: /var/wiki/storage/git
    sync:
      interval: 5m
      enabled: true
EOF

# Step 4: Push to Git
git add .
git commit -m "Initial wiki content"
git push -u origin main

# Step 5: Configure Wiki.js Git storage
# Admin → Storage → Git Storage
# Enable and configure with repository URL

# Step 6: Enable auto-sync
# Admin → Storage → Git Storage → Sync Schedule
# Set to: Every 5 minutes

# Step 7: Test workflow
# Make changes to local repository
echo "# Updated Content" > pages/setup/test.md
git add pages/setup/test.md
git commit -m "Test update"
git push

# Wait 5 minutes or trigger manual sync
# Changes appear automatically in Wiki.js

# Done! Git-based workflow active
```

**Team Workflow:**

```bash
# Developer workflow
git clone https://github.com/yourorg/wiki-content.git
cd wiki-content

# Create feature branch
git checkout -b update-ssh-guide

# Make changes
nano pages/setup/05-ssh-key-setup.md

# Commit and push
git add .
git commit -m "Update SSH setup guide with new instructions"
git push origin update-ssh-guide

# Create PR for review
gh pr create --title "Update SSH guide" --body "Added troubleshooting section"

# After approval and merge, content auto-syncs to Wiki.js
```

---

## 🔐 Scenario 5: High-Security Setup (45 minutes)

**Use case:** Sensitive documentation with strict access control

```bash
# Step 1: Secure infrastructure setup
cd wiki-js-scaffold/docker

# Use hardened PostgreSQL
cat >> docker-compose.yml <<EOF
  db:
    image: postgres:15-alpine
    command: postgres -c ssl=on -c ssl_cert_file=/var/lib/postgresql/server.crt -c ssl_key_file=/var/lib/postgresql/server.key
    volumes:
      - ./ssl/server.crt:/var/lib/postgresql/server.crt:ro
      - ./ssl/server.key:/var/lib/postgresql/server.key:ro
EOF

# Step 2: Generate strong encryption keys
export SESSION_SECRET=$(openssl rand -hex 32)
export JWT_SECRET=$(openssl rand -hex 32)
export DB_PASSWORD=$(openssl rand -base64 32)

# Add to .env
cat >> .env <<EOF
SESSION_SECRET=$SESSION_SECRET
JWT_SECRET=$JWT_SECRET
DB_PASSWORD=$DB_PASSWORD
EOF

# Step 3: Enable MFA
# Admin → Authentication → Two-Factor Authentication
# Enable for all users

# Step 4: Configure strict TLS
cat > docker/nginx-secure.conf <<EOF
# TLS 1.3 only
ssl_protocols TLSv1.3;
ssl_ciphers 'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256';
ssl_prefer_server_ciphers off;

# HSTS with preload
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

# Security headers
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
EOF

# Step 5: Configure IP whitelist
cat >> docker/nginx.conf <<EOF
# Allow only company IPs
allow 10.0.0.0/8;
allow 172.16.0.0/12;
allow 192.168.1.0/24;
deny all;
EOF

# Step 6: Enable audit logging
# Admin → System → Logging
# Set level: info
# Enable audit log: Yes

# Step 7: Database encryption at rest
docker-compose exec db psql -U wikijs -c "ALTER SYSTEM SET ssl = on;"

# Step 8: Regular security scans
cat > scripts/security-scan.sh <<'EOF'
#!/bin/bash
# Run security scans

echo "Running vulnerability scan..."
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image ghcr.io/requarks/wiki:2

echo "Checking SSL configuration..."
docker run --rm -ti nmap/nmap --script ssl-enum-ciphers -p 443 $DOMAIN

echo "Scanning for secrets..."
docker run --rm -v $(pwd):/path trufflesecurity/trufflehog filesystem /path --json

echo "Security scan complete!"
EOF

chmod +x scripts/security-scan.sh

# Step 9: Setup intrusion detection
# NOTE: docker-compose.security.yml is optional and not included in this scaffold
# Create your own security monitoring stack (e.g., Fail2ban, OSSEC) if needed
# docker-compose -f docker-compose.security.yml up -d

# Step 10: Configure automated security updates
cat > scripts/auto-update.sh <<'EOF'
#!/bin/bash
# Automated security updates

# Backup before update
./scripts/backup-wiki.sh

# Pull latest images
docker-compose pull

# Update with zero downtime
docker-compose up -d --no-deps wiki

# Verify health
sleep 30
curl -f http://localhost:3000 || (docker-compose restart wiki && exit 1)

echo "Update complete!"
EOF

# Add to cron for weekly updates
crontab -e
# Add: 0 3 * * 0 /path/to/scripts/auto-update.sh

# Done! High-security wiki configured
```

---

## 🚀 Scenario 6: Multi-Language International Wiki (30 minutes)

**Use case:** Documentation for global teams

```bash
# Step 1: Organize multi-language content
mkdir -p content/{en,es,fr,de,ja,zh}

# Copy content for each language
cp -r content/01-setup-fundamentals content/en/
# Translate and place in respective language folders

# Step 2: Configure Wiki.js for multi-language
# Admin → Locales
# Enable: en, es, fr, de, ja, zh

# Step 3: Import content for each language
for lang in en es fr de ja zh; do
  echo "Importing $lang content..."
  LOCALE=$lang node scripts/import-multilang.js
done

# Step 4: Configure language auto-detection
# Admin → Locales → Auto-detection
# Enable: Yes
# Detection method: Browser language

# Step 5: Setup language switcher
# Admin → Theme → Custom CSS
cat >> assets/custom.css <<EOF
.language-switcher {
  position: fixed;
  top: 10px;
  right: 10px;
  z-index: 1000;
}

.language-switcher select {
  padding: 5px 10px;
  border-radius: 5px;
  border: 1px solid #ccc;
}
EOF

# Step 6: Create language-specific navigation
# Each language folder gets its own navigation structure

# Done! Multi-language wiki ready
```

---

## 📊 Scenario 7: Analytics and Monitoring Setup (20 minutes)

**Use case:** Track wiki usage and performance

```bash
# Step 1: Enable Google Analytics
# Admin → Analytics → Google Analytics
# Enter Tracking ID: UA-XXXXXXXXX-X

# Step 2: Setup Prometheus monitoring
cat > docker/docker-compose.monitoring.yml <<EOF
version: '3'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana-dashboards:/etc/grafana/provisioning/dashboards

  node-exporter:
    image: prom/node-exporter
    ports:
      - "9100:9100"

volumes:
  prometheus-data:
  grafana-data:
EOF

# Step 3: Configure Prometheus
cat > docker/prometheus.yml <<EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'wikijs'
    static_configs:
      - targets: ['wiki:3000']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'postgres'
    static_configs:
      - targets: ['db:5432']
EOF

# Step 4: Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Step 5: Import Grafana dashboards
# Access Grafana: http://localhost:3001
# Login: admin / admin
# Import dashboard ID: 11074 (PostgreSQL)
# Import dashboard ID: 1860 (Node Exporter)

# Step 6: Configure alerting
cat > docker/alertmanager.yml <<EOF
route:
  receiver: 'slack-notifications'

receivers:
  - name: 'slack-notifications'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#wiki-alerts'
        title: 'Wiki.js Alert'
EOF

# Step 7: Enable Wiki.js telemetry
# Admin → Telemetry
# Enable: Yes
# Endpoint: http://prometheus:9090

# Done! Full monitoring and analytics configured
```

---

## 🔄 Scenario 8: Continuous Integration Setup (25 minutes)

**Use case:** Automated testing and deployment

```bash
# Step 1: Create GitHub Actions workflow
mkdir -p .github/workflows

cat > .github/workflows/wiki-deploy.yml <<EOF
name: Deploy Wiki.js Content

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Validate Markdown
        uses: gaurav-nelson/github-action-markdown-link-check@v1
        with:
          folder-path: 'content'

      - name: Spell check
        uses: streetsidesoftware/cspell-action@v2
        with:
          files: 'content/**/*.md'

  deploy:
    needs: validate
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm install

      - name: Deploy to Wiki.js
        run: node scripts/import-to-wikijs.js
        env:
          WIKIJS_URL: \${{ secrets.WIKIJS_URL }}
          WIKIJS_TOKEN: \${{ secrets.WIKIJS_TOKEN }}

      - name: Notify Slack
        uses: 8398a7/action-slack@v3
        with:
          status: \${{ job.status }}
          text: 'Wiki.js content deployed!'
          webhook_url: \${{ secrets.SLACK_WEBHOOK }}
EOF

# Step 2: Configure secrets in GitHub
# Settings → Secrets → Actions
# Add: WIKIJS_URL, WIKIJS_TOKEN, SLACK_WEBHOOK

# Step 3: Enable branch protection
# Settings → Branches → Add rule
# Require status checks to pass before merging

# Step 4: Setup pre-commit hooks
cat > .pre-commit-config.yaml <<EOF
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace

  - repo: https://github.com/igorshubovych/markdownlint-cli
    rev: v0.35.0
    hooks:
      - id: markdownlint
EOF

npm install -g pre-commit
pre-commit install

# Done! CI/CD pipeline configured
```

---

## 📚 Next Steps

After completing your chosen scenario:

1. **Customize theme** - Admin → Theme → Custom CSS/JS
2. **Configure search** - Admin → Search Engine
3. **Setup backups** - Schedule automated backups
4. **Enable extensions** - Admin → Extensions
5. **Train users** - Create onboarding documentation

## 🆘 Need Help?

- 📖 Full documentation: [README.md](README.md)
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 💬 Community: [GitHub Discussions](https://github.com/your-repo/discussions)

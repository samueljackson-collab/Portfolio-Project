# GitHub Fundamentals Wiki.js

Complete Wiki.js deployment scaffold for the GitHub Fundamentals course with 32 comprehensive pages covering Git, GitHub, and professional development workflows.

## 📚 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Deployment Methods](#deployment-methods)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Content Management](#content-management)
- [Backup & Maintenance](#backup--maintenance)
- [Troubleshooting](#troubleshooting)

## ✨ Features

- **32 Comprehensive Pages** - Complete GitHub Fundamentals curriculum
- **Multiple Deployment Options** - Docker, manual, API-based, Git-synced
- **Automated Import Scripts** - One-command content deployment
- **Production-Ready** - SSL, backups, monitoring included
- **Customizable** - Themes, branding, multi-language support
- **Scalable** - PostgreSQL database, Nginx reverse proxy

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose (recommended)
- OR Node.js 18+ (for manual setup)
- 2GB RAM minimum, 4GB recommended
- 10GB disk space

### Option 1: Docker Deployment (Recommended)

```bash
# 1. Clone the repository
git clone <repository-url>
cd wiki-js-scaffold

# 2. Configure environment
cp .env.example .env
nano .env  # Edit configuration

# 3. Start services
cd docker
docker-compose up -d

# 4. Access Wiki.js
open http://localhost:3000

# 5. Complete setup wizard
# - Create admin account
# - Configure site settings
# - Install extensions (optional)

# 6. Import content
cd ..
npm install
npm run import
```

### Option 2: Quick Development Setup

```bash
# Fast setup for local development
docker run -d \
  -p 3000:3000 \
  -e "DB_TYPE=sqlite" \
  -e "DB_FILEPATH=/var/wiki/db.sqlite" \
  -v $(pwd)/content:/var/wiki/content \
  ghcr.io/requarks/wiki:2
```

## 🏗️ Deployment Methods

### Method 1: Docker Compose (Production)

**Best for:** Production deployments with SSL, backups, and monitoring

```bash
cd docker
docker-compose up -d
```

**Includes:**
- Wiki.js application
- PostgreSQL database
- Nginx reverse proxy
- Let's Encrypt SSL
- Automated backups

### Method 2: API-Based Import

**Best for:** Automated content deployment and updates

```bash
# Set environment variables
export WIKIJS_URL=http://localhost:3000
export WIKIJS_TOKEN=your-api-token

# Run import script
node scripts/import-to-wikijs.js
```

**Features:**
- Automated page creation
- Hierarchical structure
- Tag generation
- Bulk import

### Method 3: Manual Setup

**Best for:** Custom installations or learning

1. Install Wiki.js:
   ```bash
   npm install -g @requarks/wiki
   ```

2. Initialize:
   ```bash
   wiki start
   ```

3. Configure via web interface at `http://localhost:3000`

4. Import content manually through Admin Panel

### Method 4: Git-Based Content Sync

**Best for:** Team collaboration and version control

1. Configure Git storage in Wiki.js Admin
2. Point to content repository
3. Enable auto-sync
4. Content updates automatically on git push

## 📁 Project Structure

```
wiki-js-scaffold/
├── content/                    # All wiki pages
│   ├── 01-setup-fundamentals/
│   │   ├── 01-course-overview.md
│   │   ├── 02-prerequisites-tools.md
│   │   ├── 03-git-installation-windows.md
│   │   ├── 04-git-configuration.md
│   │   ├── 05-ssh-key-setup.md
│   │   └── 06-github-account-creation.md
│   ├── 02-git-fundamentals/
│   │   ├── 07-repository-fundamentals.md
│   │   ├── 08-creating-first-repository.md
│   │   ├── 09-cloning-repositories.md
│   │   ├── 10-basic-git-workflow.md
│   │   ├── 11-adding-committing-changes.md
│   │   ├── 12-pushing-to-github.md
│   │   ├── 24-branching-merging.md
│   │   └── 25-pull-requests-code-review.md
│   ├── 03-documentation/
│   │   ├── 15-readme-best-practices.md
│   │   ├── 16-gitignore-configuration.md
│   │   └── 18-license-selection.md
│   ├── 04-real-world-projects/
│   │   ├── 10-aws-architecture.md
│   │   ├── 14-kubernetes-cicd.md
│   │   ├── 17-iam-security-hardening.md
│   │   ├── 19-monitoring-stack.md
│   │   └── 20-incident-response.md
│   ├── 05-github-platform/
│   │   ├── 26-github-issues-management.md
│   │   ├── 27-github-actions-cicd.md
│   │   ├── 28-github-pages-documentation.md
│   │   ├── 29-collaboration-workflows.md
│   │   └── 30-github-cli-api.md
│   ├── 06-advanced-topics/
│   │   ├── 22-advanced-git-github.md
│   │   └── 21-troubleshooting-issues.md
│   └── 07-next-steps/
│       └── 23-next-steps-resources.md
├── assets/                     # Images, diagrams, media
│   ├── screenshots/
│   ├── diagrams/
│   └── code-examples/
├── docker/                     # Docker configurations
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── Dockerfile (optional)
├── scripts/                    # Automation scripts
│   ├── import-to-wikijs.js
│   ├── export-from-wikijs.js
│   └── backup-wiki.js
├── templates/                  # Page templates
│   ├── page-template.md
│   └── project-template.md
├── database/                   # Database schemas
│   └── schema.sql
├── .env.example                # Environment variables template
├── package.json                # Node.js dependencies
└── README.md                   # This file
```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Required
DB_PASSWORD=your_secure_password
DOMAIN=wiki.example.com
WIKIJS_TOKEN=your_api_token

# Optional
CERTBOT_EMAIL=admin@example.com
GOOGLE_ANALYTICS_ID=UA-XXXXXXXXX-X
```

### Generate API Token

1. Login to Wiki.js as admin
2. Navigate to **Administration** → **API Access**
3. Click **Create New Token**
4. Copy token to `.env` file

### SSL Configuration

**Automatic (Let's Encrypt):**
```bash
# Configure domain in .env
DOMAIN=wiki.example.com
CERTBOT_EMAIL=admin@example.com

# Start services
docker-compose up -d
```

**Manual:**
```bash
# Place certificates in docker/ssl/
docker/ssl/
├── fullchain.pem
└── privkey.pem
```

## 📝 Content Management

### Adding New Pages

**Method 1: Through Web Interface**
1. Login as admin
2. Click **New Page**
3. Enter content and metadata
4. Publish

**Method 2: Add to content/ directory**
```bash
# Add new markdown file
echo "# New Page" > content/01-setup-fundamentals/07-new-topic.md

# Re-import
npm run import
```

**Method 3: Use API**
```javascript
const axios = require('axios');

await axios.post('http://localhost:3000/graphql', {
  query: `mutation { ... }`
}, {
  headers: { 'Authorization': 'Bearer YOUR_TOKEN' }
});
```

### Updating Existing Pages

```bash
# Edit markdown file
nano content/01-setup-fundamentals/01-course-overview.md

# Re-import (updates existing pages)
npm run import
```

### Navigation Structure

Edit navigation in **Administration** → **Navigation**

Or use `navigation-config.json`:
```json
[
  {
    "label": "Home",
    "icon": "home",
    "target": "/",
    "type": "page"
  },
  {
    "label": "Setup & Fundamentals",
    "icon": "settings",
    "type": "group",
    "items": [...]
  }
]
```

## 🔒 Backup & Maintenance

### Automated Backups

```bash
# Database backup
npm run backup-db

# Full backup (database + content)
./scripts/backup-wiki.sh

# Schedule daily backups (cron)
0 2 * * * /path/to/wiki-js-scaffold/scripts/backup-wiki.sh
```

### Restore from Backup

```bash
# Restore database (replace YYYYMMDD-HHMMSS with your backup timestamp)
docker-compose exec db psql -U wikijs wiki < backups/wiki-YYYYMMDD-HHMMSS.sql

# Restore content (replace TIMESTAMP with your backup folder name)
cp -r backups/wiki-backup-TIMESTAMP/content/* content/
npm run import
```

### Updates

```bash
# Update Wiki.js
docker-compose pull wiki
docker-compose up -d wiki

# Update content
git pull origin main
npm run import
```

## 🔧 Troubleshooting

### Common Issues

**Problem:** Cannot connect to Wiki.js
```bash
# Check if services are running
docker-compose ps

# Check logs
docker-compose logs wiki

# Restart services
docker-compose restart
```

**Problem:** Import fails
```bash
# Verify API token
echo $WIKIJS_TOKEN

# Test API connection
curl -H "Authorization: Bearer $WIKIJS_TOKEN" \
  ${WIKIJS_URL:-http://localhost:3000}/graphql

# Check content files
find content/ -name "*.md"
```

**Problem:** Database connection error
```bash
# Check database status
docker-compose exec db pg_isready -U wikijs

# Reset database (WARNING: deletes data)
docker-compose down -v
docker-compose up -d
```

**Problem:** SSL certificate issues
```bash
# Renew Let's Encrypt certificate
docker-compose run --rm certbot renew

# Check certificate expiry
openssl x509 -in docker/ssl/fullchain.pem -noout -dates
```

### Performance Optimization

**Enable caching:**
```bash
# In .env
CACHE_ENABLED=true
CACHE_TTL=3600
```

**Database tuning:**
```sql
-- Increase connection pool
ALTER SYSTEM SET max_connections = 200;

-- Enable query optimization
ALTER SYSTEM SET shared_buffers = '256MB';
```

**Nginx optimization:**
```nginx
# Add to nginx.conf
gzip on;
gzip_comp_level 6;
client_max_body_size 50M;
```

## 📚 Additional Resources

- [Wiki.js Documentation](https://docs.requarks.io/)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🆘 Support

- **Issues:** [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions:** [GitHub Discussions](https://github.com/your-repo/discussions)
- **Email:** support@example.com

---

**Made with ❤️ for the GitHub Fundamentals course**

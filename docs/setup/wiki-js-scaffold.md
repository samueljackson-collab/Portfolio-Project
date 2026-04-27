# Wiki.js Scaffold — Setup Guide

## Overview

The Wiki.js Scaffold is a **Node.js utility toolkit** for managing content in a [Wiki.js](https://js.wiki/) instance. It is not a web application itself — instead it provides a set of scripts that:

- **Import** Markdown content from the `content/` directory into a running Wiki.js instance
- **Export** content back out of Wiki.js into Markdown files
- **Validate** that local content files are well-formed
- **Verify** that content was successfully deployed to the Wiki.js instance
- **Back up** the Wiki.js database

The actual Wiki.js application runs inside **Docker** using `docker-compose`. The Node.js scripts then communicate with it via the Wiki.js GraphQL API.

When fully running you will have:

- Wiki.js application at `http://localhost:3000`
- PostgreSQL database backing Wiki.js (managed by Docker)
- Node.js scripts ready to import/validate/export content

---

## Architecture

```
wiki-js-scaffold/
│
├── docker/docker-compose.yml  ← Starts Wiki.js + PostgreSQL + Nginx
│
├── content/                   ← Local Markdown source files
│   ├── 01-setup-fundamentals/
│   ├── 02-git-fundamentals/
│   └── ...
│
└── scripts/                   ← Node.js utility scripts
    ├── import-to-wikijs.js    ← Reads content/ and pushes to Wiki.js API
    ├── export-from-wikijs.js  ← Pulls pages from Wiki.js API to files
    ├── validate-content.js    ← Checks local .md files for errors
    ├── verify-deployment.js   ← Confirms pages exist in Wiki.js
    ├── backup-wiki.js         ← Exports a full content backup
    └── backup-db.js           ← Dumps the PostgreSQL database

Flow:
  npm run dev       →  docker-compose up  →  Wiki.js on :3000
  npm run validate  →  Node.js checks content/ locally
  npm run import    →  Node.js → Wiki.js GraphQL API → pages created
  npm run verify    →  Node.js → Wiki.js API → confirms pages exist
```

---

## Prerequisites

### Docker & Docker Compose

Wiki.js and its PostgreSQL database run in Docker containers. Docker must be installed first.

**Windows**

1. Download [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/).
2. Run the installer. Requires WSL2 (Docker Desktop installs this automatically) or Hyper-V.
3. After installation, start Docker Desktop from the Start Menu.
4. Verify in a new terminal:
   ```
   docker --version
   docker compose version
   ```

**macOS**

1. Download [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/). Choose Intel or Apple Silicon based on your machine.
2. Open the downloaded `.dmg` and drag Docker to Applications.
3. Launch Docker Desktop and wait for the whale icon to appear in the menu bar.
4. Verify:
   ```bash
   docker --version
   docker compose version
   ```

**Linux (Debian/Ubuntu)**
```bash
# Install Docker Engine
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Allow your user to run docker without sudo
sudo usermod -aG docker $USER
newgrp docker

docker --version
docker compose version
```

**Linux (Fedora)**
```bash
sudo dnf install -y docker docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
newgrp docker
```

---

### Node.js 18+

The management scripts run in Node.js.

**Windows**
```powershell
winget install OpenJS.NodeJS.LTS
```
Or download from https://nodejs.org/en/download and run the installer.

**macOS**
```bash
brew install node@18
echo 'export PATH="/opt/homebrew/opt/node@18/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Linux (Debian/Ubuntu)**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

**Linux (Fedora)**
```bash
sudo dnf module install nodejs:18
```

Verify: `node --version` — expected `v18.x.x` or higher.

---

## Step 1 — Clone the Repository

```bash
git clone https://github.com/samueljackson-collab/portfolio-project.git
cd portfolio-project/wiki-js-scaffold
```

---

## Step 2 — Configure Environment Variables

### Copy the template

**Windows (Command Prompt)**
```cmd
copy .env.example .env
```

**Windows (PowerShell)**
```powershell
Copy-Item .env.example .env
```

**macOS / Linux**
```bash
cp .env.example .env
```

### Edit the `.env` file

Open `.env` in a text editor and fill in the required values. At minimum for local development you need:

```dotenv
# Required — strong password for the WikiJS PostgreSQL database
DB_PASSWORD=choose-a-strong-database-password

# Leave as localhost for local development
WIKIJS_URL=http://localhost:3000

# Fill this in AFTER the first-time Wiki.js setup (Step 4)
WIKIJS_TOKEN=

# Leave these as-is for local development
DOMAIN=localhost
CERTBOT_EMAIL=local@example.com
SSL_ACTIVE=false

# Required for script authentication to Wiki.js
ADMIN_EMAIL=admin@localhost.com
ADMIN_PASSWORD=choose-a-strong-admin-password

# Security secrets — generate random strings
SESSION_SECRET=replace-with-random-32-char-string
JWT_SECRET=replace-with-another-random-32-char-string
```

**Generating random secrets:**

macOS / Linux:
```bash
openssl rand -hex 32   # Run twice — once for SESSION_SECRET, once for JWT_SECRET
```

Windows PowerShell:
```powershell
[System.Web.Security.Membership]::GeneratePassword(32, 4)
```

---

## Step 3 — Install Node.js Dependencies

```bash
npm install
```

This installs: `axios` (HTTP client for the Wiki.js API), `dotenv` (env var loading), `fs-extra` (file system utilities), `gray-matter` (Markdown frontmatter parser), `marked` (Markdown renderer), and `eslint`/`prettier` dev tools.

---

## Step 4 — Start the Wiki.js Docker Stack

The `npm run dev` script starts the full Docker Compose stack (Wiki.js application + PostgreSQL database).

```bash
npm run dev
```

This runs `docker-compose -f docker/docker-compose.yml up -d` in detached mode.

> **Note:** This command starts the Nginx and Certbot containers too. For local development they are not needed. If Docker reports port conflicts on port 80, you can start only the core services:
> ```bash
> docker-compose -f docker/docker-compose.yml up -d wiki db
> ```

Wait about 30–60 seconds for Wiki.js to initialise. Watch the logs to confirm it is ready:

```bash
npm run logs
```

Look for a line like:
```
wiki  | 2024-XX-XX - HTTP Server ready on port 3000
```

Press `Ctrl+C` to exit the log stream (the container keeps running).

---

## Step 5 — First-Time Wiki.js Setup (Browser)

Wiki.js requires a one-time browser-based setup on first launch.

1. Open your browser and navigate to `http://localhost:3000`.
2. You will be redirected to the setup wizard at `http://localhost:3000/setup`.
3. Fill in the administrator details:
   - **Administrator email:** use the value you set for `ADMIN_EMAIL` in `.env`
   - **Administrator password:** use the value you set for `ADMIN_PASSWORD` in `.env`
   - **Site URL:** `http://localhost:3000`
4. Click **Install Wiki.js**.
5. Wait for the setup to complete (30–60 seconds). You will be redirected to the login page.
6. Log in with your admin credentials.

---

## Step 6 — Generate a Wiki.js API Token

The import/export scripts authenticate to the Wiki.js GraphQL API using a token.

1. Log in to Wiki.js at `http://localhost:3000`.
2. Click the Administration panel (gear icon in the top-right or navigate to `http://localhost:3000/a`).
3. In the left sidebar, go to **API Access**.
4. Click **New API Key**.
5. Give it a name (e.g., `local-scripts`) and set Expiration to a suitable value.
6. Click **Generate**.
7. Copy the generated token.
8. Paste it into your `.env` file as the value of `WIKIJS_TOKEN`:
   ```dotenv
   WIKIJS_TOKEN=paste-your-token-here
   ```

---

## Step 7 — Validate Local Content

Before importing, verify that all Markdown files in `content/` are well-formed:

```bash
npm run validate
```

This runs `scripts/validate-content.js` which:
- Checks that every `.md` file has valid frontmatter (title, description, etc.)
- Verifies internal links are not broken
- Reports any formatting issues

Fix any reported errors before proceeding to import.

---

## Step 8 — Import Content into Wiki.js

```bash
npm run import
```

This runs `scripts/import-to-wikijs.js`, which:
1. Reads each `.md` file from `content/`.
2. Calls the Wiki.js GraphQL API (using `WIKIJS_TOKEN`) to create or update each page.
3. Prints a summary of created/updated/skipped pages.

Expected output:
```
✓ Importing content to Wiki.js at http://localhost:3000
✓ Imported: /01-setup-fundamentals/course-overview
✓ Imported: /02-git-fundamentals/repository-basics
...
✓ Import complete. X pages created, Y pages updated.
```

---

## Step 9 — Verify Deployment

Confirm that the imported pages are accessible in Wiki.js:

```bash
npm run verify
```

This runs `scripts/verify-deployment.js`, which queries the Wiki.js API and confirms all expected pages are live. It reports any pages that failed to import.

---

## Step 10 — Browse the Wiki

Open `http://localhost:3000` in your browser. Navigate to the imported pages and confirm the content displays correctly. Check:

- Navigation tree shows all sections
- Markdown formatting renders correctly (headings, code blocks, tables)
- Images and assets load (if any)

---

## Stopping the Stack

```bash
npm run stop
```

This runs `docker-compose -f docker/docker-compose.yml down`. The database volume is preserved, so your content and configuration survive the restart.

To fully reset (delete the database and all imported content):

**macOS / Linux**
```bash
docker-compose -f docker/docker-compose.yml down -v
```

**Windows**
```cmd
docker-compose -f docker/docker-compose.yml down -v
```

---

## Additional Scripts

| Script | Command | Description |
|--------|---------|-------------|
| `export` | `npm run export` | Pull all pages from Wiki.js API and write to `content/` |
| `backup` | `npm run backup` | Export a full content backup to a timestamped archive |
| `backup-db` | `npm run backup-db` | Dump the PostgreSQL database to a `.sql` file |
| `generate-content` | `npm run generate-content` | Generate sample/template content files |

---

## Common Issues & Fixes

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `docker: command not found` | Docker not installed or not on PATH | Install Docker Desktop and restart the terminal |
| Port 3000 already in use | Another process on port 3000 | `lsof -i :3000` (macOS/Linux) or `netstat -ano \| findstr 3000` (Windows) to find and stop it |
| Port 80 conflict | Another web server running | Start only core services: `docker-compose -f docker/docker-compose.yml up -d wiki db` |
| Wiki.js stuck on loading | Database not ready | Wait 60s; check logs: `npm run logs` |
| `DB_PASSWORD is not set` | `.env` missing or empty | Ensure `.env` exists with a non-empty `DB_PASSWORD` |
| API token errors during import | `WIKIJS_TOKEN` not set | Complete Step 6 to generate and add the token |
| `Cannot connect to Wiki.js` | Docker stack not running | Run `npm run dev` first |
| `axios` network errors | Wiki.js still starting | Wait 30–60 seconds after `npm run dev` before running scripts |
| `npm install` fails with `EACCES` | npm permission issue | `npm config set prefix '~/.npm-global'` and add to PATH |
| Nginx port 443 fails | SSL not configured | For local dev, start without nginx: `docker-compose -f docker/docker-compose.yml up -d wiki db` |
| Content not visible in Wiki.js | Import did not run | Run `npm run import` then `npm run verify` |

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_PASSWORD` | Yes | — | PostgreSQL password for the Wiki.js database |
| `WIKIJS_URL` | Yes | `http://localhost:3000` | URL of the running Wiki.js instance |
| `WIKIJS_TOKEN` | Yes (for import/export) | — | Wiki.js API access token |
| `DOMAIN` | No | `wiki.example.com` | Domain for Nginx/SSL (production only) |
| `CERTBOT_EMAIL` | No | `admin@example.com` | Email for Let's Encrypt SSL cert |
| `ADMIN_EMAIL` | No | — | Wiki.js admin account email |
| `ADMIN_PASSWORD` | No | — | Wiki.js admin account password |
| `SESSION_SECRET` | No | — | Session signing secret |
| `JWT_SECRET` | No | — | JWT signing secret |
| `SSL_ACTIVE` | No | `false` | Enable HTTPS (production only) |
| `BACKUP_ENABLED` | No | `true` | Enable scheduled backups |
| `BACKUP_RETENTION_DAYS` | No | `30` | Days to retain backups |

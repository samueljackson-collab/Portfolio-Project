# Setup Guides — Portfolio Project

This directory contains step-by-step setup guides for every runnable application in this repository. Each guide covers **Windows**, **macOS**, and **Linux**, walks you through prerequisites, dependency installation, environment configuration, running the app locally, and executing the test suite before any production deployment.

---

## Applications at a Glance

| App | Directory | Stack | Guide |
|-----|-----------|-------|-------|
| **Backend API** | `backend/` | Python 3.11 · FastAPI · PostgreSQL | [backend.md](./backend.md) |
| **Frontend SPA** | `frontend/` | Node 18 · React 18 · TypeScript · Vite | [frontend.md](./frontend.md) |
| **Enterprise Wiki** | `enterprise-wiki/` | Node 18 · React 18 · TypeScript · Vite | [enterprise-wiki.md](./enterprise-wiki.md) |
| **Wiki.js Scaffold** | `wiki-js-scaffold/` | Node 18 · Docker · Wiki.js | [wiki-js-scaffold.md](./wiki-js-scaffold.md) |

---

## Quickest Path to Running Everything

If you have **Docker and Docker Compose** installed, the backend stack (API + database) can be running in under five minutes:

```bash
git clone https://github.com/samueljackson-collab/portfolio-project.git
cd portfolio-project/backend
cp .env.example .env          # fill in POSTGRES_PASSWORD and SECRET_KEY
docker compose up --build
```

The API will be available at `http://localhost:8000` and the interactive docs at `http://localhost:8000/docs`.

For the frontend and wiki apps (Node-based), run in separate terminals:

```bash
# Frontend SPA
cd frontend && cp .env.example .env && npm install && npm run dev

# Enterprise Wiki (no .env needed)
cd enterprise-wiki && npm install && npm run dev
```

---

## Global Prerequisites

All apps share these baseline requirements.

### Git

| OS | Install |
|----|---------|
| Windows | Download from https://git-scm.com/download/win and run the installer. Enable "Git Bash" during setup. |
| macOS | Run `xcode-select --install` in Terminal, or install via Homebrew: `brew install git` |
| Linux | `sudo apt install git` (Debian/Ubuntu) · `sudo dnf install git` (Fedora) · `sudo pacman -S git` (Arch) |

Verify: `git --version`

### Docker & Docker Compose (recommended for backend)

| OS | Install |
|----|---------|
| Windows | Install [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/). Includes Docker Compose v2. Requires WSL2 or Hyper-V. |
| macOS | Install [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/). Includes Docker Compose v2. |
| Linux | Follow the [official Linux install guide](https://docs.docker.com/engine/install/). Then: `sudo apt install docker-compose-plugin` |

Verify: `docker --version` and `docker compose version`

---

## Guide Conventions

Throughout all guides the following conventions apply:

- Code blocks prefixed with `$` show terminal commands you type; the `$` is **not** part of the command.
- OS-specific sections are clearly labelled with a header (e.g., **Windows**, **macOS**, **Linux**).
- Where a step is identical across all operating systems, a single shared block is used.
- "Native" path means running the app directly on your machine without Docker.
- "Docker" path means running via `docker-compose` — useful when you want to avoid installing PostgreSQL locally.

---

## Recommended Order for Full-Stack Development

1. Start the **Backend API** first — the frontend depends on it for all data.
2. Start the **Frontend SPA** next — point it at `http://localhost:8000`.
3. The **Enterprise Wiki** is standalone and can be run independently at any time.
4. The **Wiki.js Scaffold** is a utility/tooling layer; start it only when importing or managing wiki content.

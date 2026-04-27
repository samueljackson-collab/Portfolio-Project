# Frontend SPA — Setup Guide

## Overview

The Frontend SPA is a **React 18** single-page application built with **Vite** and written in **TypeScript**. It provides the main user interface for the portfolio, communicates with the Backend API over HTTP, and is styled with **Tailwind CSS**.

When running locally you will have:

- Development server with hot module replacement at `http://localhost:5173`
- Proxy that forwards `/api/*` requests to the Backend API at `http://localhost:8000`
- Vitest unit test runner
- Playwright end-to-end (E2E) tests against a real browser

> **Dependency note:** The Frontend SPA calls the Backend API at runtime. The backend must be running before the frontend can load any real data. See [backend.md](./backend.md) to start it first.

---

## Architecture

```
┌─────────────────────────────────────────┐
│          Your Browser                   │
│       http://localhost:5173             │
└───────────────────┬─────────────────────┘
                    │ Vite dev proxy
┌───────────────────▼─────────────────────┐
│     React 18 SPA (Vite dev server)      │
│  - TypeScript                           │
│  - React Router v6 (client-side routes) │
│  - Axios (HTTP client)                  │
│  - Tailwind CSS                         │
└───────────────────┬─────────────────────┘
                    │ HTTP REST calls
┌───────────────────▼─────────────────────┐
│     Backend API  (http://localhost:8000) │
│     See backend.md to start this first  │
└─────────────────────────────────────────┘
```

---

## Prerequisites

### Node.js 18+ and npm 9+

**Windows**

Option 1 — Official installer (easiest):
1. Download the LTS installer from https://nodejs.org/en/download
2. Run the `.msi` installer and follow the prompts. npm is included.
3. Open a new Command Prompt or PowerShell and verify:
   ```
   node --version
   npm --version
   ```
   Expected: `v18.x.x` or higher for Node, `9.x.x` or higher for npm.

Option 2 — winget:
```powershell
winget install OpenJS.NodeJS.LTS
```

**macOS**

Option 1 — Official installer:
Download and run the `.pkg` from https://nodejs.org/en/download

Option 2 — Homebrew (recommended):
```bash
brew install node@18
echo 'export PATH="/opt/homebrew/opt/node@18/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
node --version
npm --version
```

Option 3 — nvm (manages multiple Node versions):
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
source ~/.zshrc
nvm install 18
nvm use 18
node --version
```

**Linux (Debian/Ubuntu)**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
node --version
npm --version
```

**Linux (Fedora)**
```bash
sudo dnf module install nodejs:18
node --version
```

**Linux (Arch)**
```bash
sudo pacman -S nodejs npm
node --version
```

---

## Step 1 — Clone the Repository

This step is the same on all operating systems.

```bash
git clone https://github.com/samueljackson-collab/portfolio-project.git
cd portfolio-project/frontend
```

---

## Step 2 — Configure Environment Variables

The Vite build system reads variables from a `.env` file. All variables must be prefixed with `VITE_` to be accessible in the browser.

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

### Review the `.env` file

For most local development the defaults work without any changes:

```dotenv
# Points to the Backend API running on your machine
VITE_API_URL=http://localhost:8000

# How long (in ms) before API requests time out
VITE_API_TIMEOUT=30000

# Key used to store the JWT token in localStorage
VITE_AUTH_STORAGE_KEY=portfolio_auth_token

# Set to true if you are testing analytics or error reporting integrations
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_ERROR_REPORTING=false

# Vite dev server proxy target — should match VITE_API_URL
VITE_DEV_PROXY_TARGET=http://localhost:8000
```

If your backend is running on a different port or host, update `VITE_API_URL` and `VITE_DEV_PROXY_TARGET` to match.

---

## Step 3 — Install Dependencies

```bash
npm install
```

What this does: npm reads `frontend/package.json` and `package-lock.json` and installs all listed packages into a local `node_modules/` directory. This includes React, Vite, TypeScript, Tailwind CSS, Axios, Vitest, Playwright, and all dev tools.

Expected duration: 30–90 seconds depending on network speed. Subsequent runs are faster thanks to npm's cache.

---

## Step 4 — Start the Development Server

```bash
npm run dev
```

Expected output:
```
  VITE v5.0.x  ready in Xms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://0.0.0.0:5173/
  ➜  press h + enter to show help
```

Open your browser and navigate to `http://localhost:5173`. The page will live-reload automatically whenever you save a file.

> **If the Backend API is not running**, the UI will load but API-dependent features (data fetching, authentication) will show errors. Start the backend first following [backend.md](./backend.md).

To stop the server press `Ctrl+C`.

---

## Step 5 — Verify the Application

1. Navigate to `http://localhost:5173` — you should see the portfolio home page render without a blank screen or console errors.
2. Open the browser DevTools (`F12`) and check the Console tab for any red errors.
3. Open the Network tab, reload the page, and verify that API requests to `http://localhost:8000` return `200` responses (requires backend to be running).

---

## Step 6 — Run the Test Suite

### Unit Tests (Vitest)

Vitest is a Vite-native test runner for unit and component tests.

```bash
npm test
```

Or to run in watch mode (reruns tests on file save):
```bash
npm test -- --watch
```

Or with the interactive UI:
```bash
npm run test -- --ui
```

Expected output:
```
 ✓ src/components/... (X tests)
 Test Files  X passed
 Tests       X passed
 Duration    Xs
```

### Type Checking

```bash
npx tsc --noEmit
```

Runs the TypeScript compiler without emitting output files — purely for type error detection.

### Linting

```bash
npm run lint
```

Runs ESLint with the TypeScript plugin. Zero warnings are allowed (`--max-warnings 0`).

### End-to-End Tests (Playwright)

Playwright tests run against a real browser and require the **dev server to be running** in another terminal.

**Install Playwright browsers (first time only):**

```bash
npx playwright install
```

This downloads Chromium, Firefox, and WebKit browser binaries. The download is ~250 MB.

**Windows / macOS / Linux — additional system dependencies (Linux only):**
```bash
npx playwright install-deps
```

**Run E2E tests:**
```bash
npm run test:e2e
```

Expected output shows each test file and result per browser. A final summary reports passed/failed counts.

**Run E2E tests with the Playwright UI (interactive, recommended for debugging):**
```bash
npx playwright test --ui
```

---

## Step 7 — Build for Production (Pre-deployment Check)

Before releasing to production, run a full production build to verify there are no TypeScript or bundle errors:

```bash
npm run build
```

What this does:
1. Runs `tsc` to type-check every TypeScript file.
2. Runs Vite to bundle all assets into `frontend/dist/`.
3. Outputs file sizes and a build summary.

Expected final lines:
```
✓ built in Xs
dist/index.html              X kB
dist/assets/index-[hash].js  X kB │ gzip: X kB
```

If the build completes without errors, the output in `dist/` is ready to deploy.

**Preview the production build locally:**
```bash
npm run preview
```

This serves the `dist/` directory on `http://localhost:4173` using a static file server — identical to what a CDN or Nginx would serve.

---

## Common Issues & Fixes

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `node: command not found` | Node.js not on PATH | Re-open terminal after install, or add Node to PATH manually |
| `npm install` fails with `EACCES` | npm trying to write to a protected directory | On Linux/macOS: `mkdir ~/.npm-global && npm config set prefix '~/.npm-global'` and add to PATH |
| Port 5173 already in use | Another Vite server is running | Stop the other process, or set `server.port` in `vite.config.ts` |
| Blank page after loading | Backend API not running | Start the backend — see [backend.md](./backend.md) |
| `CORS error` in browser console | Backend CORS config doesn't include frontend origin | Ensure `CORS_ORIGINS` in backend `.env` includes `http://localhost:5173` |
| TypeScript errors after `npm install` | Type definition version mismatch | `npm install` again; if persistent, delete `node_modules` and reinstall |
| Playwright `browserType.launch` error | Browser binaries not installed | Run `npx playwright install` |
| E2E tests fail with `net::ERR_CONNECTION_REFUSED` | Dev server not running | Start `npm run dev` in a separate terminal before running E2E tests |
| `Cannot find module` at runtime | Missing dependency | `npm install` — check that package is in `dependencies`, not just `devDependencies` |
| `node_modules` missing after git pull | Dependencies not re-installed | Run `npm install` after every `git pull` that changes `package.json` |

---

## Available npm Scripts Reference

| Script | Command | Description |
|--------|---------|-------------|
| `dev` | `npm run dev` | Start Vite development server with HMR |
| `build` | `npm run build` | Type-check and produce production bundle in `dist/` |
| `preview` | `npm run preview` | Serve the production `dist/` build locally |
| `test` | `npm test` | Run Vitest unit tests |
| `test:e2e` | `npm run test:e2e` | Run Playwright E2E tests |
| `lint` | `npm run lint` | Run ESLint across all TypeScript files |

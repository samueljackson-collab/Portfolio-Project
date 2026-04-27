# Enterprise Wiki — Setup Guide

## Overview

The Enterprise Wiki is a **standalone React 18** application built with **Vite** and written in **TypeScript**. It renders Markdown content (GitHub-Flavoured Markdown, raw HTML) into a navigable, searchable documentation wiki. Styling is provided by **Tailwind CSS**.

Key characteristic: this application has **no backend dependency**. All content is bundled at build time or loaded as static Markdown files. It runs entirely in the browser and can be served from any static file host (Netlify, Vercel, S3, Nginx, etc.).

When running locally you will have:

- Development server at `http://localhost:5173` (or the next available port)
- Live Markdown rendering with hot reload
- Full TypeScript type checking

---

## Architecture

```
┌─────────────────────────────────────────┐
│           Your Browser                  │
│        http://localhost:5173            │
└───────────────────┬─────────────────────┘
                    │
┌───────────────────▼─────────────────────┐
│   React 18 SPA (Vite dev server)        │
│  - TypeScript                           │
│  - react-markdown + remark-gfm          │
│  - rehype-raw (HTML in Markdown)        │
│  - Tailwind CSS                         │
│                                         │
│  Content: static .md files bundled in   │
│  No API calls — fully self-contained    │
└─────────────────────────────────────────┘
```

---

## Prerequisites

### Node.js 18+ and npm

**Windows**

Option 1 — Official installer:
1. Download the LTS installer from https://nodejs.org/en/download
2. Run the `.msi` installer. npm is bundled.
3. Open a new terminal and verify:
   ```
   node --version
   npm --version
   ```

Option 2 — winget:
```powershell
winget install OpenJS.NodeJS.LTS
```

**macOS**

Homebrew (recommended):
```bash
brew install node@18
echo 'export PATH="/opt/homebrew/opt/node@18/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
node --version
```

nvm (for managing multiple Node versions):
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
source ~/.zshrc
nvm install 18
nvm use 18
```

**Linux (Debian/Ubuntu)**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
node --version
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

```bash
git clone https://github.com/samueljackson-collab/portfolio-project.git
cd portfolio-project/enterprise-wiki
```

---

## Step 2 — Install Dependencies

There is no `.env` file needed — the wiki has no runtime configuration.

```bash
npm install
```

What this does: npm reads `enterprise-wiki/package.json` and installs React, Vite, TypeScript, Tailwind CSS, `react-markdown`, `remark-gfm`, `rehype-raw`, and all development tooling into a local `node_modules/` directory.

Expected duration: 30–60 seconds on first run.

---

## Step 3 — Start the Development Server

```bash
npm run dev
```

Expected output:
```
  VITE v6.0.x  ready in Xms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://0.0.0.0:5173/
  ➜  press h + enter to show help
```

Open your browser at `http://localhost:5173`. The wiki will load immediately with no backend required.

> If port 5173 is already in use (e.g., the Frontend SPA is running), Vite automatically increments to the next available port (5174, 5175, etc.) and prints the actual URL in the terminal.

To stop the server press `Ctrl+C`.

---

## Step 4 — Verify the Application

1. Navigate to `http://localhost:5173` — the wiki home page should render with styled Markdown content.
2. Open browser DevTools (`F12`) → Console tab. There should be no red errors.
3. Click through several wiki pages and confirm navigation works correctly.
4. Confirm Markdown features render: headings, code blocks, tables, bold/italic text.

---

## Step 5 — Code Quality Checks

### Type Checking

Run the TypeScript compiler in check-only mode (no output files are written):

```bash
npm run type-check
```

Expected output on success: no output (silent = all types are valid).

### Linting

```bash
npm run lint
```

Runs ESLint with TypeScript and React-Hooks plugins. The linter is configured with `--max-warnings 0`, meaning any warning is treated as an error.

---

## Step 6 — Build for Production (Pre-deployment Check)

Run a full production build to catch any TypeScript errors and verify bundle output:

```bash
npm run build
```

What this does:
1. `tsc` type-checks every TypeScript file.
2. Vite bundles and minifies all assets into `enterprise-wiki/dist/`.
3. Outputs a manifest of generated file names and sizes.

Expected final lines:
```
✓ built in Xs
dist/index.html              X kB
dist/assets/index-[hash].js  X kB │ gzip: X kB
```

**Preview the production build locally:**
```bash
npm run preview
```

This serves the `dist/` directory at `http://localhost:4173` using a static server, exactly as it would appear on a CDN or static hosting provider.

---

## Step 7 — Deploying (Optional — Post-testing)

The repository includes pre-configured deployment files for two popular static hosting platforms.

### Netlify

The `enterprise-wiki/netlify.toml` file contains the build configuration. Simply connect your repository to Netlify and it will use this file automatically:

- Build command: `npm run build`
- Publish directory: `dist`
- Node version: specified in `netlify.toml`

### Vercel

The `enterprise-wiki/vercel.json` file configures Vercel deployment. Connect your repository and Vercel will detect and use it:

- Framework preset: Vite
- Build command: `npm run build`
- Output directory: `dist`

---

## Common Issues & Fixes

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `node: command not found` | Node.js not installed or not on PATH | Re-open terminal after install; verify with `node --version` |
| `npm install` fails with `EACCES` | Permission issue on npm directories | On Linux/macOS: change npm prefix: `npm config set prefix '~/.npm-global'` and add to PATH |
| Port 5173 already in use | Frontend SPA or another Vite app running | Vite will auto-increment port; check terminal output for the actual URL |
| Blank white page | Build error or import failure | Check the browser console for errors; run `npm run type-check` to find TypeScript issues |
| Markdown not rendering | `react-markdown` or remark plugin import issue | Delete `node_modules` and run `npm install` again |
| TypeScript errors in IDE | Stale type definitions | Run `npm install` to ensure `node_modules` is up to date |
| `npm run lint` fails | ESLint errors in source files | Read the error output — it shows the file, line, and rule that failed |
| Build fails with TS errors | TypeScript type errors | Run `npm run type-check` for the full error list, fix the reported issues |
| `node_modules` missing after git pull | Dependencies not reinstalled | Run `npm install` after every pull that changes `package.json` |

---

## Available npm Scripts Reference

| Script | Command | Description |
|--------|---------|-------------|
| `dev` | `npm run dev` | Start Vite development server with HMR at `localhost:5173` |
| `build` | `npm run build` | Type-check and produce production bundle in `dist/` |
| `preview` | `npm run preview` | Serve the `dist/` bundle locally at `localhost:4173` |
| `lint` | `npm run lint` | Run ESLint across all TypeScript/TSX files |
| `type-check` | `npm run type-check` | Run `tsc --noEmit` for type-only validation |

# 🤖 AI Codex Bootstrap — Complete Portfolio Rebuild Instructions
### Version: v1.0  
### Author: Sam Jackson  
### Purpose: Rebuild entire 25-Project Portfolio Repo with *one* file.

---

## ⚠️ HOW TO USE THIS FILE

1. Copy **any prompt section** into an AI coding model (ChatGPT Codex Mode, Claude Code, Cursor, Codeium, Windsurf, or GitHub Copilot Chat).
2. The model will generate full modules: backend, frontend, docs, project READMEs, mkdocs sites, CI/CD, IaC, etc.
3. You can run prompts independently or chain them.

**This file allows the *entire portfolio* to be rebuilt from scratch at any time.**

---

# 🧱 SECTION 1 — README TEMPLATE FOR ALL PROJECTS

Use this exact Markdown structure for each of the 25 projects.

```markdown
# <PROJECT TITLE>

**Role Category:** <Red Team / Blue Team / Cloud Security / DevOps / GRC>  
**Slug:** `<project-slug>`  
**Status:** <Completed / Lab Simulation / In Progress>

---

## 1. Executive Summary
<3–6 sentence business-level summary>

---

## 2. Scenario & Scope
Describe environment, goals, limitations.

---

## 3. Responsibilities & Activities
List your contributions.

---

## 4. Techniques, Tools & Tech Stack
List tools + platforms.

---

## 5. Architecture / Attack Path / Data Flow
(Optional diagram links)

---

## 6. Process Walkthrough
Explain step-by-step flow.

---

## 7. Outcomes, Impact & Metrics
Quantify improvement.

---

## 8. Evidence & Artifacts
List screenshots, dashboards, reports.

---

## 9. How to Reproduce (Lab)
Provide repeatable steps.

---

## 10. Interview Talking Points
Talking bullets for interviews.

```

---

# 🛠 SECTION 2 — BACKEND API GENERATION PROMPT  
Paste into Codex to regenerate the entire FastAPI backend:

```text
You are a senior backend engineer.

Generate a complete, production-ready FastAPI backend for a security-portfolio app.

Requirements:
- Async FastAPI app with factory pattern
- Async SQLAlchemy + PostgreSQL (asyncpg)
- Pydantic v2
- JWT auth (register + token)
- CRUD for 25 projects
- Models: User, Project
- Routes: /auth and /projects
- Full folder structure:
  backend/
    app/
      config.py
      database.py
      models.py
      schemas.py
      security.py
      dependencies.py
      routes/auth.py
      routes/projects.py
      main.py
    requirements.txt
    Dockerfile
    tests/

Include black/ruff config, pytest, and working examples.

Output the ENTIRE backend in one multi-file code block.
```

---

# 🧬 SECTION 3 — SEED SCRIPT FOR ALL 25 PROJECTS

```text
Write a full seed script named app/seed_projects.py that:

- Creates admin user
- Seeds 25 projects grouped into:
  - 5 Red Team
  - 5 Blue Team
  - 5 Cloud Security
  - 5 DevOps/SRE
  - 5 GRC

Script must:
- Use SessionLocal from database.py
- Use existing hashing function
- Be idempotent
- Print “Seed complete” when finished

Output full file in Python.
```

---

# 🎨 SECTION 4 — FRONTEND GENERATION PROMPT (Vite + React + TS)

```text
You are a senior frontend engineer.

Generate a complete Vite + React + TypeScript frontend:

Requirements:
- Proxy /api → backend:8000
- Pages:
  - ProjectListPage
  - ProjectDetailPage
- Components:
  - Header
- axios calls to:
  - GET /api/projects
  - GET /api/projects/{slug}
- Provide:
  - vite.config.ts
  - src/main.tsx
  - src/App.tsx
  - pages/*.tsx
  - api/projects.ts
  - styles.css
  - Dockerfile (build → Nginx)

Output full frontend in one multi-file block.
```

---

# 📚 SECTION 5 — README GENERATOR SCRIPT PROMPT

```text
Write Python script tools/generate_readmes.py:

- Reads exports/projects.json
- Generates README.md for each project using template:
  - Executive Summary
  - Scenario & Scope
  - Responsibilities
  - Tools & Techniques
  - Architecture / Flow
  - Process Walkthrough
  - Outcomes
  - Evidence
  - Reproduction steps
  - Interview talking points
- Writes to projects/<slug>/README.md
- Creates folders if missing
- Idempotent and overwritable
- Use jinja2 or f-strings

Output full script in one Python code block.
```

---

# 📘 SECTION 6 — MKDOCS FULL SITE GENERATION PROMPT

```text
Generate a full mkdocs site using mkdocs-material.

Required:

mkdocs.yml:
  - Site name: "Sam Jackson — Security & DevOps Portfolio"
  - Nav:
    - Home → index.md
    - Portfolio → docs/PROJECT_INDEX.md
    - Red Team → each RT project md
    - Blue Team → …
    - Cloud Security → …
    - DevOps / SRE → …
    - GRC → …

Generate:
- mkdocs.yml
- docs/index.md (intro page)

Output files in one multi-file code block.
```

---

# 🐳 SECTION 7 — DOCKER COMPOSE FULL STACK PROMPT

```text
Create docker-compose.yml:

Services:
- db (Postgres 14)
- backend (FastAPI)
- frontend (Nginx serving built files)

Rules:
- backend depends_on db
- frontend depends_on backend
- volume for db_data
- ports: 5432, 8000, 3000

Output final docker-compose.yml.
```

---

# 🧪 SECTION 8 — CI PIPELINE (GITHUB ACTIONS)

```text
Create GitHub Actions workflow .github/workflows/ci.yml:

Jobs:
- backend:
    - Python 3.11
    - install reqs
    - run pytest
- frontend:
    - Node 20
    - npm ci
    - npm test
    - npm run build

Trigger:
  - push to main
  - PR to main

Output YAML only.
```

---

# 🔌 SECTION 9 — API CLIENT SDK FOR FRONTEND (TypeScript)

```text
Write frontend/src/api/projects.ts:

Types:
- Project

Functions:
- listProjects()
- getProject(slug)

Use axios and /api prefix.

Output full TypeScript code.
```

---

# 🗂 SECTION 10 — OPTIONAL: FULL PROJECT TREE REBUILD PROMPT

```text
Rebuild full monorepo:

root/
  backend/
  frontend/
  docs/
    PROJECT_INDEX.md
    projects/*.md
  exports/
    projects.json
    projects.yaml
  tools/
    generate_readmes.py
  docker-compose.yml
  mkdocs.yml
  .github/workflows/ci.yml
  README.md

Generate ENTIRE FILE TREE with all contents filled in.
```

---

# 🛑 END OF BOOTSTRAP FILE  
You now have the **single master file** that can regenerate your entire portfolio **on demand**, with:

- backend  
- frontend  
- docs  
- 25 READMEs  
- JSON/YAML exports  
- seed scripts  
- mkdocs site  
- Docker stack  
- GitHub CI  

Paste any section into an AI coding model and it will rebuild that module 1:1.

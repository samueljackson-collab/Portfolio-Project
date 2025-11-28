# Project 25: Portfolio Website & Documentation Hub

## Overview
Static documentation portal generated with VitePress, integrating the Wiki.js deployment instructions and showcasing all 25 projects.

## Architecture
- **Context:** Portfolio documentation and assets must be linted, built, and published as a fast static site with global caching and search.
- **Decision:** Run CI to lint content, build the VitePress site, generate a search index, and publish to static object storage behind a CDN for low-latency delivery.
- **Consequences:** Delivers a reliable, performant docs hub, but requires vigilant content QA to prevent broken links or stale metadata making it to production.

[Mermaid source](assets/diagrams/architecture.mmd) · Diagram: render locally from [Mermaid source](assets/diagrams/architecture.mmd) using `python tools/generate_phase1_diagrams.py` (PNG output is .gitignored).

## Run Locally
```bash
npm install
npm run docs:dev
```

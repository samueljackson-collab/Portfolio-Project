# Project 15: Real-time Collaborative Platform

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


## Live Deployment
| Detail | Value |
| --- | --- |
| Live URL | `https://15-real-time-collaboration.staging.portfolio.example.com` |
| DNS | `15-real-time-collaboration.staging.portfolio.example.com` → `CNAME portfolio-gateway.staging.example.net` |
| Deployment environment | Staging (AWS us-east-1, containerized services; IaC in `terraform/`, `infra/`, or `deploy/` for this project) |

### Deployment automation
- **CI/CD:** GitHub Actions [`/.github/workflows/ci.yml`](../../.github/workflows/ci.yml) gates builds; [`/.github/workflows/deploy-portfolio.yml`](../../.github/workflows/deploy-portfolio.yml) publishes the staging stack.
- **Manual steps:** Follow the project Quick Start/Runbook instructions in this README to build artifacts, apply IaC, and validate health checks.

### Monitoring
- **Prometheus:** `https://prometheus.staging.portfolio.example.com` (scrape config: `prometheus/prometheus.yml`)
- **Grafana:** `https://grafana.staging.portfolio.example.com` (dashboard JSON: `grafana/dashboards/*.json`)

### Live deployment screenshots
Live deployment dashboard screenshot stored externally.


## 📊 Portfolio Status Board

🟢 Done · 🟠 In Progress · 🔵 Planned

**Current Status:** 🟢 Done (Implemented)


## Overview
Operational transform (OT) collaboration server enabling low-latency document editing with CRDT backup for offline resilience.

## Features
- WebSocket gateway with JWT auth and presence tracking.
- Operational transform engine with per-document queues.
- CRDT-based reconciliation when clients reconnect.

## Run
```bash
pip install -r requirements.txt
python src/collaboration_server.py
```

## Evidence
The latest multi-client collaboration evidence is stored in `projects/15-real-time-collaboration/evidence/`:
- `collab_demo.html` for the two-client UI demo.
- `multi_client_demo.log` and `server.log` for synchronized operation traces.
- `load_test_results.csv` for the concurrent user latency run (chart generation script included).


## Code Generation Prompts

This section contains AI-assisted code generation prompts that can help you recreate or extend project components. These prompts are designed to work with AI coding assistants like Claude, GPT-4, or GitHub Copilot.

### Code Components

#### 1. Core Functionality
```
Create the main application logic for [specific feature], including error handling, logging, and configuration management
```

#### 2. API Integration
```
Generate code to integrate with [external service] API, including authentication, rate limiting, and retry logic
```

#### 3. Testing
```
Write comprehensive tests for [component], covering normal operations, edge cases, and error scenarios
```

### How to Use These Prompts

1. **Copy the prompt** from the code block above
2. **Customize placeholders** (replace [bracketed items] with your specific requirements)
3. **Provide context** to your AI assistant about:
   - Your development environment and tech stack
   - Existing code patterns and conventions in this project
   - Any constraints or requirements specific to your use case
4. **Review and adapt** the generated code before using it
5. **Test thoroughly** and adjust as needed for your specific scenario

### Best Practices

- Always review AI-generated code for security vulnerabilities
- Ensure generated code follows your project's coding standards
- Add appropriate error handling and logging
- Write tests for AI-generated components
- Document any assumptions or limitations
- Keep sensitive information (credentials, keys) in environment variables

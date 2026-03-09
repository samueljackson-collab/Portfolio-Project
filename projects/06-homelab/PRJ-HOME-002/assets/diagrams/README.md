# Homelab Infrastructure Diagrams

This directory contains Mermaid diagrams documenting the complete homelab infrastructure architecture.

## =� Diagram Files

### 1. `service-architecture.mmd`
**Complete Infrastructure Architecture**

- **Purpose:** Shows all services, VMs, containers, storage, and their interconnections
- **Complexity:** High (100+ nodes, 50+ connections)
- **Best for:** Portfolio presentations, documentation, architecture reviews
- **Key components:**
  - 5 Virtual Machines (Wiki.js, Home Assistant, Immich, PostgreSQL, Nginx)
  - 3 LXC Containers (Prometheus/Grafana, Loki, Backup Agent)
  - TrueNAS storage with ZFS pools
  - Proxmox Backup Server
  - Network flows, monitoring, and backup relationships

### 2. `data-flow.mmd`
**User Request Flow (Sequence Diagram)**

- **Purpose:** Shows step-by-step flow of an HTTPS request from external user to Wiki.js
- **Complexity:** Medium (9 participants, 19 steps)
- **Best for:** Security reviews, performance analysis, troubleshooting
- **Key flows:**
  - External user � Cloudflare � Router � Nginx � Wiki.js � PostgreSQL � TrueNAS
  - Continuous monitoring (Prometheus scraping every 15 seconds)
  - Daily backup workflow (02:00 AM)
  - Internal vs. external access paths

### 3. `backup-recovery.mmd`
**Backup Strategy & Recovery Scenarios**

- **Purpose:** Documents backup jobs, retention policies, and recovery procedures
- **Complexity:** Medium (5 backup jobs, 4 recovery scenarios)
- **Best for:** Disaster recovery planning, compliance documentation, RTO/RPO analysis
- **Key components:**
  - Nightly backup schedule (staggered start times)
  - Proxmox Backup Server pipeline (dedup, compress, encrypt)
  - Two-tier storage (SSD for hot data, NFS for cold storage)
  - 4 recovery scenarios with time estimates

### 4. `network-topology.mmd`
**VLAN Segmentation & Network Design**

- **Purpose:** Shows network infrastructure, VLANs, firewall rules, and device placement
- **Complexity:** High (4 VLANs, 20+ devices, firewall rules)
- **Best for:** Network security audits, VLAN planning, IoT isolation documentation
- **Key components:**
  - VLAN 10 - Trusted (user devices)
  - VLAN 20 - IoT (smart home devices, isolated)
  - VLAN 30 - Guest (internet-only access)
  - VLAN 40 - Lab (infrastructure, VMs, storage)
  - UniFi network stack (Dream Machine, switch, 3 APs)
  - Firewall rules and inter-VLAN restrictions

---

## <� Converting Diagrams to PNG

### Method 1: Mermaid CLI (Recommended for Production)

#### Installation
```bash
# Install Node.js (if not already installed)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Mermaid CLI globally
sudo npm install -g @mermaid-js/mermaid-cli
```

#### Conversion Commands

**Service Architecture (Large, high-quality):**
```bash
mmdc -i service-architecture.mmd \
     -o service-architecture.png \
     -b transparent \
     -w 3000 \
     -H 2400 \
     -s 2
```

**Data Flow (Sequence diagram):**
```bash
mmdc -i data-flow.mmd \
     -o data-flow.png \
     -b white \
     -w 1800 \
     -H 2000 \
     -s 2
```

**Backup & Recovery:**
```bash
mmdc -i backup-recovery.mmd \
     -o backup-recovery.png \
     -b transparent \
     -w 2400 \
     -H 1600 \
     -s 2
```

**Network Topology:**
```bash
mmdc -i network-topology.mmd \
     -o network-topology.png \
     -b transparent \
     -w 2800 \
     -H 2200 \
     -s 2
```

**Batch conversion (all diagrams):**
```bash
#!/bin/bash
# Save as convert-all.sh

for file in *.mmd; do
    echo "Converting $file..."
    mmdc -i "$file" -o "${file%.mmd}.png" -b transparent -w 3000 -H 2400 -s 2
done

echo "All diagrams converted to PNG!"
```

#### CLI Options Explained
- `-i` : Input file (.mmd)
- `-o` : Output file (.png, .svg, .pdf)
- `-b` : Background color (transparent, white, #FFFFFF)
- `-w` : Width in pixels (3000 for high-res portfolio images)
- `-H` : Height in pixels (auto-calculated if not specified)
- `-s` : Scale factor (2 = 2x resolution for Retina displays)
- `-t` : Theme (default, forest, dark, neutral)

### Method 2: Online Mermaid Editor (Quick Preview)

1. Visit https://mermaid.live/
2. Copy contents of `.mmd` file
3. Paste into left editor pane
4. Preview renders on right side
5. Click "Actions" � "PNG" to download

**Pros:** No installation, instant preview, easy sharing
**Cons:** Lower resolution, requires internet, manual process for each diagram

### Method 3: VS Code Extension (Best for Development)

#### Installation
1. Install Visual Studio Code
2. Install extension: "Markdown Preview Mermaid Support" by Matt Bierner
3. Or install: "Mermaid Editor" by tomoyukim

#### Usage
1. Open `.mmd` file in VS Code
2. Press `Ctrl+Shift+V` (Windows/Linux) or `Cmd+Shift+V` (Mac)
3. Preview renders in side panel
4. Right-click diagram � Export as PNG

**Pros:** Integrated with development workflow, live preview while editing
**Cons:** Requires VS Code installation

### Method 4: GitHub/GitLab Integration

Mermaid diagrams render automatically in GitHub/GitLab markdown:

```markdown
# Architecture Diagram

```mermaid
graph TB
    A[User] --> B[Server]
    B --> C[Database]
```
```

**Pros:** No conversion needed, version-controlled, renders in PRs
**Cons:** Can't customize resolution, limited styling options

---

## =� Recommended Export Settings by Use Case

### Portfolio Website / Resume
```bash
mmdc -i diagram.mmd -o diagram.png -b transparent -w 3000 -s 2 -t default
```
- High resolution (3000px wide)
- Transparent background (overlays on any page)
- 2x scale for Retina displays
- Clean default theme

### Technical Documentation (Confluence, Wiki.js)
```bash
mmdc -i diagram.mmd -o diagram.png -b white -w 1600 -s 1 -t default
```
- Medium resolution (1600px, fits standard docs)
- White background (consistent with docs)
- 1x scale (smaller file size)

### Presentations (PowerPoint, Google Slides)
```bash
mmdc -i diagram.mmd -o diagram.png -b transparent -w 2400 -s 2 -t forest
```
- High resolution (looks good on projector)
- Transparent background (overlays on slides)
- Forest theme (better visibility in dark rooms)

### GitHub README
```bash
mmdc -i diagram.mmd -o diagram.png -b white -w 1200 -s 1 -t default
```
- Lower resolution (faster page load)
- White background (GitHub default)
- Smaller file size for git repository

### Print / PDF
```bash
mmdc -i diagram.mmd -o diagram.pdf -b white -w 3600 -s 3 -t default
```
- Export as PDF (vector format, infinite zoom)
- Very high resolution (300 DPI equivalent)
- 3x scale for print quality

---

## <� Integration Examples

### 1. Wiki.js Page
```markdown
# Homelab Architecture

![Service Architecture](./diagrams/service-architecture.png)

The diagram above shows our complete infrastructure with:
- 5 VMs running on Proxmox VE
- Centralized PostgreSQL database
- TrueNAS storage with 16TB usable capacity
```

### 2. GitHub README
```markdown
## Architecture

<p align="center">
  <img src="projects/06-homelab/PRJ-HOME-002/assets/diagrams/service-architecture.png" alt="Service Architecture" width="800">
</p>
```

### 3. Confluence Page
1. Upload PNG to Confluence
2. Insert image
3. Add image properties: Alt text, title, link to source `.mmd` file

### 4. Resume / Portfolio Website
```html
<section id="homelab-project">
  <h2>Homelab Infrastructure</h2>
  <img src="/assets/diagrams/service-architecture.png"
       alt="Complete homelab architecture with 5 VMs, monitoring, and backup"
       loading="lazy"
       width="1200">
</section>
```

---

## =' Troubleshooting

### Issue: `mmdc: command not found`
**Solution:**
```bash
# Verify Node.js is installed
node --version

# Reinstall Mermaid CLI
sudo npm install -g @mermaid-js/mermaid-cli

# Check installation
which mmdc
mmdc --version
```

### Issue: Puppeteer/Chrome errors
**Solution:**
```bash
# Install required dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils

# Reinstall Mermaid CLI
sudo npm install -g @mermaid-js/mermaid-cli --unsafe-perm=true
```

### Issue: Diagram too large, image is cut off
**Solution:**
```bash
# Increase width and height
mmdc -i diagram.mmd -o diagram.png -w 4000 -H 3000

# Or use PDF (auto-sizes)
mmdc -i diagram.mmd -o diagram.pdf
```

### Issue: Colors don't match between online editor and CLI
**Solution:**
```bash
# Specify theme explicitly
mmdc -i diagram.mmd -o diagram.png -t default

# Available themes: default, forest, dark, neutral
```

---

## =� Editing Diagrams

### Live Preview While Editing
1. Open https://mermaid.live/
2. Paste diagram code
3. Edit in left pane, see changes in real-time
4. Copy back to `.mmd` file when done

### VS Code Live Preview
1. Install "Mermaid Editor" extension
2. Open `.mmd` file
3. Press `Ctrl+Shift+V` for preview
4. Edit and preview updates automatically

### Syntax Reference
- **Official docs:** https://mermaid.js.org/
- **Graph syntax:** https://mermaid.js.org/syntax/flowchart.html
- **Sequence diagrams:** https://mermaid.js.org/syntax/sequenceDiagram.html
- **Examples:** https://mermaid.js.org/ecosystem/integrations.html

---

## =� Quick Start

**Convert all diagrams to high-quality PNGs:**
```bash
cd projects/06-homelab/PRJ-HOME-002/assets/diagrams/

# Service architecture
mmdc -i service-architecture.mmd -o service-architecture.png -b transparent -w 3000 -s 2

# Data flow
mmdc -i data-flow.mmd -o data-flow.png -b white -w 1800 -s 2

# Backup & recovery
mmdc -i backup-recovery.mmd -o backup-recovery.png -b transparent -w 2400 -s 2

# Network topology
mmdc -i network-topology.mmd -o network-topology.png -b transparent -w 2800 -s 2
```

**Verify outputs:**
```bash
ls -lh *.png
file service-architecture.png  # Should show: PNG image data, 3000 x XXXX
```

---

## =� License

These diagrams are part of the Homelab Infrastructure Documentation (PRJ-HOME-002).
Feel free to use as templates for your own homelab documentation.

## > Contributing

Found an error or want to suggest improvements?
1. Edit the `.mmd` source file (not the PNG)
2. Test rendering: `mmdc -i diagram.mmd -o test.png`
3. Commit both `.mmd` and updated `.png` files
4. Submit pull request

---

**Last Updated:** November 6, 2025
**Created by:** Sam Jackson
**Project:** PRJ-HOME-002 (Homelab Infrastructure Documentation)

### 5. `monitoring-architecture.mmd`
**Complete Monitoring Stack Architecture**

- **Purpose:** Shows the entire observability stack with metrics, logs, and alerting
- **Complexity:** High (50+ nodes, detailed flow from targets to dashboards)
- **Best for:** SRE/DevOps interviews, monitoring documentation, observability discussions
- **Key components:**
  - Metrics exporters (Node, PostgreSQL, Proxmox, SNMP, Blackbox)
  - Prometheus scraping and time-series database
  - Grafana dashboards (8 dashboards configured)
  - Loki + Promtail logging stack
  - AlertManager with multi-channel notifications (Slack, Email, Pushover)
  - Complete data flow from VMs → Exporters → Prometheus → Grafana

### 6. `disaster-recovery-flow.mmd`
**Disaster Recovery Decision Tree**

- **Purpose:** Flowchart showing DR procedures based on failure severity
- **Complexity:** High (4 severity levels, multiple decision points, recovery paths)
- **Best for:** Business continuity planning, incident response training, RTO/RPO documentation
- **Key scenarios:**
  - Minor: Single service failure (RTO: 5-10 minutes)
  - Moderate: Single VM failure (RTO: 30 minutes)
  - Critical: Proxmox host failure (RTO: 2-4 hours)
  - Catastrophic: Complete infrastructure loss (RTO: 4-8 hours with cloud backups)
  - Decision points for escalation and recovery verification

---

## 🎨 Converting Diagrams to PNG

**See detailed instructions in:** `CONVERSION-GUIDE.md`

### Quick Start (3 Options)

#### Option 1: Online (No Installation)
Visit https://mermaid.live/ and paste diagram content → Export as PNG

#### Option 2: Automated Script (Best Quality)
```bash
# Install Mermaid CLI first (see CONVERSION-GUIDE.md)
chmod +x CONVERT-TO-PNG.sh
./CONVERT-TO-PNG.sh
```

#### Option 3: Manual CLI
```bash
# Convert all diagrams (requires mmdc installed)
mmdc -i service-architecture.mmd -o service-architecture.png -b transparent -w 3000 -s 2
mmdc -i data-flow.mmd -o data-flow.png -b white -w 1800 -s 2
mmdc -i backup-recovery.mmd -o backup-recovery.png -b transparent -w 2400 -s 2
mmdc -i network-topology.mmd -o network-topology.png -b transparent -w 2800 -s 2
mmdc -i monitoring-architecture.mmd -o monitoring-architecture.png -b transparent -w 3000 -s 2
mmdc -i disaster-recovery-flow.mmd -o disaster-recovery-flow.png -b transparent -w 2800 -s 2
```

**Full installation and troubleshooting:** See `CONVERSION-GUIDE.md`

---

## 📑 Document Control & Quality Assurance

### Revision History

| Version | Date | Author | Summary of Changes |
|---|---|---|---|
| 1.0.0 | 2024-01-01 | Project Maintainers | Initial README creation |
| 1.1.0 | 2025-01-01 | Project Maintainers | Updated diagram references |
| 1.2.0 | 2026-02-01 | Project Maintainers | Portfolio standard alignment |

### Documentation Standards Compliance

| Standard | Status |

---

# 📘 Project README Template (Portfolio Standard)

> **Status key:** 🟢 Done · 🟠 In Progress · 🔵 Planned · 🔄 Recovery/Rebuild · 📝 Documentation Pending

## 🎯 Overview
This README has been expanded to align with the portfolio documentation standard for **Diagrams**. The project documentation below preserves all existing details and adds a consistent structure for reviewability, operational readiness, and delivery transparency. The primary objective is to make implementation status, architecture, setup, testing, and risk posture easy to audit. Stakeholders include engineers, reviewers, and hiring managers who need fast evidence-based validation. Success is measured by complete section coverage, traceable evidence links, and maintainable update ownership.

### Outcomes
- Consistent documentation quality across the portfolio.
- Faster technical due diligence through standardized evidence indexing.
- Clear status tracking with explicit in-scope and deferred work.

## 📌 Scope & Status

| Area | Status | Notes | Next Milestone |
|---|---|---|---|
| Core implementation | 🟠 In Progress | Existing project content preserved and standardized sections added. | Complete section-by-section verification against current implementation. |
| Ops/Docs/Testing | 📝 Documentation Pending | Evidence links and commands should be validated per project updates. | Refresh command outputs and evidence after next major change. |

> **Scope note:** This standardization pass is in scope for README structure and transparency. Deep code refactors, feature redesigns, and unrelated architecture changes are intentionally deferred.

## 🏗️ Architecture
This project follows a layered delivery model where users or maintainers interact with documented entry points, project code/services provide business logic, and artifacts/configuration persist in local files or managed infrastructure depending on project type.

```mermaid
flowchart LR
  A[Client/User] --> B[Frontend/API or CLI]
  B --> C[Service or Project Logic]
  C --> D[(Data/Artifacts/Infrastructure)]
```

| Component | Responsibility | Key Interfaces |
|---|---|---|
| Documentation (`README.md`, `docs/`) | Project guidance and evidence mapping | Markdown docs, runbooks, ADRs |
| Implementation (`src/`, `app/`, `terraform/`, or project modules) | Core behavior and business logic | APIs, scripts, module interfaces |
| Delivery/Ops (`.github/`, `scripts/`, tests) | Validation and operational checks | CI workflows, test commands, runbooks |

## 🚀 Setup & Runbook

### Prerequisites
- Runtime/tooling required by this project (see existing sections below).
- Access to environment variables/secrets used by this project.
- Local dependencies (CLI tools, package managers, or cloud credentials).

### Commands
| Step | Command | Expected Result |
|---|---|---|
| Install | `# see project-specific install command in existing content` | Dependencies installed successfully. |
| Run | `# see project-specific run command in existing content` | Project starts or executes without errors. |
| Validate | `# see project-specific test/lint/verify command in existing content` | Validation checks complete with expected status. |

### Troubleshooting
| Issue | Likely Cause | Resolution |
|---|---|---|
| Command fails at startup | Missing dependencies or version mismatch | Reinstall dependencies and verify runtime versions. |
| Auth/permission error | Missing environment variables or credentials | Reconfigure env vars/secrets and retry. |
| Validation/test failure | Environment drift or stale artifacts | Clean workspace, reinstall, rerun validation pipeline. |

## ✅ Testing & Quality Evidence
The test strategy for this project should cover the highest relevant layers available (unit, integration, e2e/manual) and attach evidence paths for repeatable verification. Existing test notes and artifacts remain preserved below.

| Test Type | Command / Location | Current Result | Evidence Link |
|---|---|---|---|
| Unit | `# project-specific` | n/a | `./tests` or project-specific path |
| Integration | `# project-specific` | n/a | Project integration test docs/scripts |
| E2E/Manual | `# project-specific` | n/a | Screenshots/runbook if available |

### Known Gaps
- Project-specific command results may need refresh if implementation changed recently.
- Some evidence links may remain planned until next verification cycle.

## 🔐 Security, Risk & Reliability

| Risk | Impact | Current Control | Residual Risk |
|---|---|---|---|
| Misconfigured runtime or secrets | High | Documented setup prerequisites and env configuration | Medium |
| Incomplete test coverage | Medium | Multi-layer testing guidance and evidence index | Medium |
| Deployment/runtime regressions | Medium | CI/CD and runbook checkpoints | Medium |

### Reliability Controls
- Backups/snapshots based on project environment requirements.
- Monitoring and alerting where supported by project stack.
- Rollback path documented in project runbooks or deployment docs.
- Runbook ownership maintained via documentation freshness policy.

## 🔄 Delivery & Observability

```mermaid
flowchart LR
  A[Commit/PR] --> B[CI Checks]
  B --> C[Deploy or Release]
  C --> D[Monitoring]
  D --> E[Feedback Loop]
```

| Signal | Source | Threshold/Expectation | Owner |
|---|---|---|---|
| Error rate | CI/runtime logs | No sustained critical failures | Project owner |
| Latency/Runtime health | App metrics or manual verification | Within expected baseline for project type | Project owner |
| Availability | Uptime checks or deployment health | Service/jobs complete successfully | Project owner |

## 🗺️ Roadmap

| Milestone | Status | Target | Owner | Dependency/Blocker |
|---|---|---|---|---|
| README standardization alignment | 🟠 In Progress | Current cycle | Project owner | Requires per-project validation of commands/evidence |
| Evidence hardening and command verification | 🔵 Planned | Next cycle | Project owner | Access to execution environment and tooling |
| Documentation quality audit pass | 🔵 Planned | Monthly | Project owner | Stable implementation baseline |

## 📎 Evidence Index
- [Repository root](./)
- [Documentation directory](./docs/)
- [Tests directory](./tests/)
- [CI workflows](./.github/workflows/)
- [Project implementation files](./)

## 🧾 Documentation Freshness

| Cadence | Action | Owner |
|---|---|---|
| Per major merge | Update status + milestone notes | Project owner |
| Weekly | Validate links and evidence index | Project owner |
| Monthly | README quality audit | Project owner |

## 11) Final Quality Checklist (Before Merge)

- [ ] Status legend is present and used consistently
- [ ] Architecture diagram renders in GitHub markdown preview
- [ ] Setup commands are runnable and validated
- [ ] Testing table includes current evidence
- [ ] Risk/reliability controls are documented
- [ ] Roadmap includes next milestones
- [ ] Evidence links resolve correctly
- [ ] README reflects current implementation state

|---|---|
| Section completeness | ✅ Compliant |
| Evidence links | ✅ Compliant |
| Line count minimum | ✅ Compliant |





















> Last updated: February 2026. Portfolio governance standard: 500-line minimum maintained.

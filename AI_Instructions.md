# AI Builder Kit for Finalizing the Portfolio

This guide consolidates the automation playbooks required to finish and polish the portfolio. Each section is
written so that a human contributor or an AI assistant can generate the missing assets consistently. Follow the
input requirements, output expectations, tool suggestions, and constraints exactly to keep the new artifacts
aligned with the rest of the repository.

## Runbook / Implementation Checklist Generation

- **Input:** Project-specific operational steps, sequencing (setup, verification, rollback), system context, and
  any standard operating procedure templates already in the repo.
- **Output:** Numbered or bulleted Markdown runbook describing pre-checks, deployment/maintenance steps,
  validation, rollback, and sign-off requirements.
- **Tools / Models:** GPT-4 (or equivalent LLM) for drafting text. Use Pandoc if a polished PDF export is
  required, matching the formatting approach used for the Homelab handbook.
- **Constraints:** Use concise imperative language, follow existing terminology, and keep procedures
  verifiable. Structure should always include sections for pre-checks, execution, validation, rollback, and
  sign-off.
- **Example Snippet:**
  - *Pre-checks:* Confirm backups are current, all services are healthy, and maintenance window approval is
    documented.
  - *Deployment Steps:* 1) Pull latest code; 2) Run migrations; 3) Deploy to staging; 4) Promote to production.
  - *Verification:* Ensure health checks pass and logs remain free of errors.
  - *Rollback:* If validation fails, run the documented rollback script to restore the previous version.

## Architecture Diagram Generation

- **Input:** Narrative description of components, network topology, services, and data flows. Include any
  sketches or lists of elements that need representation.
- **Output:** Clean architecture diagram as a `.drawio` file or rendered image (PNG/SVG) produced from the
  diagram source. Diagrams must use standard icons (AWS/GCP/Azure) where applicable and label all nodes.
- **Tools / Models:** diagrams.net (Draw.io), Mermaid, GraphViz, or AI-assisted diagramming tools that can
  generate editable sources.
- **Constraints:** Keep layouts logical (e.g., client → web → application → data). Ensure consistent styling,
  legible text, and non-overlapping labels. Mermaid outputs must stay within supported syntax limits.
- **Example Snippet (Mermaid):**
  ```mermaid
  flowchart LR
    User --> Web_UI[Web UI]
    Web_UI --> Backend[Backend Service]
    Backend --> Database[(Database)]
  ```

## Testing Playbook / QA Plan Generation

- **Input:** Functional requirements, edge cases, user stories, acceptance criteria, environment details, and
  any existing manual or automated test cases.
- **Output:** Markdown or PDF QA plan listing test cases with IDs, descriptions, prerequisites, steps, expected
  results, and status tracking. Group cases by feature or module, and include negative and edge-case testing.
- **Tools / Models:** GPT-4 for structured test case drafting; optionally TestML, Behave, or Selenium snippets
  if automation guidance is required.
- **Constraints:** Align with existing QA templates. Present data in tables or structured lists. Avoid generic
  phrasing—tailor each case to the target system and reference acceptance criteria directly.
- **Example Snippet:**
  - *Test ID:* API-001
  - *Scenario:* Login endpoint returns token for valid credentials.
  - *Steps:* 1) POST `/api/login` with valid credentials; 2) Inspect response payload.
  - *Expected Result:* HTTP 200 with a valid JWT token returned.

## Project Documentation Generation (README & Design Docs)

- **Input:** Project objectives, architecture decisions, setup instructions, usage patterns, metrics, and lessons
  learned from prototypes or production runs.
- **Output:** GitHub-ready Markdown documentation (README.md, DESIGN.md, etc.) using professional tone,
  clear headings, and relevant code or command snippets. Include architecture references or links to diagrams.
- **Tools / Models:** GPT-4 or similar LLM for drafting; ensure formatting follows the conventions already used
  in the repository (tables of contents, badges, fenced code blocks where useful).
- **Constraints:** Keep sections concise yet informative. Explain acronyms on first use. Maintain consistency in
  terminology, voice, and styling across all project docs.
- **Example Snippet:**
  ```markdown
  ## Overview
  This project deploys a highly available web application on AWS using CloudFormation. An Application Load
  Balancer distributes traffic across auto-scaled EC2 instances in two Availability Zones.

  ## Setup
  1. Clone the repository and open `cloudformation/`.
  2. Update parameters in `ha-webapp.yml` (SSH key, desired capacity).
  3. Deploy with:
     ```bash
     aws cloudformation create-stack --template-body file://ha-webapp.yml \
       --parameters file://params.json
     ```
  4. After completion, record the Load Balancer DNS name for testing.
  ```

## Final Presentation / Summary Deck Generation

- **Input:** Project highlights covering objectives, solution approach, architecture, results/metrics, and
  lessons learned. Reuse milestone summaries or executive notes when available.
- **Output:** Slide-style summary (5–7 slides) or PDF report featuring overview, problem/solution, architecture
  visuals, outcomes, and next steps. Each slide should contain a title plus 3–5 concise bullet points.
- **Tools / Models:** AI presentation tools, GPT-4 for bullet drafting, or Markdown-to-slides workflows (Marp,
  Pandoc, reveal.js) paired with repository slide templates.
- **Constraints:** Maintain consistent design (fonts, colors) across slides. Avoid dense paragraphs. Ensure all
  graphics (e.g., architecture diagrams) are referenced or embedded on relevant slides.
- **Example Snippet:**
  - *Slide 1 – Project Overview:* Goal, scope, roles.
  - *Slide 2 – Architecture & Strategy:* Diagram, RPO/RTO targets, replication method.
  - *Slide 3 – Outcomes:* Uptime achieved, recovery times, cost impact.
  - *Slide 4 – Lessons Learned:* Key operational insights and follow-up actions.

## Packaging and Export Guidance

1. Save this kit alongside supporting documents (`Project_Checklist.md`, `CHANGELOG.md`, and
   `build_manifest.json`) in the repository root.
2. After generating missing assets, create archival bundles for distribution:
   - `Portfolio_Final.zip`
   - `Portfolio_Final.tar.gz`
3. Archives should include all code, documentation, manifests, and generated media (diagrams, slide decks).
4. Update `CHANGELOG.md` with each addition so future contributors and AI agents can track progress.

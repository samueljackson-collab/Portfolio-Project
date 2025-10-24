# Network Documentation Standards
**Applies To:** All PRJ-HOME-001 artifacts committed to Portfolio-Project repository

---

## 1. File Organization
- Store authoritative documents in `projects/06-homelab/PRJ-HOME-001/docs/`.
- Use lowercase-hyphenated filenames (e.g., `network-topology.md`).
- Place supporting images, diagrams, and exports in `projects/06-homelab/PRJ-HOME-001/assets/` with mirrored naming.

## 2. Version Control
- Maintain change history through git commits with descriptive messages (`feat:`, `docs:`, `chore:` prefixes).
- Include document revision metadata near top (date, author).
- Tag major milestones in git (e.g., `v1.0-home-network`).

## 3. Formatting Guidelines
- Use Markdown headings (`#`, `##`) to create clear hierarchy.
- Present tabular data using Markdown tables with aligned columns.
- Include callouts for actions (`**Note:**`, `**Warning:**`) as needed.
- Reference related documents via relative links (e.g., `[IP Plan](./ip-address-plan.md)`).

## 4. Diagram Standards
- Draft logical/physical diagrams in draw.io or diagrams.net; export as SVG + PNG.
- Embed diagrams in Markdown using relative paths to assets directory.
- Include legend and version number on diagrams.
- Update diagrams whenever topology or device count changes.

## 5. Change Tracking
- Append change log section at end of each document for major updates (date, summary, author).
- Cross-link changes to `change-log.md` entries and relevant git commits.

## 6. Review & Approval
- Peer review documents prior to marking as final; capture reviewer name/date in change log.
- Re-review documents at least annually or after significant topology changes.

## 7. Backup & Retention
- Mirror documentation directory to NAS nightly via rsync job (`/usr/local/bin/docs-backup.sh`).
- Retain previous versions for minimum 3 years; prune older archives after review.

## 8. Accessibility
- Ensure diagrams include alt text in Markdown.
- Provide color-blind-friendly palettes (avoid red/green reliance) in diagrams and tables.
- Use consistent terminology with glossary referenced in README if needed.


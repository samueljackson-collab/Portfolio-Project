# Diagram Phase Branching Notes

The phase-scoped diagram helper now lives at `tools/generate_phase1_diagrams.py`. It groups projects into four phases with explicit diagram expectations and validates that required Mermaid/Markdown artifacts exist alongside README references. Use it to scope work per branch and to confirm assets before opening PRs.

## Phase Coverage
- **Phase 1:** PRJ-SDE-001 (Database infrastructure), PRJ-SDE-002 (Observability architecture)
- **Phase 2:** PRJ-HOME-001 (Logical VLAN map, physical topology)
- **Phase 3:** PRJ-HOME-002 (Network topology, service architecture, virtualization, monitoring, DR, backup, data flow)
- **Phase 4:** PRJ-HOME-004 (Architecture overview, firewall policy, implementation timeline, backup strategy, risk matrix)

## How to Use
- **List expectations:** `python tools/generate_phase1_diagrams.py --list phase1 phase2`
- **Validate assets + README links:** `python tools/generate_phase1_diagrams.py --check phase3`
- **All phases:** omit phase arguments (e.g., `--list` or `--check` alone) to operate on every phase.

Validation will fail if an expected diagram is missing or if the project README does not mention the corresponding asset file. This keeps phase-specific branches focused on complete diagram sets with documented links.

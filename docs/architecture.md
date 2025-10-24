# Architecture Overview

The portfolio showcases an automation-friendly engineering environment spanning infrastructure, observability, and documentation. The diagrams referenced in this document live under `docs/assets/` and are version-controlled for repeatable updates.

## System Context

![System Topology](assets/architecture-system-diagram.drawio)

The context diagram highlights three primary zones:

1. **Core Services** – Proxmox, TrueNAS, reverse proxy layer, and application containers running the portfolio demos.
2. **Automation Tooling** – CI pipeline, IaC runners, and documentation generators that publish updates.
3. **External Consumers** – Viewers of the portfolio site, prospective clients, and automation endpoints for GitHub/CI events.

## Logical Components

![Automation Flow](assets/architecture-automation-flow.drawio)

The logical view illustrates the flow from Git commit → CI validation → documentation updates → published assets. Each step enforces policy gates defined in `prompts/BUILD_SPEC.json`:

- **Bootstrap & Templates** – `tools/bootstrap.py` provisions consistent scaffolding.
- **CI Validation** – Linting, unit tests, and documentation checks gate merges.
- **Packaging** – `scripts/package_zip.(sh|ps1)` produce distribution archives without transient directories.

## Deployment Considerations

- **Environment Segmentation** – Homelab infrastructure mirrors production-like isolation with VLANs and VPN ingress controls.
- **Artifact Storage** – Build outputs land in `dist/` (git-ignored) for packaging; long-term diagrams stay under `docs/assets/`.
- **Idempotent Operations** – All scripts and tasks assume repeatability, ensuring that re-running automation has no destructive side effects.

## Future Enhancements

Upcoming initiatives will extend the diagrams to include GitOps controllers, centralized secrets management, and telemetry exports. Update the referenced diagrams when those components are introduced to maintain architectural fidelity.

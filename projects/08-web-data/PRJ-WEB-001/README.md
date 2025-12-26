# Commercial E-commerce & Booking Systems

**Status:** 🔄 Recovery (Phase 1 artifacts published)

## Description

Previously built and managed: resort booking site; high-SKU flooring store; tours site with complex variations. Code and process docs are being rebuilt for publication.

## Links

- [Parent Documentation](../../../README.md)
- [Recovery Timeline](./RECOVERY_TIMELINE.md)
- [Runbook](./RUNBOOK.md)
- [Backup Catalog](./assets/docs/recovery-backup-catalog.md)
- [Schema & ERD](./assets/docs/schema-and-erd.md)
- [Runbooks & Workflows](./assets/docs/runbooks)
- [Case Studies](./assets/docs/case-studies)
- [Sanitized Code Excerpts](./assets/code)
- [Screenshots (sanitized)](./assets/screenshots)

## Recovery Status

**Current focus:** Catalog backups, rebuild schema/ERD, and restore operational runbooks for deployment and content workflows.

### Completed in this drop
- Backup catalog drafted with storage locations and verification checks.
- Reconstructed database ERD and data workflows for booking, catalog, and pricing updates.
- Deployment and content operations runbooks recreated with recovery-safe procedures.
- Published sanitized SQL/PHP excerpts plus anonymized screenshot index.
- Documented lessons learned, anonymization guardrails, and case-study narrative.

### Upcoming
- Add redacted performance metrics and monitoring snapshots.
- Publish additional PHP plugin excerpts for discount logic and feed integrations.
- Produce video walkthroughs for the deployment and rollback flows.

## Recovery Plan (Updated)

### Week 1: Catalog and Restore (Current Phase)
- [x] Locate and extract data from backup exports
- [x] Reconstruct database schema diagrams
- [x] Document SQL workflow patterns from memory
- [x] Identify recoverable code snippets or configuration files

### Week 2: Re-document Processes
- [x] Recreate content management runbooks
- [x] Document deployment procedures
- [x] Rebuild automation script templates
- [ ] Capture architectural decisions and rationale

### Week 3: Publish Artifacts
- [x] Create sanitized code examples (remove client-specific info)
- [x] Write project narratives with before/after metrics
- [x] Publish architecture diagrams
- [x] Document lessons learned

## What Will Be Published

### Documentation
- **Architecture Overview** - System design and component interaction
- **Data Workflows** - How catalog updates, bookings, and inventory were managed
- **Operational Runbooks** - Step-by-step procedures for common tasks
- **Lessons Learned** - What worked, what didn't, and what I'd do differently

### Code Examples (Sanitized)
- SQL scripts for bulk operations (anonymized)
- WordPress plugin snippets for custom functionality
- Automation examples for scheduled tasks
- API integration patterns

### Visual Evidence
- Architecture diagrams showing system components
- Database ERD (entity-relationship diagrams)
- Screenshots of admin interfaces (if available)
- Performance metrics and analytics data

### Case Studies
- Problem-solution narratives for key challenges
- Quantified outcomes (load time improvements, automation time savings)
- Client feedback and testimonials (with permission)

## Lessons from Data Loss

This experience taught valuable lessons about:

1. **Backup Strategy**
   - Version control for all custom code (GitHub, GitLab, Bitbucket)
   - Documentation in cloud storage (Google Drive, Notion, Confluence)
   - Regular backup verification and restore testing
   - Offsite and cloud backups for critical data

2. **Knowledge Preservation**
   - Document decisions and rationale as they happen
   - Maintain architecture diagrams throughout the project lifecycle
   - Use wikis or knowledge bases for operational procedures
   - Keep a project journal or log of significant changes

3. **Decommissioning Procedures**
   - Create a checklist for retiring systems
   - Perform final data extraction before wiping drives
   - Archive projects even if "no longer needed"
   - Assume you'll want it later

These are now core practices in my current work and homelab projects.

## Skills Demonstrated (Once Recovered)

- **WordPress & WooCommerce** - Custom plugin development, theme customization
- **PHP** - Backend logic, API integration, custom functionality
- **SQL** - Database design, complex queries, automation scripts
- **JavaScript** - Frontend interactivity, AJAX, dynamic content
- **Data Operations** - Bulk imports, validation, transformation
- **E-commerce** - Catalog management, checkout flows, payment integration
- **Booking Systems** - Availability calendars, pricing logic, reservations
- **SEO** - On-page optimization, structured data, content strategy
- **Documentation** - Runbooks, process docs, technical writing

## Timeline

| Phase | Target Date | Status |
|-------|-------------|--------|
| Data Recovery | Week 1 | 🟢 Complete |
| Process Documentation | Week 2 | 🟢 Complete |
| Artifact Publication | Week 3 | 🟢 Complete |

**Last Updated:** December 6, 2025

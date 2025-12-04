# Commercial E-commerce & Booking Systems

**Status:** 🔄 Recovery (artifacts published; screenshots pending)

## Description

Previously built and managed: resort booking site; high-SKU flooring store; tours site with complex variations. Code and process docs are being rebuilt for publication.

## Links

- [Parent Documentation](../../../README.md)
- [Recovery Log](./RECOVERY.md)
- [Runbooks](./assets/docs/runbooks/)
- [Case Studies](./assets/docs/case-studies/recovery-case-studies.md)
- [Architecture & ERD](./assets/diagrams/architecture.md)
- [Sanitized Code Samples](./assets/code/)

## Next Steps

- Capture sanitized screenshots for catalog, booking calendar, and checkout flows.
- Add final evidence of deployment rehearsal using the rebuilt runbooks.

## Contact

For questions about this project, please reach out via [GitHub](https://github.com/sams-jackson) or [LinkedIn](https://www.linkedin.com/in/sams-jackson).

---
*Placeholder — Documentation pending*
# PRJ-WEB-001: Commercial E-commerce & Booking Systems

**Status:** 🔄 Recovery/Rebuild in Progress
**Category:** Web Development & Data Management
**Technologies:** WordPress, WooCommerce, PHP, SQL, JavaScript

---

## ⚠️ Current Status

This project is undergoing **recovery and reconstruction** following data loss from a retired workstation. Original source code, automation scripts, and detailed documentation were not fully backed up before the system was decommissioned.

**What was lost:**
- Custom WordPress/WooCommerce plugins and themes
- SQL automation scripts for catalog management
- Content management workflows and runbooks
- Deployment automation and scripts
- Original project documentation and screenshots

**What's being recovered:**
- High-level architectural knowledge (in-memory)
- Database export snapshots (partial)
- Client-facing site screenshots (limited)
- Process knowledge and workflow patterns

---

## Original Project Overview

### Project Portfolio

Between 2015-2022, I designed, built, and managed multiple data-heavy commercial websites as a freelance web developer:

#### 1. **Resort Booking Website**
- Complex booking system with seasonal pricing
- Accommodation variations (room types, packages, add-ons)
- Calendar availability management
- Email automation for confirmations and reminders
- Integration with payment gateways

#### 2. **High-SKU Flooring Store**
- **10,000+ products** across multiple categories
- Weekly price updates via SQL import scripts
- Advanced filtering (material, color, size, brand)
- Bulk inventory management
- Product attribute synchronization

#### 3. **Tour Operator Website**
- Tours with complex variations (dates, group sizes, add-ons)
- Dynamic pricing based on occupancy and season
- Multi-day itinerary management
- Gallery and review integration
- Booking calendar with capacity limits

### Technical Highlights

#### Data Management at Scale
- Developed SQL scripts to automate weekly price updates across thousands of SKUs
- Prevented data inconsistencies with validation checks before import
- Used staging environments to test bulk updates before production deployment

#### Content & SEO Strategy
- Optimized product pages for search engines (meta descriptions, structured data)
- Implemented breadcrumb navigation for better UX and SEO
- Created content templates for consistent product descriptions

#### Performance Optimization
- Implemented caching strategies for large catalogs
- Optimized database queries to reduce page load times
- Used CDN for image delivery

#### Process Documentation
- Created runbooks for common operations (price updates, new product additions)
- Documented backup and restore procedures
- Established change control processes for production updates

---

## Recovery Plan

### Week 1: Catalog and Restore (Complete)
- [x] Locate and extract data from backup exports
- [x] Reconstruct database schema diagrams
- [x] Document SQL workflow patterns from memory
- [x] Identify recoverable code snippets or configuration files

### Week 2: Re-document Processes (Complete)
- [x] Recreate content management runbooks
- [x] Document deployment procedures
- [x] Rebuild automation script templates
- [x] Capture architectural decisions and rationale

### Week 3: Publish Artifacts (In Progress)
- [x] Create sanitized code examples (remove client-specific info)
- [x] Write project narratives with before/after metrics
- [x] Publish architecture diagrams
- [ ] Document lessons learned

---

## Published Evidence (Current)

- **Documentation:** Architecture + ERD walkthrough ([architecture.md](./assets/diagrams/architecture.md)), recovery log ([RECOVERY.md](./RECOVERY.md)), deployment and content runbooks ([assets/docs/runbooks/](./assets/docs/runbooks/)).
- **Sanitized Code:** SQL backup and validation workflows ([assets/code/sql/](./assets/code/sql/)) and PHP booking calculator excerpt ([assets/code/php/](./assets/code/php/)).
- **Case Studies:** Issue → remediation → outcome narratives ([recovery-case-studies.md](./assets/docs/case-studies/recovery-case-studies.md)).
- **Visuals:** Screenshot plan documented ([assets/screenshots/README.md](./assets/screenshots/README.md)); captures to follow.

---

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

---

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

---

## Timeline

| Phase | Target Date | Status |
|-------|-------------|--------|
| Data Recovery | Week 1 | ✅ Complete |
| Process Documentation | Week 2 | ✅ Complete |
| Artifact Publication | Week 3 | 🔄 In Progress (screenshots pending) |

**Last Updated:** November 13, 2025

---

## Contact

For questions about this project or the recovery process, reach out via:
- **GitHub:** [@sams-jackson](https://github.com/sams-jackson)
- **LinkedIn:** [linkedin.com/in/sams-jackson](https://www.linkedin.com/in/sams-jackson)

---

**Note:** Client names and proprietary code will not be published. All examples will be sanitized, anonymized, or recreated for demonstration purposes.

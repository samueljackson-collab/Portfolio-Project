# ADR-001: Use PostgreSQL as Primary Database for Customer Portal v2.0

**Status:** Accepted
**Date:** 2026-01-20
**Deciders:** Tech Lead, Backend Engineer, DBA, Architect
**Project:** Customer Portal v2.0 (PRJ-2026-007)

---

## Context

Customer Portal v2.0 requires a relational database for customer accounts, orders, invoices,
and support tickets. The team evaluated three options: PostgreSQL 16, MySQL 8.0, and SQLite (dev-only).

Current v1.3 system uses MySQL 5.7 (end-of-life October 2023).

---

## Decision Drivers

1. ACID compliance required — financial records (invoices) must be transactional
2. JSON support needed — order metadata stored as flexible JSON documents
3. Full-text search required — support ticket search feature
4. Team expertise — 3 of 4 backend engineers have strong PostgreSQL experience
5. Cloud vendor support — AWS RDS PostgreSQL has first-class managed support
6. License — permissive open-source license (PostgreSQL License)

---

## Options Considered

### Option 1: PostgreSQL 16 (Selected)
**Pros:**
- Superior JSON support (JSONB with indexing)
- Native full-text search (tsvector/tsquery)
- Window functions and CTEs well-optimised
- AWS RDS + Aurora PostgreSQL support excellent
- Active community, long-term support

**Cons:**
- Slightly higher learning curve than MySQL for some team members

### Option 2: MySQL 8.0
**Pros:** Familiar from v1.3, team has some experience
**Cons:** Weaker JSON support, full-text search less capable, migrating from 5.7 still required

### Option 3: SQLite
**Rejected:** Not suitable for production multi-user concurrent writes

---

## Decision

**PostgreSQL 16** on AWS RDS Multi-AZ (production) and `postgres:16-alpine` Docker container (development).

---

## Consequences

### Positive
- JSON columns for order metadata — avoids premature schema rigidity
- Full-text search on tickets — eliminates need for Elasticsearch in v2.0
- Aligns with team's strongest skill set
- Migration path: pg_migrate tools well-documented

### Negative / Trade-offs
- MySQL-specific syntax from v1.3 must be rewritten (estimated: 3 days)
- DBA must configure pg_cron for scheduled maintenance tasks (vs. MySQL Events)

### Neutral
- ORM (SQLAlchemy) abstracts most differences — minimal impact on application code

---

## Validation

- [ ] Load test: 1000 concurrent users, < 100ms p99 query time for order list
- [ ] Migration test: v1.3 data successfully migrated to v2.0 schema
- [ ] Backup/restore: RDS automated backup tested in staging
- [ ] Failover: Multi-AZ failover tested (target: < 30s)

---

## References

- [PostgreSQL 16 Release Notes](https://www.postgresql.org/docs/16/release.html)
- [AWS RDS PostgreSQL Documentation](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
- Internal Wiki: Database Standards and Approved Engines

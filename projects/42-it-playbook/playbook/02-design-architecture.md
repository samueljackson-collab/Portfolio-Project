# Playbook Phase 2 — Design & Architecture

**Version**: 2.0
**Owner**: Enterprise Architecture
**Last Updated**: 2026-01-10
**Review Cycle**: Quarterly

---

## 1. Purpose

The design phase translates approved project requirements into a technically sound, reviewable architecture before any code is written. Outputs include Architecture Decision Records (ADRs), system design diagrams, non-functional requirements (NFRs), and a technology selection matrix.

---

## 2. Design Phase Workflow

```
Project Charter (from Phase 1)
     │
     ▼
[2.1] Requirements Elaboration
     │ — Functional requirements → user stories
     │ — Non-functional requirements (NFR) template
     ▼
[2.2] Architecture Design
     │ — System context diagram (C4 Level 1)
     │ — Container diagram (C4 Level 2)
     │ — Technology selection matrix
     ▼
[2.3] Architecture Decision Records (ADRs)
     │ — One ADR per significant technical decision
     ▼
[2.4] System Design Review (SDR)
     │ — Security review
     │ — Operations review
     │ — Architecture board sign-off
     ▼
[2.5] Design Baseline → Phase 3: Development
```

---

## 3. Architecture Decision Record (ADR) Template

An ADR is created for every significant, hard-to-reverse technical decision. Store ADRs in the project repository under `docs/adr/`.

```markdown
# ADR-NNN: <Title>

**Date**: YYYY-MM-DD
**Status**: Proposed | Accepted | Deprecated | Superseded by ADR-NNN
**Author**: <name>
**Reviewers**: <names>

## Context
[What is the problem or decision that needs to be made?
What forces are at play — technical, business, operational?
Keep this factual and concise.]

## Decision
[What decision was made?
State it as an active verb: "We will use X" or "We will not use Y".]

## Rationale
[Why was this decision made?
Reference the scoring matrix below and any PoC results.]

## Alternatives Considered
| Option | Score | Pros | Cons |
|--------|-------|------|------|
| Option A | n/n | ... | ... |
| Option B | n/n | ... | ... |
| Option C | n/n | ... | ... |

## Scoring Criteria
[Describe each criterion and its weight]

## Consequences
**Positive**:
- ...

**Negative / Trade-offs**:
- ...

**Risks**:
- ...

## References
- ...
```

---

## 4. Example ADR-001 — Database Technology Selection

### ADR-001: Relational Database Technology Selection

**Date**: 2026-01-20
**Status**: Accepted
**Author**: Jordan Kim (Lead Engineer)
**Reviewers**: Marcus Webb (VP Technology), Chris Monroe (InfoSec)

#### Context

The e-commerce platform (PRJ-2026-008) requires a relational database for product catalogue, orders, customer accounts, and inventory. The existing Magento system uses MySQL 5.7 (also EOL). We need to select a database technology for the new Shopify-adjacent services layer that will:
- Store order history imported from Magento
- Power the custom recommendation engine
- Handle analytics queries alongside transactional workloads
- Support JSONB for flexible product attribute storage
- Be managed (cloud-hosted) to reduce operational overhead

Key forces:
- Team has strong MySQL experience; PostgreSQL experience is limited but growing
- Product catalogue has highly variable attribute schemas (60% of SKUs have custom attributes stored as JSON)
- Compliance: PCI-DSS requires encryption at rest and audit logging
- Budget: managed service cost must be < $500/month for expected data volume (~50GB)

#### Decision

**We will use Amazon RDS for PostgreSQL 16** as the primary relational database for the e-commerce services layer.

#### Rationale

PostgreSQL scored highest across the weighted criteria matrix (see below). The deciding factors were:
1. **Native JSONB support**: 40% of queries involve flexible product attributes. PostgreSQL JSONB with GIN indexes outperforms MySQL's JSON functions by 3–5x in our PoC tests.
2. **ACID compliance + JSON**: MySQL 8.0 supports JSON but lacks true JSONB indexing. PostgreSQL delivers full ACID compliance with performant JSON operations.
3. **RDS managed service**: Both PostgreSQL and MySQL are available on RDS at comparable cost. Aurora was evaluated but exceeds budget for expected data volume.
4. **Long-term viability**: PostgreSQL is actively developed, has no single corporate owner, and has broad community/tooling support.

#### Alternatives Considered

| Option | Weighted Score | Pros | Cons |
|--------|---------------|------|------|
| **PostgreSQL 16 (RDS)** | **87/100** | JSONB, ACID, window functions, RLS, strong typing | Team unfamiliar; smaller talent pool vs MySQL |
| MySQL 8.0 (RDS) | 71/100 | Team familiarity, proven with Magento, wide talent pool | JSON support inferior, no JSONB indexes, less advanced features |
| Amazon Aurora MySQL | 68/100 | Auto-scaling, high availability, MySQL compatible | $1,200/month minimum cost (over budget), MySQL limitations still apply |
| MongoDB Atlas | 54/100 | Flexible schema, horizontal scaling | Not relational — complex transactions, PCI compliance harder, mixed signals on ACID |
| Amazon DynamoDB | 49/100 | Serverless, auto-scaling | No joins — reports require ETL; steep learning curve; SQL skills wasted |

#### Scoring Matrix

| Criterion | Weight | PostgreSQL | MySQL 8 | Aurora MySQL | MongoDB | DynamoDB |
|-----------|--------|-----------|---------|-------------|---------|----------|
| JSON/flexible schema support | 25% | 9 | 6 | 6 | 10 | 8 |
| ACID compliance | 20% | 10 | 9 | 9 | 7 | 5 |
| Team expertise | 15% | 5 | 9 | 8 | 4 | 3 |
| Managed service cost (<$500/mo) | 15% | 9 | 9 | 4 | 8 | 8 |
| PCI-DSS compliance features | 10% | 9 | 8 | 8 | 7 | 8 |
| Query performance (mixed workload) | 10% | 9 | 7 | 8 | 6 | 5 |
| Community & ecosystem | 5% | 10 | 9 | 7 | 8 | 6 |
| **Weighted Total** | 100% | **87** | **71** | **68** | **54** | **49** |

#### Consequences

**Positive**:
- JSONB indexes will make product attribute queries 3–5x faster than the current MySQL implementation
- Row Level Security (RLS) simplifies multi-tenant data isolation
- Advanced window functions reduce application-layer complexity in analytics
- PostgreSQL 16 logical replication enables zero-downtime migrations in the future

**Negative / Trade-offs**:
- Team will need PostgreSQL training (~8 hours per developer)
- Some Magento export tooling is MySQL-specific — migration scripts require adaptation
- ORM configuration changes needed (Sequelize dialect switch)

**Risks**:
- Medium: Team unfamiliarity could slow initial development — mitigate with pair programming and internal training sprint
- Low: psycopg2 vs mysql-connector differences in Python analytics code — 2 days rework estimated

#### References
- PostgreSQL 16 JSONB performance: https://www.postgresql.org/docs/16/datatype-json.html
- AWS RDS PostgreSQL pricing: https://aws.amazon.com/rds/postgresql/pricing/
- PCI-DSS on RDS: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html
- PoC results: `docs/poc/db-jsonb-benchmark.md`

---

## 5. System Design Review Checklist

Complete before signoff and advancement to Phase 3.

### Functional Completeness
- [ ] All user stories from the intake have a corresponding technical design
- [ ] API contracts defined (OpenAPI 3.0 specs or equivalent)
- [ ] Data models reviewed and approved by DBA or data architect
- [ ] Integration points identified with source/target system owners confirmed

### Non-Functional Requirements
- [ ] Performance targets defined (latency, throughput, concurrency)
- [ ] Scalability approach documented (horizontal/vertical, autoscaling triggers)
- [ ] Availability target set (e.g. 99.9% = 8.7h downtime/year)
- [ ] Disaster recovery RTO/RPO defined and achievable with chosen technology
- [ ] Data retention policy documented and compliant with regulations

### Security
- [ ] Threat model completed (STRIDE or equivalent)
- [ ] Authentication and authorisation design reviewed by security team
- [ ] Secrets management approach defined (no secrets in code or config files)
- [ ] Data encryption: in-transit (TLS 1.2+) and at-rest specified
- [ ] Network segmentation/security groups/firewall rules designed
- [ ] OWASP Top 10 mitigations identified for all user-facing components

### Operability
- [ ] Deployment architecture matches environment parity (dev/staging/prod)
- [ ] Logging strategy defined (log levels, structured format, retention)
- [ ] Metrics and alerting approach agreed with operations team
- [ ] Runbook outline exists for go-live and rollback

### Architecture Board Sign-off
- [ ] ADRs written for all significant decisions (≥ 1 ADR per project)
- [ ] Architecture review meeting held with attendees recorded
- [ ] No outstanding blocker items from security review
- [ ] Final design baseline stored in version control

---

## 6. Non-Functional Requirements Template

### NFR Template

| ID | Category | Requirement | Target | Measurement Method | Priority |
|----|----------|-------------|--------|--------------------|----------|
| NFR-01 | Performance | API p50 response time | < 100ms | APM tool (p50 over 5-min window) | Must Have |
| NFR-02 | Performance | API p99 response time | < 500ms | APM tool (p99 over 5-min window) | Must Have |
| NFR-03 | Performance | Page load (mobile, 4G) | < 2.0s LCP | Lighthouse, WebPageTest | Must Have |
| NFR-04 | Scalability | Concurrent users (peak) | 5,000 | Load test (k6 or Locust) | Must Have |
| NFR-05 | Availability | Uptime SLA | 99.9% | Uptime monitor (1-min checks) | Must Have |
| NFR-06 | Durability | Data loss (RPO) | < 1 hour | RDS automated backups (hourly) | Must Have |
| NFR-07 | Recovery | Recovery time (RTO) | < 4 hours | DR test results | Should Have |
| NFR-08 | Security | Vulnerabilities (Critical) | 0 in prod | DAST + dependency scan in CI | Must Have |
| NFR-09 | Compliance | PCI-DSS SAQ level | SAQ A-EP | Annual QSA assessment | Must Have |
| NFR-10 | Maintainability | Deployment frequency | Weekly | CI/CD pipeline metrics | Should Have |
| NFR-11 | Observability | Time to detect (MTTD) | < 5 min | Alert latency monitoring | Should Have |
| NFR-12 | Accessibility | WCAG standard | 2.1 AA | axe-core automated + manual | Should Have |

### E-commerce Upgrade — NFRs (Excerpt)

| ID | Category | Requirement | Target | Method |
|----|----------|-------------|--------|--------|
| NFR-01 | Performance | Mobile page load (LCP) | < 2.0s | Lighthouse CI in pipeline |
| NFR-02 | Performance | Checkout API p99 | < 300ms | Datadog APM |
| NFR-03 | Scalability | Peak concurrent sessions | 3,000 | k6 load test pre-launch |
| NFR-04 | Availability | Storefront uptime | 99.95% | Pingdom (1-min checks) |
| NFR-05 | Compliance | PCI-DSS | SAQ A-EP | Annual QSA |
| NFR-06 | Security | Critical CVEs in prod | 0 | Snyk + Trivy in CI |

---

## 7. Technology Selection Matrix Template

Use this matrix when comparing multiple technology options.

| Criterion | Weight | Option A | Option B | Option C |
|-----------|--------|----------|----------|----------|
| Functional fit | 25% | /10 | /10 | /10 |
| Operational maturity | 20% | /10 | /10 | /10 |
| Security posture | 20% | /10 | /10 | /10 |
| Total cost of ownership | 15% | /10 | /10 | /10 |
| Team expertise | 10% | /10 | /10 | /10 |
| Vendor/community support | 10% | /10 | /10 | /10 |
| **Weighted Score** | 100% | — | — | — |

**Example: Front-end Framework Selection (PRJ-2026-008)**

| Criterion | Weight | Next.js 14 | Nuxt 3 | Remix |
|-----------|--------|-----------|--------|-------|
| Functional fit (SSR, SSG, ISR) | 25% | 10 | 9 | 8 |
| Operational maturity | 20% | 9 | 7 | 6 |
| Shopify Hydrogen compatibility | 20% | 10 | 5 | 7 |
| Team expertise (React vs Vue) | 15% | 9 | 4 | 8 |
| Community & ecosystem | 10% | 10 | 8 | 7 |
| Total cost of ownership | 10% | 9 | 9 | 8 |
| **Weighted Score** | 100% | **9.6** | **6.8** | **7.3** |

**Decision: Next.js 14** — highest score, team already proficient in React, best Shopify integration story.

---

## 8. Design Phase Outputs

| Output | Owner | Stored In |
|--------|-------|-----------|
| System architecture diagram | Lead Engineer | `docs/architecture/` |
| ADR-001..N | Lead Engineer | `docs/adr/` |
| NFR register | PM + Architect | `docs/requirements/nfr.md` |
| Technology selection matrices | Lead Engineer | `docs/adr/` |
| Threat model | Security Team | `docs/security/threat-model.md` |
| API specification (OpenAPI) | Lead Engineer | `api/openapi.yaml` |
| Design Review minutes | PM | `docs/reviews/` |

**Next Phase**: [03-development.md](03-development.md)

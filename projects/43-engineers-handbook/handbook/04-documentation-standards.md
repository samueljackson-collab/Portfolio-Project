# Documentation Standards

**Version:** 2.1 | **Owner:** Engineering | **Last Updated:** 2026-01-10

---

## 1. README Requirements

Every repository must have a README.md with the following sections in order:

```markdown
# Project Name
[One sentence: what this does and who uses it]

## Prerequisites
[What you need before running]

## Quick Start
[3–5 commands to get it running]

## Architecture
[Diagram + brief explanation]

## Configuration
[Environment variables / config reference]

## Development
[How to run tests, lint, build locally]

## Deployment
[How to deploy; link to full runbook]

## Contributing
[Branch strategy, PR process, code owners]
```

**Anti-patterns** (README will be rejected at review):
- "This project does X things" with no quick start
- Only "See the wiki" with no local content
- Setup instructions that require tribal knowledge
- No information about how to run tests

---

## 2. Architecture Decision Records (ADRs)

Use Nygard format. ADRs are stored in `docs/decisions/ADR-NNN-title.md`.

```markdown
# ADR-NNN: [Title]

Status: [Proposed / Accepted / Deprecated / Superseded by ADR-NNN]
Date: YYYY-MM-DD
Deciders: [names / team]

## Context
[1–3 paragraphs: what problem are we solving? what constraints apply?]

## Options Considered
[List each option with pros and cons]

## Decision
[What was decided and why — be specific]

## Consequences
[What becomes easier, what becomes harder, what we accept]
```

**When to write an ADR:**
- Technology/framework selection
- Significant architectural changes
- Decisions with non-obvious trade-offs
- Anything that will be questioned in code review

---

## 3. Runbooks

Runbooks live in `docs/runbooks/`. Use this template:

```markdown
# Runbook: [Process Name]

Owner: [team]
Review cycle: [quarterly/annual]
Last tested: YYYY-MM-DD

## Purpose
[One sentence]

## Prerequisites
[What you need: access, tools, credentials location]

## Steps
1. [Action]
   Expected output: [what you should see]
2. [Action]
   Expected output: [what you should see]

## Verification
[How to confirm it worked]

## Rollback
[How to undo, if applicable]

## Escalation
[Who to contact if this fails]
```

---

## 4. Inline Code Documentation

### When Comments Are Required

- Complex algorithms or non-obvious logic
- Business rules embedded in code (explain the "why", not the "what")
- Performance-sensitive code with known trade-offs
- Security-sensitive sections

### When Comments Are NOT Required

- Self-documenting code with clear variable/function names
- Standard library usage
- Obvious control flow

```python
# GOOD comment — explains WHY, not WHAT
# We use a 5-minute buffer to account for clock skew between
# client and server in distributed environments (see ADR-007)
expiry = datetime.utcnow() + timedelta(minutes=15 - 5)

# BAD comment — describes what the code already says
# Add 15 minutes to current time
expiry = datetime.utcnow() + timedelta(minutes=15)
```

---

## 5. API Documentation

All REST APIs must have OpenAPI 3.0 documentation auto-generated from code annotations.

```python
# FastAPI example — documentation auto-generated
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Order Service", version="2.1.0")

class OrderRequest(BaseModel):
    product_id: int
    quantity: int
    """Quantity must be between 1 and 100."""

@app.post("/orders", summary="Create a new order", response_model=OrderResponse)
async def create_order(order: OrderRequest) -> OrderResponse:
    """
    Create a new order for the authenticated customer.

    - Validates product availability
    - Deducts from inventory atomically
    - Returns order ID and estimated delivery date
    """
```

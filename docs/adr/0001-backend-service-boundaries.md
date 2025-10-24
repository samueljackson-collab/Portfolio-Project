# ADR 0001: Backend Service Boundaries

- **Status:** Accepted
- **Date:** 2025-10-11

## Context
The portfolio requires a backend capable of user authentication, content management, and reporting metrics. We evaluated splitting these functions into microservices versus a single monolith.

## Decision
Adopt a modular monolith built with FastAPI. The service exposes routers for authentication, content, and health checks while sharing a unified database.

## Consequences
- ✅ Simpler deployment story and fewer network hops.
- ✅ Easier to reason about transactions during content creation.
- ⚠️ Requires discipline to keep modules decoupled; enforce via package boundaries and tests.


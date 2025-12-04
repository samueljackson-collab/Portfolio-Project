# ADR-001: Choose FastAPI for POC
- **Status:** Accepted
- **Context:** Need fast iteration, OpenAPI support, async IO.
- **Decision:** Use FastAPI + uvicorn instead of Flask.
- **Consequences:**
  - Built-in docs and validation reduce boilerplate.
  - Requires async-friendly patterns and type hints.

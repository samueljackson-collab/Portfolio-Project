# Architecture Overview

The toolkit is organized as:
- `scripts/`: automation helpers (backup, monitoring, maintenance, security, migration).
- `sql/`: reusable report queries and checks.
- `docs/`: runbooks and operator guidance.

Execution relies on standard PostgreSQL client tooling and environment variables defined in `.env`.

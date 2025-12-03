# ADR-001: Use In-Memory Queue for POC

## Status
Accepted

## Context
The POC needs lightweight async processing without external dependencies during demos.

## Decision
- Use an in-memory queue backed by Python `asyncio.Queue` with optional Redis adapter later.
- Worker runs as a separate process/Pod consuming from the queue.

## Consequences
- Not durable across restarts; acceptable for POC but must upgrade for production.
- Simplifies local development and CI.

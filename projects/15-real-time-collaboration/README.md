# Project 15: Real-time Collaborative Platform

## Overview
Operational transform (OT) collaboration server enabling low-latency document editing with CRDT backup for offline resilience.

## Phase 2 Architecture Diagram

Diagram: render locally from [Mermaid source](assets/diagrams/architecture.mmd) using `python tools/generate_phase1_diagrams.py` (PNG output is .gitignored).

- **Context**: Clients connect through a WebSocket gateway and JWT auth layer before rate-limited operations hit the OT engine
  that coordinates presence, ordering, and persistence.
- **Decision**: Separate edge, collaboration core, and persistence boundaries so transient presence data never crosses the
  durable CRDT snapshot layer, and recovery paths stay isolated from live traffic.
- **Consequences**: Message buses and CRDT snapshots can be tuned for durability without slowing foreground edits, while
  WebSocket gateways keep reconciliation feedback loops close to the client. Keep the [Mermaid source](assets/diagrams/architec
ture.mmd) synchronized with the exported PNG.

## Features
- WebSocket gateway with JWT auth and presence tracking.
- Operational transform engine with per-document queues.
- CRDT-based reconciliation when clients reconnect.

## Run
```bash
pip install -r requirements.txt
python src/collaboration_server.py
```

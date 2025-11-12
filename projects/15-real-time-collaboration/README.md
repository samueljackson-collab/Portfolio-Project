# Project 15: Real-time Collaborative Platform

## Overview
Operational transform (OT) collaboration server enabling low-latency document editing with CRDT backup for offline resilience.

## Features
- WebSocket gateway with JWT auth and presence tracking.
- Operational transform engine with per-document queues.
- CRDT-based reconciliation when clients reconnect.

## Run
```bash
pip install -r requirements.txt
python src/collaboration_server.py
```

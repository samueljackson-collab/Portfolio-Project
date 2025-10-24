# Electron Desktop App

## Overview
Cross-platform desktop application providing offline-first access to task data, analytics, and admin tooling. Built with Electron, React, and secure IPC patterns.

## Features
- Synchronizes with FastAPI backend and Kafka topics via WebSockets.
- Local SQLite cache for offline usage with conflict resolution strategies.
- Auto-update support using Electron Builder + GitHub Releases.
- Integrates OS-level notifications, tray icon, and deep links.

## Development Workflow
1. Install dependencies: `npm install`.
2. Run in development: `npm run dev` (spawns Electron + Vite).
3. Lint/test: `npm run lint`, `npm test`.
4. Package builds: `npm run build` generates installers for macOS, Windows, Linux.

## Security Practices
- Context isolation, disabled `nodeIntegration`, sanitized IPC channels.
- Code signing (Apple Notarization, Windows SignTool) configured in `electron-builder.yml`.
- Auto-update endpoints secured with signed manifests.

## Operations
- Telemetry collected via Sentry/Amplitude with opt-in analytics.
- Release checklist ensures QA validation on all supported OS variants.
- Runbook details support procedures, log file collection, and rollback.


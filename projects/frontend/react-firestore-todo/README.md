# React To-Do List App with Firestore

## Overview
A single-page application that demonstrates real-time collaboration patterns using React 18, Firebase Authentication, and Cloud Firestore. It showcases responsive UX, optimistic updates, and offline-first capabilities.

## Architecture
- **UI Layer:** React + TypeScript with React Query and Tailwind CSS.
- **State Sync:** Firestore listeners stream task changes; client maintains offline cache via IndexedDB.
- **Authentication:** Firebase Auth (email/password + OAuth providers) with JWT tokens validated by backend APIs.
- **API Integration:** Communicates with `backend/fastapi-backend-api` for business rules, audit logging, and integrations.

## Key Features
- Real-time list updates, drag-and-drop prioritization, and due-date reminders.
- Role-based permissions (owner, contributor, viewer) enforced at Firestore rules layer.
- Accessibility-first design (WCAG 2.1 AA) with full keyboard navigation and screen reader support.

## Getting Started
1. Install dependencies: `npm install`.
2. Copy `env/.example` to `.env.local` and supply Firebase project credentials.
3. Run locally: `npm run dev` (Vite dev server) and connect to emulator suite with `npm run emulators` if desired.
4. Execute unit tests: `npm test`.
5. Build for production: `npm run build`; deploy static assets via `terraform-s3-static-site` module.

## Quality Gates
- ESLint + Prettier enforced via Git hooks (`lint-staged`).
- Jest + Testing Library for component/unit tests; Cypress suite stored under `tests/e2e`.
- Lighthouse CI pipeline ensures performance/accessibility budgets.

## Operations
- Observability via OpenTelemetry web instrumentation emitting to collector.
- Release artifacts uploaded to S3 and distributed by CloudFront with invalidation automation.
- Feature flags integrated with LaunchDarkly for progressive delivery.

## Documentation & Runbooks
- ADRs in `docs/adr/` capture major UI/UX decisions.
- Runbook in `ops/runbook.md` covers deployment, rollback, and incident response for frontend outages.


# Frontend Guide

The frontend is a React + Vite application written in TypeScript.

## Development
1. Install dependencies: `npm install --prefix projects/frontend`.
2. Start the development server: `npm run dev --prefix projects/frontend`.
3. Access the UI at `http://localhost:5173`.

## Testing
- Unit tests: `npm test --prefix projects/frontend -- --run` (Vitest + React Testing Library).
- E2E tests: `npm run e2e --prefix projects/frontend` (Playwright).
- Linting: `npm run lint --prefix projects/frontend` (ESLint + Prettier).

## Deployment
Production builds are generated with `npm run build --prefix projects/frontend`. The Dockerfile within `projects/frontend/` builds and serves the optimized bundle using `node:20-alpine` and `vite preview`.

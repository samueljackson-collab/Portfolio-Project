# Frontend Runbook

## Service Summary
- **Component:** React + Vite SPA
- **Entry Point:** `npm run dev` (local) / `npm run preview` (production container)
- **Health Check:** `GET /health` served by backend (frontend proxies through for uptime checks).

## On-Call Checklist
1. Confirm CDN or static hosting returns HTTP 200 for `/`.
2. Validate API connectivity by hitting `/api/projects` from browser console.
3. Run `npm run lint` and `npm test -- --run` before deploying hotfixes.

## Common Issues
| Symptom | Action |
|---------|--------|
| Build failures | Run `npm run build --prefix projects/frontend` and inspect TypeScript diagnostics. |
| Styling regressions | Execute `npm run format` and review component snapshots. |
| API errors | Ensure backend URL in `.env` is correct and reachable. |

## Deployment Steps
1. Update version in `projects/frontend/package.json` if necessary.
2. Build artifacts: `npm run build --prefix projects/frontend`.
3. Deploy via container (`projects/frontend/Dockerfile`) or static hosting pipeline.

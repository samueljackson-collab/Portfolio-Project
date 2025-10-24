# Frontend Application

React single-page application built with Vite and Tailwind CSS. It consumes the backend API to display content and manage authentication.

## Commands

```bash
npm install
npm run dev
npm run build
npm run test
```

Set the API endpoint in `.env` or environment variables:

```
VITE_API_URL=http://localhost:8000
```

## Structure
- `src/api` – Axios client configuration.
- `src/components` – Reusable UI components.
- `src/pages` – Route-level components.
- `src/context` – React context for authentication state.


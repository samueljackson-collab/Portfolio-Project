# Frontend Service

React + Vite application that consumes the backend API. The app provides authentication, content management, and dashboard views styled with Tailwind CSS.

## Commands
- `npm install` – Install dependencies.
- `npm run dev` – Start development server.
- `npm run build` – Build production bundle.
- `npm run preview` – Preview production build locally.
- `npm run lint` – Run ESLint with project configuration.

## Environment Variables
Copy `.env.example` to `.env` and configure:
- `VITE_API_BASE_URL` – Base URL for backend API (e.g., `http://localhost:8000`).

## Production Build
The Dockerfile creates a multi-stage build that outputs static assets served by Nginx.

# Portfolio Frontend

A modern, responsive React application built with TypeScript, Vite, and Tailwind CSS.

## Features

- ⚛️ **React 18.2** - Modern React with hooks and functional components
- 🔷 **TypeScript** - Full type safety with strict mode
- ⚡ **Vite** - Lightning-fast HMR and optimized builds
- 🎨 **Tailwind CSS** - Utility-first CSS framework
- 🛣️ **React Router v6** - Client-side routing
- 🔐 **Authentication** - JWT-based auth with Context API
- 📡 **Axios** - HTTP client with interceptors
- 🐳 **Docker** - Multi-stage production builds with nginx
- ✅ **ESLint & Prettier** - Code quality and formatting

## Quick Start

### Prerequisites

- Node.js 18+ and npm 9+
- Backend API running on http://localhost:8000

### Local Development

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

   The app will be available at http://localhost:5173

4. **Build for production**
   ```bash
   npm run build
   ```

5. **Preview production build**
   ```bash
   npm run preview
   ```

### Docker Deployment

1. **Build Docker image**
   ```bash
   docker build -t portfolio-frontend .
   ```

2. **Run container**
   ```bash
   docker run -p 80:80 portfolio-frontend
   ```

   The app will be available at http://localhost

## Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── api/            # API client and services
│   │   ├── client.ts   # Axios instance with interceptors
│   │   ├── services.ts # API service functions
│   │   ├── types.ts    # TypeScript type definitions
│   │   └── index.ts
│   ├── components/     # Reusable components
│   │   ├── Navbar.tsx
│   │   ├── ProtectedRoute.tsx
│   │   ├── ContentCard.tsx
│   │   └── index.ts
│   ├── context/        # React Context providers
│   │   ├── AuthContext.tsx
│   │   └── index.ts
│   ├── pages/          # Route pages
│   │   ├── Home.tsx
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Dashboard.tsx
│   │   └── index.ts
│   ├── styles/         # Global styles
│   │   └── index.css
│   ├── App.tsx         # Main app component with routing
│   ├── main.tsx        # Application entry point
│   └── vite-env.d.ts   # Vite type definitions
├── Dockerfile          # Multi-stage Docker build
├── nginx.conf          # Production nginx configuration
├── vite.config.ts      # Vite configuration
├── tsconfig.json       # TypeScript configuration
├── tailwind.config.js  # Tailwind CSS configuration
└── package.json        # Dependencies and scripts
```

## Available Scripts

### Development

- `npm run dev` - Start development server with HMR
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally

### Code Quality

- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier
- `npm run type-check` - Run TypeScript type checking

### Testing

- `npm run test` - Run tests with Vitest
- `npm run test:ui` - Run tests with UI
- `npm run test:coverage` - Generate coverage report

## API Integration

The frontend communicates with the backend API through:

- **Base URL**: Configured via `VITE_API_URL` environment variable
- **Proxy**: Dev server proxies `/api/*` to backend (see `vite.config.ts`)
- **Authentication**: JWT tokens stored in localStorage
- **Interceptors**: Automatic token injection and error handling

### API Services

```typescript
import { authService, contentService } from './api'

// Authentication
await authService.login({ username, password })
await authService.register({ email, password })
const user = await authService.getCurrentUser()

// Content Management
const contents = await contentService.getAll()
const content = await contentService.getById(id)
await contentService.create(data)
await contentService.update(id, data)
await contentService.delete(id)
```

## Authentication Flow

1. **Login/Register**: User submits credentials
2. **Token Storage**: JWT token stored in localStorage
3. **Auto-Injection**: Axios interceptor adds token to all requests
4. **Route Protection**: ProtectedRoute component guards authenticated routes
5. **Auto-Logout**: 401 responses clear token and redirect to login

## Routing

- `/` - Home page (public)
- `/login` - Login page (public)
- `/register` - Registration page (public)
- `/dashboard` - User dashboard (protected)

## Styling

### Tailwind CSS

The app uses Tailwind CSS with custom configuration:

```javascript
// tailwind.config.js
theme: {
  extend: {
    colors: {
      primary: { /* Custom color palette */ }
    }
  }
}
```

### Custom CSS Classes

Defined in `src/styles/index.css`:

- `.btn-primary` - Primary button styles
- `.btn-secondary` - Secondary button styles
- `.input-field` - Form input styles
- `.card` - Card container styles

## Environment Variables

Create `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

## Production Deployment

### Nginx Configuration

The production build uses nginx with:

- Gzip compression
- Security headers
- API proxy to backend
- React Router support (serve index.html for all routes)
- Static asset caching
- Health check endpoint

### Docker Multi-Stage Build

1. **Build stage**: Install deps and build app
2. **Production stage**: Copy build to nginx alpine

Benefits:
- Small image size (~25MB)
- Fast startup time
- Production-optimized nginx config

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### Development server won't start

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### API calls fail

```bash
# Check backend is running
curl http://localhost:8000/health

# Verify VITE_API_URL in .env
cat .env
```

### Build errors

```bash
# Run type checking
npm run type-check

# Check for linting errors
npm run lint
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run type checking: `npm run type-check`
4. Run linting: `npm run lint`
5. Format code: `npm run format`
6. Test your changes
7. Submit pull request

## License

MIT License - See LICENSE file for details

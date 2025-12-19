# AstraDup Frontend

Intelligent Video Duplicate Detection & Management Interface

## Features

- **Duplicate Detection**: Compare two videos using multi-modal analysis
- **File Renaming**: Batch rename video files using enriched metadata
- **Video Details**: View comprehensive information about videos

## Getting Started

### Prerequisites

- Node.js >= 18.0.0
- npm >= 9.0.0

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Build

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   ├── pages/           # Page components
│   ├── services/        # API and service layer
│   ├── types/           # TypeScript type definitions
│   ├── App.tsx          # Main application component
│   ├── main.tsx         # Application entry point
│   └── index.css        # Global styles
├── public/              # Static assets
└── index.html          # HTML template
```

## Technologies

- React 18
- TypeScript
- Vite
- React Router v6
- Tailwind CSS

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

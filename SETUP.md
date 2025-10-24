# Portfolio Project Setup Guide

This repository contains a full-stack portfolio application with a FastAPI backend and React + TypeScript frontend.

## Architecture

- **Backend**: FastAPI with async PostgreSQL, JWT authentication, and content management
- **Frontend**: React + TypeScript + Vite with TailwindCSS
- **Database**: PostgreSQL 15
- **UI Components**: EnterpriseWiki - Interactive learning paths for technical roles

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker and Docker Compose (for database)
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/samueljackson-collab/Portfolio-Project.git
cd Portfolio-Project
```

### 2. Start the Database

```bash
docker-compose up -d
```

This starts a PostgreSQL database on port 5432.

### 3. Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run Backend

```bash
# From the backend directory with venv activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend API will be available at http://localhost:8000
API documentation at http://localhost:8000/docs

### 5. Setup Frontend

```bash
# In a new terminal, from the project root
npm install
```

### 6. Run Frontend

```bash
npm run dev
```

Frontend will be available at http://localhost:5173

## Project Structure

```
Portfolio-Project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Database setup
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── auth.py              # Authentication utilities
│   │   ├── dependencies.py      # FastAPI dependencies
│   │   └── routers/
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── content.py       # Content CRUD endpoints
│   │       └── health.py        # Health check endpoint
│   └── requirements.txt
├── src/
│   ├── components/
│   │   └── EnterpriseWiki.tsx  # Main Wiki component
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── docker-compose.yml
└── README.md
```

## API Endpoints

### Health
- `GET /health` - Health check

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login (returns JWT token)

### Content Management
- `POST /api/content/` - Create content (requires auth)
- `GET /api/content/` - List user's content (requires auth)
- `GET /api/content/{id}` - Get specific content (requires auth)
- `PUT /api/content/{id}` - Update content (requires auth)
- `DELETE /api/content/{id}` - Delete content (requires auth)

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://portfolio:portfolio_dev_pass@localhost:5432/portfolio
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENVIRONMENT=development
```

## Testing

### Backend
```bash
cd backend
python -m pytest
```

### Frontend
```bash
npm test
```

## Building for Production

### Backend
```bash
cd backend
pip install -r requirements.txt
# Deploy with gunicorn or uvicorn
```

### Frontend
```bash
npm run build
# Output will be in dist/ directory
```

## Features

### EnterpriseWiki Component
Interactive learning platform featuring:
- **System Development Engineer** (8-week program)
- **DevOps Engineer** (6-week program)
- **QA Engineer III** (6-week program)
- **Solutions Architect** (8-week program)

Each role includes:
- Detailed week-by-week curriculum
- Topics covered
- Deliverables
- Progress tracking
- Key responsibilities and core skills

## Security Notes

- Change default passwords and secrets in production
- Use HTTPS in production
- Keep dependencies updated
- Review and audit code regularly
- Use environment-specific configurations

## Development Workflow

1. Create a feature branch
2. Make changes
3. Test locally
4. Commit with meaningful messages
5. Push and create pull request
6. Code review
7. Merge to main

## Troubleshooting

### Database Connection Issues
- Ensure Docker container is running: `docker-compose ps`
- Check database logs: `docker-compose logs postgres`
- Verify connection settings in `.env`

### Frontend Build Errors
- Clear node_modules: `rm -rf node_modules package-lock.json && npm install`
- Check Node.js version: `node --version` (should be 18+)

### Backend Errors
- Verify Python version: `python --version` (should be 3.10+)
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
- Check database migrations are applied

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is private and proprietary.

## Support

For issues and questions, please create an issue in the GitHub repository.

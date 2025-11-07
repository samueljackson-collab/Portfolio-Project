# Enterprise Portfolio Wiki

An interactive learning path tracker for technical roles including System Development Engineer, DevOps Engineer, QA Engineer III, and Solutions Architect.

## Overview

This web application provides comprehensive, week-by-week learning paths for different technical roles. Each role includes:

- **Key responsibilities** and **core skills** overview
- **Weekly learning modules** with specific topics and deliverables
- **Progress tracking** to monitor your learning journey
- **Interactive navigation** to explore different roles and weeks

## Features

- **4 Technical Roles**: SDE, DevOps, QA, Solutions Architect
- **28 Learning Weeks**: Comprehensive curriculum across all roles
- **200+ Topics**: Detailed coverage of essential technologies and practices
- **100+ Deliverables**: Clear outcomes for each week
- **Progress Tracking**: Visual progress indicators
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Theme**: Modern, eye-friendly interface

## Technology Stack

- **React 18** - Modern React with hooks
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icon library

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn

### Installation

1. Clone the repository
2. Navigate to the enterprise-wiki-app directory:
   ```bash
   cd enterprise-wiki-app
   ```

3. Install dependencies:
   ```bash
   npm install
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

5. Open your browser to `http://localhost:3000`

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
enterprise-wiki-app/
├── src/
│   ├── components/
│   │   └── EnterpriseWiki.jsx    # Main component
│   ├── App.jsx                    # App wrapper
│   ├── main.jsx                   # Entry point
│   └── index.css                  # Global styles
├── public/                        # Static assets
├── index.html                     # HTML template
├── vite.config.js                 # Vite configuration
├── tailwind.config.js             # Tailwind configuration
├── postcss.config.js              # PostCSS configuration
├── .eslintrc.cjs                  # ESLint configuration
└── package.json                   # Dependencies
```

## Learning Paths

### System Development Engineer (8 weeks)
Infrastructure, automation, and system reliability
- Week 1: Infrastructure Foundations
- Week 2: Compute & Load Balancing
- Week 3: Database & Storage
- Week 4: Container Orchestration
- Week 5: Monitoring & Observability
- Week 6: Event-Driven Architecture
- Week 7: Disaster Recovery
- Week 8: Security Hardening

### DevOps Engineer (6 weeks)
CI/CD, GitOps, and deployment automation
- Week 1: CI/CD Pipeline Setup
- Week 2: GitOps Implementation
- Week 3: Configuration Management
- Week 4: Container Registry
- Week 5: Deployment Strategies
- Week 6: Pipeline Optimization

### QA Engineer III (6 weeks)
Testing strategy, automation, and quality assurance
- Week 1: Test Framework Setup
- Week 2: API Testing
- Week 3: E2E Testing
- Week 4: Performance Testing
- Week 5: Security Testing
- Week 6: CI/CD Integration

### Solutions Architect (8 weeks)
System design, architecture patterns, and trade-offs
- Week 1: Architecture Fundamentals
- Week 2: Microservices Design
- Week 3: Event-Driven Architecture
- Week 4: Scalability Patterns
- Week 5: Security Architecture
- Week 6: Resilience Patterns
- Week 7: Multi-Region Architecture
- Week 8: Cost Optimization

## Deployment

### Build for Production

```bash
npm run build
```

The build output will be in the `dist/` directory.

### Deploy to Static Hosting

The application can be deployed to any static hosting service:

- **GitHub Pages**: Use GitHub Actions to deploy
- **Netlify**: Connect your repository and deploy automatically
- **Vercel**: Import your project and deploy
- **AWS S3 + CloudFront**: Deploy to S3 bucket with CloudFront CDN

### Environment Variables

No environment variables are required for this application.

## Customization

### Adding a New Role

1. Add the role to the `roles` object in `EnterpriseWiki.jsx`
2. Add the role content to the `roleContent` object
3. Define weeks with topics and deliverables

### Modifying Existing Content

Edit the `roleContent` object in `EnterpriseWiki.jsx` to update:
- Responsibilities
- Skills
- Week topics
- Deliverables

### Styling

- Global styles: `src/index.css`
- Tailwind configuration: `tailwind.config.js`
- Component styles: Inline Tailwind classes in `EnterpriseWiki.jsx`

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Opera 76+

## Contributing

This is a portfolio project, but suggestions and feedback are welcome!

## License

MIT License - See LICENSE file for details

## Author

**Sam Jackson**
- GitHub: [@samueljackson-collab](https://github.com/samueljackson-collab)
- LinkedIn: [sams-jackson](https://www.linkedin.com/in/sams-jackson)

## Acknowledgments

- Icons by [Lucide](https://lucide.dev/)
- Built with [React](https://react.dev/)
- Styled with [Tailwind CSS](https://tailwindcss.com/)
- Powered by [Vite](https://vitejs.dev/)

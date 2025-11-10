# Enterprise Portfolio Wiki

An interactive web application providing comprehensive learning paths for various technical roles in enterprise environments.

## Overview

This React-based web application serves as an educational wiki that guides users through structured learning paths for four key technical roles:

- **System Development Engineer (SDE)** - 8-week infrastructure and automation program
- **DevOps Engineer** - 6-week CI/CD and GitOps curriculum
- **QA Engineer III** - 6-week testing strategy and automation track
- **Solutions Architect** - 8-week system design and architecture course

## Features

### Interactive Role Selection
- Choose from four distinct technical roles
- Each role includes custom learning paths tailored to the position
- Visual progress tracking throughout the curriculum

### Weekly Learning Modules
Each role is broken down into weekly modules that include:
- **Topics Covered** - Key concepts and technologies for the week
- **Deliverables** - Concrete outputs expected at the end of the week
- **Progress Tracking** - Visual indicators showing completion percentage

### Role-Specific Content

#### System Development Engineer (8 weeks)
Focus areas:
- Infrastructure foundations (VPC, networking, security)
- Compute and load balancing (EC2, ALB, auto-scaling)
- Database and storage (RDS, ElastiCache, S3)
- Container orchestration (EKS, Kubernetes)
- Monitoring and observability (Prometheus, Grafana)
- Event-driven architecture (SQS, SNS, EventBridge)
- Disaster recovery and backup automation
- Security hardening and compliance

#### DevOps Engineer (6 weeks)
Focus areas:
- CI/CD pipeline setup (GitHub Actions)
- GitOps implementation (ArgoCD)
- Configuration management (Ansible)
- Container registry and security
- Deployment strategies (blue-green, canary)
- Pipeline optimization and cost management

#### QA Engineer III (6 weeks)
Focus areas:
- Test framework setup (Jest, Cypress)
- API testing (REST, GraphQL, contract testing)
- E2E testing (cross-browser, visual regression)
- Performance testing (load, stress, spike testing)
- Security testing (OWASP Top 10, pen testing)
- CI/CD integration and quality gates

#### Solutions Architect (8 weeks)
Focus areas:
- Architecture fundamentals and patterns
- Microservices design
- Event-driven architecture (CQRS, event sourcing)
- Scalability patterns (caching, sharding, CDN)
- Security architecture (zero trust, IAM)
- Resilience patterns (circuit breakers, chaos engineering)
- Multi-region architecture
- Cost optimization strategies

## Technology Stack

- **React 18.2** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling and responsive design
- **Lucide React** - Icon library
- **PostCSS & Autoprefixer** - CSS processing

## Getting Started

### Prerequisites
- Node.js 16.x or higher
- npm or yarn package manager

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The application will open at `http://localhost:3000`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint checks

## Project Structure

```
wiki-app/
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── components/
│   │   └── EnterpriseWiki.jsx  # Main wiki component
│   ├── App.jsx             # Root application component
│   ├── main.jsx            # Application entry point
│   └── index.css           # Global styles & Tailwind imports
├── index.html              # Vite HTML entry
├── package.json            # Dependencies and scripts
├── vite.config.js          # Vite configuration
├── tailwind.config.js      # Tailwind CSS configuration
├── postcss.config.js       # PostCSS configuration
└── README.md               # This file
```

## Component Architecture

### EnterpriseWiki Component

The main component manages:
- Role selection state
- Week navigation state
- Content rendering for selected role and week
- Progress tracking visualization

Key features:
- Responsive design (mobile, tablet, desktop)
- Smooth transitions and animations
- Accessible button states and indicators
- Dynamic content rendering based on user selection

## Customization

### Adding New Roles

To add a new role, update the `roles` and `roleContent` objects in `EnterpriseWiki.jsx`:

```javascript
// Add to roles object
newrole: {
  title: 'New Role Title',
  icon: IconComponent,
  color: 'blue', // tailwind color
  description: 'Role description',
  weeks: 6
}

// Add to roleContent object
newrole: {
  overview: {
    responsibilities: [...],
    skills: [...]
  },
  weeks: [...]
}
```

### Styling

The application uses Tailwind CSS with a dark theme palette. Key colors:
- Background: Slate shades (slate-900, slate-800, slate-700)
- Accent colors: Blue, green, purple, orange (600 shades)
- Text: White and slate shades for hierarchy

## Deployment

### Build for Production

```bash
npm run build
```

This creates an optimized production build in the `dist/` directory.

### Deployment Options

- **Static Hosting**: Deploy to Netlify, Vercel, or GitHub Pages
- **CDN**: Upload to AWS S3 + CloudFront or similar
- **Container**: Build a Docker image and deploy to any container platform

Example Netlify deployment:
```bash
npm run build
netlify deploy --prod --dir=dist
```

## Future Enhancements

Potential improvements:
- [ ] User authentication and progress persistence
- [ ] Interactive code examples and sandboxes
- [ ] Video tutorial integration
- [ ] Quiz and assessment features
- [ ] Certificate generation upon completion
- [ ] Community discussion forums
- [ ] Mobile app version
- [ ] Offline mode support

## Contributing

This is part of the Enterprise Portfolio project. To contribute:

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request with clear description

## License

Part of the Sam Jackson Portfolio Project.

## Contact

For questions or feedback about this learning platform:
- GitHub: [samueljackson-collab](https://github.com/samueljackson-collab)
- LinkedIn: [sams-jackson](https://www.linkedin.com/in/sams-jackson)

---

**Note**: This application is designed as an educational resource and portfolio demonstration. The content represents comprehensive learning paths for enterprise technical roles and can be customized for specific organizational needs.

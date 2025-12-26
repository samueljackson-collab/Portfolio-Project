# Enterprise Portfolio Wiki v5

> A comprehensive interactive portfolio showcasing 22 enterprise-grade projects with documentation, learning paths, and interview preparation.

## 🚀 Features

- **📁 Portfolio Hub**: Browse 22 projects across Cloud, DevOps, Security, QA, and AI domains
- **📚 Documentation Browser**: Access 176+ enterprise-grade documentation pages
- **🎓 Learning Paths**: Role-aligned study plans with progress tracking (SDE, DevOps, QA, Architect)
- **💡 Skills Matrix**: Technology frequency analysis across projects
- **🎯 Interview Prep**: STAR story templates for behavioral interviews
- **🔍 Advanced Search**: Fuzzy matching with keyboard shortcuts (Ctrl+K)
- **📊 KPI Dashboard**: Visual metrics and project statistics
- **⚙️ Wiki.js Integration**: Connect to external Wiki.js documentation

## 🛠 Tech Stack

- **React 18** with TypeScript
- **Vite** for blazing-fast builds
- **Tailwind CSS** for styling
- **React Markdown** with GFM and raw HTML support
- **LocalStorage** for state persistence

## 📦 Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check

# Linting
npm run lint
```

## 🏗 Project Structure

```
enterprise-wiki/
├── components/          # React components
│   ├── ui/             # Reusable UI components
│   ├── AdvancedSearch  # Fuzzy search modal
│   ├── KPIDashboard    # Metrics dashboard
│   ├── ProjectCard     # Project preview cards
│   ├── ProjectModal    # Detailed project view
│   ├── Sidebar         # Navigation sidebar
│   └── ToastContainer  # Notifications
├── pages/              # Page components
│   ├── PortfolioPage   # Main project gallery
│   ├── DocsPage        # Documentation browser
│   ├── LearningPage    # Learning paths
│   ├── SkillsPage      # Skills matrix
│   ├── InterviewPage   # Interview prep
│   ├── ReferencePage   # Reference guides
│   └── SettingsPage    # Configuration
├── hooks/              # Custom React hooks
│   ├── useHashRoute    # Hash-based routing
│   ├── useToast        # Toast notifications
│   ├── useAnalytics    # Event tracking
│   └── useKeyboard     # Keyboard shortcuts
├── utils/              # Utilities
│   ├── docGenerator    # Documentation templates
│   └── index           # Helper functions
├── constants.ts        # Project data & config
├── types.ts            # TypeScript definitions
└── index.tsx           # App entry point
```

## ⌨️ Keyboard Shortcuts

- **Ctrl+K**: Open advanced search
- **Escape**: Close modals/search
- **Arrow Keys**: Navigate search results
- **Enter**: Select search result

## 🎨 Customization

### Update Project Data

Edit `constants.ts` to modify:
- Projects list (PROJECTS array)
- Domain definitions (DOMAINS)
- Standard documentation templates (STANDARD_DOCS)
- Learning paths (LEARNING_ROLES, LEARNING_TOPICS)

### Styling

Tailwind configuration in `tailwind.config.js`. Custom utility classes in `index.css`.

### Wiki.js Integration

Configure in Settings page:
- **Wiki Base URL**: Your Wiki.js instance URL
- **Projects Base Path**: Path prefix for projects (`/projects`)
- **Docs Subdirectory**: Where docs live (`wiki`)

## 📊 Analytics

Built-in event tracking via `useAnalytics` hook. Currently logs to console. Integrate with:
- Google Analytics
- Plausible
- Mixpanel
- Custom analytics service

## 🚢 Deployment

### Static Hosting (Recommended)

```bash
npm run build
# Deploy dist/ folder to:
# - GitHub Pages
# - Netlify
# - Vercel
# - AWS S3 + CloudFront
```

### GitHub Pages

See deployment instructions in main project README.

## 📝 Documentation Generation

Generate documentation templates for projects:

```typescript
import { generateAllDocs, downloadDocumentation } from './utils/docGenerator';

// Generate all docs for a project
const docs = generateAllDocs(project);

// Download as files
downloadDocumentation(project);
```

Generates:
- README.md
- architecture.md
- runbook.md
- playbook.md

## 🧪 Development

```bash
# Install dependencies
npm install

# Start dev server (http://localhost:3000)
npm run dev

# Type check without emitting
npm run type-check

# Lint code
npm run lint
```

## 📄 License

Part of the Enterprise Portfolio Project.

## 🤝 Contributing

This is a portfolio project, but suggestions and improvements are welcome via issues or pull requests.

---

**Built with ❤️ using React, TypeScript, and Vite**

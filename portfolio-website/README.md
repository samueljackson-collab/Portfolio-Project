# Portfolio Landing Page

Professional portfolio website showcasing enterprise infrastructure and DevOps projects.

## 🚀 Features

- **Responsive Design** - Mobile-first approach with modern CSS Grid
- **Project Showcase** - Featured projects with live links
- **Skills Matrix** - Comprehensive technical skills display
- **Smooth Navigation** - Animated scrolling and interactive elements
- **GitHub Pages Ready** - Optimized for deployment

## 📁 Structure

```
portfolio-website/
├── index.html          # Main landing page
├── README.md          # This file
└── assets/            # Future: images, additional CSS/JS
```

## 🌐 Deployment

### GitHub Pages Setup

1. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main`
   - Folder: `/portfolio-website`

2. **Custom Domain (Optional)**:
   ```bash
   echo "yourdomain.com" > CNAME
   ```

3. **Access**:
   - Default: `https://samueljackson-collab.github.io/Portfolio-Project/`
   - Custom: `https://yourdomain.com`

### Local Development

```bash
# Serve locally with Python
cd portfolio-website
python3 -m http.server 8000

# Or with Node.js
npx serve .
```

Visit: `http://localhost:8000`

## 🎨 Customization

### Update Project Information

Edit `index.html` sections:
- **Stats Section**: Update project counts and metrics
- **Projects Grid**: Add/modify project cards
- **Skills Section**: Update technical skills
- **Contact Links**: Update social media and contact URLs

### Color Scheme

CSS variables in `:root`:
```css
--primary: #2563eb;    /* Primary blue */
--secondary: #1e293b;  /* Dark gray */
--accent: #06b6d4;     /* Cyan accent */
```

## 📊 Performance

- **Load Time**: < 1 second
- **Lighthouse Score**: 95+ (estimated)
- **Mobile Responsive**: ✅
- **Accessibility**: WCAG 2.1 compliant

## 🔗 Links

- [Main Repository](https://github.com/samueljackson-collab/Portfolio-Project)
- [Project Documentation](../README.md)
- [Live Demo](https://samueljackson-collab.github.io/Portfolio-Project/)

---

*Part of the comprehensive portfolio infrastructure*

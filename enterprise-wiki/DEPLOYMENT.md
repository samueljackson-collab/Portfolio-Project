# Deployment Guide

Complete guide for deploying the Enterprise Portfolio Wiki to various platforms.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Build Process](#build-process)
- [GitHub Pages](#github-pages)
- [Netlify](#netlify)
- [Vercel](#vercel)
- [AWS S3 + CloudFront](#aws-s3--cloudfront)
- [Docker](#docker)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Node.js 18+ and npm
- Git
- Build dependencies installed (`npm install`)

## Build Process

### Local Build

```bash
# Navigate to project directory
cd enterprise-wiki

# Install dependencies
npm install

# Run type checking
npm run type-check

# Build for production
npm run build

# Preview production build
npm run preview
```

The build output will be in the `dist/` directory.

### Build Verification

Check the build:

```bash
# Size of build
du -sh dist/

# List files
ls -lh dist/

# Test locally
npm run preview
# Visit http://localhost:4173
```

## GitHub Pages

### Automatic Deployment (Recommended)

A GitHub Actions workflow is already configured in `.github/workflows/deploy.yml`.

**Setup:**

1. Go to repository **Settings** → **Pages**
2. Set **Source** to "GitHub Actions"
3. Push to `main` branch
4. Workflow runs automatically and deploys to GitHub Pages

**Custom Domain:**

1. Add `CNAME` file to `public/` directory:
   ```
   your-domain.com
   ```
2. Configure DNS:
   ```
   A record: 185.199.108.153
   A record: 185.199.109.153
   A record: 185.199.110.153
   A record: 185.199.111.153
   ```
3. Enable **Enforce HTTPS** in Pages settings

### Manual Deployment

```bash
npm run build
npx gh-pages -d dist
```

## Netlify

### Via Git Integration (Recommended)

1. Log in to [Netlify](https://netlify.com)
2. Click **Add new site** → **Import an existing project**
3. Connect to GitHub repository
4. Configure build settings:
   - **Base directory**: `enterprise-wiki`
   - **Build command**: `npm run build`
   - **Publish directory**: `enterprise-wiki/dist`
5. Click **Deploy site**

The `netlify.toml` file provides automatic configuration.

### Via CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Build
npm run build

# Deploy
netlify deploy --prod --dir=dist
```

### Custom Domain

1. In Netlify dashboard → **Domain settings**
2. Add custom domain
3. Configure DNS:
   ```
   CNAME: <your-subdomain> → <your-site>.netlify.app
   ```

## Vercel

### Via Git Integration (Recommended)

1. Log in to [Vercel](https://vercel.com)
2. Click **Add New Project**
3. Import GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `enterprise-wiki`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Click **Deploy**

The `vercel.json` file provides automatic configuration.

### Via CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd enterprise-wiki
vercel --prod
```

## AWS S3 + CloudFront

### Step 1: Build

```bash
npm run build
```

### Step 2: Create S3 Bucket

```bash
# Create bucket
aws s3 mb s3://your-portfolio-bucket

# Enable static website hosting
aws s3 website s3://your-portfolio-bucket \
  --index-document index.html \
  --error-document index.html
```

### Step 3: Upload Build

```bash
# Sync build to S3
aws s3 sync dist/ s3://your-portfolio-bucket \
  --delete \
  --cache-control "public, max-age=31536000, immutable" \
  --exclude "index.html"

# Upload index.html separately (no cache)
aws s3 cp dist/index.html s3://your-portfolio-bucket/index.html \
  --cache-control "public, max-age=0, must-revalidate"
```

### Step 4: CloudFront Distribution

```bash
# Create distribution (use AWS Console or CLI)
aws cloudfront create-distribution \
  --origin-domain-name your-portfolio-bucket.s3.amazonaws.com \
  --default-root-object index.html
```

**CloudFront Configuration:**
- Origin: S3 bucket
- Viewer Protocol Policy: Redirect HTTP to HTTPS
- Custom Error Response: 404 → /index.html (for SPA routing)
- Caching: Cache based on headers

### Step 5: Invalidate Cache on Deploy

```bash
aws cloudfront create-invalidation \
  --distribution-id YOUR_DIST_ID \
  --paths "/*"
```

### Automated Deployment Script

Create `deploy-aws.sh`:

```bash
#!/bin/bash
set -e

echo "Building..."
npm run build

echo "Uploading to S3..."
aws s3 sync dist/ s3://your-portfolio-bucket \
  --delete \
  --cache-control "public, max-age=31536000, immutable" \
  --exclude "index.html"

aws s3 cp dist/index.html s3://your-portfolio-bucket/index.html \
  --cache-control "public, max-age=0, must-revalidate"

echo "Invalidating CloudFront cache..."
aws cloudfront create-invalidation \
  --distribution-id YOUR_DIST_ID \
  --paths "/*"

echo "Deployment complete!"
```

Make executable: `chmod +x deploy-aws.sh`

## Docker

### Build Docker Image

Create `Dockerfile`:

```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Create `nginx.conf`:

```nginx
events {
  worker_connections 1024;
}

http {
  include /etc/nginx/mime.types;
  default_type application/octet-stream;

  server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip
    gzip on;
    gzip_types text/css application/javascript application/json;

    # SPA routing
    location / {
      try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location /assets/ {
      add_header Cache-Control "public, max-age=31536000, immutable";
    }

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
  }
}
```

### Build and Run

```bash
# Build image
docker build -t portfolio-wiki .

# Run container
docker run -d -p 8080:80 portfolio-wiki

# Visit http://localhost:8080
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  portfolio:
    build: .
    ports:
      - "8080:80"
    restart: unless-stopped
```

Run: `docker-compose up -d`

## Troubleshooting

### Build Fails

**Issue**: TypeScript errors during build

**Solution**:
```bash
npm run type-check  # See all type errors
# Fix errors or use --skipLibCheck if needed
```

---

**Issue**: Out of memory during build

**Solution**:
```bash
NODE_OPTIONS=--max_old_space_size=4096 npm run build
```

### Routing Issues (404 on refresh)

**Issue**: Direct navigation to routes shows 404

**Solution**: Configure server to serve `index.html` for all routes
- GitHub Pages: Handled automatically
- Netlify: See `netlify.toml` redirects
- Vercel: See `vercel.json` rewrites
- Nginx: Use `try_files $uri /index.html`
- AWS S3: Set error document to `index.html`

### Assets Not Loading

**Issue**: CSS/JS not loading

**Solution**:
1. Check `vite.config.ts` base URL:
   ```ts
   export default defineConfig({
     base: '/repository-name/', // For GitHub Pages subdirectory
   })
   ```
2. Rebuild: `npm run build`

### CORS Issues

**Issue**: Cannot load external resources

**Solution**: Add CORS headers in deployment config or fetch from same origin.

### Performance Issues

**Optimization checklist**:
- ✅ Code splitting (already configured in `vite.config.ts`)
- ✅ Lazy load images
- ✅ Enable compression (gzip/brotli)
- ✅ Use CDN
- ✅ Optimize bundle size: `npm run build -- --analyze`

## Post-Deployment Checklist

- [ ] Site loads correctly
- [ ] All pages accessible
- [ ] Hash routing works (#/portfolio, #/docs, etc.)
- [ ] Search functionality works (Ctrl+K)
- [ ] External links open correctly
- [ ] Images load
- [ ] Responsive on mobile
- [ ] Performance acceptable (Lighthouse score)
- [ ] Analytics tracking (if configured)
- [ ] SEO meta tags present
- [ ] HTTPS enabled
- [ ] Custom domain configured (if applicable)

## Continuous Deployment

For automatic deployments on every push:

1. **GitHub Pages**: Already configured via Actions
2. **Netlify**: Auto-deploys from Git integration
3. **Vercel**: Auto-deploys from Git integration
4. **AWS**: Add deployment to CI/CD pipeline

Example GitHub Actions for AWS:

```yaml
- name: Deploy to AWS
  run: |
    npm run build
    aws s3 sync dist/ s3://${{ secrets.S3_BUCKET }} --delete
    aws cloudfront create-invalidation --distribution-id ${{ secrets.CF_DIST_ID }} --paths "/*"
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

---

**Need help?** Check the main [README.md](./README.md) or open an issue.

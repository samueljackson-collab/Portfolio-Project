# Visual Assets & Diagrams

**Complete collection of diagrams, AI prompts, and visual resources for the enterprise portfolio code examples.**

---

## 📊 Available Diagrams

### Architecture Diagrams (Mermaid)

Located in: `diagrams/architecture/`

1. **`01-terraform-infrastructure-overview.mermaid`**
   - Complete AWS infrastructure overview
   - VPC + EKS + RDS modules
   - Multi-AZ deployment
   - Security and monitoring layers
   - **Use case**: High-level architecture presentations

2. **`02-eks-cluster-detail.mermaid`**
   - Detailed EKS cluster components
   - Control plane and data plane
   - Worker nodes and pods
   - IAM/IRSA configuration
   - **Use case**: Kubernetes expertise demonstration

3. **`03-rds-high-availability.mermaid`**
   - Multi-AZ PostgreSQL architecture
   - Replication topology
   - Backup and recovery strategy
   - Monitoring and alerting
   - **Use case**: Database reliability discussions

### CI/CD Diagrams (Mermaid)

Located in: `diagrams/cicd/`

1. **`01-github-actions-pipeline.mermaid`**
   - 8-stage production pipeline
   - Parallel and sequential jobs
   - Deployment strategy
   - Rollback scenarios
   - **Use case**: DevOps pipeline presentations

2. **`02-argocd-gitops-flow.mermaid`**
   - GitOps workflow visualization
   - ArgoCD sync process
   - Self-healing capabilities
   - Multi-environment strategy
   - **Use case**: GitOps and continuous deployment talks

### Networking Diagrams (Mermaid)

Located in: `diagrams/networking/`

1. **`01-network-architecture.mermaid`**
   - Defense-in-depth security layers
   - 3-tier subnet architecture
   - Security groups and NACLs
   - Traffic flow paths
   - **Use case**: Network security presentations

### Testing Diagrams (Mermaid)

Located in: `diagrams/testing/`

1. **`01-test-pyramid.mermaid`**
   - Test distribution strategy
   - Unit, integration, E2E breakdown
   - Performance testing approach
   - Test tools and frameworks
   - **Use case**: QA strategy discussions

---

## 🎨 AI Prompts for Advanced Visuals

Located in: `diagrams/ai-prompts/`

### Architecture 3D Diagrams

**File**: `01-architecture-3d-diagram.md`

Contains 4 detailed prompts for:

1. **AWS Infrastructure Overview (Isometric 3D)**
   - Tools: Midjourney, DALL-E, Stable Diffusion
   - Style: Professional, AWS-style 3D isometric
   - Output: 4K landscape PNG
   - **Use case**: Portfolio homepage, executive presentations

2. **EKS Cluster Detail (Cross-Section View)**
   - Tools: Midjourney, DALL-E
   - Style: Technical blueprint with neon accents
   - Output: 4K dark theme
   - **Use case**: Technical deep-dives, blog posts

3. **Data Flow & Security Layers**
   - Tools: Midjourney, DALL-E
   - Style: Horizontal layered defense visualization
   - Output: Ultra-wide 21:9
   - **Use case**: Security presentations, infographics

4. **CI/CD Pipeline Visualization**
   - Tools: Midjourney, DALL-E
   - Style: Modern DevOps aesthetic with flowing connections
   - Output: Ultra-wide dark theme
   - **Use case**: DevOps portfolio, presentations

### Dashboard Mockups

**File**: `02-dashboard-mockups.md`

Contains 4 detailed prompts for:

1. **CloudWatch Dashboard Mockup**
   - Tools: Figma AI, Midjourney, DALL-E
   - Style: AWS CloudWatch dark theme
   - Resolution: 2560x1440
   - **Use case**: Monitoring expertise, portfolio screenshots

2. **Grafana Metrics Dashboard**
   - Tools: Figma AI, Real Grafana
   - Style: Grafana dark theme with realistic metrics
   - Resolution: 2560x1440
   - **Use case**: SRE portfolio, monitoring demonstrations

3. **ArgoCD Applications Dashboard**
   - Tools: Figma AI, Real ArgoCD
   - Style: Modern GitOps interface
   - Resolution: 2560x1440
   - **Use case**: GitOps expertise, DevOps portfolio

4. **K6 Performance Test Results**
   - Tools: Real K6, Figma
   - Style: Technical test report
   - Resolution: 2560x1440
   - **Use case**: Performance testing portfolio, QA demonstrations

---

## 🚀 How to Use These Diagrams

### Viewing Mermaid Diagrams

#### Option 1: GitHub (Automatic Rendering)
```
Simply view the .mermaid files directly on GitHub
GitHub automatically renders Mermaid diagrams
```

#### Option 2: VS Code
```bash
# Install Mermaid Preview extension
code --install-extension bierner.markdown-mermaid

# Open .mermaid file and use preview
```

#### Option 3: Mermaid Live Editor
```
1. Visit: https://mermaid.live/
2. Copy diagram code
3. Paste into editor
4. Export as PNG/SVG
```

#### Option 4: Command Line (mermaid-cli)
```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Generate PNG
mmdc -i diagram.mermaid -o diagram.png -b transparent

# Generate SVG
mmdc -i diagram.mermaid -o diagram.svg

# Batch convert all diagrams
find . -name "*.mermaid" -exec mmdc -i {} -o {}.png \;
```

### Generating AI Diagrams

#### Using Midjourney

```bash
1. Join Midjourney Discord server
2. Go to any #general or #newbies channel
3. Type: /imagine
4. Paste prompt from ai-prompts/ files
5. Add parameters: --v 6 --ar 16:9 --quality 2
6. Wait for generation (~60 seconds)
7. Upscale desired variant
8. Download high-resolution image
```

**Example Command:**
```
/imagine [paste prompt here] --v 6 --ar 16:9 --quality 2
```

#### Using DALL-E 3 (ChatGPT Plus)

```bash
1. Open ChatGPT (ChatGPT Plus subscription required)
2. Paste prompt from ai-prompts/ files
3. Wait for generation (~30 seconds)
4. Download image
5. Iterate with "Make it darker" or "Add more detail" if needed
```

#### Using Figma for Dashboards

```bash
1. Create new Figma file
2. Use AWS/Grafana UI kit templates
3. Or generate base with AI, then import to Figma
4. Customize with real data/labels
5. Export as PNG (2x resolution for crisp display)
```

---

## 📏 Diagram Specifications

### Mermaid Diagrams

| Diagram Type | Node Count | Complexity | Render Time |
|--------------|------------|------------|-------------|
| Infrastructure Overview | 50+ | High | 2-3s |
| EKS Cluster Detail | 40+ | High | 2-3s |
| RDS High Availability | 30+ | Medium | 1-2s |
| GitHub Actions Pipeline | 60+ | Very High | 3-4s |
| ArgoCD GitOps Flow | 45+ | High | 2-3s |
| Network Architecture | 55+ | Very High | 3-4s |
| Test Pyramid | 25+ | Medium | 1-2s |

### AI-Generated Diagrams

#### Recommended Specifications:

**For Presentations:**
- Format: PNG
- Resolution: 3840x2160 (4K)
- DPI: 300
- Color space: sRGB
- Compression: Moderate

**For Web:**
- Format: WebP or PNG
- Resolution: 1920x1080 (1080p)
- Optimization: TinyPNG
- Lazy loading: Yes

**For Print:**
- Format: PDF or TIFF
- Resolution: 300 DPI minimum
- Color space: CMYK (if printing)
- Bleed: 0.125" if applicable

---

## 🎯 Use Cases by Role

### For System Development Engineers:

**Best Diagrams:**
- Terraform Infrastructure Overview
- EKS Cluster Detail
- RDS High Availability
- Network Architecture

**Talking Points:**
- "This diagram shows the multi-AZ architecture I designed..."
- "Here's how I implemented IRSA for pod-level IAM..."
- "The backup strategy includes 30-day retention..."

### For DevOps Engineers:

**Best Diagrams:**
- GitHub Actions Pipeline
- ArgoCD GitOps Flow
- All infrastructure diagrams

**Talking Points:**
- "My 8-stage pipeline includes automated security scanning..."
- "GitOps provides audit trail and rollback capabilities..."
- "Canary deployments reduce production risk..."

### For QA Engineers:

**Best Diagrams:**
- Test Pyramid
- K6 Performance Results (mockup)
- GitHub Actions Pipeline (testing stages)

**Talking Points:**
- "70% unit tests provide fast feedback..."
- "Performance testing validates SLAs..."
- "E2E tests cover critical user journeys..."

### For Solutions Architects:

**Best Diagrams:**
- All architecture diagrams
- Network Architecture
- Data flow diagrams

**Talking Points:**
- "Defense-in-depth security with multiple layers..."
- "High availability across 3 availability zones..."
- "Cost-optimized with right-sizing and reserved instances..."

---

## 🛠️ Tools & Resources

### Diagramming Tools

**Free & Open Source:**
- [Mermaid.js](https://mermaid.js.org/) - Diagram as code
- [Diagrams.net / Draw.io](https://app.diagrams.net/) - Visual diagramming
- [Excalidraw](https://excalidraw.com/) - Hand-drawn style
- [PlantUML](https://plantuml.com/) - UML diagrams as code

**Commercial:**
- [Lucidchart](https://www.lucidchart.com/) - Professional diagramming
- [Cloudcraft](https://www.cloudcraft.co/) - 3D AWS diagrams
- [Figma](https://www.figma.com/) - UI/UX design (dashboards)
- [Miro](https://miro.com/) - Collaborative whiteboarding

**AI Tools:**
- [Midjourney](https://www.midjourney.com/) - AI image generation
- [DALL-E 3](https://openai.com/dall-e-3) - AI image generation (ChatGPT Plus)
- [Stable Diffusion](https://stability.ai/) - Open source AI generation
- [Adobe Firefly](https://www.adobe.com/products/firefly.html) - AI design tool

### AWS-Specific Tools

**AWS Architecture Icons:**
- [Official AWS Icon Set](https://aws.amazon.com/architecture/icons/) - Latest SVG icons
- Download: PNG, SVG, PowerPoint formats

**Cloudcraft:**
- 3D AWS architecture diagrams
- Real-time AWS resource scanning
- Cost estimation integration
- Export to PNG, SVG, PDF

**Diagram as Code (Python):**
```python
# Install
pip install diagrams

# Example
from diagrams import Diagram
from diagrams.aws.compute import EKS
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB

with Diagram("AWS Architecture", show=False):
    ELB("lb") >> EKS("eks") >> RDS("database")
```

---

## 📤 Export & Usage Guidelines

### File Naming Convention

```
{category}-{description}-{version}.{extension}

Examples:
- architecture-terraform-overview-v1.png
- cicd-github-actions-pipeline-v2.svg
- monitoring-cloudwatch-dashboard-dark.png
- testing-pyramid-strategy-v1.pdf
```

### Export Checklist

**Before Publishing:**
- [ ] Remove any sensitive information (IPs, account IDs, domains)
- [ ] Verify color contrast for accessibility
- [ ] Test rendering on light/dark backgrounds
- [ ] Check file size (<5MB for web)
- [ ] Add alt text for accessibility
- [ ] Include attribution if using templates
- [ ] Optimize for target platform

**Metadata to Include:**
```yaml
Title: AWS Infrastructure Architecture
Author: Sam Jackson
Date: 2025-11-06
Description: Multi-AZ infrastructure with EKS and RDS
Tools Used: Terraform, AWS, Mermaid
License: Portfolio Use Only
```

### Usage Rights

**Portfolio Use**: ✅ Allowed
- Personal website
- LinkedIn posts
- GitHub README
- Interview presentations
- Blog posts

**Not Allowed**: ❌
- Commercial redistribution
- Template marketplaces
- Stock image sites
- Claiming sole authorship if using AI generation

---

## 🎓 Best Practices

### Diagram Design Principles

1. **Clarity Over Complexity**
   - Remove unnecessary details
   - Use consistent styling
   - Label all components
   - Include legends

2. **Hierarchy & Flow**
   - Top to bottom for processes
   - Left to right for timelines
   - Concentric circles for layers
   - Clear arrows for data flow

3. **Color Usage**
   - Consistent color coding
   - Accessible contrast ratios (WCAG AA)
   - 3-5 colors maximum
   - Semantic colors (red=error, green=success)

4. **Typography**
   - Sans-serif fonts (Inter, Roboto)
   - Minimum 10pt font size
   - Consistent text sizing
   - High contrast text

### Presentation Tips

**For Technical Interviews:**
- Print in color if presenting in person
- Have high-res digital version ready
- Prepare to explain each component
- Know trade-offs and alternatives

**For Portfolio Website:**
- Use WebP format for faster loading
- Provide click-to-zoom functionality
- Add captions with context
- Include "View Code" links

**For Documentation:**
- Embed diagrams directly in markdown
- Provide alt text descriptions
- Link to editable source
- Version control diagram sources

---

## 📊 Diagram Metrics

### Complexity Ratings

| Diagram | Components | Connections | Time to Create | Expertise Required |
|---------|------------|-------------|----------------|-------------------|
| Infrastructure Overview | 50+ | 40+ | 2-3 hours | High |
| EKS Cluster | 40+ | 35+ | 2 hours | High |
| RDS HA | 30+ | 25+ | 1.5 hours | Medium |
| GitHub Actions | 60+ | 50+ | 3 hours | High |
| ArgoCD GitOps | 45+ | 40+ | 2.5 hours | High |
| Network Architecture | 55+ | 45+ | 3 hours | Very High |
| Test Pyramid | 25+ | 20+ | 1 hour | Medium |

### Estimated Generation Times

**Mermaid Diagrams:**
- Simple (< 20 nodes): 30 minutes
- Medium (20-40 nodes): 1-2 hours
- Complex (40+ nodes): 2-4 hours

**AI-Generated Diagrams:**
- Single generation: 1-2 minutes
- Iterations for perfection: 5-10 minutes
- Post-processing: 10-30 minutes

---

## 🤝 Contributing

Found an issue or have an improvement?

1. Check existing diagrams for style consistency
2. Follow naming conventions
3. Test rendering across platforms
4. Update this README with new diagrams
5. Submit with clear documentation

---

## 📚 Additional Resources

### Learning Resources:
- [Mermaid Documentation](https://mermaid.js.org/intro/)
- [AWS Architecture Center](https://aws.amazon.com/architecture/)
- [Kubernetes Docs - Architecture](https://kubernetes.io/docs/concepts/architecture/)
- [C4 Model](https://c4model.com/) - Software architecture diagrams

### Inspiration:
- [AWS Reference Architectures](https://aws.amazon.com/architecture/)
- [Kubernetes Production Patterns](https://kubernetes.io/case-studies/)
- [Cloud Architecture Patterns](https://docs.microsoft.com/en-us/azure/architecture/patterns/)

---

**Created by**: Sam Jackson
**Last Updated**: November 6, 2025
**Total Diagrams**: 7 Mermaid + 8 AI Prompts = 15 visual assets

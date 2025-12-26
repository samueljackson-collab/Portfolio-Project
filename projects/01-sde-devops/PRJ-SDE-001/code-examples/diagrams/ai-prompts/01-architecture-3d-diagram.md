# AI Prompts for 3D Architecture Diagrams

These prompts can be used with tools like:
- **Midjourney** (Discord bot)
- **DALL-E 3** (ChatGPT Plus / API)
- **Stable Diffusion** (Local/Cloud)
- **Adobe Firefly**
- **Canva AI**

---

## Prompt 1: AWS Infrastructure Overview (Isometric 3D)

### For Midjourney / DALL-E:

```
Create a professional 3D isometric technical diagram of AWS cloud infrastructure showing:

FOREGROUND (Internet/Edge Layer):
- Globe icon representing internet users
- CloudFront CDN nodes (orange cubes with CDN icon)
- Route 53 DNS (blue globe with DNS label)
- AWS WAF shield icon (protective barrier)

MIDDLE LAYER (VPC - Primary focus):
- Large transparent cube labeled "VPC 10.0.0.0/16"
- Inside VPC, three vertical layers:
  1. TOP: Public Subnet tier (light blue) with Load Balancer icons
  2. MIDDLE: Private Subnet tier (light green) with Kubernetes pod clusters
  3. BOTTOM: Database Subnet tier (light red) with database cylinders

DETAILED COMPONENTS:
- Application Load Balancer: Blue rectangular prisms with "ALB" label
- NAT Gateways: Orange cubes with outward arrows
- EKS Cluster: Green hexagonal containers representing pods
- RDS PostgreSQL: Red cylinders with "PostgreSQL 15" label
- ElastiCache Redis: Purple cube with "Redis" label

RIGHT SIDE (Security & Monitoring):
- Security Group shields (yellow)
- CloudWatch dashboard (monitoring charts)
- VPC Flow Logs icon (flowing arrows into logs)

CONNECTIONS:
- Blue glowing lines for HTTPS traffic
- Green lines for internal communication
- Red dashed lines for database connections
- Orange lines for replication

STYLE:
- Clean, professional AWS architecture style
- Soft shadows and depth
- Pastel colors with clear labels
- Technical but approachable
- White or light gray background
- Sans-serif fonts (like Inter or Roboto)
- Icons should match AWS service icons style

TECHNICAL SPECIFICATIONS:
- 4K resolution
- PNG format with transparent background option
- Aspect ratio: 16:9 (landscape)
- Lighting: Soft top-down with minimal shadows
- Perspective: 30-degree isometric view
```

### Expected Output:
- High-quality 3D isometric diagram
- Clear service boundaries
- Professional AWS-style design
- Suitable for presentations and documentation

---

## Prompt 2: EKS Cluster Detail (Cross-Section View)

### For Midjourney / DALL-E:

```
Create a detailed cross-section technical diagram of a Kubernetes EKS cluster showing:

TOP SECTION (Control Plane - Managed by AWS):
- Transparent dome labeled "AWS Managed Control Plane"
- Inside dome: Four interconnected spheres
  1. API Server (blue sphere with API icon)
  2. Scheduler (green sphere with calendar icon)
  3. Controller Manager (orange sphere with gears icon)
  4. etcd (purple cylinder with database icon)
- Encryption lock icon on etcd showing KMS encryption

MIDDLE SECTION (Data Plane - Customer Managed):
Three availability zones shown as separate columns:

AZ-A Column:
- Worker Node 1 (gray rectangular prism)
  - Inside: 2-3 small colorful cubes representing pods
  - Labels: "t3.medium", "8GB RAM", "2 vCPU"
- Connection lines to pods

AZ-B Column:
- Worker Node 2 (gray rectangular prism)
  - Inside: 2-3 small colorful cubes representing pods
  - Same specifications

AZ-C Column:
- Worker Node 3 (gray rectangular prism)
  - Inside: 2-3 small colorful cubes representing pods
  - Same specifications

BOTTOM SECTION (Storage & Networking):
- EBS volumes (orange cylinders attached to nodes)
- EFS shared storage (purple cloud shape)
- VPC networking layer (blue grid/mesh underneath)
- Security groups (yellow shields around components)

LEFT SIDE (IAM & Security):
- OIDC Provider badge
- IAM Roles icons connected to pods with green lines
- KMS encryption keys (lock icons)

RIGHT SIDE (Monitoring):
- CloudWatch Logs (dashboard icon)
- Container Insights (charts and graphs)
- Prometheus metrics (time-series graph icon)

VISUAL STYLE:
- Technical blueprint aesthetic
- Dark blue grid background
- Neon-style glowing connection lines
- Component labels with arrows
- Legend in bottom corner
- Professional cloud architecture style

TECHNICAL SPECIFICATIONS:
- 4K resolution
- Dark theme with neon accents
- Aspect ratio: 16:9
- Cross-section view (side angle)
- Clear component labels
```

### Expected Output:
- Detailed Kubernetes architecture visualization
- Clear separation of control and data planes
- Professional technical diagram style
- Suitable for technical presentations

---

## Prompt 3: Data Flow & Security Layers

### For Midjourney / DALL-E:

```
Create a horizontal layer diagram showing data flow through security layers:

Layout from top to bottom showing concentric security layers:

LAYER 1 (Top - Internet):
- Users/devices icons (laptops, phones, browsers)
- Threat actors icon (red hacker symbol)
- Both pointing downward

LAYER 2 (Edge Security):
- CloudFront CDN shield (wide protective layer)
- AWS WAF filtering rules (firewall icon)
- DDoS Protection (shield with lightning bolt)
- Green checkmark for allowed traffic
- Red X for blocked malicious traffic

LAYER 3 (Network Perimeter):
- Internet Gateway (gateway icon)
- VPC boundary (thick blue line)
- Network ACLs (first firewall layer)
- Public subnet DMZ zone (light blue band)

LAYER 4 (Application Security):
- Application Load Balancer (horizontal bar with distribution arrows)
- Security Groups (yellow shields)
- SSL/TLS encryption lock icons
- Private subnet zone (green band)

LAYER 5 (Application Layer):
- EKS Pod security contexts
- Service Mesh (if applicable)
- Container security scanning results
- Green application containers

LAYER 6 (Data Security):
- Database security group (red shield)
- Database subnet (red band completely isolated)
- KMS encryption at rest (lock icon)
- Audit logging (document with checkmarks)

VISUAL ELEMENTS:
- Data flow arrows in green (allowed) moving through layers
- Red X marks where threats are blocked at each layer
- Each layer should have distinct color and thickness
- Annotations showing what each layer protects against
- Side panel showing: "Stopped: DDoS, SQL Injection, Unauthorized Access"

STYLE:
- Horizontal layered defense visualization
- Clean, professional security diagram style
- Color-coded threat levels
- Clear data flow paths
- White or light background
- Professional cybersecurity aesthetic

TECHNICAL SPECIFICATIONS:
- 4K resolution
- Horizontal orientation (landscape wide)
- Aspect ratio: 21:9 (ultra-wide)
- Clear security layer boundaries
```

### Expected Output:
- Clear defense-in-depth visualization
- Security layers easily understood
- Threat blocking points identified
- Professional security presentation style

---

## Prompt 4: CI/CD Pipeline Visualization

### For Midjourney / DALL-E:

```
Create a modern, flowing CI/CD pipeline visualization:

LAYOUT:
Horizontal flow from left to right, showing pipeline stages as connected segments

STAGE 1 (Code):
- GitHub Octocat icon
- Developer icon pushing code
- Git branches visualization
- Color: Dark gray/black

STAGE 2 (Build):
- Automated build icon (gears turning)
- Docker container icon
- Multi-platform badges (AMD64, ARM64)
- Color: Blue

STAGE 3 (Test):
- Three parallel test tracks:
  1. Unit Tests (fast track - green)
  2. Integration Tests (medium track - yellow)
  3. E2E Tests (slower track - orange)
- Checkmark icons for passed tests
- Code coverage badge "85%"
- Color: Green gradient

STAGE 4 (Security Scan):
- Shield with magnifying glass
- Vulnerability scanner icon
- Security badges (PASSING)
- SBOM document icon
- Color: Yellow/Gold

STAGE 5 (Deploy to Staging):
- Kubernetes logo
- Staging environment icon (cloud with "STG" label)
- Helm chart icon
- Smoke test indicator
- Color: Purple

STAGE 6 (Performance Test):
- Load testing graph (upward trend)
- K6 logo
- Performance metrics dashboard
- Green "PASS" indicator
- Color: Teal

STAGE 7 (Deploy to Production):
- Production environment (cloud with "PROD" label)
- Canary deployment split (10% vs 90%)
- Monitoring dashboard
- Success checkmark
- Color: Red/Orange gradient

VISUAL STYLE:
- Modern DevOps aesthetic
- Flowing connections between stages (like a river)
- Each stage is a rounded rectangle with icon + label
- Success indicators (green checkmarks)
- Parallel tracks for concurrent operations
- Timeline showing duration at bottom
- Dark theme with vibrant accent colors

ANNOTATIONS:
- Time duration for each stage
- Success/Failure indicators
- Automated vs Manual gates
- Rollback arrows (red dashed lines)

TECHNICAL SPECIFICATIONS:
- 4K resolution
- Ultra-wide format (21:9)
- Dark theme (#1e1e1e background)
- Vibrant accent colors
- Modern SaaS UI style
```

### Expected Output:
- Modern CI/CD pipeline visualization
- Clear stage progression
- Professional DevOps design
- Suitable for executive presentations

---

## Tools and Tips

### Recommended Tools:

1. **Midjourney** (Best for stylized diagrams)
   - Access via Discord
   - Use `/imagine` command with prompt
   - Use `--v 6` for latest model
   - Add `--ar 16:9` for landscape
   - Use `--quality 2` for high quality

2. **DALL-E 3** (Best for detailed technical diagrams)
   - Access via ChatGPT Plus
   - More literal interpretation
   - Great for technical accuracy
   - Can iterate with feedback

3. **Figma + AI Plugins**
   - For editable diagrams
   - Can add annotations
   - Export to multiple formats

4. **Lucidchart + AI**
   - Technical diagram templates
   - AWS shape libraries
   - Collaborative editing

### Post-Processing Tips:

1. **Add Annotations** in tools like:
   - Figma
   - Sketch
   - Adobe Illustrator
   - Canva

2. **Export Formats**:
   - PNG (for presentations)
   - SVG (for web, scalable)
   - PDF (for print)

3. **Optimize**:
   - Compress images (TinyPNG)
   - Add alt text for accessibility
   - Maintain consistent style

### Alternative: Diagram-as-Code Tools

If AI generation isn't suitable:

- **Diagrams.net / Draw.io**: AWS shapes library
- **Cloudcraft**: 3D AWS architecture diagrams
- **Diagram (Python)**: Code-based diagrams
- **Structurizr**: C4 model diagrams

```python
# Example: diagram as code
from diagrams import Diagram, Cluster
from diagrams.aws.compute import EKS, EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB, VPC

with Diagram("AWS Architecture", show=False):
    with Cluster("VPC"):
        lb = ELB("Load Balancer")
        with Cluster("EKS Cluster"):
            eks = [EKS("Pod 1"), EKS("Pod 2"), EKS("Pod 3")]
        db = RDS("PostgreSQL")

        lb >> eks >> db
```

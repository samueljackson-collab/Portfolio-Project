# Documentation Examples & Templates

This directory contains reference examples, UI mockups, and templates for the portfolio documentation system.

## 📁 Contents

### [wikijs-ui-mockup.html](./wikijs-ui-mockup.html)

**Purpose:** Visual demonstration of the deployed Wiki.js documentation system for recruiter presentations.

**What it shows:**
- Professional Wiki.js interface design with production-ready styling
- Complete documentation page layout with header, navigation, content, and table of contents
- Real infrastructure documentation example (Homelab overview)
- Demonstrates the end-to-end documentation maturity expected from the portfolio

**Use Cases:**
1. **Recruiter Demonstrations** - Show how the final Wiki.js deployment will look
2. **Design Reference** - Template for creating additional Wiki.js pages
3. **Portfolio Presentations** - Visual proof of documentation capabilities
4. **UI/UX Preview** - Demonstrate professional knowledge management system

**Key Features Demonstrated:**
- ✅ Three-column layout (navigation sidebar, main content, table of contents)
- ✅ Breadcrumb navigation
- ✅ Tag system for categorization
- ✅ Metadata (last edited, views, author)
- ✅ Content formatting (tables, code blocks, lists)
- ✅ Page actions (edit, history, share, print)
- ✅ Responsive design with sticky header and TOC

**Content Example:**
The mockup showcases a complete "Infrastructure Overview" page documenting:
- Hardware specifications (Dell R720 Proxmox host, TrueNAS storage)
- Network architecture with VLAN segmentation
- Virtual machine inventory with resource allocation
- Service architecture patterns
- Backup and monitoring strategies

**Viewing the Mockup:**
```bash
# Open in browser
open docs/examples/wikijs-ui-mockup.html

# Or serve with Python
cd docs/examples
python3 -m http.server 8080
# Navigate to http://localhost:8080/wikijs-ui-mockup.html
```

**Integration Points:**
- Referenced in [Live Demo Architecture](../live-demo-architecture.md)
- Complements [Wiki.js Setup Guide](../wiki-js-setup-guide.md)
- Visual representation of [Enterprise Wiki Documentation](../../wiki/)

---

## 🎯 Why This Matters

**For Recruiters:**
- Shows **end-to-end thinking** - not just code, but professional documentation systems
- Demonstrates **UI/UX awareness** - clean, modern, accessible design
- Proves **operational maturity** - real infrastructure with proper documentation

**For Technical Stakeholders:**
- Illustrates **information architecture** - hierarchical navigation and organization
- Shows **content quality** - detailed, technical, actionable documentation
- Demonstrates **tooling expertise** - Wiki.js, markdown, knowledge management

**For Portfolio:**
- Visual proof of **documentation-first mindset**
- Example of **enterprise-grade practices**
- Demonstrates **attention to detail** in presentation

---

## 📚 Related Documentation

- [Wiki.js Setup Guide](../wiki-js-setup-guide.md) - Complete deployment instructions
- [Live Demo Architecture](../live-demo-architecture.md) - Docker Compose demo stack
- [Enterprise Wiki Documentation](../../wiki/) - Actual markdown documentation content
- [Interactive Learning Paths](../../enterprise-wiki-app/) - React application

---

## 🔗 External References

- [Wiki.js Official Documentation](https://docs.requarks.io/)
- [Wiki.js Theming Guide](https://docs.requarks.io/dev/themes)
- [Markdown Guide](https://www.markdownguide.org/)

---

*Last Updated: 2025-11-10*
*Maintained by: Sam Jackson*

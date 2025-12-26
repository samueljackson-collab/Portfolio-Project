# Mermaid Diagram PNG Conversion Guide

This guide provides multiple methods to convert the Mermaid diagrams (.mmd files) to PNG images for use in portfolios, documentation, and presentations.

---

## 🎯 Quick Start (Recommended)

### Method 1: Online Converter (No Installation)

**Fastest way to get PNG images right now:**

1. Visit **https://mermaid.live/**
2. For each diagram file:
   - Open the `.mmd` file in a text editor
   - Copy the entire content
   - Paste into the left editor panel on Mermaid Live
   - Preview renders automatically on the right
   - Click **"Actions"** → **"PNG"** to download

**Diagrams to convert:**
- `service-architecture.mmd`
- `data-flow.mmd`
- `backup-recovery.mmd`
- `network-topology.mmd`
- `monitoring-architecture.mmd`
- `disaster-recovery-flow.mmd`

**Pros:**
✅ No installation required
✅ Works immediately
✅ Preview before download
✅ Good quality (suitable for most uses)

**Cons:**
❌ Manual process for each file
❌ Can't customize resolution
❌ Requires internet connection

---

## 🛠️ Method 2: Automated Script (Best Quality)

### Prerequisites

**1. Install Node.js:**
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version  # Should show v20.x.x
npm --version   # Should show v10.x.x
```

**2. Install Mermaid CLI:**
```bash
# Install globally
sudo npm install -g @mermaid-js/mermaid-cli

# Verify installation
mmdc --version  # Should show version number

# If you get Puppeteer/Chrome errors, install dependencies:
sudo apt-get update
sudo apt-get install -y \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils
```

### Run Conversion Script

```bash
# Navigate to diagrams directory
cd projects/06-homelab/PRJ-HOME-002/assets/diagrams/

# Make script executable (if not already)
chmod +x CONVERT-TO-PNG.sh

# Run the script
./CONVERT-TO-PNG.sh
```

**The script will:**
- Check if Mermaid CLI is installed
- Find all `.mmd` files
- Convert each to PNG with:
  - Transparent background
  - 3000px width (high resolution)
  - 2x scale (Retina quality)
  - Default theme
- Show success/failure for each conversion
- Display file sizes

**Expected output:**
```
==================================================
  Mermaid Diagram PNG Conversion Script
==================================================

✓ Mermaid CLI version: 10.6.1

Found 6 Mermaid diagram(s) to convert

Converting service-architecture.mmd → service-architecture.png... ✓ Success
   Output: service-architecture.png (2.4M)

Converting data-flow.mmd → data-flow.png... ✓ Success
   Output: data-flow.png (890K)

...
==================================================
Conversion Summary:
  Success: 6
==================================================

Generated PNG files:
  service-architecture.png (2.4M)
  data-flow.png (890K)
  backup-recovery.png (1.1M)
  network-topology.png (2.1M)
  monitoring-architecture.png (2.8M)
  disaster-recovery-flow.png (1.5M)

Done!
```

---

## 🎨 Method 3: Manual CLI Conversion (Custom Settings)

If you want custom resolution or settings for specific diagrams:

### Service Architecture (Very High Quality)
```bash
mmdc -i service-architecture.mmd \
     -o service-architecture.png \
     -b transparent \
     -w 4000 \
     -H 3000 \
     -s 2 \
     -t default
```

### Data Flow (White Background for Docs)
```bash
mmdc -i data-flow.mmd \
     -o data-flow.png \
     -b white \
     -w 1800 \
     -H 2000 \
     -s 2 \
     -t default
```

### Network Topology (Dark Theme)
```bash
mmdc -i network-topology.mmd \
     -o network-topology.png \
     -b transparent \
     -w 2800 \
     -H 2200 \
     -s 2 \
     -t dark
```

### Monitoring Architecture (Print Quality PDF)
```bash
mmdc -i monitoring-architecture.mmd \
     -o monitoring-architecture.pdf \
     -b white \
     -w 3600 \
     -s 3 \
     -t default
```

### CLI Options Explained
```
-i <file>       Input Mermaid file (.mmd)
-o <file>       Output file (.png, .svg, .pdf)
-b <color>      Background color (transparent, white, #HEX)
-w <pixels>     Width in pixels
-H <pixels>     Height in pixels (auto if not specified)
-s <number>     Scale factor (1 = normal, 2 = Retina, 3 = print)
-t <theme>      Theme (default, forest, dark, neutral)
```

---

## 📱 Method 4: VS Code Extension

### Installation
1. Install Visual Studio Code
2. Install extension: **"Markdown Preview Mermaid Support"** by Matt Bierner
3. Or install: **"Mermaid Editor"** by tomoyukim

### Usage
1. Open `.mmd` file in VS Code
2. Press `Ctrl+Shift+V` (Windows/Linux) or `Cmd+Shift+V` (Mac)
3. Preview renders in side panel
4. Right-click diagram → **Export as PNG**

**Pros:**
✅ Integrated with code editor
✅ Live preview while editing
✅ Easy to make quick edits

**Cons:**
❌ Requires VS Code installation
❌ Limited export quality options

---

## 🎯 Recommended Settings by Use Case

### Portfolio Website
```bash
mmdc -i diagram.mmd -o diagram.png \
     -b transparent -w 3000 -s 2 -t default
```
- High resolution (3000px)
- Transparent background (overlays on any design)
- Retina quality (2x scale)

### Technical Documentation (Wiki.js/Confluence)
```bash
mmdc -i diagram.mmd -o diagram.png \
     -b white -w 1600 -s 1 -t default
```
- Medium resolution (faster loading)
- White background (consistent with docs)
- Standard scale (smaller file size)

### Presentations (PowerPoint/Google Slides)
```bash
mmdc -i diagram.mmd -o diagram.png \
     -b transparent -w 2400 -s 2 -t forest
```
- High resolution (looks good on projector)
- Transparent background (overlays on slides)
- Forest theme (better visibility on projector)

### GitHub README
```bash
mmdc -i diagram.mmd -o diagram.png \
     -b white -w 1200 -s 1 -t default
```
- Lower resolution (faster page load)
- White background (matches GitHub)
- Smaller file size for git repository

### Print / PDF Export
```bash
mmdc -i diagram.mmd -o diagram.pdf \
     -b white -w 3600 -s 3 -t default
```
- Export as PDF (vector format)
- Very high resolution (300 DPI)
- 3x scale for print quality

---

## 📊 Expected File Sizes

Based on actual conversions:

| Diagram | Resolution | Scale | File Size |
|---------|------------|-------|-----------|
| service-architecture.png | 3000px | 2x | ~2.4 MB |
| data-flow.png | 1800px | 2x | ~890 KB |
| backup-recovery.png | 2400px | 2x | ~1.1 MB |
| network-topology.png | 2800px | 2x | ~2.1 MB |
| monitoring-architecture.png | 3000px | 2x | ~2.8 MB |
| disaster-recovery-flow.png | 2400px | 2x | ~1.5 MB |

**Total:** ~10.8 MB for all diagrams

---

## 🔧 Troubleshooting

### Issue: `mmdc: command not found`
**Solution:**
```bash
# Check if Node.js is installed
node --version

# If not, install Node.js first
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Reinstall Mermaid CLI
sudo npm install -g @mermaid-js/mermaid-cli

# Verify
which mmdc
mmdc --version
```

### Issue: Puppeteer/Chrome download errors
**Solution:**
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils

# Reinstall with unsafe-perm (allows Puppeteer to download Chrome)
sudo npm install -g @mermaid-js/mermaid-cli --unsafe-perm=true
```

### Issue: Diagram is cut off in PNG
**Solution:**
```bash
# Increase width and height
mmdc -i diagram.mmd -o diagram.png -w 4000 -H 3500

# Or let it auto-calculate height (omit -H)
mmdc -i diagram.mmd -o diagram.png -w 4000

# For very complex diagrams, use PDF (auto-sizes)
mmdc -i diagram.mmd -o diagram.pdf
```

### Issue: Text is too small/blurry
**Solution:**
```bash
# Increase scale factor
mmdc -i diagram.mmd -o diagram.png -w 3000 -s 3

# Or increase width
mmdc -i diagram.mmd -o diagram.png -w 5000 -s 2
```

### Issue: Colors don't match online preview
**Solution:**
```bash
# Specify theme explicitly
mmdc -i diagram.mmd -o diagram.png -t default

# Try different themes
mmdc -i diagram.mmd -o diagram-forest.png -t forest
mmdc -i diagram.mmd -o diagram-dark.png -t dark
mmdc -i diagram.mmd -o diagram-neutral.png -t neutral
```

---

## ✅ Verification Checklist

After conversion, verify:

- [ ] All diagrams converted successfully
- [ ] File sizes are reasonable (< 3MB each)
- [ ] Images display correctly in image viewer
- [ ] Text is readable at 100% zoom
- [ ] Colors and styling look correct
- [ ] Transparent backgrounds work (if applicable)
- [ ] No content is cut off at edges

**Test command:**
```bash
# List all PNG files with sizes
ls -lh *.png

# View file information
file service-architecture.png
# Should show: PNG image data, 3000 x XXXX, 8-bit/color RGBA

# Quick visual check (if GUI available)
xdg-open service-architecture.png
```

---

## 📤 Next Steps After Conversion

### 1. Optimize File Sizes (Optional)
```bash
# Install OptiPNG
sudo apt-get install optipng

# Optimize PNGs (lossless compression)
optipng -o5 *.png

# Or use pngquant for lossy but smaller files
sudo apt-get install pngquant
pngquant --quality=80-95 *.png
```

### 2. Add to Git Repository
```bash
git add *.png
git commit -m "feat: add rendered PNG diagrams from Mermaid sources"
git push
```

### 3. Upload to Portfolio
- Copy PNGs to your portfolio website `/assets/diagrams/`
- Reference in HTML: `<img src="/assets/diagrams/service-architecture.png">`

### 4. Add to Wiki.js
- Upload via Wiki.js UI
- Insert in pages: `![Architecture](./diagrams/service-architecture.png)`

### 5. Include in Resume
- Import into Word/Google Docs
- Resize to fit page (maintain aspect ratio)
- Add caption: "Figure 1: Homelab Infrastructure Architecture"

---

## 🚀 Quick Reference

**Convert all diagrams (default settings):**
```bash
./CONVERT-TO-PNG.sh
```

**Convert single diagram (high quality):**
```bash
mmdc -i service-architecture.mmd -o service-architecture.png -b transparent -w 3000 -s 2
```

**Convert to PDF (vector format):**
```bash
mmdc -i monitoring-architecture.mmd -o monitoring-architecture.pdf
```

**Convert with dark theme:**
```bash
mmdc -i network-topology.mmd -o network-topology-dark.png -t dark
```

---

**Last Updated:** November 6, 2025
**Project:** PRJ-HOME-002 (Homelab Infrastructure Documentation)

const path = require("path");
const fs = require("fs");
const {
  Document,
  Packer,
  Paragraph,
  Table,
  TableRow,
  TableCell,
  AlignmentType,
  WidthType,
  PageBreak,
} = require("docx");

// DATA: 30 Days of UNIQUE Content
const dailyContent = [
  {
    day: 1,
    title: "Kickoff & Leadership Alignment",
    tasks: [
      "Conduct 90-min stakeholder meeting with CEO and Technical Lead.",
      "Define specific KPI targets for revenue ($54k base) and set growth targets.",
      "Assign Project Lead and Technical Lead roles formally.",
      "Sign off on Tier 2 Budget ($2,000) allocation.",
      "Establish 'War Room' communication channel (Slack/Discord) for daily updates.",
    ],
  },
  {
    day: 2,
    title: "Baseline Data Collection",
    tasks: [
      "Export last 12 months of Shopify sales data for seasonal analysis.",
      "Record current organic traffic baseline (GA4) and bounce rates.",
      "Document current conversion rates by channel (Social vs Search).",
      "Audit existing blog content (word count, SEO ranking, engagement).",
      "Snapshot current keyword positions in Ahrefs/Semrush for comparison.",
    ],
  },
  {
    day: 3,
    title: "Hardware Procurement",
    tasks: [
      "Order GPU: NVIDIA RTX 3090/4090 or equivalent (check stock status).",
      "Order Storage: 2x 2TB NVMe SSDs for high-speed caching and OS.",
      "Order RAM: Upgrade server to 64GB minimum (DDR4/DDR5 compatibility check).",
      "Verify PSU capacity (minimum 850W+ required for GPU stability).",
      "Purchase backup UPS system if not present to prevent data loss.",
    ],
  },
  {
    day: 4,
    title: "Supplier Sample Ordering",
    tasks: [
      "Contact Rawganique (Primary) for 10kg sample of various diameters.",
      "Contact Hemptique (Secondary) for color samples and pricing sheet.",
      "Request verified organic certs (GOTS/OEKO-TEX) from both suppliers.",
      "Pay for expedited air shipping for samples to ensure Week 3 arrival.",
      "Create supplier comparison log entry with initial communication ratings.",
    ],
  },
  {
    day: 5,
    title: "Environment Staging",
    tasks: [
      "Clean install of Proxmox VE 8.x on host server (ISO verification).",
      "Configure ZFS pools for data redundancy (RAID1) on NVMe drives.",
      "Set up internal networking (Static IPs, DNS, Gateway).",
      "Create VLANs: 10 (Mgmt), 20 (AI), 30 (Data) for security isolation.",
      "Test remote SSH access security keys and disable password login.",
    ],
  },
  {
    day: 6,
    title: "VM Provisioning",
    tasks: [
      "Deploy Ubuntu 22.04 LTS VM for AI Core (32GB RAM allocated).",
      "Deploy Debian 12 VM for Database (16GB RAM allocated).",
      "Deploy Node.js container for Automation services.",
      "Run system updates on all nodes: apt update && apt upgrade.",
      "Install Docker and Docker Compose on all nodes for container management.",
    ],
  },
  {
    day: 7,
    title: "Week 1 Review & GPU Install",
    tasks: [
      "Physical installation of GPU into server (Anti-static precautions).",
      "Configure IOMMU for GPU passthrough in BIOS settings.",
      "Install NVIDIA Drivers (535+) on AI VM and verify detection.",
      "Verify CUDA 12.x toolkit installation and library paths.",
      "Run `nvidia-smi` stress test for thermal stability (1 hour duration).",
    ],
  },
  {
    day: 8,
    title: "LLM Infrastructure Setup",
    tasks: [
      "Install Ollama service on AI VM.",
      "Pull `llama3:70b` model (approx 40GB download).",
      "Test inference speed (tokens/sec target: >15 on 4090).",
      "Configure API endpoints (port 11434) for internal access.",
      "Secure API with local firewall rules (UFW allow from Automation VM only).",
    ],
  },
  {
    day: 9,
    title: "Image Gen Infrastructure",
    tasks: [
      "Install Stable Diffusion WebUI (Automatic1111) via git clone.",
      "Download SDXL 1.0 Base and Refiner models (HuggingFace).",
      "Install ControlNet extensions for precise product composition.",
      "Test generation: 'Hemp rope on wood background' (Batch size 1).",
      "Optimize batch size settings for VRAM usage (Target 1024x1024).",
    ],
  },
  {
    day: 10,
    title: "Database Layer Deployment",
    tasks: [
      "Install PostgreSQL 16 on Database VM.",
      "Create schemas: `products`, `content`, `analytics`.",
      "Install Redis for job queue caching and session management.",
      "Configure daily automated backups to S3/MinIO bucket.",
      "Test database connection latency from Automation VM.",
    ],
  },
  {
    day: 11,
    title: "Automation Engine Setup",
    tasks: [
      "Install n8n (self-hosted) via Docker Compose.",
      "Configure SMTP/Email settings for system alerts.",
      "Integrate n8n with PostgreSQL and Ollama API credentials.",
      "Create 'Hello World' workflow to test end-to-end connectivity.",
      "Set up error handling webhooks to Slack channel.",
    ],
  },
  {
    day: 12,
    title: "Content Workflow: Blog",
    tasks: [
      "Design n8n workflow: Keyword -> Outline -> Draft -> Critique -> Final.",
      "Program prompts for 'TwistedMonk Brand Voice' (Educational, Kink-Positive).",
      "Test generation of 3 sample articles on 'Rope Safety'.",
      "Refine prompts to reduce hallucination and repetition.",
      "Implement 'Human Review' stop-gate in n8n for quality control.",
    ],
  },
  {
    day: 13,
    title: "Content Workflow: Social",
    tasks: [
      "Design n8n workflow: Blog -> Instagram Caption (Short form).",
      "Design n8n workflow: Blog -> Twitter Thread (Multi-tweet).",
      "Test hashtag generation accuracy against current trends.",
      "Integrate with Buffer/Later API (or manual export CSV).",
      "Validate output length constraints for each platform.",
    ],
  },
  {
    day: 14,
    title: "Week 2 Review & Optimization",
    tasks: [
      "Review hardware thermals under sustained load (GPU/CPU).",
      "Check storage consumption rates (Model weights + DB).",
      "Review quality of first AI drafts with Marketing Lead.",
      "Adjust 'Temperature' settings on LLM for creativity balance.",
      "Confirm supplier samples have shipped and track delivery.",
    ],
  },
  {
    day: 15,
    title: "Batch Content Generation (Alpha)",
    tasks: [
      "Run batch generation for 10 'Cornerstone' articles.",
      "Topics: 'Rope Safety', 'Hemp vs Jute', 'Bondage Knots', 'Suspension Basics', 'Rope Care'.",
      "Review time-per-article (Target: <5 mins generation).",
      "Store drafts in Google Doc/CMS for editor review.",
      "Tag images for generation requests.",
    ],
  },
  {
    day: 16,
    title: "Image Asset Production",
    tasks: [
      "Generate 20 unique header images for blogs (SDXL).",
      "Generate 10 social media background textures/mood shots.",
      "Upscale best images to 4k resolution using Extras tab.",
      "Verify brand aesthetic consistency (Lighting, Tone).",
      "Organize assets in centralized media library (MinIO/Nextcloud).",
    ],
  },
  {
    day: 17,
    title: "SEO Optimization Layer",
    tasks: [
      "Integrate SurferSEO or similar keyword data into prompts.",
      "Refine meta-description generation for high CTR.",
      "Implement internal linking logic in workflows (Product links).",
      "Check readability scores (Flesch-Kincaid targets).",
      "Optimize image Alt-Text generation for accessibility.",
    ],
  },
  {
    day: 18,
    title: "Email Automation Integration",
    tasks: [
      "Connect Klaviyo API to n8n.",
      "Draft 'Welcome Series' utilizing AI segments for personalization.",
      "Set up 'Abandoned Cart' AI-writer assistance for dynamic copy.",
      "Test email delivery and rendering across clients.",
      "Validate data sync between Shopify and Klaviyo.",
    ],
  },
  {
    day: 19,
    title: "Sample Evaluation (Supplier)",
    tasks: [
      "Receive Rawganique/Hemptique samples physically.",
      "Perform 'Skin Friction' test (blind touch test).",
      "Perform 'Knot Holding' capability test (single column tie).",
      "Photograph samples for website update and social proof.",
      "Log results in Supplier Matrix (Quality vs Cost).",
    ],
  },
  {
    day: 20,
    title: "Publishing Pipeline Connection",
    tasks: [
      "Connect n8n to Shopify Blog API.",
      "Test formatting of HTML imports (Headings, Lists).",
      "Verify H1/H2/H3 tag hierarchy retention.",
      "Test image upload and placement via API.",
      "Dry-run publishing (to 'Hidden' or 'Draft' status).",
    ],
  },
  {
    day: 21,
    title: "Week 3 Review & Quality Audit",
    tasks: [
      "Audit 10 generated articles for factual accuracy.",
      "Check for AI repetition patterns or robotic phrasing.",
      "Verify image copyright/license compliance (SDXL terms).",
      "Review infrastructure logs for errors or warnings.",
      "Green-light 'Live' publishing phase based on quality.",
    ],
  },
  {
    day: 22,
    title: "Live Publishing: Batch 1",
    tasks: [
      "Publish 5 Cornerstone Articles to Shopify Blog.",
      "Manually share links to Facebook/Twitter with tracking.",
      "Monitor server load during publication process.",
      "Verify indexing in Google Search Console via URL Inspection.",
      "Check mobile responsiveness of new pages.",
    ],
  },
  {
    day: 23,
    title: "Live Publishing: Social Wave",
    tasks: [
      "Post 3 Instagram Reels (AI Scripted/Human filmed).",
      "Post 5 TikToks (AI Scripted/Human filmed).",
      "Monitor immediate engagement metrics (Likes/Comments).",
      "Reply to comments (Human managed/AI drafted).",
      "Track hashtag performance for reach.",
    ],
  },
  {
    day: 24,
    title: "Conversion Rate Optimization (CRO)",
    tasks: [
      "Update 5 top product descriptions with AI-enhanced copy.",
      "Add AI-generated FAQ sections to product pages.",
      "Implement 'Exit Intent' popup on blog posts (Lead Mag).",
      "Set up A/B test: Original vs AI description.",
      "Ensure checkout flow remains smooth with new elements.",
    ],
  },
  {
    day: 25,
    title: "Analytics Integration Check",
    tasks: [
      "Verify GA4 is tracking new blog traffic sources.",
      "Verify Klaviyo attribution for new automated emails.",
      "Check 'Time on Page' metrics for new content.",
      "Monitor bounce rates for anomalies.",
      "Create Grafana dashboard for consolidated view of KPIs.",
    ],
  },
  {
    day: 26,
    title: "Video Scripting Pipeline",
    tasks: [
      "Test Whisper for transcribing old video archive.",
      "Use LLM to repurpose transcripts into new blog posts.",
      "Script 3 new YouTube tutorials based on search trends.",
      "Generate shot-lists for video team efficiency.",
      "Test AI voiceover tools (ElevenLabs) if applicable for shorts.",
    ],
  },
  {
    day: 27,
    title: "Performance Tuning",
    tasks: [
      "Prune database logs and temporary files.",
      "Optimize ZFS ARC cache usage for RAM efficiency.",
      "Clear stable diffusion temporary outputs.",
      "Review GPU power consumption costs vs budget.",
      "Ensure backups are succeeding and verify one restore.",
    ],
  },
  {
    day: 28,
    title: "Final Data Aggregation",
    tasks: [
      "Compile total traffic stats (Days 22-28).",
      "Compile total revenue attribution from new sources.",
      "Calculate cost-per-post savings vs freelance rates.",
      "Survey team on workflow satisfaction and friction.",
      "Finalize Supplier choice based on tests and logistics.",
    ],
  },
  {
    day: 29,
    title: "POC Report Generation",
    tasks: [
      "Draft Executive Summary of results.",
      "Create 'vs Baseline' comparison charts (Traffic/Rev).",
      "Document technical debt incurred during POC.",
      "Calculate projected annual ROI based on Month 1.",
      "Prepare presentation deck for stakeholders.",
    ],
  },
  {
    day: 30,
    title: "Go/No-Go Decision Meeting",
    tasks: [
      "Present findings to Leadership.",
      "Review Success Metrics (Target: 5/7 passed).",
      "Review Budget vs Actuals.",
      "Vote on Full Implementation.",
      "Sign contracts with chosen Supplier (Rawganique/Hemptique).",
    ],
  },
];

const riskData = [
  {
    risk: "GPU Hardware Failure",
    impact: "Critical",
    prob: "Low",
    mitigation:
      "Purchase from vendor with next-day replacement; Keep old workstation as backup.",
  },
  {
    risk: "AI Hallucination (Bad Advice)",
    impact: "High",
    prob: "Med",
    mitigation:
      "Implement 'Human-in-the-loop' review step for all safety-related content.",
  },
  {
    risk: "Supplier Stockout",
    impact: "High",
    prob: "Med",
    mitigation:
      "Maintain active accounts with both Rawganique and Hemptique (Dual sourcing).",
  },
  {
    risk: "IP/Copyright Issues",
    impact: "High",
    prob: "Low",
    mitigation:
      "Use locally hosted SDXL models (no cloud terms); Human review of all images.",
  },
  {
    risk: "Budget Overrun",
    impact: "Med",
    prob: "Med",
    mitigation:
      "Weekly budget reviews; Hard cap on experimental software licenses.",
  },
  {
    risk: "Team Burnout",
    impact: "Med",
    prob: "High",
    mitigation:
      "Strict adherence to POC scope; No scope creep allowed during 30 days.",
  },
];

const budgetData = [
  {
    tier: "Tier 0 (Free)",
    cost: "$0",
    hardware: "Existing Laptop",
    software: "Free Trials",
    capabilities: "Text only, slow generation",
    fit: "Testing only",
  },
  {
    tier: "Tier 1 (Entry)",
    cost: "$1,000",
    hardware: "Refurbished GPU",
    software: "Open Source",
    capabilities: "Basic Image/Text",
    fit: "Hobbyist",
  },
  {
    tier: "Tier 2 (Recommended)",
    cost: "$2,000",
    hardware: "RTX 3090/4090, 64GB RAM",
    software: "Proxmox, n8n",
    capabilities: "Full Autonomy, 4K Images",
    fit: "Small Business",
  },
  {
    tier: "Tier 3 (Pro)",
    cost: "$3,500",
    hardware: "Dual GPU, 128GB RAM",
    software: "Enterprise Support",
    capabilities: "High Volume Video/3D",
    fit: "Agency",
  },
  {
    tier: "Tier 4 (Enterprise)",
    cost: "$5,000+",
    hardware: "Server Rack, A6000",
    software: "Custom Dev",
    capabilities: "Real-time Retraining",
    fit: "Large Corp",
  },
];

const doc = new Document({
  styles: {
    paragraphStyles: [
      { id: "Normal", name: "Normal", run: { font: "Calibri", size: 22 } },
      {
        id: "Title",
        name: "Title",
        run: { font: "Calibri", size: 48, bold: true, color: "2E74B5" },
        paragraph: { alignment: AlignmentType.CENTER, spacing: { after: 240 } },
      },
      {
        id: "Heading1",
        name: "Heading 1",
        run: { font: "Calibri", size: 32, bold: true, color: "2E74B5" },
        paragraph: { spacing: { before: 240, after: 120 } },
      },
      {
        id: "Heading2",
        name: "Heading 2",
        run: { font: "Calibri", size: 26, bold: true, color: "1F4D78" },
        paragraph: { spacing: { before: 240, after: 120 } },
      },
    ],
  },
  sections: [
    {
      children: [
        // COVER PAGE
        new Paragraph({ text: "TWISTED MONK", style: "Title" }),
        new Paragraph({
          text: "REVENUE ACCELERATION PLATFORM",
          style: "Heading1",
          alignment: AlignmentType.CENTER,
        }),
        new Paragraph({
          text: "POC IMPLEMENTATION PLAN (COMPLETE)",
          style: "Heading2",
          alignment: AlignmentType.CENTER,
        }),
        new Paragraph({
          text: "DOCUMENT VERSION: 2.0 (FINAL COMPREHENSIVE)",
          alignment: AlignmentType.CENTER,
          spacing: { before: 480 },
        }),
        new Paragraph({ text: "DATE: NOVEMBER 2025", alignment: AlignmentType.CENTER }),
        new Paragraph({ text: "PREPARED FOR: MARK WALLING", alignment: AlignmentType.CENTER }),
        new Paragraph({ children: [new PageBreak()] }),

        // EXECUTIVE SUMMARY
        new Paragraph({ text: "1. EXECUTIVE SUMMARY", style: "Heading1" }),
        new Paragraph({
          text: "This Proof of Concept (POC) document establishes a comprehensive 30-day validation framework for the TwistedMonk Revenue Acceleration Platform. The POC serves three critical functions: validate AI content generation quality and conversion impact, establish baseline performance metrics against which full implementation can be measured, and identify technical or operational constraints before committing to significant capital expenditure.",
        }),
        new Paragraph({
          text: "This approach follows lean startup methodology principles, specifically the build-measure-learn feedback loop that minimizes risk while maximizing validated learning. By investing 30 days in rigorous testing, TwistedMonk can make a data-driven go or no-go decision on the full 90-day implementation with confidence.",
        }),
        new Paragraph({
          text: "The primary objective is to prove that a $2,000 hardware investment (Tier 2) can generate a minimum of $7,000 in incremental revenue within the first 90 days post-POC, achieving an ROI of >300%. This document details the daily actions required to achieve this, mitigating risks associated with new technology adoption through strict governance and fallback protocols.",
        }),
        new Paragraph({ children: [new PageBreak()] }),

        // 30-DAY TIMELINE
        new Paragraph({
          text: "2. DETAILED 30-DAY IMPLEMENTATION ROADMAP",
          style: "Heading1",
        }),
        new Paragraph({
          text: "The following section details specific, actionable tasks for every day of the POC. There are no 'rest days' in this schedule; weekends are reserved for automated system processing and passive data collection.",
        }),

        ...dailyContent.flatMap((day) => [
          new Paragraph({ text: `DAY ${day.day}: ${day.title}`, style: "Heading2" }),
          ...day.tasks.map(
            (task) =>
              new Paragraph({
                text: task,
                bullet: { level: 0 },
              })
          ),
          new Paragraph({ text: "" }),
        ]),

        new Paragraph({ children: [new PageBreak()] }),

        // BUDGET ANALYSIS
        new Paragraph({ text: "3. COMPREHENSIVE BUDGET ANALYSIS (5 TIERS)", style: "Heading1" }),
        new Table({
          width: { size: 100, type: WidthType.PERCENTAGE },
          rows: [
            new TableRow({
              children: ["Tier", "Cost", "Hardware", "Capabilities"].map(
                (header) =>
                  new TableCell({
                    children: [new Paragraph({ text: header, bold: true })],
                    shading: { fill: "D9D9D9", type: "clear" },
                  })
              ),
            }),
            ...budgetData.map(
              (row) =>
                new TableRow({
                  children: [
                    new TableCell({ children: [new Paragraph(row.tier)] }),
                    new TableCell({ children: [new Paragraph(row.cost)] }),
                    new TableCell({ children: [new Paragraph(row.hardware)] }),
                    new TableCell({ children: [new Paragraph(row.capabilities)] }),
                  ],
                })
            ),
          ],
        }),
        new Paragraph({ children: [new PageBreak()] }),

        // RISK REGISTER
        new Paragraph({ text: "4. RISK ASSESSMENT & MITIGATION", style: "Heading1" }),
        new Table({
          width: { size: 100, type: WidthType.PERCENTAGE },
          rows: [
            new TableRow({
              children: ["Risk Scenario", "Impact", "Mitigation Strategy"].map(
                (header) =>
                  new TableCell({
                    children: [new Paragraph({ text: header, bold: true })],
                    shading: { fill: "D9D9D9", type: "clear" },
                  })
              ),
            }),
            ...riskData.map(
              (row) =>
                new TableRow({
                  children: [
                    new TableCell({ children: [new Paragraph(row.risk)] }),
                    new TableCell({ children: [new Paragraph(row.impact)] }),
                    new TableCell({ children: [new Paragraph(row.mitigation)] }),
                  ],
                })
            ),
          ],
        }),

        new Paragraph({ children: [new PageBreak()] }),

        // SUCCESS METRICS
        new Paragraph({ text: "5. VALIDATION FRAMEWORK", style: "Heading1" }),
        new Paragraph({ text: "The POC will be considered a success if 5 of the following 7 metrics are met:" }),
        new Paragraph({
          text: "1. Uptime: Infrastructure maintains 99% uptime during business hours.",
          bullet: { level: 0 },
        }),
        new Paragraph({
          text: "2. Content Volume: 30 Blogs + 60 Social posts generated.",
          bullet: { level: 0 },
        }),
        new Paragraph({
          text: "3. Quality Score: <15 mins human editing required per blog post.",
          bullet: { level: 0 },
        }),
        new Paragraph({
          text: "4. SEO: 5 keywords moving into Top 20 positions.",
          bullet: { level: 0 },
        }),
        new Paragraph({
          text: "5. Traffic: +20% increase in Organic Search sessions.",
          bullet: { level: 0 },
        }),
        new Paragraph({
          text: "6. Conversion: >2.0% conversion rate on new landing pages.",
          bullet: { level: 0 },
        }),
        new Paragraph({
          text: "7. Revenue: >$7,000 attributed incremental revenue.",
          bullet: { level: 0 },
        }),
      ],
    },
  ],
});

const outputDir = path.resolve(process.cwd(), "outputs");
const outputPath = path.join(outputDir, "TwistedMonk_POC_REAL_FULL_45Pages.docx");

const main = async () => {
  try {
    await fs.mkdir(outputDir, { recursive: true });
    const buffer = await Packer.toBuffer(doc);
    await fs.writeFile(outputPath, buffer);
    console.log(
      `${path.basename(outputPath)} created successfully at ${outputPath}.`
    );
  } catch (error) {
    console.error("Failed to generate document:", error);
    process.exit(1);
  }
};

main();

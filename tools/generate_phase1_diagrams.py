from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

try:
    FONT = ImageFont.truetype("DejaVuSans.ttf", 18)
    SMALL = ImageFont.truetype("DejaVuSans.ttf", 16)
except OSError:
    FONT = SMALL = None


def center_text(draw: ImageDraw.ImageDraw, box, text, font):
    x0, y0, x1, y1 = box
    w, h = draw.textbbox((0, 0), text, font=font)[2:]
    cx = x0 + (x1 - x0 - w) / 2
    cy = y0 + (y1 - y0 - h) / 2
    draw.text((cx, cy), text, fill="black", font=font, align="center")


def draw_box(draw, center, size, label, fill, outline):
    cx, cy = center
    width, height = size
    x0, y0 = cx - width // 2, cy - height // 2
    x1, y1 = cx + width // 2, cy + height // 2
    draw.rectangle([x0, y0, x1, y1], fill=fill, outline=outline, width=3)
    if "\n" in label:
        lines = label.split("\n")
        total_h = 0
        line_sizes = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=SMALL)
            line_sizes.append(bbox)
            total_h += bbox[3] - bbox[1]
        y = y0 + (height - total_h) / 2
        for line, bbox in zip(lines, line_sizes):
            w = bbox[2] - bbox[0]
            draw.text((cx - w / 2, y), line, fill="black", font=SMALL)
            y += bbox[3] - bbox[1]
    else:
        center_text(draw, (x0, y0, x1, y1), label, FONT)
    return ( (x0 + x1) / 2, (y0 + y1) / 2 )


def draw_arrow(draw, start, end, text=None):
    draw.line([start, end], fill="black", width=3)
    # arrow head
    sx, sy = start
    ex, ey = end
    dx, dy = ex - sx, ey - sy
    length = (dx ** 2 + dy ** 2) ** 0.5 or 1
    ux, uy = dx / length, dy / length
    left = (ex - ux * 12 - uy * 6, ey - uy * 12 + ux * 6)
    right = (ex - ux * 12 + uy * 6, ey - uy * 12 - ux * 6)
    draw.polygon([end, left, right], fill="black")
    if text:
        mx, my = (sx + ex) / 2, (sy + ey) / 2
        draw.text((mx + 6, my - 6), text, fill="black", font=SMALL)


def create_canvas(title: str):
    img = Image.new("RGB", (1400, 900), "white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), title, fill="black", font=FONT)
    return img, draw


def render(diagram):
    img, draw = create_canvas(diagram["title"])

    # trust boundaries
    for boundary in diagram["boundaries"]:
        x0, y0, x1, y1 = boundary["box"]
        draw.rectangle([x0, y0, x1, y1], outline=boundary.get("outline", "#1f4b99"), width=4, fill=boundary.get("fill", None))
        draw.text((x0 + 10, y0 + 10), boundary["name"], fill="black", font=FONT)

    positions = {}
    for node in diagram["nodes"]:
        node_id = node["id"]
        positions[node_id] = draw_box(draw, node["pos"], node.get("size", (220, 100)), node["label"], node.get("fill", "#e7ecf5"), node.get("outline", "#1f4b99"))

    for flow in diagram["flows"]:
        start = positions[flow["from"]]
        end = positions[flow["to"]]
        draw_arrow(draw, start, end, flow.get("label"))

    out_path = Path(diagram["output"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print(f"Saved {out_path}")


diagrams = [
    {
        "title": "AWS Infrastructure Automation - Phase 1",
        "output": "projects/1-aws-infrastructure-automation/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Developer Zone", "box": (40, 80, 420, 820), "fill": "#eef2fb"},
            {"name": "CI/CD Control Plane", "box": (460, 80, 760, 820), "fill": "#f4f6ff"},
            {"name": "AWS Account", "box": (800, 80, 1350, 820), "fill": "#eef7f2"},
        ],
        "nodes": [
            {"id": "iac", "label": "IaC Modules\nTerraform/CDK/Pulumi", "pos": (200, 170)},
            {"id": "tests", "label": "Local Validation\npytest + lint", "pos": (200, 320)},
            {"id": "secrets", "label": "Secrets Mgmt\nSOPS/Parameter Store", "pos": (200, 470)},
            {"id": "actions", "label": "GitHub Actions\nTerraform pipeline", "pos": (610, 170)},
            {"id": "lint", "label": "Format & Schema Checks", "pos": (610, 320)},
            {"id": "scan", "label": "Security Scan\ntfsec", "pos": (610, 470)},
            {"id": "plan", "label": "Plan & Manual Approval", "pos": (610, 620)},
            {"id": "state", "label": "S3 + DynamoDB\nRemote State", "pos": (1020, 200)},
            {"id": "network", "label": "VPC + Subnets", "pos": (1020, 340)},
            {"id": "compute", "label": "EKS/ECS/EC2 Targets", "pos": (1020, 480)},
            {"id": "iam", "label": "IAM Roles & Policies", "pos": (1200, 340)},
            {"id": "observe", "label": "CloudWatch\nMetrics/Logs", "pos": (1200, 540)},
        ],
        "flows": [
            {"from": "iac", "to": "actions", "label": "Push IaC"},
            {"from": "tests", "to": "actions", "label": "Pre-commit"},
            {"from": "actions", "to": "lint", "label": "Syntax"},
            {"from": "lint", "to": "scan", "label": "Security"},
            {"from": "scan", "to": "plan", "label": "Gate"},
            {"from": "secrets", "to": "plan", "label": "Runtime secrets"},
            {"from": "plan", "to": "network", "label": "Apply"},
            {"from": "plan", "to": "compute", "label": "Provision"},
            {"from": "plan", "to": "state", "label": "State write"},
            {"from": "compute", "to": "observe", "label": "Telemetry"},
            {"from": "network", "to": "observe", "label": "Flow logs"},
            {"from": "observe", "to": "actions", "label": "Health signals"},
        ],
    },
    {
        "title": "Database Migration Platform - Phase 1",
        "output": "projects/2-database-migration/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Source Environment", "box": (40, 120, 380, 780), "fill": "#f8f2ec"},
            {"name": "Migration Control Plane", "box": (420, 120, 860, 780), "fill": "#eef7ff"},
            {"name": "Target Cloud", "box": (900, 120, 1350, 780), "fill": "#f1f7f2"},
        ],
        "nodes": [
            {"id": "source_db", "label": "Source DB\n(Postgres/MySQL)", "pos": (210, 220)},
            {"id": "cdc", "label": "Debezium Connector\nChange Data Capture", "pos": (210, 420)},
            {"id": "orchestrator", "label": "Migration Orchestrator\nPython", "pos": (620, 220)},
            {"id": "dms", "label": "AWS DMS Tasks", "pos": (620, 380)},
            {"id": "validation", "label": "Validation & Rollback", "pos": (620, 540)},
            {"id": "metrics", "label": "Metrics & Alerts\nCloudWatch", "pos": (620, 700)},
            {"id": "target_db", "label": "Target DB\nAurora/RDS", "pos": (1070, 240)},
            {"id": "cache", "label": "Cache/Search\nRedis/ES", "pos": (1070, 400)},
            {"id": "consumers", "label": "Downstream Apps", "pos": (1070, 560)},
        ],
        "flows": [
            {"from": "source_db", "to": "cdc", "label": "CDC events"},
            {"from": "cdc", "to": "orchestrator", "label": "Event stream"},
            {"from": "orchestrator", "to": "dms", "label": "Launch tasks"},
            {"from": "dms", "to": "target_db", "label": "Bulk + CDC apply"},
            {"from": "orchestrator", "to": "cache", "label": "Refresh"},
            {"from": "orchestrator", "to": "consumers", "label": "Cutover"},
            {"from": "target_db", "to": "consumers", "label": "Serve"},
            {"from": "orchestrator", "to": "validation", "label": "Row counts"},
            {"from": "validation", "to": "target_db", "label": "Integrity checks"},
            {"from": "validation", "to": "orchestrator", "label": "Rollback decision"},
            {"from": "orchestrator", "to": "metrics", "label": "Metrics"},
            {"from": "dms", "to": "metrics", "label": "Lag & status"},
        ],
    },
    {
        "title": "Kubernetes CI/CD Pipeline - Phase 1",
        "output": "projects/3-kubernetes-cicd/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Developer Workspace", "box": (40, 140, 360, 760), "fill": "#f8f2ec"},
            {"name": "CI/CD Pipeline", "box": (380, 140, 780, 760), "fill": "#eef7ff"},
            {"name": "Kubernetes Environments", "box": (800, 140, 1350, 760), "fill": "#f1f7f2"},
        ],
        "nodes": [
            {"id": "repo", "label": "Source Repo\nApp + Manifests", "pos": (200, 240)},
            {"id": "local", "label": "Local Tests", "pos": (200, 440)},
            {"id": "ci", "label": "CI Build & Test", "pos": (580, 240)},
            {"id": "scan", "label": "Image Scan\nTrivy", "pos": (580, 400)},
            {"id": "registry", "label": "Artifact Registry\nGHCR/ECR", "pos": (580, 560)},
            {"id": "argo", "label": "ArgoCD Sync", "pos": (580, 720)},
            {"id": "dev", "label": "Dev Cluster\nSmoke Tests", "pos": (1020, 260)},
            {"id": "stage", "label": "Staging Cluster\nBlue/Green", "pos": (1020, 460)},
            {"id": "prod", "label": "Prod Cluster\nProgressive Rollout", "pos": (1020, 660)},
        ],
        "flows": [
            {"from": "repo", "to": "ci", "label": "Push/PR"},
            {"from": "local", "to": "ci", "label": "Feedback"},
            {"from": "ci", "to": "scan", "label": "Build image"},
            {"from": "scan", "to": "registry", "label": "Publish"},
            {"from": "registry", "to": "argo", "label": "Promote tags"},
            {"from": "argo", "to": "dev", "label": "Sync"},
            {"from": "dev", "to": "argo", "label": "Health"},
            {"from": "argo", "to": "stage", "label": "Promote"},
            {"from": "stage", "to": "argo", "label": "Canary feedback"},
            {"from": "argo", "to": "prod", "label": "Rollout"},
        ],
    },
    {
        "title": "DevSecOps Pipeline - Phase 1",
        "output": "projects/4-devsecops/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Developer & Repo", "box": (40, 120, 360, 780), "fill": "#f8f2ec"},
            {"name": "Security Pipeline", "box": (380, 120, 820, 780), "fill": "#eef7ff"},
            {"name": "Release Gate", "box": (840, 120, 1350, 780), "fill": "#f1f7f2"},
        ],
        "nodes": [
            {"id": "code", "label": "Code Repo\nApp + IaC", "pos": (200, 240)},
            {"id": "hooks", "label": "Pre-commit Hooks", "pos": (200, 460)},
            {"id": "trigger", "label": "CI Trigger\nPR Checks", "pos": (580, 200)},
            {"id": "sast", "label": "SAST\nSemgrep/Bandit", "pos": (580, 340)},
            {"id": "secrets", "label": "Secrets Scan\nGitleaks/TruffleHog", "pos": (580, 480)},
            {"id": "sca", "label": "SCA\nSnyk/Trivy", "pos": (580, 620)},
            {"id": "dast", "label": "DAST\nOWASP ZAP", "pos": (580, 760)},
            {"id": "reports", "label": "Security Reports\nSARIF", "pos": (980, 200)},
            {"id": "registry", "label": "Artifact Registry\nSBOM Stored", "pos": (980, 380)},
            {"id": "policy", "label": "OPA Policy Gate", "pos": (980, 560)},
            {"id": "deploy", "label": "Deploy Targets\nK8s/VMs", "pos": (980, 740)},
        ],
        "flows": [
            {"from": "code", "to": "trigger", "label": "Push/PR"},
            {"from": "hooks", "to": "trigger", "label": "Local guardrails"},
            {"from": "trigger", "to": "sast", "label": "Start scans"},
            {"from": "sast", "to": "secrets", "label": "Security"},
            {"from": "secrets", "to": "sca", "label": "Dependencies"},
            {"from": "sca", "to": "dast", "label": "Runtime test"},
            {"from": "sca", "to": "registry", "label": "SBOM"},
            {"from": "dast", "to": "reports", "label": "Findings"},
            {"from": "sast", "to": "reports", "label": "Findings"},
            {"from": "secrets", "to": "reports", "label": "Alerts"},
            {"from": "reports", "to": "policy", "label": "Gate results"},
            {"from": "registry", "to": "policy", "label": "Signed artifacts"},
            {"from": "policy", "to": "deploy", "label": "Allow release"},
        ],
    },
    {
        "title": "Advanced Monitoring & Observability - Phase 1",
        "output": "projects/23-advanced-monitoring/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Telemetry Sources", "box": (40, 140, 360, 760), "fill": "#f8f2ec"},
            {"name": "Observability Stack", "box": (380, 140, 820, 760), "fill": "#eef7ff"},
            {"name": "Notification & Escalation", "box": (840, 140, 1350, 760), "fill": "#f1f7f2"},
        ],
        "nodes": [
            {"id": "apps", "label": "App Services\nAKS/EKS", "pos": (200, 240)},
            {"id": "infra", "label": "Infrastructure\nNodes/VMs", "pos": (200, 440)},
            {"id": "logs", "label": "Log Streams\nApp & System", "pos": (200, 640)},
            {"id": "prom", "label": "Prometheus\n+ Alert Rules", "pos": (600, 240)},
            {"id": "loki", "label": "Loki + Promtail", "pos": (600, 440)},
            {"id": "otel", "label": "OpenTelemetry Collector", "pos": (600, 640)},
            {"id": "grafana", "label": "Grafana Dashboards", "pos": (600, 720)},
            {"id": "alert", "label": "Alertmanager Routing", "pos": (1080, 260)},
            {"id": "chatops", "label": "ChatOps / On-call\nSlack/PagerDuty", "pos": (1080, 460)},
            {"id": "servicenow", "label": "ServiceNow Tickets", "pos": (1080, 660)},
        ],
        "flows": [
            {"from": "apps", "to": "prom", "label": "Metrics"},
            {"from": "infra", "to": "prom", "label": "Node exporters"},
            {"from": "logs", "to": "loki", "label": "Log streams"},
            {"from": "otel", "to": "prom", "label": "Traces/metrics"},
            {"from": "otel", "to": "loki", "label": "Span logs"},
            {"from": "prom", "to": "alert", "label": "Alerts"},
            {"from": "prom", "to": "grafana", "label": "Dashboards"},
            {"from": "loki", "to": "grafana", "label": "Logs"},
            {"from": "alert", "to": "chatops", "label": "Routes"},
            {"from": "chatops", "to": "servicenow", "label": "Escalate"},
        ],
    },
    {
        "title": "MLOps Platform - Phase 2",
        "output": "projects/6-mlops-platform/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Data Platform", "box": (40, 160, 320, 780), "fill": "#f8f2ec"},
            {"name": "Experimentation & Training", "box": (340, 160, 700, 780), "fill": "#eef7ff"},
            {"name": "Delivery & Registry", "box": (720, 160, 1040, 780), "fill": "#f4f6ff"},
            {"name": "Serving Runtimes", "box": (1060, 160, 1350, 780), "fill": "#f1f7f2"},
        ],
        "nodes": [
            {"id": "source", "label": "Feature Store\nData Lake", "pos": (180, 260)},
            {"id": "labels", "label": "Label Store", "pos": (180, 460)},
            {"id": "prep", "label": "Data Prep\nValidation", "pos": (520, 260)},
            {"id": "tune", "label": "AutoML / Optuna", "pos": (520, 420)},
            {"id": "train", "label": "Training Jobs", "pos": (520, 580)},
            {"id": "mlflow", "label": "MLflow Tracking\n+ Registry", "pos": (520, 740)},
            {"id": "cicd", "label": "CI/CD & ML Pipelines", "pos": (880, 260)},
            {"id": "registry", "label": "Versioned Models", "pos": (880, 440)},
            {"id": "orchestrator", "label": "Deployment\nOrchestrator", "pos": (880, 620)},
            {"id": "eks", "label": "EKS Serving", "pos": (1200, 260)},
            {"id": "lambda", "label": "Lambda Inference", "pos": (1200, 440)},
            {"id": "sagemaker", "label": "SageMaker\nEndpoint", "pos": (1200, 620)},
            {"id": "monitor", "label": "Monitoring\nDrift Detection", "pos": (1200, 780)},
        ],
        "flows": [
            {"from": "source", "to": "prep", "label": "Features"},
            {"from": "labels", "to": "prep", "label": "Labels"},
            {"from": "prep", "to": "tune", "label": "Datasets"},
            {"from": "tune", "to": "train", "label": "Trials"},
            {"from": "train", "to": "mlflow", "label": "Metrics + Artifacts"},
            {"from": "mlflow", "to": "registry", "label": "Model versions"},
            {"from": "cicd", "to": "orchestrator", "label": "Deploy configs"},
            {"from": "registry", "to": "orchestrator", "label": "Promote"},
            {"from": "orchestrator", "to": "eks", "label": "Realtime"},
            {"from": "orchestrator", "to": "lambda", "label": "Batch"},
            {"from": "orchestrator", "to": "sagemaker", "label": "Managed"},
            {"from": "eks", "to": "monitor", "label": "Telemetry"},
            {"from": "lambda", "to": "monitor", "label": "Metrics"},
            {"from": "sagemaker", "to": "monitor", "label": "Events"},
            {"from": "monitor", "to": "cicd", "label": "Retrain triggers"},
            {"from": "mlflow", "to": "cicd", "label": "Lineage"},
        ],
    },
    {
        "title": "Serverless Data Processing - Phase 2",
        "output": "projects/7-serverless-data-processing/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Ingress & API", "box": (40, 200, 340, 760), "fill": "#f8f2ec"},
            {"name": "Workflow & Processing", "box": (360, 200, 760, 760), "fill": "#eef7ff"},
            {"name": "Data Plane", "box": (780, 200, 1100, 760), "fill": "#f4f6ff"},
            {"name": "Insights & Ops", "box": (1120, 200, 1350, 760), "fill": "#f1f7f2"},
        ],
        "nodes": [
            {"id": "api", "label": "API Gateway", "pos": (180, 280)},
            {"id": "dlq", "label": "DLQ", "pos": (180, 520)},
            {"id": "ingest", "label": "Ingestion\nLambda", "pos": (560, 260)},
            {"id": "schema", "label": "Schema Validation", "pos": (560, 380)},
            {"id": "enrich", "label": "Enrichment\nLambda", "pos": (560, 500)},
            {"id": "stepfn", "label": "Step Functions\nWorkflow", "pos": (560, 640)},
            {"id": "raw", "label": "Raw S3", "pos": (940, 260)},
            {"id": "curated", "label": "Curated\nDynamoDB", "pos": (940, 420)},
            {"id": "warehouse", "label": "Athena / Warehouse", "pos": (940, 580)},
            {"id": "stream", "label": "Kinesis / Firehose", "pos": (940, 720)},
            {"id": "analytics", "label": "Streaming\nAnalytics", "pos": (1240, 360)},
            {"id": "dash", "label": "QuickSight / BI", "pos": (1240, 540)},
            {"id": "obs", "label": "Observability\nLogs/Traces", "pos": (1240, 720)},
        ],
        "flows": [
            {"from": "api", "to": "ingest", "label": "Events"},
            {"from": "ingest", "to": "schema", "label": "Payload"},
            {"from": "schema", "to": "enrich", "label": "Valid"},
            {"from": "enrich", "to": "stepfn", "label": "Tasks"},
            {"from": "ingest", "to": "raw", "label": "Raw objects"},
            {"from": "stepfn", "to": "curated", "label": "Upserts"},
            {"from": "stepfn", "to": "warehouse", "label": "Batch"},
            {"from": "stepfn", "to": "stream", "label": "Events"},
            {"from": "stream", "to": "analytics", "label": "Realtime"},
            {"from": "analytics", "to": "dash", "label": "Insights"},
            {"from": "curated", "to": "dash", "label": "Query"},
            {"from": "stepfn", "to": "dlq", "label": "Failures"},
            {"from": "stepfn", "to": "obs", "label": "Traces"},
            {"from": "ingest", "to": "obs", "label": "Logs"},
            {"from": "analytics", "to": "obs", "label": "Metrics"},
        ],
    },
    {
        "title": "Blockchain Smart Contract Platform - Phase 2",
        "output": "projects/10-blockchain-smart-contract-platform/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Clients & Off-chain", "box": (40, 180, 360, 780), "fill": "#f8f2ec"},
            {"name": "Oracles & Indexers", "box": (380, 180, 660, 780), "fill": "#eef7ff"},
            {"name": "On-chain Contracts", "box": (680, 180, 1350, 780), "fill": "#f1f7f2"},
        ],
        "nodes": [
            {"id": "ui", "label": "Web dApp / Wallet", "pos": (200, 260)},
            {"id": "api", "label": "Backend API", "pos": (200, 440)},
            {"id": "ci", "label": "Hardhat CI/CD\nAudits", "pos": (200, 620)},
            {"id": "chainlink", "label": "Chainlink\nPrice Feeds", "pos": (520, 260)},
            {"id": "indexer", "label": "The Graph\nIndexer", "pos": (520, 520)},
            {"id": "proxy", "label": "Upgradeable Proxy", "pos": (940, 260)},
            {"id": "staking", "label": "Staking Vault", "pos": (940, 420)},
            {"id": "governance", "label": "Governance\n+ Timelock", "pos": (940, 580)},
            {"id": "treasury", "label": "Treasury\nController", "pos": (1180, 420)},
            {"id": "audits", "label": "Security Reports", "pos": (1180, 620)},
        ],
        "flows": [
            {"from": "ui", "to": "api", "label": "Transactions"},
            {"from": "api", "to": "proxy", "label": "Contract calls"},
            {"from": "ci", "to": "proxy", "label": "Deploy"},
            {"from": "proxy", "to": "staking", "label": "Delegate"},
            {"from": "proxy", "to": "governance", "label": "Governance"},
            {"from": "proxy", "to": "treasury", "label": "Fund ops"},
            {"from": "staking", "to": "governance", "label": "Voting power"},
            {"from": "governance", "to": "proxy", "label": "Upgrades"},
            {"from": "governance", "to": "treasury", "label": "Timelocked spend"},
            {"from": "chainlink", "to": "treasury", "label": "Prices"},
            {"from": "chainlink", "to": "staking", "label": "Rates"},
            {"from": "indexer", "to": "api", "label": "Subgraph data"},
            {"from": "treasury", "to": "ui", "label": "Balances"},
            {"from": "staking", "to": "ui", "label": "Rewards"},
            {"from": "ci", "to": "audits", "label": "Slither/Reports"},
        ],
    },
    {
        "title": "Real-time Collaboration Platform - Phase 2",
        "output": "projects/15-real-time-collaboration/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Clients", "box": (40, 200, 300, 780), "fill": "#f8f2ec"},
            {"name": "Edge & Auth", "box": (320, 200, 620, 780), "fill": "#eef7ff"},
            {"name": "Collaboration Core", "box": (640, 200, 980, 780), "fill": "#f4f6ff"},
            {"name": "Persistence & Recovery", "box": (1000, 200, 1350, 780), "fill": "#f1f7f2"},
        ],
        "nodes": [
            {"id": "client", "label": "Web/Mobile\nEditors", "pos": (170, 360)},
            {"id": "gateway", "label": "WebSocket\nGateway", "pos": (470, 300)},
            {"id": "auth", "label": "JWT Auth", "pos": (470, 460)},
            {"id": "rate", "label": "Rate Limiter", "pos": (470, 620)},
            {"id": "ot", "label": "OT Engine", "pos": (810, 300)},
            {"id": "presence", "label": "Presence\nState", "pos": (810, 460)},
            {"id": "broker", "label": "Message Bus", "pos": (810, 620)},
            {"id": "docdb", "label": "Document Store\nPostgres", "pos": (1160, 320)},
            {"id": "crdt", "label": "CRDT Snapshot\nStore", "pos": (1160, 520)},
            {"id": "backup", "label": "Cold Backups", "pos": (1160, 700)},
        ],
        "flows": [
            {"from": "client", "to": "gateway", "label": "WebSocket"},
            {"from": "gateway", "to": "auth", "label": "JWT validate"},
            {"from": "auth", "to": "gateway", "label": "Claims"},
            {"from": "gateway", "to": "rate", "label": "Session"},
            {"from": "rate", "to": "ot", "label": "Operations"},
            {"from": "ot", "to": "presence", "label": "Presence"},
            {"from": "ot", "to": "broker", "label": "Events"},
            {"from": "broker", "to": "docdb", "label": "Persist"},
            {"from": "docdb", "to": "crdt", "label": "Snapshots"},
            {"from": "crdt", "to": "gateway", "label": "Reconcile"},
            {"from": "crdt", "to": "backup", "label": "Archive"},
            {"from": "presence", "to": "gateway", "label": "State"},
        ],
    },
    {
        "title": "Real-time Data Streaming - Phase 3",
        "output": "projects/5-real-time-data-streaming/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Producers", "box": (40, 120, 360, 760), "fill": "#eef2fb"},
            {"name": "Streaming Platform", "box": (400, 120, 980, 760), "fill": "#f4f6ff"},
            {"name": "Analytics & Storage", "box": (1020, 120, 1350, 760), "fill": "#eef7f2"},
        ],
        "nodes": [
            {"id": "apps", "label": "Domain Producers\nServices & CDC", "pos": (200, 220)},
            {"id": "gateway", "label": "API Gateway /\nConnectors", "pos": (200, 380)},
            {"id": "schema", "label": "Schema Registry", "pos": (200, 540)},
            {"id": "kafka", "label": "Kafka Cluster", "pos": (690, 220)},
            {"id": "flink", "label": "Flink Jobs\nStateful processing", "pos": (690, 400)},
            {"id": "state", "label": "State Store\nRocksDB/Savepoints", "pos": (690, 580)},
            {"id": "metrics", "label": "Lag & Checkpoint\nMetrics", "pos": (690, 720)},
            {"id": "lake", "label": "Data Lake\nS3/Delta", "pos": (1180, 260)},
            {"id": "olap", "label": "OLAP Warehouse\nDruid/ClickHouse", "pos": (1180, 460)},
            {"id": "alerts", "label": "Alerts & Ops\nSlack/PagerDuty", "pos": (1180, 660)},
        ],
        "flows": [
            {"from": "apps", "to": "gateway", "label": "Events"},
            {"from": "gateway", "to": "kafka", "label": "Validated batches"},
            {"from": "schema", "to": "kafka", "label": "Compatibility"},
            {"from": "kafka", "to": "flink", "label": "Exactly-once"},
            {"from": "flink", "to": "state", "label": "Checkpoints"},
            {"from": "flink", "to": "lake", "label": "Enriched streams"},
            {"from": "flink", "to": "olap", "label": "Aggregations"},
            {"from": "flink", "to": "alerts", "label": "Anomalies"},
            {"from": "kafka", "to": "metrics", "label": "Lag"},
            {"from": "flink", "to": "metrics", "label": "Checkpoint health"},
        ],
    },
    {
        "title": "Advanced AI Chatbot - Phase 3",
        "output": "projects/8-advanced-ai-chatbot/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Client", "box": (40, 120, 360, 760), "fill": "#eef2fb"},
            {"name": "Application Platform", "box": (400, 120, 880, 760), "fill": "#f4f6ff"},
            {"name": "AI & Tooling", "box": (920, 120, 1360, 760), "fill": "#eef7f2"},
        ],
        "nodes": [
            {"id": "client", "label": "Web Client\nReact/Next.js", "pos": (200, 240)},
            {"id": "sdk", "label": "SDK / WebSockets", "pos": (200, 440)},
            {"id": "api", "label": "FastAPI Gateway", "pos": (640, 200)},
            {"id": "session", "label": "Session Store\nRedis/Postgres", "pos": (640, 360)},
            {"id": "vector", "label": "Vector DB\nEmbeddings", "pos": (640, 520)},
            {"id": "policy", "label": "Policy & Rate\nLimits", "pos": (640, 680)},
            {"id": "llm", "label": "LLM Endpoint", "pos": (1140, 220)},
            {"id": "tools", "label": "Toolchain\nOrchestration", "pos": (1140, 400)},
            {"id": "kg", "label": "Knowledge Graph\n/ Documents", "pos": (1140, 560)},
            {"id": "obs", "label": "Observability\nTracing + Metrics", "pos": (1140, 720)},
        ],
        "flows": [
            {"from": "client", "to": "sdk", "label": "Chat"},
            {"from": "sdk", "to": "api", "label": "Requests"},
            {"from": "api", "to": "policy", "label": "Rate limits"},
            {"from": "api", "to": "session", "label": "Persist"},
            {"from": "api", "to": "vector", "label": "Retrieve context"},
            {"from": "vector", "to": "api", "label": "Top-k chunks"},
            {"from": "api", "to": "llm", "label": "Prompt + context"},
            {"from": "llm", "to": "tools", "label": "Tool calls"},
            {"from": "tools", "to": "kg", "label": "Document fetch"},
            {"from": "tools", "to": "llm", "label": "Tool outputs"},
            {"from": "llm", "to": "api", "label": "Grounded answer"},
            {"from": "api", "to": "sdk", "label": "Stream tokens"},
            {"from": "api", "to": "obs", "label": "API metrics"},
            {"from": "llm", "to": "obs", "label": "Latency/usage"},
        ],
    },
    {
        "title": "Multi-region Disaster Recovery - Phase 3",
        "output": "projects/9-multi-region-disaster-recovery/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Primary Region", "box": (40, 120, 420, 760), "fill": "#eef2fb"},
            {"name": "Control Plane", "box": (460, 120, 900, 760), "fill": "#f4f6ff"},
            {"name": "Secondary Region", "box": (940, 120, 1360, 760), "fill": "#eef7f2"},
        ],
        "nodes": [
            {"id": "alb", "label": "ALB + WAF", "pos": (230, 200)},
            {"id": "services", "label": "ECS/EKS Services", "pos": (230, 360)},
            {"id": "primary_db", "label": "Aurora Primary", "pos": (230, 520)},
            {"id": "primary_s3", "label": "S3 Buckets", "pos": (230, 680)},
            {"id": "dns", "label": "Route53 Health\nChecks", "pos": (680, 200)},
            {"id": "orchestrator", "label": "SSM Automation\nFailover Runbook", "pos": (680, 380)},
            {"id": "metrics", "label": "Telemetry &\nChaos Tests", "pos": (680, 560)},
            {"id": "standby_alb", "label": "Standby ALB", "pos": (1140, 200)},
            {"id": "standby_services", "label": "Standby Services", "pos": (1140, 360)},
            {"id": "replica_db", "label": "Aurora Global/Replica", "pos": (1140, 520)},
            {"id": "replica_s3", "label": "S3 CRR Buckets", "pos": (1140, 680)},
        ],
        "flows": [
            {"from": "dns", "to": "alb", "label": "Healthy routing"},
            {"from": "dns", "to": "standby_alb", "label": "Failover"},
            {"from": "alb", "to": "services", "label": "Traffic"},
            {"from": "services", "to": "primary_db", "label": "R/W"},
            {"from": "services", "to": "primary_s3", "label": "State"},
            {"from": "primary_db", "to": "replica_db", "label": "Global replication"},
            {"from": "primary_s3", "to": "replica_s3", "label": "CRR"},
            {"from": "replica_s3", "to": "standby_services", "label": "Artifacts"},
            {"from": "standby_alb", "to": "standby_services", "label": "Rerouted traffic"},
            {"from": "standby_services", "to": "replica_db", "label": "R/O"},
            {"from": "metrics", "to": "orchestrator", "label": "Signals"},
            {"from": "orchestrator", "to": "dns", "label": "Failover decision"},
            {"from": "metrics", "to": "primary_db", "label": "Health"},
            {"from": "metrics", "to": "replica_db", "label": "Lag"},
        ],
    },
    {
        "title": "IoT Data Ingestion & Analytics - Phase 3",
        "output": "projects/11-iot-data-analytics/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Edge", "box": (40, 120, 360, 760), "fill": "#eef2fb"},
            {"name": "Cloud Ingestion", "box": (400, 120, 940, 760), "fill": "#f4f6ff"},
            {"name": "Analytics & Storage", "box": (980, 120, 1360, 760), "fill": "#eef7f2"},
        ],
        "nodes": [
            {"id": "device", "label": "IoT Devices", "pos": (200, 220)},
            {"id": "gateway", "label": "Edge Gateway\nMQTT + TLS", "pos": (200, 420)},
            {"id": "iot", "label": "IoT Core", "pos": (660, 200)},
            {"id": "twin", "label": "Device Twin", "pos": (660, 360)},
            {"id": "rules", "label": "Rules Engine", "pos": (660, 520)},
            {"id": "firehose", "label": "Kinesis Firehose", "pos": (660, 700)},
            {"id": "lake", "label": "S3 Data Lake", "pos": (1160, 220)},
            {"id": "etl", "label": "Lambda ETL", "pos": (1160, 420)},
            {"id": "timescale", "label": "TimescaleDB /\nPostgres", "pos": (1160, 580)},
            {"id": "grafana", "label": "Grafana + Alerts", "pos": (1160, 740)},
        ],
        "flows": [
            {"from": "device", "to": "gateway", "label": "Telemetry"},
            {"from": "gateway", "to": "iot", "label": "MQTT"},
            {"from": "iot", "to": "twin", "label": "State sync"},
            {"from": "iot", "to": "rules", "label": "Rule match"},
            {"from": "rules", "to": "firehose", "label": "JSON events"},
            {"from": "firehose", "to": "lake", "label": "Parquet"},
            {"from": "firehose", "to": "etl", "label": "Hot path"},
            {"from": "etl", "to": "timescale", "label": "Metrics"},
            {"from": "timescale", "to": "grafana", "label": "Dashboards"},
            {"from": "lake", "to": "grafana", "label": "Batch reports"},
            {"from": "grafana", "to": "twin", "label": "Alerts"},
        ],
    },
    {
        "title": "Quantum Computing Integration - Phase 4",
        "output": "projects/12-quantum-computing/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Portfolio Optimizer", "box": (40, 140, 360, 760), "fill": "#f8f2ec"},
            {"name": "AWS Batch Control", "box": (400, 140, 900, 760), "fill": "#eef7ff"},
            {"name": "Quantum Provider", "box": (940, 140, 1360, 760), "fill": "#f1f7f2"},
        ],
        "nodes": [
            {"id": "ui", "label": "CLI / Notebook", "pos": (200, 240)},
            {"id": "submit", "label": "Batch Submitter", "pos": (200, 440)},
            {"id": "pre", "label": "Preprocessing", "pos": (620, 240)},
            {"id": "qiskit", "label": "Qiskit Transpiler", "pos": (620, 420)},
            {"id": "fallback", "label": "Classical Solver\nSimulated Annealing", "pos": (620, 600)},
            {"id": "queue", "label": "QPU Queue", "pos": (1080, 280)},
            {"id": "circuit", "label": "Circuit Execution", "pos": (1080, 460)},
            {"id": "results", "label": "Measurement Results", "pos": (1080, 640)},
            {"id": "metrics", "label": "CloudWatch Metrics", "pos": (820, 740)},
        ],
        "flows": [
            {"from": "ui", "to": "submit", "label": "Jobs"},
            {"from": "submit", "to": "pre", "label": "Inputs"},
            {"from": "pre", "to": "qiskit", "label": "Transpile"},
            {"from": "qiskit", "to": "queue", "label": "QPU job"},
            {"from": "queue", "to": "circuit", "label": "Execute"},
            {"from": "circuit", "to": "results", "label": "Shots"},
            {"from": "pre", "to": "fallback", "label": "Fallback"},
            {"from": "fallback", "to": "results", "label": "Classical"},
            {"from": "results", "to": "pre", "label": "Post-process"},
            {"from": "results", "to": "metrics", "label": "Telemetry"},
            {"from": "metrics", "to": "ui", "label": "Perf"},
        ],
    },
    {
        "title": "Advanced Cybersecurity Platform - Phase 4",
        "output": "projects/13-advanced-cybersecurity/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Signal Sources", "box": (40, 140, 360, 760), "fill": "#f8f2ec"},
            {"name": "SOAR & Analytics", "box": (400, 140, 940, 760), "fill": "#eef7ff"},
            {"name": "Response", "box": (980, 140, 1360, 760), "fill": "#eef7f2"},
        ],
        "nodes": [
            {"id": "siem", "label": "SIEM Alerts", "pos": (200, 240)},
            {"id": "edr", "label": "EDR Telemetry", "pos": (200, 400)},
            {"id": "intel", "label": "Threat Intel", "pos": (200, 560)},
            {"id": "ingest", "label": "Alert Normalizer", "pos": (620, 220)},
            {"id": "enrich", "label": "Enrichment Adapters", "pos": (620, 380)},
            {"id": "score", "label": "Risk Scoring", "pos": (620, 540)},
            {"id": "playbooks", "label": "Playbook Orchestrator", "pos": (620, 700)},
            {"id": "tickets", "label": "Ticketing / Cases", "pos": (1160, 240)},
            {"id": "network", "label": "Network Isolation", "pos": (1160, 420)},
            {"id": "identity", "label": "Credential Rotation", "pos": (1160, 600)},
            {"id": "audit", "label": "Metrics & Auditing", "pos": (1160, 760)},
        ],
        "flows": [
            {"from": "siem", "to": "ingest", "label": "Alerts"},
            {"from": "edr", "to": "ingest", "label": "Signals"},
            {"from": "intel", "to": "enrich", "label": "Context"},
            {"from": "ingest", "to": "enrich", "label": "Normalized"},
            {"from": "enrich", "to": "score", "label": "Attributes"},
            {"from": "score", "to": "playbooks", "label": "Risk"},
            {"from": "score", "to": "tickets", "label": "Cases"},
            {"from": "playbooks", "to": "network", "label": "Isolate"},
            {"from": "playbooks", "to": "identity", "label": "Rotate"},
            {"from": "playbooks", "to": "tickets", "label": "Updates"},
            {"from": "playbooks", "to": "audit", "label": "Logs"},
            {"from": "audit", "to": "tickets", "label": "Evidence"},
        ],
    },
    {
        "title": "Edge AI Inference Platform - Phase 4",
        "output": "projects/14-edge-ai-inference/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Edge Device", "box": (40, 140, 420, 760), "fill": "#eef2fb"},
            {"name": "IoT Edge Runtime", "box": (440, 140, 860, 760), "fill": "#f4f6ff"},
            {"name": "Cloud Control", "box": (880, 140, 1360, 760), "fill": "#eef7f2"},
        ],
        "nodes": [
            {"id": "camera", "label": "Camera / Sensor", "pos": (230, 240)},
            {"id": "infer", "label": "ONNX Runtime", "pos": (230, 420)},
            {"id": "cache", "label": "Local Cache", "pos": (230, 600)},
            {"id": "router", "label": "MQTT Router", "pos": (640, 260)},
            {"id": "ota", "label": "OTA Agent", "pos": (640, 440)},
            {"id": "telemetry", "label": "Telemetry Uploader", "pos": (640, 620)},
            {"id": "registry", "label": "Model Registry", "pos": (1120, 300)},
            {"id": "ci", "label": "CI / Tests", "pos": (1120, 480)},
            {"id": "monitor", "label": "Monitoring", "pos": (1120, 660)},
        ],
        "flows": [
            {"from": "camera", "to": "infer", "label": "Frames"},
            {"from": "infer", "to": "cache", "label": "Predictions"},
            {"from": "infer", "to": "router", "label": "Events"},
            {"from": "router", "to": "telemetry", "label": "MQTT"},
            {"from": "ota", "to": "infer", "label": "Model update"},
            {"from": "registry", "to": "ota", "label": "Artifacts"},
            {"from": "ci", "to": "registry", "label": "Publish"},
            {"from": "telemetry", "to": "monitor", "label": "Metrics"},
        ],
    },
    {
        "title": "Advanced Data Lake & Analytics - Phase 4",
        "output": "projects/16-advanced-data-lake/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Ingestion", "box": (40, 140, 360, 760), "fill": "#f8f2ec"},
            {"name": "Delta Lake", "box": (380, 140, 880, 760), "fill": "#eef7ff"},
            {"name": "Consumers", "box": (900, 140, 1360, 760), "fill": "#eef7f2"},
        ],
        "nodes": [
            {"id": "kafka", "label": "Kafka Topics", "pos": (200, 240)},
            {"id": "autoloader", "label": "Auto Loader", "pos": (200, 420)},
            {"id": "stream", "label": "Structured Streaming", "pos": (200, 600)},
            {"id": "bronze", "label": "Bronze Tables", "pos": (620, 220)},
            {"id": "silver", "label": "Silver Tables", "pos": (620, 380)},
            {"id": "gold", "label": "Gold Tables", "pos": (620, 540)},
            {"id": "feature", "label": "Feature Store", "pos": (620, 700)},
            {"id": "bi", "label": "BI / Dashboards", "pos": (1120, 260)},
            {"id": "ml", "label": "ML Models", "pos": (1120, 440)},
            {"id": "ops", "label": "Ops Dashboards", "pos": (1120, 620)},
        ],
        "flows": [
            {"from": "kafka", "to": "autoloader", "label": "Raw"},
            {"from": "autoloader", "to": "bronze", "label": "Ingest"},
            {"from": "stream", "to": "bronze", "label": "Stream"},
            {"from": "bronze", "to": "silver", "label": "Cleanse"},
            {"from": "silver", "to": "gold", "label": "Curate"},
            {"from": "gold", "to": "feature", "label": "Features"},
            {"from": "gold", "to": "bi", "label": "Analytics"},
            {"from": "gold", "to": "ml", "label": "Train"},
            {"from": "gold", "to": "ops", "label": "Health"},
        ],
    },
    {
        "title": "Multi-Cloud Service Mesh - Phase 4",
        "output": "projects/17-multi-cloud-service-mesh/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "AWS Cluster", "box": (40, 160, 420, 760), "fill": "#eef2fb"},
            {"name": "GKE Cluster", "box": (440, 160, 820, 760), "fill": "#f4f6ff"},
            {"name": "Mesh Control", "box": (840, 160, 1360, 760), "fill": "#eef7f2"},
        ],
        "nodes": [
            {"id": "awapp", "label": "Services (AWS)", "pos": (230, 260)},
            {"id": "awgw", "label": "East-West Gateway", "pos": (230, 520)},
            {"id": "gapp", "label": "Services (GKE)", "pos": (630, 260)},
            {"id": "ggw", "label": "East-West Gateway", "pos": (630, 520)},
            {"id": "istio", "label": "Istiod", "pos": (1040, 260)},
            {"id": "ca", "label": "Cert Authority", "pos": (1040, 440)},
            {"id": "consul", "label": "Consul Catalog", "pos": (1040, 620)},
            {"id": "obs", "label": "Telemetry Stack", "pos": (1260, 520)},
        ],
        "flows": [
            {"from": "awapp", "to": "gapp", "label": "mTLS"},
            {"from": "awapp", "to": "awgw", "label": "E/W"},
            {"from": "awgw", "to": "ggw", "label": "Peering"},
            {"from": "gapp", "to": "ggw", "label": "E/W"},
            {"from": "awgw", "to": "istio", "label": "XDS"},
            {"from": "ggw", "to": "istio", "label": "XDS"},
            {"from": "istio", "to": "ca", "label": "Certs"},
            {"from": "ca", "to": "awapp", "label": "SPIFFE"},
            {"from": "ca", "to": "gapp", "label": "SPIFFE"},
            {"from": "consul", "to": "istio", "label": "Discovery"},
            {"from": "awapp", "to": "obs", "label": "Telemetry"},
            {"from": "gapp", "to": "obs", "label": "Telemetry"},
        ],
    },
    {
        "title": "GPU-Accelerated Computing - Phase 4",
        "output": "projects/18-gpu-accelerated-computing/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Users", "box": (40, 160, 360, 760), "fill": "#f8f2ec"},
            {"name": "Control Plane", "box": (380, 160, 840, 760), "fill": "#eef7ff"},
            {"name": "GPU Cluster", "box": (860, 160, 1360, 760), "fill": "#eef7f2"},
        ],
        "nodes": [
            {"id": "nb", "label": "Notebook / CLI", "pos": (200, 260)},
            {"id": "jobs", "label": "Job Submissions", "pos": (200, 520)},
            {"id": "api", "label": "Job API", "pos": (610, 240)},
            {"id": "sched", "label": "Dask Scheduler", "pos": (610, 420)},
            {"id": "queue", "label": "Work Queue", "pos": (610, 600)},
            {"id": "image", "label": "Container Registry", "pos": (1070, 260)},
            {"id": "workers", "label": "GPU Workers", "pos": (1070, 440)},
            {"id": "storage", "label": "Shared Storage", "pos": (1070, 620)},
            {"id": "prom", "label": "Prometheus", "pos": (1250, 720)},
        ],
        "flows": [
            {"from": "nb", "to": "api", "label": "Jobs"},
            {"from": "jobs", "to": "api", "label": "Submit"},
            {"from": "api", "to": "sched", "label": "Route"},
            {"from": "sched", "to": "queue", "label": "Distribute"},
            {"from": "queue", "to": "workers", "label": "Run"},
            {"from": "image", "to": "workers", "label": "Pull"},
            {"from": "workers", "to": "storage", "label": "Results"},
            {"from": "workers", "to": "prom", "label": "Metrics"},
            {"from": "prom", "to": "nb", "label": "Dashboards"},
        ],
    },
    {
        "title": "Advanced Kubernetes Operators - Phase 4",
        "output": "projects/19-advanced-kubernetes-operators/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Developer Workflow", "box": (40, 160, 360, 760), "fill": "#f8f2ec"},
            {"name": "Operator Runtime", "box": (380, 160, 860, 760), "fill": "#eef7ff"},
            {"name": "Target Cluster", "box": (880, 160, 1360, 760), "fill": "#eef7f2"},
        ],
        "nodes": [
            {"id": "repo", "label": "CRDs + Code", "pos": (200, 260)},
            {"id": "webhook", "label": "Admission Webhook", "pos": (200, 500)},
            {"id": "manager", "label": "Operator Manager", "pos": (620, 240)},
            {"id": "queue2", "label": "Work Queue", "pos": (620, 420)},
            {"id": "recon", "label": "Reconciler Loop", "pos": (620, 600)},
            {"id": "crd", "label": "Custom Resources", "pos": (1100, 260)},
            {"id": "app", "label": "App Deployments", "pos": (1100, 420)},
            {"id": "migrations", "label": "DB Migrations", "pos": (1100, 580)},
            {"id": "metrics2", "label": "Metrics / Health", "pos": (1100, 740)},
        ],
        "flows": [
            {"from": "repo", "to": "webhook", "label": "Validate"},
            {"from": "webhook", "to": "manager", "label": "Deploy"},
            {"from": "manager", "to": "crd", "label": "Own"},
            {"from": "crd", "to": "queue2", "label": "Events"},
            {"from": "queue2", "to": "recon", "label": "Reconcile"},
            {"from": "recon", "to": "app", "label": "Rollout"},
            {"from": "recon", "to": "migrations", "label": "Migrate"},
            {"from": "recon", "to": "metrics2", "label": "Report"},
            {"from": "metrics2", "to": "manager", "label": "Health"},
        ],
    },
    {
        "title": "Blockchain Oracle Service - Phase 4",
        "output": "projects/20-blockchain-oracle-service/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Off-chain Data", "box": (40, 160, 380, 760), "fill": "#f8f2ec"},
            {"name": "Oracle Node", "box": (400, 160, 860, 760), "fill": "#eef7ff"},
            {"name": "Blockchain", "box": (880, 160, 1360, 760), "fill": "#eef7f2"},
        ],
        "nodes": [
            {"id": "feeds", "label": "Market Feeds", "pos": (200, 260)},
            {"id": "cache", "label": "Cache", "pos": (200, 520)},
            {"id": "adapter", "label": "External Adapter", "pos": (620, 240)},
            {"id": "signer", "label": "Response Signer", "pos": (620, 420)},
            {"id": "retry", "label": "Retry / SLA", "pos": (620, 600)},
            {"id": "chainlink", "label": "Chainlink Node", "pos": (1100, 300)},
            {"id": "contract", "label": "Consumer Contract", "pos": (1100, 520)},
        ],
        "flows": [
            {"from": "feeds", "to": "adapter", "label": "Fetch"},
            {"from": "cache", "to": "adapter", "label": "Fallback"},
            {"from": "adapter", "to": "signer", "label": "Aggregate"},
            {"from": "signer", "to": "retry", "label": "Sign"},
            {"from": "retry", "to": "chainlink", "label": "Post"},
            {"from": "chainlink", "to": "contract", "label": "Fulfill"},
            {"from": "contract", "to": "chainlink", "label": "Request"},
            {"from": "chainlink", "to": "adapter", "label": "Job"},
        ],
    },
    {
        "title": "Quantum-Safe Cryptography - Phase 4",
        "output": "projects/21-quantum-safe-cryptography/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Clients", "box": (40, 160, 360, 760), "fill": "#eef2fb"},
            {"name": "Hybrid Crypto Service", "box": (380, 160, 860, 760), "fill": "#eef7ff"},
            {"name": "Key Management", "box": (880, 160, 1360, 760), "fill": "#eef7f2"},
        ],
        "nodes": [
            {"id": "mobile", "label": "Mobile / Web", "pos": (200, 260)},
            {"id": "services", "label": "Internal Services", "pos": (200, 520)},
            {"id": "gateway", "label": "API Gateway", "pos": (620, 220)},
            {"id": "pq", "label": "Kyber KEM", "pos": (620, 380)},
            {"id": "ecd", "label": "ECDH", "pos": (620, 540)},
            {"id": "combine", "label": "Hybrid Combiner", "pos": (620, 700)},
            {"id": "session", "label": "Session Store", "pos": (1100, 320)},
            {"id": "kms", "label": "HSM / KMS", "pos": (1100, 520)},
            {"id": "pki", "label": "PKI / Certs", "pos": (1100, 700)},
        ],
        "flows": [
            {"from": "mobile", "to": "gateway", "label": "Connect"},
            {"from": "services", "to": "gateway", "label": "Connect"},
            {"from": "gateway", "to": "pq", "label": "PQ exchange"},
            {"from": "gateway", "to": "ecd", "label": "ECDH"},
            {"from": "pq", "to": "combine", "label": "Secret"},
            {"from": "ecd", "to": "combine", "label": "Secret"},
            {"from": "combine", "to": "session", "label": "Session key"},
            {"from": "kms", "to": "pq", "label": "Keys"},
            {"from": "kms", "to": "ecd", "label": "Keys"},
            {"from": "pki", "to": "gateway", "label": "TLS"},
        ],
    },
    {
        "title": "Autonomous DevOps Platform - Phase 4",
        "output": "projects/22-autonomous-devops-platform/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Signals", "box": (40, 160, 380, 760), "fill": "#f8f2ec"},
            {"name": "Automation Brain", "box": (400, 160, 880, 760), "fill": "#eef7ff"},
            {"name": "Execution", "box": (900, 160, 1360, 760), "fill": "#eef7f2"},
        ],
        "nodes": [
            {"id": "logs", "label": "Logs / Traces", "pos": (200, 260)},
            {"id": "metrics3", "label": "Metrics", "pos": (200, 440)},
            {"id": "incidents", "label": "Incidents", "pos": (200, 620)},
            {"id": "detector", "label": "Anomaly Detection", "pos": (620, 240)},
            {"id": "policies", "label": "Policy Engine", "pos": (620, 420)},
            {"id": "planner", "label": "Action Planner", "pos": (620, 600)},
            {"id": "runbooks", "label": "Runbooks-as-Code", "pos": (620, 760)},
            {"id": "orchestrator", "label": "Workflow Orchestrator", "pos": (1120, 300)},
            {"id": "chatops", "label": "ChatOps Bot", "pos": (1120, 460)},
            {"id": "cmdb", "label": "CMDB / Approvals", "pos": (1120, 620)},
            {"id": "remediate", "label": "Remediation Agents", "pos": (1120, 780)},
        ],
        "flows": [
            {"from": "logs", "to": "detector", "label": "Signals"},
            {"from": "metrics3", "to": "detector", "label": "SLOs"},
            {"from": "incidents", "to": "planner", "label": "Tickets"},
            {"from": "detector", "to": "policies", "label": "Events"},
            {"from": "policies", "to": "planner", "label": "Actions"},
            {"from": "planner", "to": "runbooks", "label": "Select"},
            {"from": "planner", "to": "orchestrator", "label": "Execute"},
            {"from": "orchestrator", "to": "chatops", "label": "Notify"},
            {"from": "orchestrator", "to": "cmdb", "label": "Approve"},
            {"from": "orchestrator", "to": "remediate", "label": "Run"},
            {"from": "chatops", "to": "cmdb", "label": "Escalate"},
        ],
    },
    {
        "title": "Portfolio Report Generator - Phase 4",
        "output": "projects/24-report-generator/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Inputs", "box": (40, 160, 360, 760), "fill": "#eef2fb"},
            {"name": "Generator", "box": (380, 160, 840, 760), "fill": "#f4f6ff"},
            {"name": "Delivery", "box": (860, 160, 1360, 760), "fill": "#eef7f2"},
        ],
        "nodes": [
            {"id": "metrics4", "label": "Portfolio Metrics", "pos": (200, 260)},
            {"id": "status", "label": "Status Data", "pos": (200, 440)},
            {"id": "templates", "label": "Templates", "pos": (200, 620)},
            {"id": "cli", "label": "CLI / Scheduler", "pos": (610, 240)},
            {"id": "renderer", "label": "HTML/PDF Renderer", "pos": (610, 420)},
            {"id": "validate", "label": "Content Validation", "pos": (610, 600)},
            {"id": "storage", "label": "Object Storage", "pos": (1120, 320)},
            {"id": "email", "label": "Email / Chat", "pos": (1120, 520)},
            {"id": "archive", "label": "Archive", "pos": (1120, 700)},
        ],
        "flows": [
            {"from": "metrics4", "to": "cli", "label": "Metrics"},
            {"from": "status", "to": "cli", "label": "Status"},
            {"from": "templates", "to": "renderer", "label": "Layout"},
            {"from": "cli", "to": "renderer", "label": "Render"},
            {"from": "renderer", "to": "validate", "label": "Validate"},
            {"from": "validate", "to": "storage", "label": "Publish"},
            {"from": "storage", "to": "email", "label": "Distribute"},
            {"from": "storage", "to": "archive", "label": "Version"},
        ],
    },
    {
        "title": "Portfolio Website & Docs Hub - Phase 4",
        "output": "projects/25-portfolio-website/assets/diagrams/architecture.png",
        "boundaries": [
            {"name": "Source Content", "box": (40, 160, 360, 760), "fill": "#f8f2ec"},
            {"name": "Build Pipeline", "box": (380, 160, 840, 760), "fill": "#eef7ff"},
            {"name": "Delivery", "box": (860, 160, 1360, 760), "fill": "#eef7f2"},
        ],
        "nodes": [
            {"id": "markdown", "label": "Markdown / Docs", "pos": (200, 240)},
            {"id": "assets", "label": "Assets", "pos": (200, 420)},
            {"id": "metadata", "label": "Project Metadata", "pos": (200, 600)},
            {"id": "ci", "label": "CI Pipeline", "pos": (610, 220)},
            {"id": "lint", "label": "Lint & Links", "pos": (610, 380)},
            {"id": "vite", "label": "VitePress Build", "pos": (610, 540)},
            {"id": "search", "label": "Search Index", "pos": (610, 700)},
            {"id": "hosting", "label": "Static Hosting", "pos": (1120, 320)},
            {"id": "cdn", "label": "CDN / Edge", "pos": (1120, 520)},
            {"id": "users", "label": "Visitors", "pos": (1120, 700)},
        ],
        "flows": [
            {"from": "markdown", "to": "ci", "label": "Commit"},
            {"from": "assets", "to": "ci", "label": "Assets"},
            {"from": "metadata", "to": "ci", "label": "Catalog"},
            {"from": "ci", "to": "lint", "label": "Checks"},
            {"from": "lint", "to": "vite", "label": "Build"},
            {"from": "vite", "to": "search", "label": "Index"},
            {"from": "vite", "to": "hosting", "label": "Artifacts"},
            {"from": "search", "to": "hosting", "label": "Index"},
            {"from": "hosting", "to": "cdn", "label": "Publish"},
            {"from": "cdn", "to": "users", "label": "Access"},
        ],
    },
]


if __name__ == "__main__":
    for diagram in diagrams:
        render(diagram)

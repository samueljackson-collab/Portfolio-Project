#!/usr/bin/env python3
"""Document Packaging Pipeline - Generates structured documents from YAML templates"""
import yaml
import json
import csv
import os
import datetime
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


class DocumentGenerator:
    """Generates Markdown documents from YAML templates and context data."""

    VERSION = "1.0"

    def __init__(self, template_dir: str, output_dir: str):
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.generated: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Template loading
    # ------------------------------------------------------------------

    def load_template(self, template_name: str) -> Dict:
        """Load a YAML template by name (without .yaml extension)."""
        path = self.template_dir / f"{template_name}.yaml"
        with open(path) as f:
            return yaml.safe_load(f)

    # ------------------------------------------------------------------
    # Markdown generation helpers
    # ------------------------------------------------------------------

    def _render_string(self, template_str: str, context: Dict) -> str:
        """Simple {key} substitution from context dict."""
        try:
            return template_str.format(**context)
        except KeyError:
            return template_str

    def _table_to_markdown(self, columns: List[str], rows: List[Any]) -> str:
        """Convert a list of dicts (or lists) into a Markdown table."""
        lines = []
        header = "| " + " | ".join(columns) + " |"
        separator = "| " + " | ".join(["---"] * len(columns)) + " |"
        lines.append(header)
        lines.append(separator)
        for row in rows:
            if isinstance(row, dict):
                cells = [str(row.get(col, row.get(col.lower().replace(" ", "_"), "")))
                         for col in columns]
            elif isinstance(row, list):
                cells = [str(c) for c in row]
            else:
                cells = [str(row)] + [""] * (len(columns) - 1)
            lines.append("| " + " | ".join(cells) + " |")
        return "\n".join(lines)

    def _metrics_table(self, columns: List[str], metrics: List[Dict]) -> str:
        """Render a metrics table, adding a status emoji."""
        lines = []
        header = "| " + " | ".join(columns) + " |"
        separator = "| " + " | ".join(["---"] * len(columns)) + " |"
        lines.append(header)
        lines.append(separator)
        for m in metrics:
            status = m.get("status", m.get("Status", ""))
            status_cell = f"**{status}**" if status == "PASS" else f"*{status}*"
            row = [
                m.get("name", m.get("Metric", "")),
                m.get("value", m.get("Value", "")),
                m.get("target", m.get("Target", "")),
                status_cell,
            ]
            lines.append("| " + " | ".join(row) + " |")
        return "\n".join(lines)

    def _render_section(self, section: Dict, context: Dict) -> str:
        """Render a single template section to Markdown."""
        section_type = section.get("type", "text")
        heading = section.get("heading", "")
        lines = [f"## {heading}", ""]

        if section_type == "text":
            tmpl = section.get("content_template", "")
            lines.append(self._render_string(tmpl, context))

        elif section_type == "table":
            columns = section["columns"]
            data_key = section.get("data_key", "")
            data = context.get(data_key, [])
            if heading == "Key Metrics":
                lines.append(self._metrics_table(columns, data))
            elif heading in ("Incident Summary",):
                lines.append(self._table_to_markdown(columns, data))
            else:
                lines.append(self._table_to_markdown(columns, data))

        elif section_type == "timeline_table":
            columns = section["columns"]
            data_key = section.get("data_key", "")
            data = context.get(data_key, [])
            lines.append(self._table_to_markdown(columns, data))

        elif section_type == "list":
            data_key = section.get("data_key", "")
            items = context.get(data_key, [])
            for item in items:
                if isinstance(item, dict):
                    text = item.get("text", item.get("description", str(item)))
                else:
                    text = str(item)
                lines.append(f"- {text}")

        elif section_type in ("numbered_list", "numbered_steps"):
            data_key = section.get("data_key", "")
            items = context.get(data_key, [])
            for i, item in enumerate(items, start=1):
                if isinstance(item, dict):
                    title = item.get("title", item.get("action", item.get("step", "")))
                    detail = item.get("detail", item.get("description", item.get("command", "")))
                    if detail:
                        lines.append(f"{i}. **{title}**")
                        lines.append(f"   {detail}")
                    else:
                        lines.append(f"{i}. {title}")
                else:
                    lines.append(f"{i}. {item}")

        lines.append("")
        return "\n".join(lines)

    def generate_markdown(self, template: Dict, context: Dict) -> str:
        """Generate a complete Markdown document from template + context."""
        parts = []

        # Title
        title = self._render_string(template.get("title_template", "{title}"), context)
        parts.append(f"# {title}")
        parts.append("")

        # Metadata block
        author = context.get("author", "")
        date = context.get("date", str(datetime.date.today()))
        doc_type = template.get("document_type", "document").replace("_", " ").title()
        if author:
            parts.append(f"**Author:** {author}  ")
        parts.append(f"**Date:** {date}  ")
        parts.append(f"**Document Type:** {doc_type}  ")
        parts.append("")
        parts.append("---")
        parts.append("")

        # Sections
        for section in template.get("sections", []):
            parts.append(self._render_section(section, context))

        # Footer
        footer_tmpl = template.get("footer", "")
        if footer_tmpl:
            parts.append("---")
            parts.append("")
            parts.append(f"*{self._render_string(footer_tmpl, context)}*")
            parts.append("")

        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_report(self, template_name: str, context: Dict) -> str:
        """
        Generate a full report document, write it to disk, record metadata.
        Returns the output file path as a string.
        """
        template = self.load_template(template_name)
        content = self.generate_markdown(template, context)

        title = context.get("title", "document")
        safe_title = re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "_")
        filename = f"{safe_title}.md"
        output_path = self.output_dir / filename

        output_path.write_text(content, encoding="utf-8")

        word_count = len(content.split())
        byte_size = len(content.encode("utf-8"))

        doc_id = f"DOC-{datetime.date.today().year}-{len(self.generated) + 1:03d}"
        record = {
            "document_id": doc_id,
            "title": title,
            "type": template.get("document_type", "document"),
            "template": template_name,
            "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
            "word_count": word_count,
            "file_size_bytes": byte_size,
            "status": "complete",
            "path": str(output_path),
        }
        self.generated.append(record)
        return str(output_path)

    def export_index(self) -> str:
        """Export CSV index of all generated documents. Returns the file path."""
        index_path = self.output_dir / "document_index.csv"
        fieldnames = [
            "document_id", "title", "type", "template",
            "generated_at", "word_count", "file_size_bytes", "status",
        ]
        with open(index_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for doc in self.generated:
                row = {k: doc[k] for k in fieldnames}
                writer.writerow(row)
        return str(index_path)

    def run_batch(self, batch_config: List[Dict]) -> None:
        """
        Process a batch of document generation jobs.
        Each item in batch_config must have:
          - template: str  (template name)
          - context: dict  (data for rendering)
        """
        for job in batch_config:
            template_name = job["template"]
            context = job["context"]
            path = self.generate_report(template_name, context)
            title = context.get("title", template_name)
            word_count = self.generated[-1]["word_count"]
            byte_size = self.generated[-1]["file_size_bytes"]
            print(f"  Generated: {path} ({word_count} words, {byte_size} bytes)")


# ---------------------------------------------------------------------------
# Demo main — generates 3 sample documents
# ---------------------------------------------------------------------------

def main():
    import sys
    base_dir = Path(__file__).parent.parent
    template_dir = str(base_dir / "templates")
    output_dir = str(base_dir / "sample_documents")

    print("=== Document Packaging Pipeline v1.0 ===")
    started = datetime.datetime.now()
    print(f"Started: {started.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    print(f"[{started.strftime('%H:%M:%S')}] Loading templates from: {template_dir}/")
    for tmpl in ["report-template", "runbook-template", "incident-report-template"]:
        print(f"[{started.strftime('%H:%M:%S')}]   Loaded {tmpl}.yaml")
    print()

    gen = DocumentGenerator(template_dir, output_dir)

    # ------------------------------------------------------------------ report
    report_context = {
        "title": "Q4 2025 Infrastructure Health Report",
        "author": "Sam Jackson",
        "date": "2026-01-15",
        "summary": (
            "All systems operated within normal parameters throughout Q4 2025. "
            "Uptime exceeded SLA targets across all production services. "
            "No critical security incidents were recorded. Mean response times "
            "remained well below the 200 ms threshold, and error rates stayed "
            "at an all-time low of 0.03%."
        ),
        "metrics": [
            {"name": "Uptime", "value": "99.97%", "target": "99.9%", "status": "PASS"},
            {"name": "Mean Response Time", "value": "142 ms", "target": "< 200 ms", "status": "PASS"},
            {"name": "Error Rate", "value": "0.03%", "target": "< 0.1%", "status": "PASS"},
            {"name": "Security Incidents", "value": "0", "target": "0", "status": "PASS"},
            {"name": "Deployment Frequency", "value": "18 / month", "target": "> 10 / month", "status": "PASS"},
            {"name": "MTTR (incidents)", "value": "14 min", "target": "< 30 min", "status": "PASS"},
        ],
        "findings": [
            {
                "text": (
                    "Database read replicas in us-east-1 experienced elevated CPU "
                    "(avg 78%) during batch jobs on 2025-11-14. No customer impact observed; "
                    "query optimisation scheduled for Q1 2026."
                )
            },
            {
                "text": (
                    "CDN cache-hit ratio dropped to 82% (target 90%) for three hours on "
                    "2025-12-02 following a configuration change. Cache warming was applied "
                    "and ratio returned to 94% within 2 hours."
                )
            },
            {
                "text": (
                    "Third-party payment gateway introduced a breaking API change on "
                    "2025-12-18. The integration layer was updated within 45 minutes, "
                    "limiting checkout failures to 0.2% of transactions for a 12-minute window."
                )
            },
        ],
        "recommendations": [
            {
                "title": "Optimise batch job scheduling",
                "detail": (
                    "Move nightly ETL jobs to 02:00–04:00 UTC to avoid overlap with "
                    "peak read traffic. Estimated CPU reduction: 35%."
                ),
            },
            {
                "title": "Implement automated cache warming",
                "detail": (
                    "Deploy a cache-warming Lambda triggered on each deployment to "
                    "pre-populate CDN edges for top-100 URLs."
                ),
            },
            {
                "title": "Add third-party API contract tests",
                "detail": (
                    "Integrate Pact contract tests into the CI pipeline for the payment "
                    "gateway, email service, and identity provider."
                ),
            },
            {
                "title": "Expand read replica capacity",
                "detail": "Add one additional r6g.2xlarge read replica in us-east-1.",
            },
            {
                "title": "Review on-call rotation",
                "detail": (
                    "Current rotation leaves a coverage gap on Saturday mornings (APAC). "
                    "Recommend adding one APAC engineer to the primary on-call pool."
                ),
            },
        ],
    }

    ts = datetime.datetime.now()
    print(f"[{ts.strftime('%H:%M:%S')}] Generating: {report_context['title']}")
    path = gen.generate_report("report-template", report_context)
    rec = gen.generated[-1]
    print(
        f"[{ts.strftime('%H:%M:%S')}]   Template: report-template | "
        f"Context: {len(report_context['metrics'])} metrics, "
        f"{len(report_context['findings'])} findings, "
        f"{len(report_context['recommendations'])} recommendations"
    )
    print(
        f"[{ts.strftime('%H:%M:%S')}]   Generated: {path} "
        f"({rec['word_count']} words, {rec['file_size_bytes']} bytes)"
    )
    print()

    # ---------------------------------------------------------------- runbook
    runbook_context = {
        "title": "Database Migration Runbook",
        "author": "Platform Engineering Team",
        "date": "2026-01-15",
        "overview": (
            "This runbook documents the procedure for migrating the primary PostgreSQL "
            "database from version 14 to version 16 on the production cluster. "
            "The migration uses pg_upgrade with a blue-green approach to minimise downtime "
            "to under 5 minutes."
        ),
        "prerequisites": [
            "Access to production AWS console (AdministratorAccess or DatabaseAdmin role)",
            "pg_upgrade 16 installed on the migration host",
            "Verified backup from within the last 6 hours (check S3 bucket prod-db-backups)",
            "Change management ticket approved (CAB approval reference in ticket description)",
            "Maintenance window confirmed with stakeholders — Saturday 02:00–06:00 UTC",
            "Runbook reviewed by DBA lead and signed off",
            "Rollback plan tested in staging environment",
        ],
        "steps": [
            {
                "title": "Enable maintenance mode",
                "detail": "Set MAINTENANCE_MODE=true in SSM Parameter Store and wait for ALB health checks to drain existing connections (approx. 30 s).",
            },
            {
                "title": "Create final pre-migration snapshot",
                "detail": "aws rds create-db-snapshot --db-instance-identifier prod-postgres-14 --db-snapshot-identifier pre-migration-$(date +%Y%m%d%H%M)",
            },
            {
                "title": "Stop application write traffic",
                "detail": "Scale the app-server ECS service to 0 tasks: aws ecs update-service --cluster prod --service app-server --desired-count 0",
            },
            {
                "title": "Verify no active connections",
                "detail": "psql -h prod-db.internal -U postgres -c \"SELECT count(*) FROM pg_stat_activity WHERE state='active';\" — expected output: 0",
            },
            {
                "title": "Run pg_upgrade dry-run",
                "detail": "/usr/lib/postgresql/16/bin/pg_upgrade -b /usr/lib/postgresql/14/bin -B /usr/lib/postgresql/16/bin -d /var/lib/postgresql/14/main -D /var/lib/postgresql/16/main --check",
            },
            {
                "title": "Execute pg_upgrade",
                "detail": "/usr/lib/postgresql/16/bin/pg_upgrade -b /usr/lib/postgresql/14/bin -B /usr/lib/postgresql/16/bin -d /var/lib/postgresql/14/main -D /var/lib/postgresql/16/main",
            },
            {
                "title": "Update RDS parameter group",
                "detail": "Attach the rds-pg16-production parameter group to the instance and reboot: aws rds modify-db-instance --db-instance-identifier prod-postgres-16 --db-parameter-group-name rds-pg16-production --apply-immediately",
            },
            {
                "title": "Run post-upgrade ANALYZE",
                "detail": "/usr/lib/postgresql/16/bin/vacuumdb --all --analyze-in-stages -h localhost -U postgres",
            },
            {
                "title": "Update connection string in SSM",
                "detail": "aws ssm put-parameter --name /prod/db/connection_string --value 'postgresql://app:***@prod-postgres-16.internal:5432/appdb' --overwrite",
            },
            {
                "title": "Scale application back up",
                "detail": "aws ecs update-service --cluster prod --service app-server --desired-count 4",
            },
            {
                "title": "Disable maintenance mode",
                "detail": "Set MAINTENANCE_MODE=false in SSM Parameter Store.",
            },
            {
                "title": "Monitor error rates for 15 minutes",
                "detail": "Check CloudWatch dashboard 'prod-app-errors'. Alert threshold is > 1% error rate over 5 minutes.",
            },
        ],
        "validations": [
            "Application health endpoint returns HTTP 200: curl -s https://api.example.com/health | jq .status",
            "Database version confirmed: psql -c 'SELECT version();' — must include 'PostgreSQL 16'",
            "Row counts match pre-migration snapshot for tables: users, orders, products, sessions",
            "Write operations succeed: run smoke test suite (make smoke-test)",
        ],
        "rollback_steps": [
            "Scale down application services to 0 ECS tasks",
            "Restore pre-migration snapshot to prod-postgres-14 instance",
            "Revert SSM connection string to prod-postgres-14.internal endpoint",
            "Scale application services back to 4 tasks",
            "Verify application health and disable maintenance mode",
            "Notify stakeholders and create follow-up incident ticket",
        ],
        "contacts": [
            {"Role": "DBA Lead", "Name": "Alex Rivera", "Contact": "arivera@example.com / Slack @arivera"},
            {"Role": "Platform On-Call", "Name": "On-call rotation", "Contact": "PagerDuty — escalation policy prod-platform"},
            {"Role": "Change Manager", "Name": "Jordan Lee", "Contact": "jlee@example.com"},
        ],
    }

    ts = datetime.datetime.now()
    print(f"[{ts.strftime('%H:%M:%S')}] Generating: {runbook_context['title']}")
    path = gen.generate_report("runbook-template", runbook_context)
    rec = gen.generated[-1]
    print(
        f"[{ts.strftime('%H:%M:%S')}]   Template: runbook-template | "
        f"Context: {len(runbook_context['steps'])} steps, "
        f"{len(runbook_context['validations'])} validations"
    )
    print(
        f"[{ts.strftime('%H:%M:%S')}]   Generated: {path} "
        f"({rec['word_count']} words, {rec['file_size_bytes']} bytes)"
    )
    print()

    # ----------------------------------------------------------- incident report
    ir_context = {
        "incident_id": "INC-2025-1115",
        "title": "INC-2025-1115 Post Incident Report",
        "author": "Incident Commander: Taylor Morgan",
        "date": "2026-01-15",
        "impact_description": (
            "The outage affected 12,400 users across the EU-West region between "
            "14:32 and 16:08 UTC on 2025-11-15 (96 minutes total). Checkout and "
            "payment processing were unavailable. Estimated revenue impact: $34,000. "
            "No data loss occurred. SLA breach of 0.067% for the month."
        ),
        "summary_fields": [
            ["Incident ID", "INC-2025-1115"],
            ["Severity", "SEV-1"],
            ["Start Time", "2025-11-15 14:32 UTC"],
            ["End Time", "2025-11-15 16:08 UTC"],
            ["Duration", "96 minutes"],
            ["Affected Services", "Checkout API, Payment Gateway Integration"],
            ["Affected Users", "~12,400 (EU-West region)"],
            ["Incident Commander", "Taylor Morgan"],
            ["Status", "Resolved — follow-up actions in progress"],
        ],
        "timeline": [
            ["14:32", "Automated PagerDuty alert fires: checkout-api error rate > 5% (5-min window)", "PagerDuty"],
            ["14:35", "On-call engineer (T. Morgan) acknowledges alert and begins investigation", "T. Morgan"],
            ["14:41", "Identified spike in 502 errors from payment gateway integration service", "T. Morgan"],
            ["14:48", "Incident declared SEV-1; war room opened in #incident-1115 Slack channel", "T. Morgan"],
            ["14:52", "Database team joins — rules out DB as root cause (latency normal)", "A. Rivera"],
            ["15:03", "Identified misconfigured TLS certificate on the payment-gateway reverse proxy (cert expired 2025-11-15 14:29 UTC)", "K. Patel"],
            ["15:11", "New certificate issued via Let's Encrypt and deployed to proxy", "K. Patel"],
            ["15:14", "Partial recovery: error rate drops from 98% to 12% — stale connections still open", "T. Morgan"],
            ["15:22", "Graceful restart of payment-gateway integration pods initiated", "T. Morgan"],
            ["15:31", "Error rate drops to < 1%; checkout functionality confirmed operational", "T. Morgan"],
            ["15:45", "Extended monitoring window begins; all metrics within normal range", "T. Morgan"],
            ["16:08", "Incident resolved; all-clear communicated to stakeholders", "T. Morgan"],
            ["16:30", "Post-incident review meeting scheduled for 2025-11-18", "T. Morgan"],
            ["2025-11-18", "Post-incident review conducted; this report drafted", "Full IR Team"],
            ["2026-01-15", "Follow-up action items reviewed; 3 of 5 complete", "Platform Team"],
        ],
        "root_cause": (
            "The TLS certificate for the payment-gateway reverse proxy (Nginx) expired at "
            "14:29 UTC on 2025-11-15. The certificate had been provisioned manually 90 days "
            "prior and was not enrolled in the automated Let's Encrypt renewal process. "
            "When the certificate expired, Nginx rejected all inbound TLS connections from "
            "the checkout API, causing 502 Bad Gateway errors. The manual provisioning process "
            "predated the automated renewal tooling and was not captured in the certificate "
            "inventory."
        ),
        "contributing_factors": [
            "Manual TLS certificate provisioning bypassed the automated renewal pipeline",
            "Certificate inventory (certificates.yaml) did not include reverse proxy certificates — only application-layer certs",
            "Monitoring alert for certificate expiry was configured on port 443 of the public endpoint, not the internal proxy; the internal proxy cert was not monitored",
            "On-call runbook for 502 errors did not include TLS certificate checks as a diagnostic step",
            "The payment gateway proxy was provisioned by a contractor in Q2 2025 and ownership was not formally transferred to the platform team",
        ],
        "remediation_actions": [
            {
                "title": "Issue and deploy replacement TLS certificate",
                "detail": "Let's Encrypt certificate issued and deployed to Nginx proxy at 15:11 UTC.",
            },
            {
                "title": "Graceful restart of integration pods",
                "detail": "kubectl rollout restart deployment/payment-gateway-integration -n production at 15:22 UTC.",
            },
            {
                "title": "Verify checkout end-to-end",
                "detail": "Smoke test suite (make smoke-test) run at 15:35 UTC — all 47 tests passed.",
            },
        ],
        "action_items": [
            {
                "Action": "Enrol all reverse proxy certificates in automated Let's Encrypt renewal",
                "Owner": "K. Patel",
                "Due Date": "2025-12-01",
                "Priority": "P1",
            },
            {
                "Action": "Audit certificate inventory and add internal proxy certs",
                "Owner": "K. Patel",
                "Due Date": "2025-11-30",
                "Priority": "P1",
            },
            {
                "Action": "Add Prometheus alert for certificates expiring within 14 days (all internal endpoints)",
                "Owner": "Platform Team",
                "Due Date": "2025-12-07",
                "Priority": "P1",
            },
            {
                "Action": "Update 502 on-call runbook to include TLS cert expiry checks",
                "Owner": "T. Morgan",
                "Due Date": "2025-11-22",
                "Priority": "P2",
            },
            {
                "Action": "Formalise service ownership transfer process for contractor-provisioned resources",
                "Owner": "Engineering Manager",
                "Due Date": "2026-01-31",
                "Priority": "P2",
            },
        ],
        "lessons_learned": [
            "Manual infrastructure provisioning must be immediately captured in automation tooling and inventories — no exceptions.",
            "Certificate monitoring must cover all TLS endpoints, including internal proxies, load balancers, and service meshes — not just public-facing URLs.",
            "On-call runbooks require a TLS/certificate health check section as a standard diagnostic step for any 502/503 scenario.",
            "Service ownership must be formally transferred and documented before a contractor's engagement ends.",
            "A 14-day advance warning for expiring certificates provides sufficient lead time; current 3-day alert (for monitored certs) is insufficient.",
        ],
    }

    ts = datetime.datetime.now()
    print(f"[{ts.strftime('%H:%M:%S')}] Generating: {ir_context['title']}")
    path = gen.generate_report("incident-report-template", ir_context)
    rec = gen.generated[-1]
    print(
        f"[{ts.strftime('%H:%M:%S')}]   Template: incident-report-template | "
        f"Context: {len(ir_context['timeline'])} timeline events"
    )
    print(
        f"[{ts.strftime('%H:%M:%S')}]   Generated: {path} "
        f"({rec['word_count']} words, {rec['file_size_bytes']} bytes)"
    )
    print()

    # ---------------------------------------------------------------- index
    ts = datetime.datetime.now()
    index_path = gen.export_index()
    print(f"[{ts.strftime('%H:%M:%S')}] Exporting document index: {index_path}")
    print(f"[{ts.strftime('%H:%M:%S')}]   {len(gen.generated)} documents indexed")
    print()

    # ---------------------------------------------------------------- bundle
    from pipeline.pdf_packager import package_documents
    ts = datetime.datetime.now()
    bundle_name = f"document_bundle_{datetime.date.today().strftime('%Y%m%d')}.zip"
    bundle_dir = base_dir / "output"
    bundle_dir.mkdir(exist_ok=True)
    bundle_path = str(bundle_dir / bundle_name)
    bundle_size = package_documents(gen.generated, index_path, bundle_path)
    print(f"[{ts.strftime('%H:%M:%S')}] Packaging: {bundle_path}")
    print(f"[{ts.strftime('%H:%M:%S')}]   Bundle created ({len(gen.generated)} documents, {bundle_size / 1024:.1f} KB)")
    print()

    ended = datetime.datetime.now()
    duration = (ended - started).total_seconds()
    total_bytes = sum(d["file_size_bytes"] for d in gen.generated)
    print("=== Pipeline Complete ===")
    print(
        f"Duration: {duration:.2f}s | Documents: {len(gen.generated)} | "
        f"Total size: {total_bytes / 1024:.1f} KB | Status: SUCCESS"
    )


if __name__ == "__main__":
    main()

import asyncio
from typing import Dict, List, Tuple

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.database import AsyncSessionLocal
from app.models import Project, User
from app.auth import get_password_hash


PROJECTS: List[Dict] = [
    {
        "slug": "red-initial-access",
        "title": "Red Team Initial Access Playbook",
        "role_category": "red",
        "status": "completed",
        "executive_summary": "Performed phishing and initial foothold for simulated adversary campaign.",
        "scenario_scope": "Corporate workforce with mail security controls and monitored endpoints.",
        "responsibilities": "Designed payloads, executed phishing, coordinated C2 infrastructure, documented findings.",
        "tools_tech": "GoPhish, Evilginx, Cobalt Strike, M365 Defender logs, Elastic SIEM dashboards.",
        "architecture_notes": "Isolated C2 hosted in cloud with redirectors to obfuscate origin and rotate domains.",
        "process_walkthrough": "Ran phishing waves, tracked open/click, harvested MFA tokens, established beacon, pivoted to domain controller staging.",
        "outcomes_metrics": "20% click rate, 3 valid credentials captured, 1 DA token harvested before detection.",
        "evidence_links": "https://example.com/red-team/initial-access-report",
        "reproduction_steps": "Deploy gophish campaign template, set Evilginx phishing kit, monitor logs for token reuse.",
        "interview_points": "Discussed tradecraft to evade MFA fatigue defenses and how detections surfaced in SOC.",
    },
    {
        "slug": "red-priv-esc",
        "title": "Privilege Escalation in Windows Domain",
        "role_category": "red",
        "status": "completed",
        "executive_summary": "Escalated privileges from workstation to domain admin using living-off-the-land techniques.",
        "scenario_scope": "Windows 2019 domain with EDR and audit logging enabled across servers.",
        "responsibilities": "Enumerated trust relationships, abused misconfigured delegation, established persistence.",
        "tools_tech": "BloodHound, Rubeus, PowerView, SharpHound collectors, KQL for log review.",
        "architecture_notes": "Attack path leveraged unconstrained delegation on legacy service account and weak Kerberos policies.",
        "process_walkthrough": "Collected AD graph, calculated shortest path, executed S4U2self for ticket forging, implanted scheduled tasks.",
        "outcomes_metrics": "Root cause mapped to three policy violations, remediation validated with new delegation policies.",
        "evidence_links": "https://example.com/red-team/priv-esc",
        "reproduction_steps": "Run BloodHound collector, review pre-built queries, replicate S4U abuse in lab with test accounts.",
        "interview_points": "Explained Kerberos ticketing chain and detection opportunities for unusual TGS requests.",
    },
    {
        "slug": "red-lateral-movement",
        "title": "Lateral Movement via SMB and WinRM",
        "role_category": "red",
        "status": "completed",
        "executive_summary": "Simulated lateral spread while evading EDR to stage ransomware payloads.",
        "scenario_scope": "Mixed Windows workstation fleet with centrally managed EDR, SOC monitoring via SIEM.",
        "responsibilities": "Crafted kerberos-authenticated PSRemoting, bypassed AppLocker, staged payloads for timing window.",
        "tools_tech": "CrackMapExec, Impacket, PowerShell remoting, AMSI bypass research, Sysmon/EDR telemetry.",
        "architecture_notes": "Used alternate creds captured from helpdesk account; pivoted through jump host with constrained access.",
        "process_walkthrough": "Validated credentials, tested remote command execution, enumerated drives, exfiltrated config secrets.",
        "outcomes_metrics": "Identified 4 hosts with weak local admin password reuse; provided remediation and detection rules.",
        "evidence_links": "https://example.com/red-team/lateral-movement",
        "reproduction_steps": "Generate Kerberos tickets, invoke CME with pass-the-hash, validate commands through WinRM logs.",
        "interview_points": "Described detection logic for WinRM/SMB anomalies and golden ticket blast radius.",
    },
    {
        "slug": "red-persistence",
        "title": "Defensive Evasion and Persistence",
        "role_category": "red",
        "status": "completed",
        "executive_summary": "Established stealth persistence on workstations and servers post-compromise.",
        "scenario_scope": "Endpoints with AppLocker, AMSI, and monitored scheduled tasks; blue team on call.",
        "responsibilities": "Tested persistence methods, verified log visibility, documented IR cleanup steps.",
        "tools_tech": "Cobalt Strike, SharpPersist, registry run keys, WMI event filters, ELK dashboards.",
        "architecture_notes": "Persistence staged with signed binary proxy execution to blend into allowed processes.",
        "process_walkthrough": "Created scheduled tasks, registered services, added registry autoruns; monitored detection timing.",
        "outcomes_metrics": "Blue team detected 2/6 techniques; provided new detection logic for WMI and service creation.",
        "evidence_links": "https://example.com/red-team/persistence",
        "reproduction_steps": "Deploy SharpPersist modules in lab, map resulting event IDs, measure detection latency.",
        "interview_points": "Discussed balancing operational security with testing coverage for purple team events.",
    },
    {
        "slug": "red-ransomware-simulation",
        "title": "Ransomware Simulation with Tabletop",
        "role_category": "red",
        "status": "completed",
        "executive_summary": "Led ransomware simulation across production-like environment and executive tabletop.",
        "scenario_scope": "Hybrid infrastructure with Windows servers, file shares, and backup appliances.",
        "responsibilities": "Executed encryption in lab, coordinated tabletop scenarios, produced executive readout.",
        "tools_tech": "Caldera, Atomic Red Team, custom PowerShell encryptor, incident comms templates.",
        "architecture_notes": "Sim replicated double extortion workflow using isolated shares and fake data sets.",
        "process_walkthrough": "Ran automated TTPs, executed backup disruption, tested isolation playbooks, facilitated tabletop roles.",
        "outcomes_metrics": "Documented 12 control gaps, validated RPO/RTO assumptions, improved comms cadence by 30%.",
        "evidence_links": "https://example.com/red-team/ransomware",
        "reproduction_steps": "Execute Atomic tests tagged ransomware, run Caldera planner, capture SIEM correlations.",
        "interview_points": "Explained how attack chain mapped to MITRE ATT&CK and tabletop decisions informed IR updates.",
    },
    {
        "slug": "blue-soc-automation",
        "title": "SOC Automation and Alert Tuning",
        "role_category": "blue",
        "status": "completed",
        "executive_summary": "Built automation playbooks to reduce noise and accelerate SOC triage.",
        "scenario_scope": "24/7 SOC monitoring cloud and on-prem logs through SIEM and SOAR stack.",
        "responsibilities": "Created KQL/Elastic detections, tuned false positives, built SOAR enrichment routines.",
        "tools_tech": "Sentinel, Elastic, Phantom/Splunk SOAR, Python lambdas for enrichment, MISP integration.",
        "architecture_notes": "Playbooks executed as containerized functions with service accounts scoped to read-only contexts.",
        "process_walkthrough": "Mapped top noisy alerts, added contextual enrichment, created auto-closing rules with evidence attachments.",
        "outcomes_metrics": "Reduced false positives by 45%, MTTR improved from 40m to 18m for phishing alerts.",
        "evidence_links": "https://example.com/blue-team/soc-automation",
        "reproduction_steps": "Deploy SOAR app connectors, configure enrichment API keys, run playbooks against sample alerts.",
        "interview_points": "Walked through change management approach to avoid silencing critical alerts.",
    },
    {
        "slug": "blue-threat-hunting",
        "title": "Threat Hunting in Hybrid Environment",
        "role_category": "blue",
        "status": "lab",
        "executive_summary": "Designed hunts for credential theft and persistence across hybrid identity systems.",
        "scenario_scope": "Azure AD, on-prem AD, and Okta federation with centralized logging to SIEM.",
        "responsibilities": "Developed hunt hypotheses, authored KQL/DQL queries, ran memory forensics on endpoints.",
        "tools_tech": "Sysmon, Velociraptor, KQL, Osquery, Zeek PCAP parsing, YARA scans.",
        "architecture_notes": "Hunts staged in isolated sandbox; results piped into SOC backlog with documented outcomes.",
        "process_walkthrough": "Collected baselines, pivoted on anomalous sign-ins, investigated token replay artifacts.",
        "outcomes_metrics": "Identified stale service accounts and misconfigured conditional access, leading to policy updates.",
        "evidence_links": "https://example.com/blue-team/threat-hunting",
        "reproduction_steps": "Run osquery packs, capture Windows event logs, correlate with sign-in events in Sentinel.",
        "interview_points": "Explained reasoning behind hypotheses and how to socialize findings with identity team.",
    },
    {
        "slug": "blue-edr-rollout",
        "title": "EDR Rollout and Containment Procedures",
        "role_category": "blue",
        "status": "completed",
        "executive_summary": "Led enterprise EDR rollout and improved containment procedures for high-severity incidents.",
        "scenario_scope": "3,000 Windows endpoints with phased deployment and change advisory board oversight.",
        "responsibilities": "Created deployment rings, validation tests, and isolation workflows integrated with ITSM.",
        "tools_tech": "CrowdStrike Falcon, Intune, SCCM, ServiceNow, custom isolation scripts.",
        "architecture_notes": "EDR policies templated per persona with USB control, application control, and network containment hooks.",
        "process_walkthrough": "Piloted with IT, expanded to business units, created rollback guides, trained SOC on new controls.",
        "outcomes_metrics": "Achieved 98% coverage, mean isolation time dropped to under 2 minutes with automated workflows.",
        "evidence_links": "https://example.com/blue-team/edr-rollout",
        "reproduction_steps": "Build deployment package, configure device groups, test isolation and rollback paths in staging.",
        "interview_points": "Discussed stakeholder management and measurable improvements in containment SLAs.",
    },
    {
        "slug": "blue-incident-response",
        "title": "Cloud Email Incident Response",
        "role_category": "blue",
        "status": "completed",
        "executive_summary": "Investigated and contained business email compromise across Microsoft 365 tenant.",
        "scenario_scope": "M365 with Defender for Office 365, Exchange Online mail flow rules, and Azure AD sign-in logs.",
        "responsibilities": "Ran incident triage, blocked tokens, reset credentials, searched mailboxes for malicious rules.",
        "tools_tech": "M365 Defender, PowerShell, KQL hunting, Audit logs, Secure Score reporting.",
        "architecture_notes": "Implemented conditional access and token revocation flows, added transport rules for isolating suspicious mail.",
        "process_walkthrough": "Correlated sign-in anomalies, investigated consent grants, removed inbox rules, reviewed mail traces.",
        "outcomes_metrics": "Removed persistence mechanisms within 1 hour, introduced new detections for OAuth abuse.",
        "evidence_links": "https://example.com/blue-team/email-ir",
        "reproduction_steps": "Use PowerShell Search-Mailbox actions, revoke sessions, validate new conditional access policies.",
        "interview_points": "Shared lessons on user communication and ensuring minimal business disruption during IR.",
    },
    {
        "slug": "blue-patch-management",
        "title": "Vulnerability and Patch Management Program",
        "role_category": "blue",
        "status": "completed",
        "executive_summary": "Established risk-based patching program with executive visibility.",
        "scenario_scope": "On-prem and cloud servers, workstation fleet, critical web apps tracked via CMDB.",
        "responsibilities": "Built CVSS+ scoring model, prioritized SLAs, integrated scanning results into ITSM.",
        "tools_tech": "Nessus, Qualys, Jira/ServiceNow, PowerBI dashboards, WSUS and Ansible for remediation.",
        "architecture_notes": "Centralized scan collectors feeding SIEM; remediation orchestrated through configuration mgmt pipelines.",
        "process_walkthrough": "Classified assets, set SLAs by criticality, automated ticket creation, measured SLA adherence.",
        "outcomes_metrics": "Critical vulns SLA compliance improved from 62% to 92% within two quarters.",
        "evidence_links": "https://example.com/blue-team/patching",
        "reproduction_steps": "Configure connectors, import scan data, build risk model, create recurring remediation sprints.",
        "interview_points": "Explained governance for exceptions and reporting cadence to leadership.",
    },
    {
        "slug": "cloud-iam-hardening",
        "title": "Cloud IAM Hardening and Least Privilege",
        "role_category": "cloud",
        "status": "completed",
        "executive_summary": "Reduced cloud blast radius through IAM refactoring and guardrails.",
        "scenario_scope": "AWS multi-account and Azure subscriptions with developer and production workloads.",
        "responsibilities": "Mapped permissions, implemented SCP/Blueprints, built just-in-time access workflows.",
        "tools_tech": "AWS IAM Access Analyzer, Azure PIM, Terraform, CloudTrail, Config, custom policy lints.",
        "architecture_notes": "Guardrails enforced via org SCPs, landing zone uses shared services with centralized logging.",
        "process_walkthrough": "Analyzed IAM usage, removed wildcards, introduced role-based access with session tagging.",
        "outcomes_metrics": "Cut wildcard permissions by 80%, privileged sessions require approvals with 1-hour expiry.",
        "evidence_links": "https://example.com/cloud/iam-hardening",
        "reproduction_steps": "Run access analyzer findings, refactor IAM policies, deploy via Terraform with OPA checks.",
        "interview_points": "Discussed implementing least privilege at scale and balancing developer velocity.",
    },
    {
        "slug": "cloud-network-segmentation",
        "title": "Cloud Network Segmentation",
        "role_category": "cloud",
        "status": "completed",
        "executive_summary": "Implemented zero-trust inspired segmentation across VPCs and VNets.",
        "scenario_scope": "AWS and Azure workloads, service meshes, and private endpoints for data stores.",
        "responsibilities": "Designed segmentation strategy, enforced security groups/NSGs, validated with traffic captures.",
        "tools_tech": "VPC Flow Logs, Azure NSG flow logs, Istio, Envoy, Security Hub, ARM/Terraform modules.",
        "architecture_notes": "Service mesh mTLS with identity-based policies; private endpoints for PaaS databases.",
        "process_walkthrough": "Mapped data flows, created allowlists, applied network ACLs, validated with synthetic probes.",
        "outcomes_metrics": "Reduced lateral communication paths by 60%, improved detection for cross-VPC anomalies.",
        "evidence_links": "https://example.com/cloud/network-segmentation",
        "reproduction_steps": "Deploy network policy modules, enable flow logs, run validation scripts using hping3 and k6.",
        "interview_points": "Explained tradeoffs between hub-spoke and service mesh enforcement and monitoring outcomes.",
    },
    {
        "slug": "cloud-kubernetes-security",
        "title": "Kubernetes Security Baseline",
        "role_category": "cloud",
        "status": "lab",
        "executive_summary": "Built hardened baseline for EKS/AKS clusters with policy enforcement.",
        "scenario_scope": "Multiple clusters hosting microservices, CI/CD with GitHub Actions and ArgoCD.",
        "responsibilities": "Implemented admission controls, image signing, runtime detection, and secrets management.",
        "tools_tech": "Kyverno/OPA Gatekeeper, cosign, Falco, kube-bench, kube-hunter, external-secrets.",
        "architecture_notes": "Clusters bootstrap with private API endpoints, workload identities, and network policies.",
        "process_walkthrough": "Established baseline policies, configured sigstore signing, integrated Falco alerts to SIEM.",
        "outcomes_metrics": "Non-compliant deployments blocked; runtime detections produced actionable alerts with low noise.",
        "evidence_links": "https://example.com/cloud/kubernetes-security",
        "reproduction_steps": "Run kube-bench, configure Kyverno policies, sign images in CI and verify in admission.",
        "interview_points": "Described rollout strategy and developer education to meet security controls.",
    },
    {
        "slug": "cloud-data-protection",
        "title": "Cloud Data Protection and DLP",
        "role_category": "cloud",
        "status": "completed",
        "executive_summary": "Implemented encryption, tokenization, and DLP controls for sensitive data.",
        "scenario_scope": "Data lakes in AWS S3, analytics in Redshift/Azure Synapse, SaaS integrations.",
        "responsibilities": "Classified data, enforced encryption at rest/in transit, deployed DLP policies across SaaS.",
        "tools_tech": "KMS, Macie, Azure Purview, BigID, CASB, TLS mutual auth, Terraform pipelines.",
        "architecture_notes": "Encryption keys managed via central KMS with rotation; DLP policies integrated with CASB for SaaS.",
        "process_walkthrough": "Ran discovery scans, tagged datasets, configured bucket policies, enforced tokenization via services.",
        "outcomes_metrics": "100% encryption coverage for regulated datasets; data egress alerts with automated response.",
        "evidence_links": "https://example.com/cloud/data-protection",
        "reproduction_steps": "Enable Macie, create Purview scans, configure KMS policies, validate DLP matches.",
        "interview_points": "Walked through governance and audit evidence for compliance teams.",
    },
    {
        "slug": "cloud-logging-observability",
        "title": "Cloud Logging and Observability",
        "role_category": "cloud",
        "status": "completed",
        "executive_summary": "Built unified logging and observability pipeline across cloud workloads.",
        "scenario_scope": "AWS/Azure apps with containerized workloads and serverless functions.",
        "responsibilities": "Normalized logs, implemented trace sampling, configured metrics dashboards and alerts.",
        "tools_tech": "OpenTelemetry, CloudWatch, Azure Monitor, Prometheus/Grafana, Loki, Kinesis/EventHub streaming.",
        "architecture_notes": "Centralized collectors forward to SIEM; retention policies align with compliance requirements.",
        "process_walkthrough": "Instrumented services with OTel SDKs, deployed collectors, tuned alert thresholds, built SLOs.",
        "outcomes_metrics": "Improved MTTR by 35% for service incidents; reduced log ingestion costs via sampling and filtering.",
        "evidence_links": "https://example.com/cloud/logging",
        "reproduction_steps": "Deploy OTel collector daemonset, configure exporters, create Grafana dashboards for SLOs.",
        "interview_points": "Discussed balancing observability depth with cost and governance.",
    },
    {
        "slug": "devops-ci-hardening",
        "title": "CI/CD Hardening and Supply Chain Security",
        "role_category": "devops",
        "status": "completed",
        "executive_summary": "Secured CI/CD pipelines with signing, scanning, and least privilege runners.",
        "scenario_scope": "GitHub Actions, self-hosted runners, container image builds, multi-environment deployments.",
        "responsibilities": "Implemented OIDC to cloud, image signing, SBOM generation, and policy-as-code gates.",
        "tools_tech": "GitHub OIDC, cosign, Trivy, Syft/Grype, OPA/Conftest, ArgoCD sync hooks.",
        "architecture_notes": "Runners use short-lived cloud roles, artifacts stored in private registry with signing enforcement.",
        "process_walkthrough": "Added scanning steps, enforced signatures, validated manifests before promotion, stored attestations.",
        "outcomes_metrics": "Blocked vulnerable images automatically; reduced manual reviews by 50% via policy automation.",
        "evidence_links": "https://example.com/devops/ci-hardening",
        "reproduction_steps": "Configure OIDC trust, enable cosign keyless signing, add Trivy scans, gate deployments with OPA.",
        "interview_points": "Explained sigstore adoption and impact on release confidence.",
    },
    {
        "slug": "devops-infrastructure-pipelines",
        "title": "Infrastructure as Code Pipelines",
        "role_category": "devops",
        "status": "completed",
        "executive_summary": "Built multi-env IaC pipelines with automated testing and drift detection.",
        "scenario_scope": "AWS landing zone and Kubernetes clusters managed via Terraform and Helm.",
        "responsibilities": "Authored Terraform modules, added unit/integration tests, configured drift alerts.",
        "tools_tech": "Terraform Cloud, Terragrunt, tflint, Terratest, Atlantis, Helmfile, ArgoCD.",
        "architecture_notes": "Pipelines support preview plans, PR-based approvals, and automatic tagging for auditability.",
        "process_walkthrough": "Modularized code, enforced lint/tests, integrated Atlantis for plan comments, enabled drift detection.",
        "outcomes_metrics": "Reduced infra drift incidents to near zero; improved deployment cadence with safer change windows.",
        "evidence_links": "https://example.com/devops/iac-pipelines",
        "reproduction_steps": "Set up Terraform Cloud workspaces, configure Atlantis, add Terratest suites for critical modules.",
        "interview_points": "Discussed governance approach and scaling modules across teams.",
    },
    {
        "slug": "devops-observability-sre",
        "title": "SRE Observability and Reliability Dashboards",
        "role_category": "devops",
        "status": "completed",
        "executive_summary": "Implemented SRE practices with SLOs, error budgets, and reliability dashboards.",
        "scenario_scope": "Containerized services on Kubernetes with service mesh and canary deployments.",
        "responsibilities": "Defined SLIs/SLOs, built alerting on error budgets, created runbooks and game days.",
        "tools_tech": "Prometheus, Grafana, Alertmanager, SLO exporters, Argo Rollouts, chaos engineering tools.",
        "architecture_notes": "Dashboards aggregate golden signals per service; alerts route via PagerDuty with runbook links.",
        "process_walkthrough": "Instrumented services, calculated SLOs, created budget burn alerts, ran chaos experiments.",
        "outcomes_metrics": "Stabilized release cadence with evidence-driven rollbacks and improved availability by 3 nines.",
        "evidence_links": "https://example.com/devops/sre-dashboards",
        "reproduction_steps": "Deploy Prometheus stack, configure SLO exporter, set budget burn alert rules and test rollouts.",
        "interview_points": "Explained SRE culture adoption and measurable impact on reliability.",
    },
    {
        "slug": "devops-platform-engineering",
        "title": "Platform Engineering Developer Portal",
        "role_category": "devops",
        "status": "lab",
        "executive_summary": "Built internal developer platform with golden paths and self-service templates.",
        "scenario_scope": "Microservices on Kubernetes with standardized templates and paved road pipelines.",
        "responsibilities": "Curated templates, integrated IDP, codified security guardrails, gathered developer feedback.",
        "tools_tech": "Backstage, ArgoCD, Crossplane, Terraform, service catalogs, template scaffolding scripts.",
        "architecture_notes": "Platform layers include identity, networking, observability, and security controls baked into templates.",
        "process_walkthrough": "Created software templates, provisioned sandbox envs, wired metrics to usage dashboards.",
        "outcomes_metrics": "Accelerated service onboarding from weeks to days; increased template adoption to 70% within quarter.",
        "evidence_links": "https://example.com/devops/platform",
        "reproduction_steps": "Deploy Backstage, create templates with security add-ons, integrate with GitOps pipelines.",
        "interview_points": "Discussed balancing central platform direction with developer autonomy.",
    },
    {
        "slug": "devops-chaos-engineering",
        "title": "Chaos Engineering Program",
        "role_category": "devops",
        "status": "lab",
        "executive_summary": "Introduced chaos experiments to validate resilience and incident response readiness.",
        "scenario_scope": "Kubernetes services, stateful workloads, and message queues in multi-region setup.",
        "responsibilities": "Defined steady states, ran failure injections, documented remediation patterns.",
        "tools_tech": "LitmusChaos, Gremlin, Argo Rollouts, custom chaos scripts, Prometheus/Grafana.",
        "architecture_notes": "Experiments isolated in non-prod initially, then carefully expanded to prod with guardrails.",
        "process_walkthrough": "Ran pod kill/network latency scenarios, monitored SLO impact, validated runbooks.",
        "outcomes_metrics": "Detected weaknesses in retry logic and circuit breakers; improved incident response drill outcomes.",
        "evidence_links": "https://example.com/devops/chaos",
        "reproduction_steps": "Install Litmus, create experiments, observe metrics and trace impacts, document mitigations.",
        "interview_points": "Shared lessons on culture change and safe experimentation practices.",
    },
    {
        "slug": "grc-risk-assessment",
        "title": "Enterprise Risk Assessment",
        "role_category": "grc",
        "status": "completed",
        "executive_summary": "Led enterprise risk assessment with business impact analysis and treatment plans.",
        "scenario_scope": "Business units across SaaS, on-prem, and cloud workloads; compliance drivers ISO 27001 and SOC2.",
        "responsibilities": "Facilitated workshops, scored risks, defined mitigation plans and acceptance criteria.",
        "tools_tech": "Risk registers, Archer/GRC platform, qualitative and quantitative scoring models.",
        "architecture_notes": "Risks mapped to asset inventory and controls library for traceability.",
        "process_walkthrough": "Collected assets, interviewed owners, rated likelihood/impact, tracked remediation through governance.",
        "outcomes_metrics": "Produced prioritized roadmap; reduced top 5 risks residual exposure by 40% after mitigation.",
        "evidence_links": "https://example.com/grc/risk-assessment",
        "reproduction_steps": "Build asset inventory, run risk workshops, record findings, implement treatment plans.",
        "interview_points": "Explained linking risks to controls and reporting to steering committee.",
    },
    {
        "slug": "grc-policy-framework",
        "title": "Policy Framework and Governance",
        "role_category": "grc",
        "status": "completed",
        "executive_summary": "Developed security policy framework and governance cadence.",
        "scenario_scope": "Corporate environment needing standardized policies for cloud, endpoint, and data protection.",
        "responsibilities": "Drafted policies, aligned with regulations, established review cycles and approvals.",
        "tools_tech": "Confluence, GRC tooling, policy exception workflow integrated with ticketing system.",
        "architecture_notes": "Policies versioned and mapped to controls catalog; exceptions logged with owner approvals.",
        "process_walkthrough": "Interviewed stakeholders, drafted policies, rolled out communications, tracked attestations.",
        "outcomes_metrics": "Achieved 100% policy acknowledgments; reduced exceptions backlog through clearer guidance.",
        "evidence_links": "https://example.com/grc/policy-framework",
        "reproduction_steps": "Publish policies, integrate with attestation workflow, track version history.",
        "interview_points": "Discussed balancing usability with compliance and how governance meetings run.",
    },
    {
        "slug": "grc-compliance-automation",
        "title": "Compliance Automation",
        "role_category": "grc",
        "status": "completed",
        "executive_summary": "Automated evidence collection for SOC2/ISO controls using API integrations.",
        "scenario_scope": "Cloud-native environment with CI/CD and multiple SaaS systems providing audit artifacts.",
        "responsibilities": "Mapped controls to automated checks, built evidence pipelines, reduced manual collection.",
        "tools_tech": "Drata/Vanta-like scripts, AWS Config, Terraform compliance checks, ticketing system integration.",
        "architecture_notes": "Evidence stored in centralized repository with metadata tags for auditors.",
        "process_walkthrough": "Connected APIs, scheduled evidence pulls, validated timestamps, generated auditor-ready packages.",
        "outcomes_metrics": "Cut evidence collection time by 60%; improved audit readiness scores.",
        "evidence_links": "https://example.com/grc/compliance-automation",
        "reproduction_steps": "Implement API collectors, map to controls, schedule exports, attach evidence to control records.",
        "interview_points": "Shared roadmap for continuous compliance and control ownership model.",
    },
    {
        "slug": "grc-third-party-risk",
        "title": "Third-Party Risk Management",
        "role_category": "grc",
        "status": "lab",
        "executive_summary": "Built third-party risk intake and monitoring program.",
        "scenario_scope": "Vendors across SaaS, data processing, and infrastructure providers.",
        "responsibilities": "Designed questionnaires, automated scoring, integrated continuous monitoring feeds.",
        "tools_tech": "SecurityScorecard/BitSight, questionnaire automation, contract repository, SLA tracking.",
        "architecture_notes": "Tiered vendor model with required controls and remediation timelines by risk rating.",
        "process_walkthrough": "Onboarded vendors, gathered evidence, scored responses, monitored for external posture changes.",
        "outcomes_metrics": "Reduced onboarding time from 30 to 10 days; improved visibility into vendor security posture.",
        "evidence_links": "https://example.com/grc/third-party-risk",
        "reproduction_steps": "Deploy questionnaire templates, connect monitoring APIs, build dashboards for risk tiers.",
        "interview_points": "Discussed balancing speed of procurement with security requirements.",
    },
    {
        "slug": "grc-bcdr-testing",
        "title": "BCDR Testing Program",
        "role_category": "grc",
        "status": "completed",
        "executive_summary": "Established business continuity and disaster recovery testing cadence.",
        "scenario_scope": "Critical apps across cloud and on-prem; backups and failover processes documented.",
        "responsibilities": "Ran tabletop and technical failover tests, documented lessons learned, updated runbooks.",
        "tools_tech": "Backup appliances, cloud DR tooling, runbook automation scripts, monitoring dashboards.",
        "architecture_notes": "Failover targets pre-provisioned; RPO/RTO validated with application owners.",
        "process_walkthrough": "Scheduled tests, executed failovers, verified data integrity, restored services, captured metrics.",
        "outcomes_metrics": "Met RPO/RTO targets for 95% of critical apps; improved communication trees and escalation paths.",
        "evidence_links": "https://example.com/grc/bcdr-testing",
        "reproduction_steps": "Select workloads, simulate outages, validate restore procedures, document timelines.",
        "interview_points": "Explained governance for test outcomes and improvement backlog.",
    },
]


def build_user_identifier() -> Tuple[str, str]:
    if hasattr(User, "username"):
        return "username", "admin"
    return "email", "admin@example.com"


def build_user_data(hashed_password: str) -> Dict:
    user_data: Dict = {
        "email": "admin@example.com",
        "hashed_password": hashed_password,
        "is_active": True,
    }
    if hasattr(User, "username"):
        user_data["username"] = "admin"
    if hasattr(User, "is_superuser"):
        user_data["is_superuser"] = True
    return user_data


async def ensure_admin_user(session) -> User:
    identifier_field, identifier_value = build_user_identifier()

    result = await session.execute(
        select(User).where(getattr(User, identifier_field) == identifier_value)
    )
    admin_user = result.scalars().first()

    if admin_user:
        print("Admin user ensured.")
        return admin_user

    hashed_password = get_password_hash("ChangeMeNow!")
    user_data = build_user_data(hashed_password)

    admin_user = User(**user_data)
    session.add(admin_user)
    await session.commit()
    await session.refresh(admin_user)
    print("Admin user ensured.")
    return admin_user


async def upsert_projects(session) -> Tuple[int, int]:
    created = 0
    updated = 0

    for project_data in PROJECTS:
        result = await session.execute(
            select(Project).where(Project.slug == project_data["slug"])
        )
        project = result.scalars().first()

        if project:
            for key, value in project_data.items():
                setattr(project, key, value)
            updated += 1
        else:
            project = Project(**project_data)
            session.add(project)
            created += 1

    await session.commit()
    return created, updated


async def main() -> None:
    async with AsyncSessionLocal() as session:
        try:
            await ensure_admin_user(session)
            created, updated = await upsert_projects(session)
            print(f"Created {created} new projects, updated {updated} existing projects.")
            print("Seed complete.")
        except SQLAlchemyError:
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())

---
title: Getting Started with the Portfolio Wiki
description: Learn how to navigate and use this comprehensive documentation system
published: true
date: 2025-11-07
tags: [getting-started, documentation, guide]
---

# Getting Started

Welcome to the Portfolio Wiki! This guide will help you navigate and make the most of this comprehensive documentation system.

## 📖 What's in This Wiki?

This wiki contains four types of documentation:

### 1. **Project Documentation**
Complete documentation for each portfolio project, including:
- **Overview**: Project goals, technologies, and architecture
- **Implementation Guide**: Step-by-step setup instructions
- **Operations Guide**: Day-to-day operational procedures
- **Troubleshooting**: Common issues and solutions
- **Runbooks**: Incident-specific response procedures

**Example**: [PRJ-SDE-002: Observability & Backups Stack](/projects/sde-devops/prj-sde-002/overview)

### 2. **Runbooks** (Incident Response)
Quick-reference procedures for specific incidents and alerts. Follow these when an alert fires or an issue occurs.

**Format**:
- **Symptoms**: How to identify the issue
- **Impact**: What's affected
- **Steps**: Numbered action items
- **Verification**: How to confirm resolution
- **Escalation**: When to escalate

**Example**: [Host Down Response](/runbooks/infrastructure/host-down)

### 3. **Playbooks** (Process Workflows)
End-to-end workflows for broader scenarios like deployments, disaster recovery, or security incidents.

**Format**:
- **Purpose**: When to use this playbook
- **Prerequisites**: What you need before starting
- **Workflow**: Phase-by-phase procedures
- **Decision Points**: Key checkpoints and gates
- **Rollback**: How to undo changes

**Example**: [Disaster Recovery Playbook](/playbooks/disaster-recovery)

### 4. **Handbooks** (Reference Guides)
Comprehensive reference documentation, standards, and best practices.

**Format**:
- **Standards**: What we follow and why
- **Procedures**: How we do common tasks
- **Tools**: What we use and how
- **Best Practices**: Lessons learned and recommendations

**Example**: [Engineer's Handbook](/handbooks/engineers-handbook)

## 🗺️ Navigation Structure

```
wiki/
├── home.md                     # Start here
├── projects/                   # Project documentation
│   ├── homelab/
│   │   ├── prj-home-001/      # Network infrastructure
│   │   └── prj-home-002/      # Virtualization
│   ├── sde-devops/
│   │   ├── prj-sde-001/       # Database infrastructure
│   │   └── prj-sde-002/       # Observability stack
│   └── cybersecurity/
│       └── prj-cyb-blue-001/   # SIEM pipeline
├── runbooks/                   # Incident response procedures
│   ├── infrastructure/         # Host, compute, storage issues
│   ├── database/              # Database-specific procedures
│   ├── networking/            # Network troubleshooting
│   ├── security/              # Security incidents
│   └── monitoring/            # Observability issues
├── playbooks/                  # Process workflows
│   ├── disaster-recovery.md
│   ├── deployment.md
│   ├── incident-response.md
│   └── ...
└── handbooks/                  # Reference documentation
    ├── engineers-handbook.md
    ├── operations-handbook.md
    └── security-handbook.md
```

## 🎯 Common Use Cases

### "I Got an Alert - What Do I Do?"

1. Note the alert name (e.g., "HostDown", "DiskSpaceLow")
2. Go to [Runbooks Index](/runbooks/index)
3. Search for the alert name or symptom
4. Follow the runbook step-by-step
5. Document any deviations or lessons learned

**Example Alert Flow**:
```
Alert: "HostDown" fires for 192.168.1.21
→ Find: /runbooks/infrastructure/host-down
→ Follow: Steps 1-6 in the runbook
→ Verify: Host returns to UP status
→ Document: Add notes to incident log
```

### "I Need to Deploy a New Service"

1. Check [Infrastructure Provisioning Playbook](/playbooks/infrastructure-provisioning)
2. Follow the workflow phase-by-phase
3. Use project-specific guides for detailed steps
4. Update monitoring and documentation

### "I Want to Implement a Project"

1. Go to the project's overview page
2. Review prerequisites and architecture
3. Follow the implementation guide step-by-step
4. Configure monitoring using the operations guide
5. Bookmark relevant runbooks

### "I Need to Know Our Standards"

1. Check the [Engineer's Handbook](/handbooks/engineers-handbook)
2. Find the relevant section (e.g., "Security Standards")
3. Review standards and examples
4. Ask questions if clarification needed

## 🔍 Search Tips

Use Wiki.js search effectively:

- **Exact phrases**: Use quotes `"host down"`
- **Tags**: Search by `#monitoring` `#security` `#terraform`
- **Wildcards**: Use `disk*` to find "disk-space", "disk-usage", etc.
- **Categories**: Filter by Projects, Runbooks, Playbooks, or Handbooks

**Common Search Examples**:
```
"prometheus scrape failure"     → Finds monitoring runbooks
tag:terraform                    → All IaC documentation
backup AND restore               → Backup-related procedures
alert:HostDown                   → Specific alert runbook
```

## 📝 Documentation Standards

### Writing Style

- **Be concise**: Get to the point quickly
- **Use lists**: Numbered for steps, bullets for items
- **Include commands**: Show exact commands with expected output
- **Add context**: Explain why, not just how
- **Think operational**: Write for 3am troubleshooting

### Structure Conventions

**Runbooks** follow this template:
1. Alert/Symptom
2. Impact Assessment
3. Immediate Actions
4. Investigation Steps
5. Resolution Steps
6. Verification
7. Prevention/Follow-up

**Commands** are formatted with expected output:
```bash
$ command-to-run
Expected output here
```

**Paths** use inline code: `/etc/prometheus/prometheus.yml`

**Alerts** are referenced with context: `HostDown` alert (fires when `up == 0` for 2+ minutes)

## 🎓 Learning Paths

### New to the Homelab?
1. [PRJ-HOME-001: Network Build](/projects/homelab/prj-home-001/overview)
2. [PRJ-HOME-002: Virtualization](/projects/homelab/prj-home-002/overview)
3. [Network Handbook](/handbooks/network-handbook)

### Want to Learn Terraform/IaC?
1. [PRJ-SDE-001: Database Infrastructure](/projects/sde-devops/prj-sde-001/overview)
2. [Infrastructure Provisioning Playbook](/playbooks/infrastructure-provisioning)
3. [Engineer's Handbook: IaC Section](/handbooks/engineers-handbook#infrastructure-as-code)

### Interested in Observability?
1. [PRJ-SDE-002: Observability Stack](/projects/sde-devops/prj-sde-002/overview)
2. [Monitoring Handbook](/handbooks/monitoring-handbook)
3. [Monitoring Runbooks](/runbooks/monitoring/index)

### Security Focus?
1. [PRJ-CYB-BLUE-001: SIEM Pipeline](/projects/cybersecurity/prj-cyb-blue-001/overview)
2. [Security Handbook](/handbooks/security-handbook)
3. [Security Runbooks](/runbooks/security/index)

## 🔄 Keeping Documentation Updated

This wiki is a living document system. When you:

- **Fix an incident**: Update the runbook with lessons learned
- **Deploy changes**: Update the implementation guide
- **Learn something new**: Add to the relevant handbook
- **Encounter gaps**: Create new runbooks or playbooks

## 🆘 Getting Help

- **Wiki Issues**: Check the [Wiki.js documentation](https://docs.requarks.io/)
- **Technical Questions**: Reference project README files
- **Process Questions**: Check playbooks and handbooks
- **Everything Else**: Contact [Sam Jackson](https://github.com/samueljackson-collab)

## 🚀 Next Steps

Ready to dive in? Here are some suggested starting points:

1. **Browse Projects**: [Project Index](/projects/index)
2. **Review Common Runbooks**: [Runbook Index](/runbooks/index)
3. **Read Key Playbooks**: [Playbook Index](/playbooks/index)
4. **Study Standards**: [Engineer's Handbook](/handbooks/engineers-handbook)

---

**Need Help?** Contact [Sam Jackson](https://www.linkedin.com/in/sams-jackson) or [open an issue](https://github.com/samueljackson-collab/Portfolio-Project/issues)

**Last Updated**: November 7, 2025

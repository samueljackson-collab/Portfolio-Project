import type { Project } from '../types';
import { STANDARD_DOCS, DOMAINS, REPO } from '../constants';

export interface DocTemplate {
  filename: string;
  content: string;
}

export const generateProjectReadme = (project: Project): string => {
  const domain = DOMAINS[project.domain];

  return `# ${project.title}

> ${domain.icon} **${domain.title}** | Status: **${project.status}**

${project.description}

## 📊 Key Metrics

${Object.entries(project.metrics || {}).map(([key, value]) => `- **${key}**: ${value}`).join('\n')}

## 🛠 Technologies

${project.technologies.map(tech => `- ${tech}`).join('\n')}

## 📚 Documentation

This project includes comprehensive enterprise-grade documentation:

${STANDARD_DOCS.map(doc => `- [${doc.label}](./wiki/${doc.file}) - ${doc.desc}`).join('\n')}

## 🔗 Links

- [GitHub Repository](${REPO.url}/tree/${REPO.branch}/${project.folder})
- [Documentation](${REPO.url}/tree/${REPO.branch}/${project.folder}/wiki)

## 📝 Tags

${project.tags.map(tag => `\`${tag}\``).join(' ')}

---

*Part of the Enterprise Portfolio Wiki showcasing 22+ production-grade projects.*
`;
};

export const generateArchitectureDoc = (project: Project): string => {
  const domain = DOMAINS[project.domain];

  return `# ${project.title} - Architecture

## Overview

${project.description}

## Architecture Decision Records (ADRs)

### ADR-001: Technology Selection

**Context**: Need to select appropriate technologies for ${project.title.toLowerCase()}.

**Decision**: Selected the following stack:
${project.technologies.map(tech => `- ${tech}`).join('\n')}

**Consequences**:
- ✅ Proven enterprise technologies
- ✅ Strong community support
- ✅ Well-documented patterns
- ⚠️ Requires specific expertise (${domain.title})

### ADR-002: Architecture Pattern

**Context**: Define the architectural approach for this ${domain.title.toLowerCase()} solution.

**Decision**: [Document your specific architecture pattern here]

**Consequences**: [Document trade-offs and implications]

## Component Design

### High-Level Architecture

\`\`\`
[Add architecture diagram or ASCII art representation]
\`\`\`

### Components

1. **Component 1**
   - Purpose: [Description]
   - Technologies: [List]
   - Interfaces: [APIs/contracts]

2. **Component 2**
   - Purpose: [Description]
   - Technologies: [List]
   - Interfaces: [APIs/contracts]

## Data Flow

[Describe how data moves through the system]

## Security Considerations

- Authentication: [Method]
- Authorization: [Approach]
- Data protection: [Encryption, etc.]
- Network security: [Firewalls, VPNs, etc.]

## Scalability

- Horizontal scaling: [Strategy]
- Vertical scaling: [Limits]
- Bottlenecks: [Identified constraints]

## Technology Decisions

${project.technologies.map(tech => `### ${tech}\n\n**Why chosen**: [Rationale]\n**Alternatives considered**: [List]\n**Trade-offs**: [Analysis]`).join('\n\n')}

## References

- [Technology docs]
- [Best practices]
- [Related ADRs]

---

*Last updated: ${new Date().toISOString().split('T')[0]}*
`;
};

export const generateRunbook = (project: Project): string => {
  return `# ${project.title} - Runbook

## Day 2 Operations & Standard Operating Procedures

### Quick Links

- [Deployment Guide](./deployment-guide.md)
- [Playbook (Troubleshooting)](./playbook.md)
- [Architecture](./architecture.md)

## Routine Operations

### Daily Checks

- [ ] Verify all services are running
- [ ] Check error rates in monitoring dashboard
- [ ] Review overnight logs for anomalies
- [ ] Confirm backup completion

### Weekly Maintenance

- [ ] Review and apply security patches
- [ ] Check disk space and cleanup if needed
- [ ] Review access logs for security concerns
- [ ] Update documentation for any changes made

### Monthly Tasks

- [ ] Full system backup verification
- [ ] Review and rotate credentials
- [ ] Capacity planning review
- [ ] Dependency updates

## Common Procedures

### Restart Service

\`\`\`bash
# Check status
systemctl status <service-name>

# Restart
systemctl restart <service-name>

# Verify
systemctl status <service-name>
curl -f http://localhost:<port>/health || echo "Health check failed"
\`\`\`

### Check Logs

\`\`\`bash
# Recent logs
journalctl -u <service-name> -n 100

# Follow logs
journalctl -u <service-name> -f

# Specific time range
journalctl -u <service-name> --since "1 hour ago"
\`\`\`

### Scale Resources

[Document scaling procedures specific to your architecture]

### Backup & Restore

**Backup**:
\`\`\`bash
# [Add backup commands]
\`\`\`

**Restore**:
\`\`\`bash
# [Add restore commands]
\`\`\`

## Monitoring

### Key Metrics

${Object.entries(project.metrics || {}).map(([key, value]) => `- **${key}**: Target ${value}`).join('\n')}

### Dashboards

- Primary Dashboard: [Link]
- Infrastructure: [Link]
- Application: [Link]

### Alerts

| Alert | Severity | Threshold | Action |
|-------|----------|-----------|--------|
| CPU High | Warning | >80% for 5min | Investigate load |
| Disk Full | Critical | >90% | Clear space immediately |
| Service Down | Critical | Health check fail | Restart service |

## Change Management

### Making Changes

1. Create change request in [system]
2. Review with team
3. Test in staging
4. Schedule maintenance window if needed
5. Execute change
6. Verify success
7. Document in runbook

### Rollback Procedure

\`\`\`bash
# [Document rollback steps]
\`\`\`

## Contacts

- On-call: [Contact info]
- Team lead: [Contact info]
- Escalation: [Contact info]

## References

- [Related documentation]
- [External resources]

---

*Last updated: ${new Date().toISOString().split('T')[0]}*
`;
};

export const generatePlaybook = (project: Project): string => {
  return `# ${project.title} - Playbook

## Incident Response & Troubleshooting

### Severity Levels

- **SEV1 (Critical)**: Complete service outage, data loss
- **SEV2 (High)**: Major functionality impaired, degraded performance
- **SEV3 (Medium)**: Minor functionality issues, workarounds available
- **SEV4 (Low)**: Cosmetic issues, feature requests

## Common Issues

### Issue: Service Won't Start

**Symptoms**:
- Service fails to start
- Health check returns 500/503
- Errors in startup logs

**Diagnosis**:
\`\`\`bash
# Check service status
systemctl status <service>

# Check logs
journalctl -u <service> -n 50

# Verify dependencies
# [Add specific checks]
\`\`\`

**Resolution**:
1. Check configuration files for syntax errors
2. Verify dependencies are available
3. Check disk space
4. Review recent changes
5. Restore from last known good state if needed

**Escalation**: If not resolved in 15 minutes, escalate to senior engineer

---

### Issue: High CPU/Memory Usage

**Symptoms**:
- Server responsiveness degraded
- Monitoring alerts firing
- Slow response times

**Diagnosis**:
\`\`\`bash
# Check resource usage
top
htop

# Identify process
ps aux --sort=-%cpu | head
ps aux --sort=-%mem | head
\`\`\`

**Resolution**:
1. Identify resource-heavy process
2. Check for runaway processes or memory leaks
3. Restart service if safe to do so
4. Scale resources if sustained high load
5. Review recent deployments

---

### Issue: Connectivity Problems

**Symptoms**:
- Cannot reach service
- Timeout errors
- DNS resolution failures

**Diagnosis**:
\`\`\`bash
# Check network
ping <host>
curl -v <url>
traceroute <host>

# Check firewall
sudo iptables -L
sudo ufw status

# Check DNS
nslookup <domain>
dig <domain>
\`\`\`

**Resolution**:
1. Verify network connectivity
2. Check firewall rules
3. Verify DNS settings
4. Check load balancer health checks
5. Review security group rules (cloud)

---

## Incident Response Flow

1. **Detect**: Alert received or issue reported
2. **Assess**: Determine severity (SEV1-4)
3. **Respond**: Follow playbook for issue type
4. **Communicate**: Update stakeholders per severity
5. **Resolve**: Implement fix and verify
6. **Document**: Update incident log
7. **Review**: Post-incident review for SEV1/2

## Escalation Matrix

| Severity | Response Time | Escalate After | Escalate To |
|----------|---------------|----------------|-------------|
| SEV1 | Immediate | 15 minutes | Engineering Lead |
| SEV2 | 15 minutes | 1 hour | Team Lead |
| SEV3 | 1 hour | 4 hours | Team Lead |
| SEV4 | Next business day | - | Backlog |

## Communication Templates

### SEV1 Announcement

\`\`\`
INCIDENT: [Brief description]
STATUS: Investigating
IMPACT: [User-facing impact]
ETA: [Estimated resolution or next update in 30min]
\`\`\`

### Resolution Notice

\`\`\`
RESOLVED: [Brief description]
DURATION: [Start - end time]
ROOT CAUSE: [Summary]
PREVENTION: [Steps taken]
\`\`\`

## Post-Incident Review

Required for SEV1 and SEV2 incidents:

1. **Timeline**: Detailed event timeline
2. **Root Cause**: 5 Whys analysis
3. **Impact**: Quantified user/business impact
4. **Response**: What went well, what didn't
5. **Action Items**: Preventive measures with owners

## Tools & Resources

- Monitoring: [Dashboard links]
- Logs: [Log aggregation system]
- Runbook: [Link to runbook]
- Documentation: [Wiki/docs]

---

*Last updated: ${new Date().toISOString().split('T')[0]}*
`;
};

export const generateAllDocs = (project: Project): DocTemplate[] => {
  return [
    { filename: 'README.md', content: generateProjectReadme(project) },
    { filename: 'wiki/architecture.md', content: generateArchitectureDoc(project) },
    { filename: 'wiki/runbook.md', content: generateRunbook(project) },
    { filename: 'wiki/playbook.md', content: generatePlaybook(project) },
  ];
};

export const downloadDocumentation = (project: Project) => {
  const docs = generateAllDocs(project);

  docs.forEach(doc => {
    const blob = new Blob([doc.content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${project.folder}-${doc.filename.replace(/\//g, '-')}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });
};

# Security Hardening Checklist

**Purpose:** Comprehensive security hardening checklist based on CIS benchmarks and best practices
**Target:** 92%+ compliance with industry standards
**Review Frequency:** Quarterly

---

## System Hardening

### Operating System (Debian/Ubuntu)

#### Account Security

- [ ] Root login disabled via SSH (`PermitRootLogin no`)
- [ ] Password authentication disabled (`PasswordAuthentication no`)
- [ ] SSH key-only authentication enforced
- [ ] Failed login attempts logged and monitored
- [ ] Account lockout policy configured (fail2ban)
- [ ] Minimum password complexity requirements set
- [ ] Password expiration policy configured (90 days)
- [ ] Inactive account auto-disable (30 days)
- [ ] sudo access limited to approved users only
- [ ] sudoers file regularly audited

#### Network Security

- [ ] Firewall enabled (UFW/iptables)
- [ ] Default deny policy for incoming traffic
- [ ] Only required ports opened
- [ ] IPv6 disabled if not in use
- [ ] Network parameter hardening in sysctl:

  ```bash
  net.ipv4.conf.all.send_redirects = 0
  net.ipv4.conf.all.accept_redirects = 0
  net.ipv4.conf.all.accept_source_route = 0
  net.ipv4.icmp_echo_ignore_broadcasts = 1
  net.ipv4.icmp_ignore_bogus_error_responses = 1
  net.ipv4.tcp_syncookies = 1
  ```

- [ ] IP forwarding disabled (unless required for routing)
- [ ] Packet filtering configured (netfilter)

#### Filesystem Security

- [ ] Separate partitions for /tmp, /var, /var/log
- [ ] noexec, nodev, nosuid options on /tmp
- [ ] File integrity monitoring enabled (AIDE/Tripwire)
- [ ] World-writable files audited
- [ ] SUID/SGID binaries reviewed and minimized
- [ ] Filesystem encryption enabled for sensitive data (LUKS)

#### Service Hardening

- [ ] Unnecessary services disabled
- [ ] Services run with minimal privileges
- [ ] Service-specific user accounts (no shared accounts)
- [ ] Logging enabled for all services
- [ ] Service configuration files properly permissioned (640 or 600)
- [ ] Default passwords changed on all services
- [ ] Unused packages removed

#### Logging and Auditing

- [ ] auditd installed and configured
- [ ] All authentication events logged
- [ ] Privilege escalation logged
- [ ] File access to sensitive files logged
- [ ] Logs sent to centralized log server (Loki)
- [ ] Log retention policy enforced (30 days)
- [ ] Log integrity protected (read-only, signed)

---

## Application Hardening

### Docker Containers

#### Container Security

- [ ] Containers run as non-root user
- [ ] Read-only root filesystem where possible
- [ ] No privileged containers (unless absolutely necessary)
- [ ] Resource limits set (CPU, memory)
- [ ] Security options enabled:

  ```yaml
  security_opt:
    - no-new-privileges:true
    - apparmor=docker-default
    - seccomp=/path/to/seccomp/profile.json
  ```

- [ ] Capabilities dropped (drop: ALL, add only needed)
- [ ] Host filesystem mounts minimized
- [ ] Docker socket not mounted in containers

#### Image Security

- [ ] Images from trusted registries only
- [ ] Image signatures verified
- [ ] Vulnerability scanning enabled (Trivy/Clair)
- [ ] Base images regularly updated
- [ ] No secrets in Dockerfiles or images
- [ ] Multi-stage builds used to minimize attack surface
- [ ] Latest tag avoided (use specific versions)

#### Docker Daemon

- [ ] Docker daemon configured with TLS
- [ ] User namespace remapping enabled
- [ ] Live restore enabled
- [ ] Default bridge network not used
- [ ] Custom networks with encryption
- [ ] Content trust enabled (DOCKER_CONTENT_TRUST=1)

### Web Applications

#### Nginx Proxy Manager

- [ ] Strong SSL/TLS configuration (TLS 1.2+ only)
- [ ] Perfect Forward Secrecy enabled
- [ ] HSTS header enabled (max-age=31536000)
- [ ] Security headers configured:

  ```nginx
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  X-XSS-Protection: 1; mode=block
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=()
  Content-Security-Policy: default-src 'self'
  ```

- [ ] Rate limiting configured
- [ ] Request size limits enforced
- [ ] Directory listing disabled
- [ ] Access logs enabled
- [ ] Failed authentication attempts logged

#### Immich Photo Service

- [ ] Multi-factor authentication enabled
- [ ] Strong password policy enforced
- [ ] Session timeout configured (30 minutes)
- [ ] Upload file type restrictions
- [ ] File size limits enforced
- [ ] API rate limiting
- [ ] CORS properly configured
- [ ] Database credentials in secrets (not env files)

### Database Security

#### PostgreSQL

- [ ] Authentication via password files or vault
- [ ] SSL/TLS encryption for connections
- [ ] Least privilege access (application-specific users)
- [ ] No superuser for applications
- [ ] Row-level security enabled where appropriate
- [ ] Audit logging enabled (pgaudit)
- [ ] Default passwords changed
- [ ] Remote connections restricted by IP
- [ ] Database firewall rules configured

---

## Network Hardening

### VLAN Segmentation

- [ ] Management VLAN isolated from user traffic
- [ ] Default-deny firewall policy between VLANs
- [ ] Explicit allow rules documented
- [ ] Guest/IoT networks isolated
- [ ] No direct internet access from management VLAN

### Firewall Configuration

- [ ] Default deny for all traffic
- [ ] Explicit allow rules only for required services
- [ ] WAN to LAN traffic blocked (except established)
- [ ] Anti-spoofing rules configured
- [ ] Bogon networks blocked
- [ ] Rate limiting for SSH/VPN
- [ ] Geo-blocking for non-local services (optional)
- [ ] IDS/IPS enabled (Suricata/Snort)

### VPN Hardening

- [ ] Strong cryptography (ChaCha20-Poly1305 or AES-256-GCM)
- [ ] Pre-shared keys in use
- [ ] Regular key rotation (quarterly)
- [ ] Split tunneling disabled
- [ ] Kill switch enabled on clients
- [ ] DNS leak prevention
- [ ] VPN logs monitored for unauthorized access
- [ ] Inactive peers automatically removed

---

## Access Control

### Authentication

- [ ] Multi-factor authentication (MFA) on all admin interfaces
- [ ] Passkey/FIDO2 support enabled where possible
- [ ] Password manager required for all users
- [ ] Biometric authentication enabled on mobile
- [ ] SSO/LDAP integration for centralized auth (future)

### Authorization

- [ ] Role-based access control (RBAC) implemented
- [ ] Principle of least privilege enforced
- [ ] Regular access reviews (quarterly)
- [ ] Privileged access logging
- [ ] Just-in-time access for sensitive operations
- [ ] Service accounts have minimal permissions

### Credential Management

- [ ] Passwords stored in encrypted vault (Bitwarden/Vaultwarden)
- [ ] SSH keys protected with passphrase
- [ ] API keys rotated regularly
- [ ] Secrets not in version control
- [ ] Environment variables used for secrets
- [ ] Secrets encrypted at rest (SOPS/Vault)

---

## Monitoring and Detection

### Security Monitoring

- [ ] Failed authentication attempts monitored
- [ ] Unusual network traffic detected
- [ ] File integrity changes alerted
- [ ] Privilege escalation logged
- [ ] New service detection
- [ ] Port scan detection
- [ ] Brute force detection (fail2ban)
- [ ] Anomaly detection configured

### Vulnerability Management

- [ ] Automated vulnerability scanning (weekly)
- [ ] Patch management process defined
- [ ] Critical patches applied within 72 hours
- [ ] Security advisories subscribed to
- [ ] CVE tracking for all components
- [ ] Penetration testing (annual)

### Incident Detection

- [ ] SIEM or log aggregation configured (Loki)
- [ ] Security alerts go to dedicated channel
- [ ] Alert thresholds tuned (low false positive rate)
- [ ] Automated response for common threats
- [ ] Incident response runbook available
- [ ] Forensics capabilities available

---

## Data Protection

### Encryption

- [ ] Data encrypted at rest (ZFS encryption or LUKS)
- [ ] Data encrypted in transit (TLS 1.2+)
- [ ] Backup encryption enabled
- [ ] Full disk encryption on admin workstations
- [ ] Encryption keys properly managed
- [ ] Key rotation schedule defined

### Backup Security

- [ ] Backups stored offline (air-gapped)
- [ ] Backup integrity verification
- [ ] Backup encryption enabled
- [ ] Backup retention policy enforced
- [ ] Backup restore regularly tested
- [ ] Immutable backups (ransomware protection)

### Data Minimization

- [ ] PII identified and minimized
- [ ] Data retention policy enforced
- [ ] Old logs automatically purged
- [ ] Sensitive data redacted in logs
- [ ] Data classification implemented
- [ ] GDPR compliance (if applicable)

---

## Compliance and Auditing

### Security Audits

- [ ] Quarterly security configuration review
- [ ] Annual penetration testing
- [ ] CIS benchmark scanning
- [ ] OWASP Top 10 assessment
- [ ] Security findings tracked and remediated

### Documentation

- [ ] Network topology diagram current
- [ ] Asset inventory maintained
- [ ] Service dependencies documented
- [ ] Access control matrix current
- [ ] Incident response plan documented
- [ ] Disaster recovery plan documented
- [ ] Security policies documented

### Change Management

- [ ] Security review for all changes
- [ ] Change approval process enforced
- [ ] Rollback plans documented
- [ ] Post-change security validation
- [ ] Change log maintained

---

## Physical Security

### Hardware

- [ ] Server room access restricted
- [ ] Physical access logged
- [ ] Console access disabled when not needed
- [ ] BIOS/UEFI password set
- [ ] Boot from USB disabled
- [ ] Secure boot enabled (if supported)

### Media

- [ ] Backup media encrypted
- [ ] Backup media stored securely
- [ ] Old drives securely wiped before disposal
- [ ] Sensitive documents shredded
- [ ] USB ports disabled on critical systems

---

## Compliance Status Dashboard

### Current Status (as of initial deployment)

| Category | Compliant | Partially Compliant | Non-Compliant | Score |
|----------|-----------|---------------------|---------------|-------|
| OS Hardening | TBD | TBD | TBD | TBD% |
| Application Security | TBD | TBD | TBD | TBD% |
| Network Security | TBD | TBD | TBD | TBD% |
| Access Control | TBD | TBD | TBD | TBD% |
| Monitoring | TBD | TBD | TBD | TBD% |
| Data Protection | TBD | TBD | TBD% |
| **Overall** | **TBD** | **TBD** | **TBD** | **TBD%** |

**Target:** ≥ 92% overall compliance

---

## Automated Compliance Checking

```bash
#!/bin/bash
# Security compliance check script
# Run weekly via cron

# OS Hardening
echo "Checking OS hardening..."
grep "PermitRootLogin no" /etc/ssh/sshd_config || echo "FAIL: Root login enabled"
grep "PasswordAuthentication no" /etc/ssh/sshd_config || echo "FAIL: Password auth enabled"

# Firewall status
ufw status | grep "Status: active" || echo "FAIL: Firewall not active"

# Failed login attempts
lastb | wc -l
echo "Failed login attempts in last 24h: $(lastb -s yesterday | wc -l)"

# World-writable files
echo "Checking for world-writable files..."
find / -xdev -type f -perm -0002 -ls 2>/dev/null | wc -l

# SUID binaries
echo "SUID binaries count: $(find / -perm -4000 2>/dev/null | wc -l)"

# Docker security
docker info --format '{{.SecurityOptions}}'

# SSL certificate expiry
echo "Checking SSL certificates..."
echo | openssl s_client -connect photos.homelab.local:443 2>/dev/null | openssl x509 -noout -dates

# Backup status
echo "Last backup: $(stat -c %y /mnt/backups/*.vma.zst | tail -1)"

echo "Compliance check complete. Review output above."
```

---

## Remediation Priorities

### Critical (Fix within 24 hours)

- Remote root access enabled
- No firewall configured
- Default passwords in use
- No backup configured

### High (Fix within 1 week)

- Missing security patches
- Weak SSH configuration
- No audit logging
- Unencrypted backups

### Medium (Fix within 1 month)

- Non-compliant file permissions
- Missing security headers
- No MFA on admin accounts
- Outdated software versions

### Low (Fix as time permits)

- Documentation gaps
- Non-critical hardening items
- Nice-to-have security features

---

## Related Documentation

- [Security Incident Response](./security-incident-response.md)
- [Access Control Policy](./access-control-policy.md)
- [Patch Management Procedure](../procedures/patch-management.md)
- [Security Monitoring Guide](./security-monitoring.md)

---

**Last Updated:** 2024-12-16
**Owner:** Samuel Jackson
**Review Frequency:** Quarterly
**Next Review:** Q1 2026

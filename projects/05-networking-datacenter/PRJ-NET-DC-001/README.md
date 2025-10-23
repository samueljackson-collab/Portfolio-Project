# Active Directory Design & Automation

This workspace captures the hybrid Active Directory lab used to validate GPOs, DSC policies, and
Ansible automations before pushing changes into production.

## Contents
- `automation/ad-bootstrap.yml` — Ansible playbook that installs AD DS and promotes the initial domain controller.
- `design/network-topology.md` — Textual network design notes for the lab environment.
- `docs/` — Store runbooks, change logs, and test evidence.

## Quick Start
1. Define Windows hosts in `inventory/domain.yml` (create with `domain_controllers` group).
2. Store the DSRM safe mode password in Ansible Vault (`vault_safemode_password`).
3. Execute `ansible-playbook -i inventory/domain.yml automation/ad-bootstrap.yml`.
4. Validate domain provisioning and document results in `docs/provisioning-report.md`.

## Next Steps
- Add Desired State Configuration scripts for OU/GPO baseline.
- Integrate with Azure AD Connect for hybrid identity scenarios.
- Capture network diagrams and site-to-site VPN configuration in `design/`.

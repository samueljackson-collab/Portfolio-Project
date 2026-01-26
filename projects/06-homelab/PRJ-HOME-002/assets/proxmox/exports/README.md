# Proxmox VM/LXC Exports

Sanitized export manifests for virtual machines and containers. These files summarize what was exported, where it was staged, and how the exports are validated before storage or transfer.

## Contents
- `vm-export-manifest.md` - VM export inventory (QEMU VMs).
- `lxc-export-manifest.md` - LXC export inventory.

## Usage Notes
- Export artifacts are stored in a restricted staging share and checksum-validated.
- UUIDs, MACs, and hostnames are sanitized for portfolio use.
- Restore validation is documented in `../../logs/restore-test-results.md`.

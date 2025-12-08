# Threat Model

## Assets
- User session data and application database.
- TLS keys on the load balancer.
- Patroni cluster credentials.

## Threats
- TLS key leakage leading to MITM.
- Split-brain database state from control-plane compromise.
- Path traversal or injection through web tier reaching DB.

## Mitigations
- Store certs in encrypted volume; rotate quarterly with audit logs.
- Patroni configured with authentication and firewall rules; weekly failover drills to verify quorum.
- NGINX WAF rules + parameterized queries; AppSec tests in CI.

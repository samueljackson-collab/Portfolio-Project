# P16 — Zero-Trust Cloud Architecture

## Overview
Zero-trust security architecture with mTLS, JWT policies, network segmentation, and comprehensive threat modeling. Demonstrates modern security practices, identity-based access, and defense-in-depth strategies.

## Key Outcomes
- [x] Zero-trust architecture design
- [x] mTLS certificate management
- [x] JWT authentication and authorization policies
- [x] Network micro-segmentation
- [x] Threat model documentation
- [x] Security policy templates

## Architecture

```mermaid
flowchart TB
    User[User/Service]
    IAM[Identity Provider<br/>IAM/OAuth2]
    Gateway[API Gateway<br/>JWT Validation]

    subgraph Zero Trust Network
        Service1[Service A<br/>mTLS]
        Service2[Service B<br/>mTLS]
        Service3[Service C<br/>mTLS]
    end

    Vault[Secret Vault]
    Monitor[Security Monitoring]

    User --> IAM --> Gateway
    Gateway --> Service1 & Service2 & Service3
    Service1 & Service2 & Service3 --> Vault
    Service1 & Service2 & Service3 --> Monitor
```

## Quickstart

```bash
make setup
make generate-certs
make deploy-policies
```

## Configuration

| Env Var | Purpose | Example | Required |
|---------|---------|---------|----------|
| `CA_CERT_PATH` | CA certificate | `/certs/ca.crt` | Yes |
| `JWT_SECRET` | JWT signing key | `<secret>` | Yes |
| `VAULT_ADDR` | Vault address | `https://vault:8200` | Yes |

## Testing

```bash
make test
make verify-mtls
```

## References

- [Zero Trust Architecture](https://www.nist.gov/publications/zero-trust-architecture)
- [mTLS Best Practices](https://www.cloudflare.com/learning/access-management/what-is-mutual-tls/)

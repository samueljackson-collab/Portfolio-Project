# Project 21 · Quantum-Safe Cryptography Platform

## 📌 Overview
Introduce quantum-resistant cryptography across services by piloting hybrid TLS, key management, and secure storage workflows. The initiative validates interoperability with existing PKI while preparing for post-quantum standards.

## 🏗️ Architecture Highlights
- **Hybrid TLS termination** using NIST PQC finalists (Kyber, Dilithium) alongside classical ECDSA certificates via Open Quantum Safe (OQS) libraries.
- **Centralized key management** with HashiCorp Vault plugins supporting PQC algorithms and automated rotation policies.
- **Secure messaging** leveraging liboqs integrations in gRPC services, with feature flags for progressive rollout.
- **Cryptographic agility** built into service configuration, allowing runtime selection of cipher suites and algorithms.
- **Compliance monitoring** generating reports for NIST SP 800-208 alignment and internal security assessments.

```
Clients --> Envoy Edge Proxy (Hybrid TLS) --> Services (gRPC + PQC) --> Vault PQC KMS --> Secure Storage
```

## 🚀 Implementation Steps
1. **Compile OQS-OpenSSL** and integrate with Envoy proxy containers for hybrid certificate support.
2. **Provision Vault** with the `vault-pqc-engine` plugin to generate Kyber key material and manage Dilithium signatures.
3. **Update service mesh** to advertise PQC cipher suites via SDS (Secret Discovery Service) and enforce minimum security policies.
4. **Instrument clients** with feature flags enabling PQC handshake opt-in, gradually rolling out to internal teams.
5. **Implement key rotation** pipelines rotating hybrid certificates quarterly with automated verification and rollback.
6. **Conduct interoperability testing** with legacy clients, capturing metrics on handshake performance and compatibility issues.
7. **Publish compliance dashboards** summarizing adoption, key age distribution, and cryptographic configuration drift.

## 🧩 Key Components
```yaml
# projects/21-quantum-safe-cryptography/envoy/hybrid-tls.yaml
static_resources:
  listeners:
  - name: https_listener
    address:
      socket_address:
        address: 0.0.0.0
        port_value: 8443
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          stat_prefix: ingress_https
          route_config:
            name: local_route
            virtual_hosts:
            - name: backend
              domains: ["*"]
              routes:
              - match: { prefix: "/" }
                route: { cluster: backend }
      transport_socket:
        name: envoy.transport_sockets.tls
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.DownstreamTlsContext
          common_tls_context:
            tls_certificates:
            - certificate_chain: { filename: "/etc/tls/hybrid_cert.pem" }
              private_key: { filename: "/etc/tls/hybrid_key.pem" }
            tls_params:
              cipher_suites: ["TLS_AES_256_GCM_SHA384", "TLS_AKEP256F_AESGCM_SHA384"]
```

## 🛡️ Fail-safes & Operations
- **Dual certificate strategy** ensuring classical TLS support remains available during PQC rollouts.
- **Automated regression tests** validating handshake success across supported clients before promoting to production.
- **Incident response playbook** detailing steps to revert to classical cryptography in case of interoperability issues.
- **Continuous education** with security champions program and documentation updates for developers and auditors.

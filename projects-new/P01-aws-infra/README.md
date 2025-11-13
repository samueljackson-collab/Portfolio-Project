# AWS Infrastructure Automation

**Project ID:** P01
**Status:** 🟢 Active | **Version:** 1.0.0 | **Last Updated:** 2025-11-10

## Overview

AWS Infrastructure Automation implements enterprise-grade solutions following the standards defined in the [Enterprise Engineer's Handbook](../../docs/PRJ-MASTER-HANDBOOK/README.md).

## Quick Start

```bash
# 1. Install dependencies
make install

# 2. Configure environment
cp .env.example .env
# Edit .env with your configuration

# 3. Run tests
make test

# 4. Deploy
make deploy
```

## Documentation

- [📘 HANDBOOK](docs/HANDBOOK.md) - Engineering standards and best practices
- [📗 RUNBOOK](docs/RUNBOOK.md) - Operational procedures and troubleshooting
- [📙 PLAYBOOK](docs/PLAYBOOK.md) - Step-by-step implementation guide
- [🏗️ ARCHITECTURE](docs/ARCHITECTURE.md) - System design and components

## Project Structure

```
P01-aws-infra/
├── README.md                 # This file
├── Makefile                  # Build and deployment automation
├── .env.example              # Example configuration
├── docs/                     # Documentation
│   ├── HANDBOOK.md
│   ├── RUNBOOK.md
│   ├── PLAYBOOK.md
│   └── ARCHITECTURE.md
├── src/                      # Source code
├── scripts/                  # Automation scripts
├── tests/                    # Test suite
├── infrastructure/           # IaC configurations
│   ├── terraform/
│   └── k8s/
└── ci/                       # CI/CD workflows
```

## Application Components

- **FastAPI control plane** exposing `/health`, `/metrics`, `/aws/*`, and `/security/posture` endpoints.
- **Security middleware** enforcing API keys plus modern security headers (CSP, HSTS, referrer policy).
- **AWS SDK integrations** for S3 inventory, Secrets Manager metadata, and CloudWatch metric publishing.
- **Observability hooks** via Prometheus metrics counters/histograms and structured JSON logging with `structlog`.

## Features

- ✅ Enterprise-grade implementation
- ✅ Comprehensive test coverage (≥80%)
- ✅ Infrastructure as Code
- ✅ CI/CD automation
- ✅ Production-ready monitoring (Prometheus rules, Grafana dashboards, OpenTelemetry collector config)
- ✅ Security best practices (API key enforcement, secrets management, Terraform guardrails)

## Requirements

- Python 3.9+
- Terraform 1.5+
- Docker 20.10+
- kubectl 1.27+

## Testing

```bash
# Run all tests
make test

# Run specific test suite
make test-unit
make test-integration
make test-e2e
```

## Deployment

```bash
# Deploy to development
make deploy ENV=dev

# Deploy to staging
make deploy ENV=staging

# Deploy to production
make deploy ENV=prod
```

## Monitoring

- **Metrics:** Prometheus scrape endpoint exposed at `/metrics` plus alert rules in `infrastructure/monitoring/prometheus-rules.yaml`
- **Logs:** Structured JSON logging to stdout for ingestion into CloudWatch Logs or Loki
- **Traces:** OpenTelemetry Collector configuration supplied (`infrastructure/monitoring/otel-collector-config.yaml`); application auto-instrumentation is a roadmap task
- **Dashboards:** Ready-to-import Grafana dashboard JSON in `infrastructure/monitoring/grafana-dashboard.json`

## Security

- 🔒 API key enforcement + hardened headers for every protected endpoint
- 🔒 Automated AWS guardrails through Terraform (encryption, public access blocks, log retention)
- 🔒 Secrets management via AWS Secrets Manager metadata surfaced through `/secrets/{name}`
- 🔵 OWASP Top 10 + CIS Level 2 audit evidence is tracked as a roadmap item while automated checks are implemented in CI

## Contributing

1. Follow the [Engineer's Handbook](../../docs/PRJ-MASTER-HANDBOOK/README.md)
2. Create feature branch: `git checkout -b feature/your-feature`
3. Run tests: `make test`
4. Submit PR with comprehensive description

## Support

- **Issues:** Open GitHub issue
- **Documentation:** See `docs/` directory
- **Runbook:** See `docs/RUNBOOK.md` for troubleshooting

## License

Proprietary - All Rights Reserved

---

**Maintained by:** Platform Engineering Team
**Last Review:** 2025-11-10

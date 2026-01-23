# Project 21: Quantum-Safe Cryptography

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


## Live Deployment
| Detail | Value |
| --- | --- |
| Live URL | `https://21-quantum-safe-cryptography.staging.portfolio.example.com` |
| DNS | `21-quantum-safe-cryptography.staging.portfolio.example.com` → `CNAME portfolio-gateway.staging.example.net` |
| Deployment environment | Staging (AWS us-east-1, containerized services; IaC in `terraform/`, `infra/`, or `deploy/` for this project) |

### Deployment automation
- **CI/CD:** GitHub Actions [`/.github/workflows/ci.yml`](../../.github/workflows/ci.yml) gates builds; [`/.github/workflows/deploy-portfolio.yml`](../../.github/workflows/deploy-portfolio.yml) publishes the staging stack.
- **Manual steps:** Follow the project Quick Start/Runbook instructions in this README to build artifacts, apply IaC, and validate health checks.

### Monitoring
- **Prometheus:** `https://prometheus.staging.portfolio.example.com` (scrape config: `prometheus/prometheus.yml`)
- **Grafana:** `https://grafana.staging.portfolio.example.com` (dashboard JSON: `grafana/dashboards/*.json`)

### Live deployment screenshots
Live deployment dashboard screenshot stored externally.


## 📊 Portfolio Status Board

🟢 Done · 🟠 In Progress · 🔵 Planned

**Current Status:** 🟢 Done (Implemented)


## Overview
Hybrid key exchange service that combines Kyber KEM with classical ECDH for defense-in-depth.

## Usage
```bash
pip install -r requirements.txt
python src/key_exchange.py
```

## Evidence & Benchmarks
Evidence from key exchange and signing flows is captured under `evidence/`, including protocol logs, test outputs, and benchmark data.

- Protocol logs: [`evidence/protocol-logs.txt`](evidence/protocol-logs.txt)
- Test output: [`evidence/test-output.txt`](evidence/test-output.txt)
- Benchmark summary: [`evidence/benchmark-summary.md`](evidence/benchmark-summary.md) - Contains latency and payload comparisons.
- Benchmark data: [`evidence/performance-benchmarks.csv`](evidence/performance-benchmarks.csv), [`evidence/performance-benchmarks.json`](evidence/performance-benchmarks.json)

> Note: If liboqs is not available, benchmarks fall back to the built-in placeholders (see logs for warnings).



## Code Generation Prompts

This section contains AI-assisted code generation prompts that can help you recreate or extend project components. These prompts are designed to work with AI coding assistants like Claude, GPT-4, or GitHub Copilot.

### Quantum Computing

#### 1. Quantum Circuit
```
Create a Qiskit quantum circuit that implements Grover's algorithm for searching an unsorted database, including oracle construction and amplitude amplification
```

#### 2. Quantum Simulation
```
Generate a quantum simulation using Cirq that models a quantum system's evolution, measures observables, and visualizes state probabilities
```

#### 3. Hybrid Algorithm
```
Write a variational quantum eigensolver (VQE) implementation that combines quantum circuits with classical optimization for molecular energy calculations
```

### How to Use These Prompts

1. **Copy the prompt** from the code block above
2. **Customize placeholders** (replace [bracketed items] with your specific requirements)
3. **Provide context** to your AI assistant about:
   - Your development environment and tech stack
   - Existing code patterns and conventions in this project
   - Any constraints or requirements specific to your use case
4. **Review and adapt** the generated code before using it
5. **Test thoroughly** and adjust as needed for your specific scenario

### Best Practices

- Always review AI-generated code for security vulnerabilities
- Ensure generated code follows your project's coding standards
- Add appropriate error handling and logging
- Write tests for AI-generated components
- Document any assumptions or limitations
- Keep sensitive information (credentials, keys) in environment variables

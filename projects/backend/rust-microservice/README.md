# High-Performance Rust Microservice

## Overview
Rust-based microservice delivering latency-sensitive operations such as analytics aggregation or recommendation scoring. Built with Axum/Tonic and async runtime (Tokio).

## Architecture
- Offers both REST (Axum) and gRPC (Tonic) endpoints.
- Connects to PostgreSQL/Redis for stateful operations; integrates with Kafka for streaming.
- Implements circuit breakers and retries using Tower middleware.

## Development
1. Install Rust toolchain via rustup (`stable` + `clippy`, `rustfmt`).
2. Run tests: `cargo test`.
3. Lint: `cargo fmt --check`, `cargo clippy --all-targets -- -D warnings`.
4. Start service: `cargo run --bin service` with configuration from `config/default.toml`.

## Performance & Observability
- Benchmarks using Criterion stored under `benches/`.
- Metrics via Prometheus exporter; tracing via `tracing` crate output to OTLP collector.
- Load tests using k6 or Locust hitting REST/gRPC endpoints.

## Security
- mTLS between services via Rustls.
- Input validation and rate limiting at Tower layer.
- Supply chain security with cargo-deny and SBOM generation (CycloneDX).

## Deployment
- Containerized with multi-stage Dockerfile (Rust builder + distroless runtime).
- Deploys using Helm chart or serverless containers (AWS Fargate). Rolling updates with zero downtime.


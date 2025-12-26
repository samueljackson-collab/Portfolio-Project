# Custom Prometheus Exporter

A configurable Prometheus exporter written in Go that polls APIs, parses files, and executes SQL queries to expose custom metrics.

## Features

- Prometheus client library usage with custom collectors
- HTTP `/metrics` endpoint and `/healthz` health check
- Gauge, Counter, Histogram, and Summary metric types
- YAML configuration with environment overrides
- Feature flags, metric filtering, and scrape interval tuning
- Structured logging and graceful shutdown
- Docker image, systemd unit, Helm chart, ServiceMonitor

## Quick start

```bash
cp configs/config.example.yaml configs/config.yaml
make run
```

## Documentation

- [Installation guide](docs/installation.md)
- [Configuration reference](docs/configuration.md)
- [Metrics reference](docs/metrics.md)
- [Troubleshooting](docs/troubleshooting.md)

## Development

```bash
go test ./...
```

## Releases

Binary releases can be built with `goreleaser` using the included `.goreleaser.yaml`.

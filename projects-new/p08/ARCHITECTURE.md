# Architecture
- **Mock Producer**: publishes sample API payloads to a local bus for replay.
- **Test Runner**: Python/pytest executes contract and performance checks.
- **Mock Consumer**: echoes responses and exposes metrics to Prometheus.
- **Kubernetes Manifests**: deploy mocks and runner as Jobs for CI pipelines.

```
[Scenario YAML] -> [Producer] -> [Mock API] -> [Tests] -> [Metrics/Dashboards]
```

## Environment
- Docker Compose for local iteration
- Kubernetes (namespace `api-testing`) for CI smoke suites

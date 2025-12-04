# Architecture

## Components
- **Mock Producer**: Serves sample REST endpoints based on OpenAPI spec.
- **Test Runner (Newman)**: Executes Postman collections with environment-specific variables.
- **Schema Validator**: Ensures responses match published JSON Schemas.
- **Report Consumer**: Aggregates Newman JUnit/JSON outputs into KPI dashboard seed data.

```
[OpenAPI Spec] -> [Mock Producer] <-[Newman Collections]-> [Report Consumer]
                                   \--> [Schema Validator]
```

## Deployment Modes
- **Local**: Node/Express mock server plus Newman CLI.
- **Compose**: Bundles mock server, runner, and report consumer for CI friendliness.
- **Kubernetes**: Kustomize overlays with ConfigMaps for environments and secrets for auth tokens.

## Data Contracts
- Request/response schemas stored in `producer/schemas/*.json`.
- Golden examples in `producer/examples/` used for snapshot comparisons.

## Security
- API keys injected via environment variables; never committed.
- TLS termination handled by ingress; mock server supports HTTPS in overlays.

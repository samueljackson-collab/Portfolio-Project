# Threat Model

## Assets
- API traffic and todo data
- API key secret

## Threats
- Unauthorized access without API key enforcement.
- Injection via todo payloads.
- Exposed metrics endpoint leaking data.

## Mitigations
- Enforce `X-API-Key` when configured.
- Validate payloads using Pydantic models.
- Expose metrics on separate port with network policies in Kubernetes overlays.

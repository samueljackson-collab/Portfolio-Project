# Monitoring Strategy

## Metrics
- **Backend:** Collect request latency, throughput, and error rates using Prometheus instrumentation.
- **Frontend:** Capture Core Web Vitals via browser Performance APIs and forward to telemetry endpoint.

## Alerts
- Backend health check failures >3 minutes trigger PagerDuty incident.
- Frontend build pipeline failures notify engineering Slack channel.

## Dashboards
- Service availability dashboard: uptime, latency, error budget burn.
- Release dashboard: deployment frequency, lead time, change failure rate.

## Logging
- Structured JSON logs emitted by FastAPI using `logging.config` and shipped via Fluent Bit.
- Frontend console logs suppressed in production builds; warnings forwarded to log aggregator.

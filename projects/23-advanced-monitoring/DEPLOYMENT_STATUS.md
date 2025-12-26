# Deployment Status — Project 23: Advanced Monitoring & Observability

**Status:** Targeted for initial live deployment

## Environment
- **Environment:** Production (Demo)
- **Deployment date:** 2025-02-14 (planned)

## Live URLs
- **Grafana:** https://monitoring.example.com/grafana
- **Prometheus:** https://monitoring.example.com/prometheus
- **Alertmanager:** https://monitoring.example.com/alertmanager
- **Health check:** https://monitoring.example.com/healthz

## Deployment artifacts & logs
- `deployments/2025-02-14/docker-compose.log`
- `deployments/2025-02-14/stack-health.json`
- `deployments/2025-02-14/release-notes.md`

## Verification steps
1. `curl -fsSL https://monitoring.example.com/healthz`
2. `curl -fsSL https://monitoring.example.com/grafana/api/health`
3. `curl -fsSL https://monitoring.example.com/prometheus/-/healthy`

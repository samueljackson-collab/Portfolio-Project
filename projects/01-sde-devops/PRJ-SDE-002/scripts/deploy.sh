#!/bin/bash
# Monitoring Stack Deployment Script
# Purpose: Automated deployment with validation and rollback capability
# Usage: ./deploy.sh [start|stop|restart|validate|backup|restore]

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"
ENV_FILE="${PROJECT_ROOT}/.env"
BACKUP_DIR="${PROJECT_ROOT}/backups"

log_info() { echo -e "${GREEN}[INFO]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

die() { log_error "$1"; exit 1; }

check_prerequisites() {
  command -v docker >/dev/null 2>&1 || die "Docker is required"
  command -v docker compose >/dev/null 2>&1 || die "Docker Compose plugin missing"
  [[ -f "$ENV_FILE" ]] || die ".env file missing; copy from .env.example"
  log_info "Prerequisites satisfied"
}

validate_config() {
  log_info "Validating Prometheus configuration"
  docker run --rm -v "${PROJECT_ROOT}/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml" prom/prometheus:v2.48.0 promtool check config /etc/prometheus/prometheus.yml || die "Prometheus config invalid"
  log_info "Validating alert rules"
  docker run --rm -v "${PROJECT_ROOT}/prometheus:/prometheus" prom/prometheus:v2.48.0 promtool check rules /prometheus/alerts/rules.yml || die "Alert rules invalid"
  log_info "Validating Alertmanager configuration"
  docker run --rm -v "${PROJECT_ROOT}/alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml" prom/alertmanager:v0.26.0 amtool check-config /etc/alertmanager/alertmanager.yml || die "Alertmanager config invalid"
  log_info "Validating Grafana dashboard JSON"
  python -m json.tool "${PROJECT_ROOT}"/grafana/dashboards/*.json >/dev/null || die "Grafana dashboards not valid JSON"
  log_info "Validation complete"
}

backup_data() {
  mkdir -p "$BACKUP_DIR"
  ts=$(date +%Y%m%d-%H%M%S)
  log_info "Backing up volumes to ${BACKUP_DIR}/${ts}.tar.gz"
  docker run --rm \
    -v prometheus_data:/volumes/prometheus_data:ro \
    -v grafana_data:/volumes/grafana_data:ro \
    -v loki_data:/volumes/loki_data:ro \
    -v alertmanager_data:/volumes/alertmanager_data:ro \
    -v "$BACKUP_DIR":/backup \
    alpine:3 sh -c "cd /volumes && tar -czf /backup/${ts}.tar.gz ." || die "Backup failed"
  log_info "Backup complete"
}

restore_backup() {
  archive="$1"
  [[ -f "$archive" ]] || die "Backup archive not found"
  log_info "Restoring from $archive"
  docker run --rm \
    -v prometheus_data:/volumes/prometheus_data \
    -v grafana_data:/volumes/grafana_data \
    -v loki_data:/volumes/loki_data \
    -v alertmanager_data:/volumes/alertmanager_data \
    -v "$archive":/backup.tar.gz \
    alpine:3 sh -c "cd /volumes && tar -xzf /backup.tar.gz" || die "Restore failed"
  log_info "Restore complete"
}

deploy_stack() {
  check_prerequisites
  validate_config
  log_info "Pulling latest images"
  docker compose -f "$COMPOSE_FILE" pull
  log_info "Starting stack"
  docker compose -f "$COMPOSE_FILE" up -d
  log_info "Waiting for services to report healthy"
  sleep 10
  docker compose -f "$COMPOSE_FILE" ps
}

stop_stack() {
  log_warn "Stopping stack"
  docker compose -f "$COMPOSE_FILE" down
}

restart_stack() {
  stop_stack
  deploy_stack
}

health_check() {
  "${SCRIPT_DIR}/health-check.sh"
}

case "${1:-}" in
  start)
    deploy_stack ;;
  stop)
    stop_stack ;;
  restart)
    restart_stack ;;
  validate)
    validate_config ;;
  backup)
    backup_data ;;
  restore)
    restore_backup "${2:-}" ;;
  health-check)
    health_check ;;
  *)
    echo "Usage: $0 [start|stop|restart|validate|backup|restore|health-check]" ;;
esac

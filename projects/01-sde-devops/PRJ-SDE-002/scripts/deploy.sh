#!/bin/bash
# Monitoring Stack Deployment Script
# Purpose: Automated deployment with validation, backup, and rollback capability.
# Usage: ./deploy.sh [start|stop|restart|validate|backup|restore|health]

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

check_prerequisites() {
  command -v docker >/dev/null || { log_error "docker not installed"; exit 1; }
  command -v docker compose >/dev/null || { log_error "docker compose plugin required"; exit 1; }
  [[ -f "$ENV_FILE" ]] || { log_error ".env missing at $ENV_FILE"; exit 1; }
  log_info "Prerequisites satisfied"
}

validate_config() {
  log_info "Validating Prometheus configuration"
  docker run --rm -v "${PROJECT_ROOT}/prometheus:/etc/prometheus" prom/prometheus:v2.48.0 \
    --config.file=/etc/prometheus/prometheus.yml --config.check-config
  log_info "Validating Alertmanager configuration"
  docker run --rm -v "${PROJECT_ROOT}/alertmanager:/etc/alertmanager" prom/alertmanager:v0.26.0 \
    check-config /etc/alertmanager/alertmanager.yml
  log_info "Validating alert rules syntax via Prometheus"
  docker run --rm -v "${PROJECT_ROOT}/prometheus:/etc/prometheus" prom/prometheus:v2.48.0 \
    --config.file=/etc/prometheus/prometheus.yml --config.check-config
  log_info "Validating Grafana dashboard JSON"
  python -m json.tool "${PROJECT_ROOT}/grafana/dashboards"/*.json >/dev/null
  log_info "Configuration validation complete"
}

backup_data() {
  mkdir -p "$BACKUP_DIR"
  ts=$(date +%Y%m%d-%H%M%S)
  log_info "Creating backup ${ts}"
  docker compose -f "$COMPOSE_FILE" -p monitoring ps >/dev/null 2>&1 || true
  for volume in prometheus_data grafana_data loki_data alertmanager_data; do
    archive="${BACKUP_DIR}/${volume}-${ts}.tar.gz"
    log_info "Backing up volume $volume to $archive"
    docker run --rm -v ${volume}:/data -v "${BACKUP_DIR}:/backup" alpine \
      sh -c "cd /data && tar -czf /backup/$(basename $archive) ."
  done
  log_info "Backup complete"
}

deploy_stack() {
  log_info "Pulling images"
  docker compose -f "$COMPOSE_FILE" pull
  log_info "Deploying stack"
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
  log_info "Waiting for health checks"
  sleep 20
  docker compose -f "$COMPOSE_FILE" ps
}

stop_stack() {
  log_info "Stopping stack"
  docker compose -f "$COMPOSE_FILE" down
}

restart_stack() {
  stop_stack
  deploy_stack
}

health_check() {
  "$SCRIPT_DIR/health-check.sh"
}

restore_backup() {
  local backup_file=${1:-}
  [[ -f "$backup_file" ]] || { log_error "Backup file required"; exit 1; }
  for volume in prometheus_data grafana_data loki_data alertmanager_data; do
    log_info "Restoring $volume from $backup_file"
    docker run --rm -v ${volume}:/data -v "$(dirname "$backup_file"):/backup" alpine \
      sh -c "cd /data && tar -xzf /backup/$(basename $backup_file)"
  done
  log_info "Restore complete"
}

case "${1:-}" in
  start)
    check_prerequisites
    validate_config
    deploy_stack
    ;;
  stop)
    stop_stack
    ;;
  restart)
    restart_stack
    ;;
  validate)
    check_prerequisites
    validate_config
    ;;
  backup)
    check_prerequisites
    backup_data
    ;;
  restore)
    check_prerequisites
    restore_backup "$2"
    ;;
  health)
    check_prerequisites
    health_check
    ;;
  *)
    echo "Usage: $0 [start|stop|restart|validate|backup|restore|health]"
    exit 1
    ;;
esac

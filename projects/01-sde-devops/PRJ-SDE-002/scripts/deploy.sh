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

check_prerequisites() {
  command -v docker >/dev/null 2>&1 || { log_error "Docker not installed"; exit 1; }
  command -v docker-compose >/dev/null 2>&1 || { log_error "docker-compose plugin required"; exit 1; }
  [[ -f "$ENV_FILE" ]] || { log_error ".env file missing"; exit 1; }
  log_info "Prerequisites validated"
}

validate_config() {
  log_info "Validating Prometheus configuration"
  docker run --rm -v "${PROJECT_ROOT}/prometheus:/etc/prometheus" prom/prometheus:v2.48.0 promtool check config /etc/prometheus/prometheus.yml
  log_info "Validating alert rules"
  docker run --rm -v "${PROJECT_ROOT}/prometheus:/etc/prometheus" prom/prometheus:v2.48.0 promtool check rules /etc/prometheus/alerts/rules.yml
  log_info "Validating Alertmanager configuration"
  docker run --rm -v "${PROJECT_ROOT}/alertmanager:/etc/alertmanager" prom/alertmanager:v0.26.0 amtool check-config /etc/alertmanager/alertmanager.yml
  log_info "Validating Grafana dashboards JSON"
  jq empty ${PROJECT_ROOT}/grafana/dashboards/*.json
}

backup_data() {
  mkdir -p "$BACKUP_DIR"
  TS=$(date +%Y%m%d-%H%M%S)
  log_info "Backing up volumes"
  docker run --rm -v prometheus_data:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/prometheus-${TS}.tgz -C /data .
  docker run --rm -v grafana_data:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/grafana-${TS}.tgz -C /data .
  docker run --rm -v loki_data:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/loki-${TS}.tgz -C /data .
  docker run --rm -v alertmanager_data:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/alertmanager-${TS}.tgz -C /data .
  log_info "Backups stored in ${BACKUP_DIR}"
}

restore_data() {
  ARCHIVE=$1
  [[ -f "$ARCHIVE" ]] || { log_error "Archive $ARCHIVE not found"; exit 1; }
  log_warn "Restoring from ${ARCHIVE}; services will be stopped"
  docker compose -f "$COMPOSE_FILE" down
  docker run --rm -v prometheus_data:/data -v "$ARCHIVE":/backup.tgz alpine sh -c "rm -rf /data/* && tar xzf /backup.tgz -C /data"
  log_info "Restore complete"
}

deploy_stack() {
  check_prerequisites
  validate_config
  log_info "Pulling images"
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull
  log_info "Starting stack"
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

case "${1:-}" in
  start)
    deploy_stack;;
  stop)
    stop_stack;;
  restart)
    restart_stack;;
  validate)
    check_prerequisites
    validate_config;;
  backup)
    backup_data;;
  restore)
    restore_data "${2:-}";;
  *)
    echo "Usage: $0 [start|stop|restart|validate|backup|restore]"
    exit 1;;
esac

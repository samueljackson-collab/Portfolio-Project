#!/bin/bash
# Monitoring Stack Deployment Script
# Purpose: Automated deployment with validation and rollback capability
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
  command -v docker >/dev/null 2>&1 || { log_error "Docker is required"; exit 1; }
  command -v docker-compose >/dev/null 2>&1 || log_warn "docker-compose CLI not found; using docker compose plugin"
  [[ -f "$ENV_FILE" ]] || { log_error ".env file missing. Copy .env.example and set secrets."; exit 1; }
  log_info "Validating port availability (3000, 9090, 9093, 3100, 8080, 9100)"
  for port in 3000 9090 9093 3100 8080 9100; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
      log_error "Port $port already in use. Stop conflicting service first."; exit 1;
    fi
  done
}

validate_config() {
  log_info "Validating Prometheus configuration"
  if command -v promtool >/dev/null 2>&1; then
    promtool check config "${PROJECT_ROOT}/prometheus/prometheus.yml"
    promtool check rules "${PROJECT_ROOT}/prometheus/alerts/rules.yml"
  else
    log_warn "promtool not installed; skip Prometheus validation"
  fi
  log_info "Validating Alertmanager configuration"
  if command -v amtool >/dev/null 2>&1; then
    amtool check-config "${PROJECT_ROOT}/alertmanager/alertmanager.yml"
  else
    log_warn "amtool not installed; skip Alertmanager validation"
  fi
  log_info "Validating Grafana dashboards JSON"
  find "${PROJECT_ROOT}/grafana/dashboards" -name '*.json' -print0 | while IFS= read -r -d '' file; do
    python -m json.tool "$file" >/dev/null || { log_error "Invalid JSON: $file"; exit 1; }
  done
}

backup_data() {
  mkdir -p "$BACKUP_DIR"
  timestamp=$(date +%Y%m%d-%H%M%S)
  archive="${BACKUP_DIR}/monitoring-backup-${timestamp}.tar.gz"
  log_info "Backing up volumes to $archive"
  docker run --rm \
    -v prometheus_data:/prometheus_data \
    -v grafana_data:/grafana_data \
    -v loki_data:/loki_data \
    -v alertmanager_data:/alertmanager_data \
    -v "$BACKUP_DIR":/backup \
    alpine sh -c "tar czf /backup/monitoring-backup-${timestamp}.tar.gz /prometheus_data /grafana_data /loki_data /alertmanager_data"
  log_info "Backup complete"
}

restore_data() {
  archive=$1
  [[ -f "$archive" ]] || { log_error "Archive $archive not found"; exit 1; }
  log_info "Restoring volumes from $archive"
  docker run --rm \
    -v prometheus_data:/prometheus_data \
    -v grafana_data:/grafana_data \
    -v loki_data:/loki_data \
    -v alertmanager_data:/alertmanager_data \
    -v "$(dirname "$archive")":/backup \
    alpine sh -c "cd / && tar xzf /backup/$(basename "$archive")"
  log_info "Restore complete"
}

deploy_stack() {
  check_prerequisites
  validate_config
  log_info "Pulling images"
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull
  log_info "Deploying stack"
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
  log_info "Waiting for health checks"
  sleep 10
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps
}

stop_stack() {
  log_info "Stopping stack"
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
}

restart_stack() {
  stop_stack
  deploy_stack
}

health_check() {
  "${SCRIPT_DIR}/health-check.sh"
}

case "${1:-}" in
  start|deploy)
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
    restore_data "${2:-}" ;;
  health)
    health_check ;;
  *)
    echo "Usage: $0 [start|stop|restart|validate|backup|restore|health]"; exit 1 ;;
 esac

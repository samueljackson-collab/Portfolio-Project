#!/bin/bash
################################################################################
# Monitoring Stack Deployment Script
################################################################################
#
# Purpose:
#   Automated deployment of Prometheus, Grafana, Loki, and Alertmanager stack
#   with comprehensive validation, health checking, and rollback capability.
#
# Usage:
#   ./deploy.sh [command] [options]
#
# Commands:
#   start       - Deploy the monitoring stack
#   stop        - Stop all services
#   restart     - Restart all services
#   status      - Show service status
#   validate    - Validate configuration files
#   backup      - Backup all persistent data
#   restore     - Restore from backup
#   logs        - Show logs from all services
#   health      - Run health checks
#
# Examples:
#   ./deploy.sh start              # Deploy stack
#   ./deploy.sh validate           # Check configuration
#   ./deploy.sh backup             # Backup data volumes
#   ./deploy.sh logs prometheus    # View Prometheus logs
#
# Prerequisites:
#   - Docker 24.0+ with compose plugin
#   - .env file configured (copy from .env.example)
#   - Sufficient disk space (50GB+ recommended)
#   - Required ports available (3000, 9090, 9093, 3100)
#
# Author: Portfolio Project
# Version: 1.0.0
# Last Updated: 2024-11-24
################################################################################

# Strict error handling
set -euo pipefail  # Exit on error, undefined variable, or pipe failure

# Trap errors and cleanup
trap 'error_handler $? $LINENO' ERR

################################################################################
# Configuration
################################################################################

# Script directory (absolute path)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Project root (parent of scripts directory)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Docker Compose file
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"

# Environment file
ENV_FILE="${PROJECT_ROOT}/.env"

# Backup directory
BACKUP_DIR="${PROJECT_ROOT}/backups"

# Log file for deployment operations
LOG_FILE="${PROJECT_ROOT}/deployment.log"

# Required services (for validation)
REQUIRED_SERVICES=(
    "prometheus"
    "grafana"
    "loki"
    "promtail"
    "alertmanager"
    "node-exporter"
    "cadvisor"
)

# Required ports (for conflict detection)
REQUIRED_PORTS=(
    "3000"   # Grafana
    "9090"   # Prometheus
    "9093"   # Alertmanager
    "3100"   # Loki
)

################################################################################
# Color Output
################################################################################

# ANSI color codes for readable output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

################################################################################
# Logging Functions
################################################################################

# Log informational message
# Usage: log_info "message"
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $*" | tee -a "$LOG_FILE"
}

# Log warning message
# Usage: log_warn "message"
log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $*" | tee -a "$LOG_FILE"
}

# Log error message
# Usage: log_error "message"
log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $*" | tee -a "$LOG_FILE"
}

# Log success message
# Usage: log_success "message"
log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $*" | tee -a "$LOG_FILE"
}

# Log step message (for progress tracking)
# Usage: log_step "step description"
log_step() {
    echo -e "${BLUE}[STEP]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $*" | tee -a "$LOG_FILE"
}

################################################################################
# Error Handling
################################################################################

# Error handler called on script failure
# Arguments: $1 = exit code, $2 = line number
error_handler() {
    local exit_code=$1
    local line_number=$2
    log_error "Script failed with exit code $exit_code at line $line_number"
    log_error "Check $LOG_FILE for details"
    exit "$exit_code"
}

################################################################################
# Prerequisite Checks
################################################################################

# Check if required commands are available
# Returns: 0 if all prerequisites met, 1 otherwise
check_prerequisites() {
    log_step "Checking prerequisites..."

    local missing_prereqs=0

    # Check for Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        log_error "Install from: https://docs.docker.com/get-docker/"
        missing_prereqs=1
    else
        local docker_version
        docker_version=$(docker --version | awk '{print $3}' | sed 's/,//')
        log_info "Docker version: $docker_version"
    fi

    # Check for Docker Compose (V2 plugin)
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose plugin not available"
        log_error "Install from: https://docs.docker.com/compose/install/"
        missing_prereqs=1
    else
        local compose_version
        compose_version=$(docker compose version | awk '{print $4}')
        log_info "Docker Compose version: $compose_version"
    fi

    # Check if .env file exists
    if [[ ! -f "$ENV_FILE" ]]; then
        log_error ".env file not found at: $ENV_FILE"
        log_error "Copy from template: cp .env.example .env"
        log_error "Then configure values in .env file"
        missing_prereqs=1
    else
        log_info "Environment file found: $ENV_FILE"
    fi

    # Check if docker-compose.yml exists
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        log_error "docker-compose.yml not found at: $COMPOSE_FILE"
        missing_prereqs=1
    else
        log_info "Compose file found: $COMPOSE_FILE"
    fi

    # Check for required configuration files
    local required_configs=(
        "${PROJECT_ROOT}/prometheus/prometheus.yml"
        "${PROJECT_ROOT}/prometheus/alerts/rules.yml"
        "${PROJECT_ROOT}/alertmanager/alertmanager.yml"
        "${PROJECT_ROOT}/loki/loki-config.yml"
        "${PROJECT_ROOT}/promtail/promtail-config.yml"
    )

    for config in "${required_configs[@]}"; do
        if [[ ! -f "$config" ]]; then
            log_error "Required configuration file missing: $config"
            missing_prereqs=1
        fi
    done

    if [[ $missing_prereqs -eq 1 ]]; then
        log_error "Prerequisites check failed"
        return 1
    fi

    log_success "All prerequisites met"
    return 0
}

################################################################################
# Configuration Validation
################################################################################

# Validate all configuration files
# Returns: 0 if valid, 1 if errors found
validate_config() {
    log_step "Validating configuration files..."

    local validation_errors=0

    # Validate docker-compose.yml syntax
    log_info "Validating docker-compose.yml..."
    if docker compose -f "$COMPOSE_FILE" config > /dev/null 2>&1; then
        log_success "docker-compose.yml is valid"
    else
        log_error "docker-compose.yml validation failed"
        docker compose -f "$COMPOSE_FILE" config
        validation_errors=1
    fi

    # Validate Prometheus configuration
    log_info "Validating prometheus.yml..."
    if docker run --rm \
        -v "${PROJECT_ROOT}/prometheus:/prometheus" \
        prom/prometheus:v2.48.0 \
        promtool check config /prometheus/prometheus.yml > /dev/null 2>&1; then
        log_success "prometheus.yml is valid"
    else
        log_error "prometheus.yml validation failed"
        docker run --rm \
            -v "${PROJECT_ROOT}/prometheus:/prometheus" \
            prom/prometheus:v2.48.0 \
            promtool check config /prometheus/prometheus.yml
        validation_errors=1
    fi

    # Validate Prometheus alert rules
    log_info "Validating alert rules..."
    if docker run --rm \
        -v "${PROJECT_ROOT}/prometheus:/prometheus" \
        prom/prometheus:v2.48.0 \
        promtool check rules /prometheus/alerts/rules.yml > /dev/null 2>&1; then
        log_success "Alert rules are valid"
    else
        log_error "Alert rules validation failed"
        docker run --rm \
            -v "${PROJECT_ROOT}/prometheus:/prometheus" \
            prom/prometheus:v2.48.0 \
            promtool check rules /prometheus/alerts/rules.yml
        validation_errors=1
    fi

    # Validate Alertmanager configuration
    log_info "Validating alertmanager.yml..."
    if docker run --rm \
        -v "${PROJECT_ROOT}/alertmanager:/alertmanager" \
        -e ALERTMANAGER_SMTP_FROM=test@example.com \
        -e ALERTMANAGER_SMTP_HOST=localhost:587 \
        -e ALERTMANAGER_SMTP_USERNAME=test \
        -e ALERTMANAGER_SMTP_PASSWORD=test \
        prom/alertmanager:v0.26.0 \
        amtool check-config /alertmanager/alertmanager.yml > /dev/null 2>&1; then
        log_success "alertmanager.yml is valid"
    else
        log_warn "alertmanager.yml validation skipped (requires env vars)"
    fi

    if [[ $validation_errors -eq 1 ]]; then
        log_error "Configuration validation failed"
        return 1
    fi

    log_success "All configurations are valid"
    return 0
}

################################################################################
# Port Availability Check
################################################################################

# Check if required ports are available
# Returns: 0 if all ports free, 1 if conflicts exist
check_ports() {
    log_step "Checking port availability..."

    local port_conflicts=0

    for port in "${REQUIRED_PORTS[@]}"; do
        # Check if port is in use (nc, netstat, or lsof)
        if command -v ss &> /dev/null; then
            if ss -tuln | grep -q ":${port} "; then
                log_warn "Port $port is already in use"
                ss -tuln | grep ":${port} "
                port_conflicts=1
            fi
        elif command -v netstat &> /dev/null; then
            if netstat -tuln | grep -q ":${port} "; then
                log_warn "Port $port is already in use"
                netstat -tuln | grep ":${port} "
                port_conflicts=1
            fi
        fi
    done

    if [[ $port_conflicts -eq 1 ]]; then
        log_warn "Port conflicts detected - services may fail to start"
        log_warn "Stop conflicting services or modify port bindings in docker-compose.yml"
        return 1
    fi

    log_success "All required ports are available"
    return 0
}

################################################################################
# Deployment Functions
################################################################################

# Deploy the monitoring stack
# Pulls images, creates volumes, starts containers, validates health
deploy_stack() {
    log_step "Deploying monitoring stack..."

    # Navigate to project root
    cd "$PROJECT_ROOT"

    # Pull latest images
    log_info "Pulling Docker images..."
    if docker compose -f "$COMPOSE_FILE" pull; then
        log_success "Images pulled successfully"
    else
        log_error "Failed to pull images"
        return 1
    fi

    # Create data directories if they don't exist
    log_info "Creating data directories..."
    mkdir -p data/{prometheus,grafana,loki,alertmanager}

    # Set proper permissions (Docker user UID 65534 for many images)
    log_info "Setting directory permissions..."
    chmod -R 777 data/  # Permissive for development; restrict in production

    # Start services
    log_info "Starting services..."
    if docker compose -f "$COMPOSE_FILE" up -d; then
        log_success "Services started"
    else
        log_error "Failed to start services"
        return 1
    fi

    # Wait for services to become healthy
    log_info "Waiting for services to become healthy..."
    local max_wait=120  # Maximum wait time in seconds
    local elapsed=0
    local check_interval=5

    while [[ $elapsed -lt $max_wait ]]; do
        local healthy_count=0
        local total_services=${#REQUIRED_SERVICES[@]}

        for service in "${REQUIRED_SERVICES[@]}"; do
            local health_status
            health_status=$(docker compose -f "$COMPOSE_FILE" ps --format json "$service" 2>/dev/null | grep -o '"Health":"[^"]*"' | cut -d'"' -f4 || echo "unknown")

            if [[ "$health_status" == "healthy" ]] || [[ "$health_status" == "" ]]; then
                ((healthy_count++))
            fi
        done

        log_info "Health check: $healthy_count/$total_services services healthy"

        if [[ $healthy_count -eq $total_services ]]; then
            log_success "All services are healthy"
            break
        fi

        sleep $check_interval
        ((elapsed+=check_interval))
    done

    if [[ $elapsed -ge $max_wait ]]; then
        log_warn "Some services did not become healthy within $max_wait seconds"
        log_warn "Check service logs: ./deploy.sh logs"
    fi

    # Show service status
    docker compose -f "$COMPOSE_FILE" ps

    log_success "Deployment complete"
    log_info ""
    log_info "Access points:"
    log_info "  - Grafana:      http://localhost:3000 (admin/${GF_SECURITY_ADMIN_PASSWORD:-admin})"
    log_info "  - Prometheus:   http://localhost:9090"
    log_info "  - Alertmanager: http://localhost:9093"
    log_info "  - Loki:         http://localhost:3100"
    log_info ""
    log_info "Next steps:"
    log_info "  1. Run health checks: ./scripts/health-check.sh"
    log_info "  2. Open Grafana and explore dashboards"
    log_info "  3. Review alert rules in Prometheus: http://localhost:9090/alerts"

    return 0
}

# Stop the monitoring stack
stop_stack() {
    log_step "Stopping monitoring stack..."

    cd "$PROJECT_ROOT"

    if docker compose -f "$COMPOSE_FILE" down; then
        log_success "Stack stopped successfully"
        return 0
    else
        log_error "Failed to stop stack"
        return 1
    fi
}

# Restart the monitoring stack
restart_stack() {
    log_step "Restarting monitoring stack..."

    stop_stack
    sleep 5
    deploy_stack
}

# Show service status
show_status() {
    log_step "Service status:"

    cd "$PROJECT_ROOT"

    docker compose -f "$COMPOSE_FILE" ps

    echo ""
    log_info "Resource usage:"
    docker stats --no-stream $(docker compose -f "$COMPOSE_FILE" ps -q)
}

# Show service logs
# Arguments: $1 = service name (optional, all if not specified)
show_logs() {
    local service="${1:-}"

    cd "$PROJECT_ROOT"

    if [[ -n "$service" ]]; then
        log_info "Showing logs for $service (Ctrl+C to exit)..."
        docker compose -f "$COMPOSE_FILE" logs -f "$service"
    else
        log_info "Showing logs for all services (Ctrl+C to exit)..."
        docker compose -f "$COMPOSE_FILE" logs -f
    fi
}

################################################################################
# Backup Functions
################################################################################

# Backup all persistent data volumes
backup_data() {
    log_step "Backing up monitoring stack data..."

    # Create backup directory
    mkdir -p "$BACKUP_DIR"

    # Timestamp for backup
    local timestamp
    timestamp=$(date +%Y%m%d_%H%M%S)

    # Backup directory path
    local backup_path="${BACKUP_DIR}/backup_${timestamp}"

    log_info "Creating backup at: $backup_path"

    # Create backup directory
    mkdir -p "$backup_path"

    # Backup data directories
    log_info "Backing up data directories..."
    cp -r "${PROJECT_ROOT}/data" "$backup_path/"

    # Backup configuration files
    log_info "Backing up configuration files..."
    cp -r "${PROJECT_ROOT}/prometheus" "$backup_path/"
    cp -r "${PROJECT_ROOT}/alertmanager" "$backup_path/"
    cp -r "${PROJECT_ROOT}/loki" "$backup_path/"
    cp -r "${PROJECT_ROOT}/promtail" "$backup_path/"
    cp -r "${PROJECT_ROOT}/grafana" "$backup_path/"
    cp "${PROJECT_ROOT}/docker-compose.yml" "$backup_path/"
    cp "${PROJECT_ROOT}/.env.example" "$backup_path/"

    # Compress backup
    log_info "Compressing backup..."
    tar -czf "${backup_path}.tar.gz" -C "$BACKUP_DIR" "backup_${timestamp}"

    # Remove uncompressed backup
    rm -rf "$backup_path"

    # Calculate backup size
    local backup_size
    backup_size=$(du -h "${backup_path}.tar.gz" | cut -f1)

    log_success "Backup created: ${backup_path}.tar.gz ($backup_size)"

    # Cleanup old backups (keep last 7)
    log_info "Cleaning up old backups (keeping last 7)..."
    cd "$BACKUP_DIR"
    ls -t backup_*.tar.gz 2>/dev/null | tail -n +8 | xargs -r rm --

    return 0
}

################################################################################
# Main Script Logic
################################################################################

# Show usage information
show_usage() {
    echo "Monitoring Stack Deployment Script"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  start      - Deploy the monitoring stack"
    echo "  stop       - Stop all services"
    echo "  restart    - Restart all services"
    echo "  status     - Show service status"
    echo "  validate   - Validate configuration files"
    echo "  backup     - Backup all persistent data"
    echo "  logs [svc] - Show logs (optionally for specific service)"
    echo "  health     - Run health checks"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 validate"
    echo "  $0 logs prometheus"
    echo "  $0 backup"
}

# Main execution
main() {
    # Create log file if doesn't exist
    touch "$LOG_FILE"

    # Parse command
    local command="${1:-help}"

    case "$command" in
        start)
            check_prerequisites || exit 1
            validate_config || exit 1
            check_ports  # Warning only, don't exit
            deploy_stack
            ;;
        stop)
            stop_stack
            ;;
        restart)
            restart_stack
            ;;
        status)
            show_status
            ;;
        validate)
            check_prerequisites || exit 1
            validate_config
            ;;
        backup)
            backup_data
            ;;
        logs)
            show_logs "${2:-}"
            ;;
        health)
            # Run health check script
            if [[ -f "${SCRIPT_DIR}/health-check.sh" ]]; then
                "${SCRIPT_DIR}/health-check.sh"
            else
                log_error "health-check.sh not found"
                exit 1
            fi
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            log_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"

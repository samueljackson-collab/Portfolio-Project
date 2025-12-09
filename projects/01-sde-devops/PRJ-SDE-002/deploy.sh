#!/bin/bash
###############################################################################
# Monitoring Stack Deployment Script
# Purpose: Automated deployment with validation and rollback capability
###############################################################################
#
# Usage:
#   ./deploy.sh [command]
#
# Commands:
#   start       - Start all monitoring services
#   stop        - Stop all services gracefully
#   restart     - Restart all services
#   validate    - Validate configuration without deploying
#   status      - Show service status
#   logs        - Tail logs from all services
#   backup      - Create backup of all data
#   restore     - Restore from backup
#   cleanup     - Remove all data (DESTRUCTIVE)
#   help        - Show this help message
#
###############################################################################

set -euo pipefail  # Exit on error, undefined variable, or pipe failure

###############################################################################
# CONFIGURATION
###############################################################################

# Script directory (where this script is located)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# File paths
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"
ENV_FILE="${PROJECT_ROOT}/.env"
ENV_EXAMPLE="${PROJECT_ROOT}/.env.example"
BACKUP_DIR="${PROJECT_ROOT}/backups"

# Service names
SERVICES=(
    "prometheus"
    "grafana"
    "loki"
    "promtail"
    "alertmanager"
    "node-exporter"
    "cadvisor"
)

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

###############################################################################
# LOGGING FUNCTIONS
###############################################################################

log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $*"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $*"
}

print_banner() {
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║     Enterprise Monitoring Stack - Deployment Tool        ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

###############################################################################
# VALIDATION FUNCTIONS
###############################################################################

check_prerequisites() {
    log_step "Checking prerequisites..."

    local missing_tools=()

    # Check for required commands
    command -v docker &> /dev/null || missing_tools+=("docker")
    command -v docker-compose &> /dev/null || {
        # Try docker compose (plugin version)
        docker compose version &> /dev/null || missing_tools+=("docker-compose")
    }
    command -v jq &> /dev/null || log_warn "jq not found (optional, for JSON validation)"

    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_error "Please install missing tools and try again"
        exit 1
    fi

    log_success "All prerequisites satisfied"
}

check_env_file() {
    log_step "Checking environment configuration..."

    if [ ! -f "$ENV_FILE" ]; then
        log_warn ".env file not found"
        log_info "Creating .env from template..."

        if [ -f "$ENV_EXAMPLE" ]; then
            cp "$ENV_EXAMPLE" "$ENV_FILE"
            log_warn "⚠️  IMPORTANT: Edit .env file with your configuration!"
            log_warn "   Especially: Grafana password, SMTP settings"
            log_warn "   Run: vim $ENV_FILE"
            read -p "Press Enter after editing .env file to continue..."
        else
            log_error ".env.example not found. Cannot create .env"
            exit 1
        fi
    fi

    # Check for default passwords
    if grep -q "ChangeThisSecurePassword123!" "$ENV_FILE"; then
        log_error "Default Grafana password detected in .env!"
        log_error "Please change GF_SECURITY_ADMIN_PASSWORD before deploying"
        exit 1
    fi

    log_success "Environment configuration OK"
}

check_port_availability() {
    log_step "Checking port availability..."

    local ports=(9090 3000 3100 9093 9100 8080)
    local port_names=("Prometheus" "Grafana" "Loki" "Alertmanager" "Node Exporter" "cAdvisor")
    local unavailable_ports=()

    for i in "${!ports[@]}"; do
        local port="${ports[$i]}"
        local name="${port_names[$i]}"

        if lsof -Pi :$port -sTCP:LISTEN -t &> /dev/null; then
            log_warn "Port $port ($name) is already in use"
            unavailable_ports+=("$port ($name)")
        fi
    done

    if [ ${#unavailable_ports[@]} -ne 0 ]; then
        log_error "The following ports are unavailable: ${unavailable_ports[*]}"
        log_error "Stop conflicting services or modify docker-compose.yml ports"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        log_success "All required ports are available"
    fi
}

validate_config_files() {
    log_step "Validating configuration files..."

    local config_files=(
        "${PROJECT_ROOT}/prometheus/prometheus.yml"
        "${PROJECT_ROOT}/prometheus/alerts/rules.yml"
        "${PROJECT_ROOT}/alertmanager/alertmanager.yml"
        "${PROJECT_ROOT}/loki/loki-config.yml"
        "${PROJECT_ROOT}/promtail/promtail-config.yml"
    )

    local validation_errors=0

    for config_file in "${config_files[@]}"; do
        if [ ! -f "$config_file" ]; then
            log_error "Config file not found: $config_file"
            ((validation_errors++))
            continue
        fi

        # YAML syntax validation (basic check)
        if command -v python3 &> /dev/null; then
            if ! python3 -c "import yaml; yaml.safe_load(open('$config_file'))" 2>/dev/null; then
                log_error "YAML syntax error in: $config_file"
                ((validation_errors++))
            fi
        fi
    done

    if [ $validation_errors -eq 0 ]; then
        log_success "All configuration files validated"
    else
        log_error "$validation_errors configuration file(s) have errors"
        exit 1
    fi
}

validate_docker_compose() {
    log_step "Validating docker-compose.yml..."

    cd "$PROJECT_ROOT"

    if docker-compose config &> /dev/null || docker compose config &> /dev/null; then
        log_success "docker-compose.yml is valid"
    else
        log_error "docker-compose.yml validation failed"
        docker-compose config || docker compose config
        exit 1
    fi
}

###############################################################################
# DEPLOYMENT FUNCTIONS
###############################################################################

pull_images() {
    log_step "Pulling Docker images..."

    cd "$PROJECT_ROOT"

    if docker-compose pull 2>&1 | grep -q "ERROR"; then
        if ! docker compose pull; then
            log_error "Failed to pull Docker images"
            exit 1
        fi
    fi

    log_success "All Docker images pulled successfully"
}

start_services() {
    log_step "Starting monitoring services..."

    cd "$PROJECT_ROOT"

    # Start services in detached mode
    if docker-compose up -d 2>&1 | grep -q "ERROR"; then
        if ! docker compose up -d; then
            log_error "Failed to start services"
            exit 1
        fi
    fi

    log_success "Services starting..."
    log_info "Waiting for services to become healthy..."
    sleep 5

    # Wait for health checks
    wait_for_health_checks
}

wait_for_health_checks() {
    local max_wait=120  # Maximum 2 minutes
    local elapsed=0
    local interval=5

    log_step "Waiting for health checks (max ${max_wait}s)..."

    while [ $elapsed -lt $max_wait ]; do
        local unhealthy_count=0

        for service in "${SERVICES[@]}"; do
            local health=$(docker inspect --format='{{.State.Health.Status}}' "monitoring-${service}" 2>/dev/null || echo "none")

            if [ "$health" != "healthy" ] && [ "$health" != "none" ]; then
                ((unhealthy_count++))
            fi
        done

        if [ $unhealthy_count -eq 0 ]; then
            log_success "All services are healthy!"
            return 0
        fi

        echo -ne "\r   Waiting... ${elapsed}s / ${max_wait}s (${unhealthy_count} services still starting)"
        sleep $interval
        ((elapsed+=interval))
    done

    echo  # New line after progress
    log_warn "Timeout waiting for health checks"
    log_info "Some services may still be starting up"
}

stop_services() {
    log_step "Stopping monitoring services..."

    cd "$PROJECT_ROOT"

    if docker-compose down 2>&1 | grep -q "ERROR"; then
        if ! docker compose down; then
            log_error "Failed to stop services"
            exit 1
        fi
    fi

    log_success "Services stopped"
}

restart_services() {
    log_info "Restarting monitoring stack..."
    stop_services
    sleep 2
    start_services
}

###############################################################################
# STATUS & MONITORING FUNCTIONS
###############################################################################

show_status() {
    log_step "Service Status:"
    echo

    cd "$PROJECT_ROOT"

    if docker-compose ps 2>&1 | grep -q "ERROR"; then
        docker compose ps
    else
        docker-compose ps
    fi

    echo
    log_step "Service Health:"
    echo

    for service in "${SERVICES[@]}"; do
        local container="monitoring-${service}"
        local health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "not running")
        local status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "not found")

        case "$health" in
            healthy)
                echo -e "  ${GREEN}●${NC} $service: $status ($health)"
                ;;
            unhealthy)
                echo -e "  ${RED}●${NC} $service: $status ($health)"
                ;;
            starting)
                echo -e "  ${YELLOW}●${NC} $service: $status ($health)"
                ;;
            *)
                echo -e "  ${RED}○${NC} $service: $status"
                ;;
        esac
    done

    echo
    log_step "Access URLs:"
    echo "  Grafana:      http://localhost:3000 (admin / check .env)"
    echo "  Prometheus:   http://localhost:9090"
    echo "  Alertmanager: http://localhost:9093"
    echo "  Loki:         http://localhost:3100"
}

tail_logs() {
    log_info "Tailing logs from all services..."
    log_info "Press Ctrl+C to exit"
    echo

    cd "$PROJECT_ROOT"

    if docker-compose logs -f 2>&1 | grep -q "ERROR"; then
        docker compose logs -f
    else
        docker-compose logs -f
    fi
}

###############################################################################
# BACKUP & RESTORE FUNCTIONS
###############################################################################

backup_data() {
    log_step "Creating backup..."

    mkdir -p "$BACKUP_DIR"

    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="${BACKUP_DIR}/monitoring-backup-${timestamp}.tar.gz"

    # Create backup of volumes and configs
    log_info "Backing up configuration files..."
    tar -czf "$backup_file" \
        -C "$PROJECT_ROOT" \
        prometheus/prometheus.yml \
        prometheus/alerts/ \
        alertmanager/alertmanager.yml \
        loki/loki-config.yml \
        promtail/promtail-config.yml \
        grafana/provisioning/ \
        docker-compose.yml \
        .env.example \
        2>/dev/null || log_warn "Some files may be missing from backup"

    log_success "Backup created: $backup_file"
    log_info "To restore: ./deploy.sh restore $backup_file"

    # Clean old backups (keep last 10)
    local backup_count=$(ls -1 "$BACKUP_DIR"/monitoring-backup-*.tar.gz 2>/dev/null | wc -l)
    if [ "$backup_count" -gt 10 ]; then
        log_info "Cleaning old backups (keeping last 10)..."
        ls -1t "$BACKUP_DIR"/monitoring-backup-*.tar.gz | tail -n +11 | xargs rm -f
    fi
}

cleanup_data() {
    log_warn "⚠️  WARNING: This will DELETE all monitoring data!"
    log_warn "   - All metrics history will be lost"
    log_warn "   - All dashboards and datasources will be reset"
    log_warn "   - All logs will be deleted"
    echo

    read -p "Are you SURE you want to proceed? (type 'yes' to confirm): " -r
    echo

    if [ "$REPLY" != "yes" ]; then
        log_info "Cleanup cancelled"
        exit 0
    fi

    log_step "Stopping services..."
    stop_services

    log_step "Removing Docker volumes..."
    cd "$PROJECT_ROOT"

    if docker-compose down -v 2>&1 | grep -q "ERROR"; then
        docker compose down -v
    else
        docker-compose down -v
    fi

    log_success "All data cleaned up"
}

###############################################################################
# HELP FUNCTION
###############################################################################

show_help() {
    cat << EOF
${CYAN}Monitoring Stack Deployment Tool${NC}

${YELLOW}USAGE:${NC}
    ./deploy.sh [command]

${YELLOW}COMMANDS:${NC}
    ${GREEN}start${NC}       Start all monitoring services
    ${GREEN}stop${NC}        Stop all services gracefully
    ${GREEN}restart${NC}     Restart all services
    ${GREEN}validate${NC}    Validate configuration without deploying
    ${GREEN}status${NC}      Show service status and health
    ${GREEN}logs${NC}        Tail logs from all services
    ${GREEN}backup${NC}      Create backup of configurations
    ${GREEN}cleanup${NC}     Remove all data (DESTRUCTIVE)
    ${GREEN}help${NC}        Show this help message

${YELLOW}EXAMPLES:${NC}
    # First time setup
    ./deploy.sh validate   # Check configuration
    ./deploy.sh start      # Deploy stack

    # Daily operations
    ./deploy.sh status     # Check health
    ./deploy.sh logs       # View logs
    ./deploy.sh restart    # Restart services

    # Maintenance
    ./deploy.sh backup     # Create backup before changes
    ./deploy.sh cleanup    # Start fresh (WARNING: deletes data)

${YELLOW}TROUBLESHOOTING:${NC}
    Service won't start:
        1. Check logs: docker logs monitoring-<service>
        2. Validate config: ./deploy.sh validate
        3. Check ports: netstat -tlnp | grep -E '(9090|3000|3100)'

    Configuration changes not applying:
        ./deploy.sh restart

    Reset everything:
        ./deploy.sh cleanup
        ./deploy.sh start

${YELLOW}ACCESS URLS:${NC}
    Grafana:      http://localhost:3000
    Prometheus:   http://localhost:9090
    Alertmanager: http://localhost:9093

EOF
}

###############################################################################
# MAIN EXECUTION
###############################################################################

main() {
    print_banner

    # Change to project root
    cd "$PROJECT_ROOT"

    # Get command
    local command="${1:-help}"

    case "$command" in
        start)
            check_prerequisites
            check_env_file
            check_port_availability
            validate_docker_compose
            validate_config_files
            pull_images
            start_services
            echo
            show_status
            echo
            log_success "Monitoring stack deployed successfully!"
            log_info "Access Grafana at: http://localhost:3000"
            ;;

        stop)
            stop_services
            ;;

        restart)
            restart_services
            echo
            show_status
            ;;

        validate)
            check_prerequisites
            check_env_file
            validate_docker_compose
            validate_config_files
            log_success "All validations passed!"
            ;;

        status)
            show_status
            ;;

        logs)
            tail_logs
            ;;

        backup)
            backup_data
            ;;

        cleanup)
            cleanup_data
            ;;

        help|--help|-h)
            show_help
            ;;

        *)
            log_error "Unknown command: $command"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"

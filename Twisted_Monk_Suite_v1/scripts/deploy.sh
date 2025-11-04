#!/bin/bash

###############################################################################
# Twisted Monk Suite v1 - Deployment Script
# 
# This script automates the deployment of the Twisted Monk Suite to production.
# It handles building, testing, and deploying the application.
###############################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
DEPLOY_ENV="${DEPLOY_ENV:-production}"

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Error handler
error_exit() {
    log_error "$1"
    exit 1
}

# Print banner
print_banner() {
    echo "=============================================="
    echo "  Twisted Monk Suite v1 - Deployment Script  "
    echo "  Environment: $DEPLOY_ENV"
    echo "=============================================="
    echo ""
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check for required commands
    command -v docker >/dev/null 2>&1 || error_exit "docker is required but not installed"
    command -v docker-compose >/dev/null 2>&1 || error_exit "docker-compose is required but not installed"
    
    # Check for .env file
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        error_exit ".env file not found in $PROJECT_ROOT"
    fi
    
    log_info "Prerequisites check passed"
}

# Run tests
run_tests() {
    log_info "Running test suite..."
    
    cd "$PROJECT_ROOT"
    
    # Install test dependencies if needed
    if [ ! -d "$BACKEND_DIR/venv" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv "$BACKEND_DIR/venv"
    fi
    
    source "$BACKEND_DIR/venv/bin/activate"
    pip install -q -r "$BACKEND_DIR/requirements.txt"
    
    # Run pytest
    cd "$PROJECT_ROOT/tests"
    pytest -v --tb=short || error_exit "Tests failed"
    
    log_info "All tests passed"
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    
    cd "$PROJECT_ROOT"
    
    # Build main API image
    docker build -t twisted-monk-suite:latest "$BACKEND_DIR" || error_exit "Docker build failed"
    
    # Tag with version if specified
    if [ -n "${VERSION:-}" ]; then
        docker tag twisted-monk-suite:latest "twisted-monk-suite:$VERSION"
        log_info "Tagged image with version: $VERSION"
    fi
    
    log_info "Docker images built successfully"
}

# Push images to registry
push_images() {
    if [ -z "${DOCKER_REGISTRY:-}" ]; then
        log_warn "DOCKER_REGISTRY not set, skipping image push"
        return
    fi
    
    log_info "Pushing images to registry..."
    
    # Tag for registry
    docker tag twisted-monk-suite:latest "$DOCKER_REGISTRY/twisted-monk-suite:latest"
    
    if [ -n "${VERSION:-}" ]; then
        docker tag twisted-monk-suite:latest "$DOCKER_REGISTRY/twisted-monk-suite:$VERSION"
    fi
    
    # Push images
    docker push "$DOCKER_REGISTRY/twisted-monk-suite:latest" || error_exit "Failed to push image"
    
    if [ -n "${VERSION:-}" ]; then
        docker push "$DOCKER_REGISTRY/twisted-monk-suite:$VERSION"
    fi
    
    log_info "Images pushed successfully"
}

# Deploy with docker-compose
deploy_docker_compose() {
    log_info "Deploying with docker-compose..."
    
    cd "$PROJECT_ROOT"
    
    # Stop existing containers
    docker-compose down || true
    
    # Pull latest images if using registry
    if [ -n "${DOCKER_REGISTRY:-}" ]; then
        docker-compose pull
    fi
    
    # Start services
    docker-compose up -d || error_exit "docker-compose up failed"
    
    log_info "Services started"
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    local max_attempts=30
    local attempt=1
    local health_url="${HEALTH_CHECK_URL:-http://localhost:8000/health}"
    
    while [ $attempt -le $max_attempts ]; do
        log_info "Health check attempt $attempt/$max_attempts..."
        
        if curl -sf "$health_url" > /dev/null; then
            log_info "Health check passed!"
            return 0
        fi
        
        sleep 2
        ((attempt++))
    done
    
    error_exit "Health check failed after $max_attempts attempts"
}

# Backup current deployment
backup_deployment() {
    log_info "Creating backup of current deployment..."
    
    local backup_dir="$PROJECT_ROOT/backups"
    local backup_name="backup_$(date +%Y%m%d_%H%M%S)"
    
    mkdir -p "$backup_dir"
    
    # Backup docker-compose.yml and .env
    if [ -f "$PROJECT_ROOT/docker-compose.yml" ]; then
        cp "$PROJECT_ROOT/docker-compose.yml" "$backup_dir/$backup_name.docker-compose.yml"
    fi
    
    if [ -f "$PROJECT_ROOT/.env" ]; then
        cp "$PROJECT_ROOT/.env" "$backup_dir/$backup_name.env"
    fi
    
    log_info "Backup created: $backup_name"
}

# Rollback deployment
rollback() {
    log_error "Rolling back deployment..."
    
    cd "$PROJECT_ROOT" || {
        log_error "Cannot change to project root directory"
        return 1
    }
    
    # Stop current deployment (don't fail if it's not running)
    docker-compose down || log_warn "Failed to stop current deployment"
    
    # Find latest backup
    local latest_backup=$(ls -t "$PROJECT_ROOT/backups"/*.docker-compose.yml 2>/dev/null | head -1)
    
    if [ -n "$latest_backup" ]; then
        log_info "Restoring from backup: $latest_backup"
        
        # Backup current state before rollback
        if [ -f "$PROJECT_ROOT/docker-compose.yml" ]; then
            cp "$PROJECT_ROOT/docker-compose.yml" "$PROJECT_ROOT/docker-compose.yml.failed" || log_warn "Failed to backup failed state"
        fi
        
        # Restore from backup
        cp "$latest_backup" "$PROJECT_ROOT/docker-compose.yml" || {
            log_error "Failed to restore docker-compose.yml from backup"
            return 1
        }
        
        # Restore .env if exists
        local env_backup="${latest_backup%.docker-compose.yml}.env"
        if [ -f "$env_backup" ]; then
            cp "$env_backup" "$PROJECT_ROOT/.env" || log_warn "Failed to restore .env from backup"
        fi
        
        # Restart services
        if docker-compose up -d; then
            log_info "Rollback completed successfully"
            return 0
        else
            log_error "Failed to start services after rollback"
            return 1
        fi
    else
        log_error "No backup found for rollback"
        return 1
    fi
}

# Clean up old images and containers
cleanup() {
    log_info "Cleaning up old Docker resources..."
    
    # Remove old images (keep last 3 versions)
    docker images twisted-monk-suite --format "{{.ID}}" | tail -n +4 | xargs -r docker rmi || true
    
    # Remove dangling images
    docker image prune -f || true
    
    log_info "Cleanup completed"
}

# Main deployment function
main() {
    print_banner
    
    # Parse command line arguments
    case "${1:-deploy}" in
        deploy)
            check_prerequisites
            backup_deployment
            run_tests
            build_images
            push_images
            deploy_docker_compose
            health_check
            cleanup
            log_info "Deployment completed successfully!"
            ;;
        
        build)
            check_prerequisites
            build_images
            log_info "Build completed successfully!"
            ;;
        
        test)
            run_tests
            log_info "Tests completed successfully!"
            ;;
        
        rollback)
            rollback
            ;;
        
        health)
            health_check
            ;;
        
        *)
            echo "Usage: $0 {deploy|build|test|rollback|health}"
            echo ""
            echo "Commands:"
            echo "  deploy   - Full deployment (default)"
            echo "  build    - Build Docker images only"
            echo "  test     - Run test suite only"
            echo "  rollback - Rollback to previous deployment"
            echo "  health   - Check application health"
            exit 1
            ;;
    esac
}

# Trap errors and perform rollback if needed (only for deploy command)
case "${1:-deploy}" in
    deploy)
        trap 'rollback || log_error "Rollback failed - manual intervention required"' ERR
        ;;
esac

# Run main function
main "$@"

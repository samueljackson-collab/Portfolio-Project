#!/bin/bash

###############################################################################
# Twisted Monk Suite v1 - Environment Setup Script
# 
# This script sets up the development or production environment.
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo "=============================================="
echo "  Twisted Monk Suite v1 - Environment Setup  "
echo "=============================================="
echo ""

# Check Python version
log_info "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
log_info "Python version: $PYTHON_VERSION"

# Create virtual environment
log_info "Creating virtual environment..."
cd "$BACKEND_DIR"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    log_info "Virtual environment created"
else
    log_warn "Virtual environment already exists"
fi

# Activate virtual environment
log_info "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
log_info "Upgrading pip..."
pip install --upgrade pip -q

# Install dependencies
log_info "Installing dependencies..."
pip install -r requirements.txt -q
log_info "Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    log_info "Creating .env file from template..."
    
    if [ -f "$PROJECT_ROOT/.env.example" ]; then
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
        log_info ".env file created. Please edit it with your configuration."
    else
        log_warn ".env.example not found. Creating basic .env file..."
        cat > "$PROJECT_ROOT/.env" << 'EOF'
# Twisted Monk Suite Configuration

# Application
DEBUG=True
PORT=8000
SECRET_KEY=change-me-in-production

# Security
ALLOWED_HOSTS=localhost,127.0.0.1
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Redis
REDIS_ENABLED=True
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
CACHE_TTL=3600

# Shopify (configure these)
SHOPIFY_API_KEY=
SHOPIFY_API_SECRET=
SHOPIFY_SHOP_URL=

# Notifications
SLACK_WEBHOOK_URL=
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=
EMAIL_PASSWORD=
EMAIL_FROM=alerts@twistedmonk.com
EMAIL_TO=

# Thresholds
LOW_STOCK_THRESHOLD=50
CRITICAL_STOCK_THRESHOLD=10
EOF
        log_info "Basic .env file created"
    fi
else
    log_warn ".env file already exists"
fi

# Check if Redis is installed
log_info "Checking Redis..."
if command -v redis-cli &> /dev/null; then
    log_info "Redis is installed"
    
    # Check if Redis is running
    if redis-cli ping &> /dev/null; then
        log_info "Redis is running"
    else
        log_warn "Redis is installed but not running. Start it with: redis-server"
    fi
else
    log_warn "Redis is not installed. Install it for caching functionality."
    echo "  macOS: brew install redis"
    echo "  Ubuntu: sudo apt install redis-server"
    echo "  Or use Docker: docker run -d -p 6379:6379 redis:7-alpine"
fi

# Check if Docker is installed
log_info "Checking Docker..."
if command -v docker &> /dev/null; then
    log_info "Docker is installed"
else
    log_warn "Docker is not installed. Install it for containerized deployment."
fi

# Run a quick test
log_info "Running quick test..."
cd "$PROJECT_ROOT/tests"
if python -m pytest test_backend.py::TestHealthEndpoint::test_health_check_success -q 2>&1 | grep -q "1 passed"; then
    log_info "Quick test passed!"
else
    log_warn "Quick test had issues. Run full test suite with: pytest tests/"
fi

echo ""
echo "=============================================="
echo "  Setup Complete!                            "
echo "=============================================="
echo ""
echo "Next steps:"
echo "  1. Edit .env file with your configuration"
echo "  2. Start Redis: redis-server (if not already running)"
echo "  3. Run the backend:"
echo "     cd $BACKEND_DIR"
echo "     source venv/bin/activate"
echo "     uvicorn main:app --reload"
echo ""
echo "  4. Visit http://localhost:8000/docs for API documentation"
echo ""

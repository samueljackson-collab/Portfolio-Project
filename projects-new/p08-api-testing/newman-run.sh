#!/usr/bin/env bash
#
# Newman Collection Runner
# Executes Postman collections using Newman CLI with automated reporting
# Usage: ./newman-run.sh [environment] [options]
#

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${SCRIPT_DIR}"
COLLECTION_DIR="${PROJECT_DIR}/producer/collections"
ENV_DIR="${PROJECT_DIR}/producer/env"
OUTPUT_DIR="${PROJECT_DIR}/out"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Default values
ENVIRONMENT="${1:-local}"
COLLECTION="${2:-core}"
VERBOSE="${VERBOSE:-false}"
BAIL="${BAIL:-true}"
TIMEOUT="${TIMEOUT:-10000}"
DELAY="${DELAY:-100}"

# Ensure output directory exists
mkdir -p "${OUTPUT_DIR}"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# Display usage information
usage() {
    cat <<EOF
Usage: $0 [options]

Options:
    -e, --environment ENV    Environment to use (default: local)
    -c, --collection COLL    Collection name (default: core)
    -v, --verbose            Enable verbose output
    --no-bail                Don't stop on first failure
    --timeout MS             Request timeout in milliseconds (default: 10000)
    --delay MS               Delay between requests in milliseconds (default: 100)
    --reporters              Specify reporters (cli, json, html, etc.)
    -h, --help               Display this help message

Examples:
    ./newman-run.sh -e local -c core
    ./newman-run.sh -e staging --no-bail -v
    ./newman-run.sh -e prod --reporters json,html --timeout 5000

EOF
    exit 0
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -c|--collection)
                COLLECTION="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE="true"
                shift
                ;;
            --no-bail)
                BAIL="false"
                shift
                ;;
            --timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            --delay)
                DELAY="$2"
                shift 2
                ;;
            --reporters)
                REPORTERS="$2"
                shift 2
                ;;
            -h|--help)
                usage
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
}

# Validate dependencies
validate_dependencies() {
    local missing_deps=0

    if ! command -v newman &> /dev/null; then
        log_error "newman is not installed. Install with: npm install -g newman"
        missing_deps=1
    fi

    if ! command -v jq &> /dev/null; then
        log_warn "jq is not installed. Report parsing will be limited."
    fi

    return $missing_deps
}

# Validate collection and environment files
validate_files() {
    local collection_file="${COLLECTION_DIR}/${COLLECTION}.postman_collection.json"
    local env_file="${ENV_DIR}/${ENVIRONMENT}.postman_environment.json"

    if [[ ! -f "${collection_file}" ]]; then
        log_error "Collection not found: ${collection_file}"
        return 1
    fi

    if [[ ! -f "${env_file}" ]]; then
        log_error "Environment not found: ${env_file}"
        return 1
    fi

    return 0
}

# Run Newman collection
run_collection() {
    local collection_file="${COLLECTION_DIR}/${COLLECTION}.postman_collection.json"
    local env_file="${ENV_DIR}/${ENVIRONMENT}.postman_environment.json"
    local report_file="${OUTPUT_DIR}/newman-report-${TIMESTAMP}.json"
    local cli_report_file="${OUTPUT_DIR}/newman-cli-report-${TIMESTAMP}.txt"

    log_info "Running collection: ${COLLECTION}"
    log_info "Environment: ${ENVIRONMENT}"
    log_info "Report output: ${report_file}"

    # Build Newman command
    local newman_cmd=(
        "newman"
        "run"
        "${collection_file}"
        "--environment"
        "${env_file}"
        "--reporters"
        "json,cli"
        "--reporter-json-export"
        "${report_file}"
        "--reporter-cli-export"
        "${cli_report_file}"
        "--request-timeout"
        "${TIMEOUT}"
        "--delay-request"
        "${DELAY}"
    )

    # Add conditional flags
    if [[ "${BAIL}" == "true" ]]; then
        newman_cmd+=("--bail")
    fi

    if [[ "${VERBOSE}" == "true" ]]; then
        newman_cmd+=("-v")
    fi

    # Execute Newman
    echo ""
    if "${newman_cmd[@]}"; then
        log_success "Collection execution completed successfully"

        # Parse and display summary
        if command -v jq &> /dev/null; then
            parse_newman_report "${report_file}"
        fi

        return 0
    else
        log_error "Collection execution failed"
        if [[ -f "${cli_report_file}" ]]; then
            log_error "See details in: ${cli_report_file}"
        fi
        return 1
    fi
}

# Parse Newman JSON report
parse_newman_report() {
    local report_file="$1"

    if [[ ! -f "${report_file}" ]]; then
        return 1
    fi

    log_info "Test Summary:"

    # Extract stats from JSON report
    local stats=$(jq '.run.stats' "${report_file}")
    local tests_total=$(echo "${stats}" | jq '.tests.total')
    local tests_passed=$(echo "${stats}" | jq '.tests.passed')
    local tests_failed=$(echo "${stats}" | jq '.tests.failed')
    local requests_total=$(echo "${stats}" | jq '.requests.total')
    local requests_received=$(echo "${stats}" | jq '.requests.received')
    local assertions_total=$(echo "${stats}" | jq '.assertions.total')
    local assertions_failed=$(echo "${stats}" | jq '.assertions.failed')

    echo ""
    echo "  Requests: ${requests_received}/${requests_total}"
    echo "  Tests: ${tests_passed}/${tests_total}"

    if [[ ${tests_failed} -gt 0 ]]; then
        echo -e "  ${RED}Failed Tests: ${tests_failed}${NC}"
    fi

    if [[ ${assertions_failed} -gt 0 ]]; then
        echo -e "  ${RED}Failed Assertions: ${assertions_failed}${NC}"
    fi

    # Calculate and display pass rate
    if [[ ${tests_total} -gt 0 ]]; then
        local pass_rate=$((tests_passed * 100 / tests_total))
        if [[ ${pass_rate} -eq 100 ]]; then
            echo -e "  ${GREEN}Pass Rate: ${pass_rate}%${NC}"
        elif [[ ${pass_rate} -ge 80 ]]; then
            echo -e "  ${YELLOW}Pass Rate: ${pass_rate}%${NC}"
        else
            echo -e "  ${RED}Pass Rate: ${pass_rate}%${NC}"
        fi
    fi

    echo ""
}

# Generate HTML report (optional)
generate_html_report() {
    local json_report="$1"
    local html_output="${OUTPUT_DIR}/newman-report-${TIMESTAMP}.html"

    if command -v newman &> /dev/null && [[ -f "${json_report}" ]]; then
        log_info "Generating HTML report..."

        # Use newman-reporter-html if available
        if npm list -g newman-reporter-html &> /dev/null; then
            newman run \
                "${COLLECTION_DIR}/${COLLECTION}.postman_collection.json" \
                --environment "${ENV_DIR}/${ENVIRONMENT}.postman_environment.json" \
                --reporters html \
                --reporter-html-export "${html_output}" \
                --reporter-html-template "${PROJECT_DIR}/producer/html-template.hbs" 2>/dev/null || true

            if [[ -f "${html_output}" ]]; then
                log_success "HTML report generated: ${html_output}"
            fi
        fi
    fi
}

# Main execution
main() {
    echo -e "${BLUE}╔═══════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     Postman Collection Newman Runner       ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════╝${NC}"
    echo ""

    parse_args "$@"

    if ! validate_dependencies; then
        exit 1
    fi

    if ! validate_files; then
        exit 1
    fi

    if run_collection; then
        log_success "All checks passed!"
        exit 0
    else
        log_error "Test suite failed!"
        exit 1
    fi
}

# Execute main function
main "$@"

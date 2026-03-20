#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# GitOps Environment Promotion Script
# Updates image tags in environment values.yaml files to promote a service
# from one environment to the next. Commit + push triggers ArgoCD sync.
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENVIRONMENTS_DIR="${PROJECT_ROOT}/environments"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

usage() {
  cat <<EOF
Usage: $(basename "$0") <environment> <app> <image_repo> <image_tag>

Promotes a container image tag to the specified environment by updating
the values.yaml file and committing the change to Git.

Arguments:
  environment    Target environment: dev | staging | prod
  app            Application name: frontend | backend
  image_repo     Container image repository (e.g., nginx, myregistry/myapp)
  image_tag      Container image tag to promote (e.g., 1.26.0-alpine, v2.3.1)

Examples:
  $(basename "$0") staging frontend nginx 1.26.0-alpine
  $(basename "$0") prod backend myregistry/api v2.3.1
  $(basename "$0") dev backend python 3.12-slim

Promotion path:
  dev --> staging --> prod

EOF
  exit 1
}

# Validate yq or python3 is available for YAML editing
check_yaml_tool() {
  if command -v yq &>/dev/null; then
    YAML_TOOL="yq"
  elif command -v python3 &>/dev/null; then
    YAML_TOOL="python3"
  else
    log_error "Neither yq nor python3 found. Install yq: https://github.com/mikefarah/yq"
    exit 1
  fi
  log_info "Using ${YAML_TOOL} for YAML editing"
}

update_image_yq() {
  local values_file="$1"
  local repo="$2"
  local tag="$3"

  yq e ".image.repository = \"${repo}\"" -i "${values_file}"
  yq e ".image.tag = \"${tag}\"" -i "${values_file}"
}

update_image_python() {
  local values_file="$1"
  local repo="$2"
  local tag="$3"

  python3 - "${values_file}" "${repo}" "${tag}" <<'PYEOF'
import sys
import re

values_file = sys.argv[1]
repo = sys.argv[2]
tag = sys.argv[3]

with open(values_file, 'r') as f:
    content = f.read()

# Update repository field
content = re.sub(
    r'^(\s*repository:\s*).*$',
    r'\g<1>' + repo,
    content,
    flags=re.MULTILINE
)

# Update tag field under image section
content = re.sub(
    r'^(\s*tag:\s*).*$',
    r'\g<1>"' + tag + '"',
    content,
    flags=re.MULTILINE,
    count=1
)

with open(values_file, 'w') as f:
    f.write(content)

print(f"  repository: {repo}")
print(f"  tag: {tag}")
PYEOF
}

# =============================================================================
# Argument parsing
# =============================================================================
if [[ $# -lt 4 ]]; then
  usage
fi

TARGET_ENV="$1"
APP_NAME="$2"
IMAGE_REPO="$3"
IMAGE_TAG="$4"

# Validate environment
VALID_ENVS=("dev" "staging" "prod")
if [[ ! " ${VALID_ENVS[*]} " =~ " ${TARGET_ENV} " ]]; then
  log_error "Invalid environment '${TARGET_ENV}'. Must be one of: ${VALID_ENVS[*]}"
  usage
fi

# Validate app name
VALID_APPS=("frontend" "backend")
if [[ ! " ${VALID_APPS[*]} " =~ " ${APP_NAME} " ]]; then
  log_error "Invalid app '${APP_NAME}'. Must be one of: ${VALID_APPS[*]}"
  usage
fi

VALUES_FILE="${ENVIRONMENTS_DIR}/${TARGET_ENV}/values.yaml"

if [[ ! -f "${VALUES_FILE}" ]]; then
  log_error "Values file not found: ${VALUES_FILE}"
  exit 1
fi

# =============================================================================
# Main promotion logic
# =============================================================================
echo ""
echo "=============================================="
echo "       GitOps Environment Promotion"
echo "=============================================="
echo ""
log_info "App:         ${APP_NAME}"
log_info "Environment: ${TARGET_ENV}"
log_info "Image:       ${IMAGE_REPO}:${IMAGE_TAG}"
log_info "Values file: ${VALUES_FILE}"
echo ""

# Read current values
CURRENT_REPO=$(grep -E '^\s*repository:' "${VALUES_FILE}" | head -1 | awk '{print $2}' | tr -d '"')
CURRENT_TAG=$(grep -E '^\s*tag:' "${VALUES_FILE}" | head -1 | awk '{print $2}' | tr -d '"')

log_info "Current image: ${CURRENT_REPO}:${CURRENT_TAG}"
log_info "New image:     ${IMAGE_REPO}:${IMAGE_TAG}"
echo ""

if [[ "${CURRENT_REPO}" == "${IMAGE_REPO}" && "${CURRENT_TAG}" == "${IMAGE_TAG}" ]]; then
  log_warn "Image is already at ${IMAGE_REPO}:${IMAGE_TAG} in ${TARGET_ENV} — no changes needed"
  exit 0
fi

# Check yaml tool
check_yaml_tool

# Create backup
cp "${VALUES_FILE}" "${VALUES_FILE}.bak"
log_info "Backup created: ${VALUES_FILE}.bak"

# Apply the update
echo ""
echo "=== Updating values.yaml ==="
if [[ "${YAML_TOOL}" == "yq" ]]; then
  update_image_yq "${VALUES_FILE}" "${IMAGE_REPO}" "${IMAGE_TAG}"
else
  update_image_python "${VALUES_FILE}" "${IMAGE_REPO}" "${IMAGE_TAG}"
fi
log_ok "Updated ${VALUES_FILE}"

# Verify the change
NEW_REPO=$(grep -E '^\s*repository:' "${VALUES_FILE}" | head -1 | awk '{print $2}' | tr -d '"')
NEW_TAG=$(grep -E '^\s*tag:' "${VALUES_FILE}" | head -1 | awk '{print $2}' | tr -d '"')

if [[ "${NEW_REPO}" != "${IMAGE_REPO}" || "${NEW_TAG}" != "${IMAGE_TAG}" ]]; then
  log_error "Verification failed — values not updated correctly"
  log_info "Restoring backup..."
  mv "${VALUES_FILE}.bak" "${VALUES_FILE}"
  exit 1
fi

log_ok "Verified: ${NEW_REPO}:${NEW_TAG}"
rm -f "${VALUES_FILE}.bak"

# =============================================================================
# Git commit and push
# =============================================================================
echo ""
echo "=== Committing Changes ==="

cd "${PROJECT_ROOT}"

if ! git rev-parse --is-inside-work-tree &>/dev/null; then
  log_warn "Not inside a git repository — skipping commit"
  log_info "Manually commit and push to trigger ArgoCD sync:"
  echo "  git add ${VALUES_FILE}"
  echo "  git commit -m \"chore(${TARGET_ENV}): promote ${APP_NAME} to ${IMAGE_REPO}:${IMAGE_TAG}\""
  echo "  git push origin HEAD"
  exit 0
fi

COMMIT_MSG="chore(${TARGET_ENV}): promote ${APP_NAME} to ${IMAGE_REPO}:${IMAGE_TAG}

- Environment: ${TARGET_ENV}
- Application: ${APP_NAME}
- Previous: ${CURRENT_REPO}:${CURRENT_TAG}
- Updated:  ${IMAGE_REPO}:${IMAGE_TAG}
- Promoted by: $(git config user.name 2>/dev/null || echo 'CI/CD')
- Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

git add "${VALUES_FILE}"

if git diff --cached --quiet; then
  log_warn "No staged changes detected"
  exit 0
fi

git commit -m "${COMMIT_MSG}"
log_ok "Committed: ${COMMIT_MSG%%$'\n'*}"

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
log_info "Pushing to origin/${CURRENT_BRANCH}..."
git push origin "${CURRENT_BRANCH}"
log_ok "Pushed to remote"

# =============================================================================
# Post-promotion instructions
# =============================================================================
echo ""
echo "=============================================="
echo "       Promotion Complete!"
echo "=============================================="
echo ""
echo "ArgoCD will automatically detect the Git change and sync:"
echo ""
echo "  Monitor sync status:"
echo "    argocd app get ${APP_NAME}"
echo "    argocd app sync ${APP_NAME}"
echo ""
echo "  Watch rollout:"
echo "    kubectl rollout status deployment/${APP_NAME} -n ${APP_NAME}"
echo ""

if [[ "${TARGET_ENV}" == "staging" ]]; then
  echo "  Next step — promote to production:"
  echo "    ${SCRIPT_DIR}/promote.sh prod ${APP_NAME} ${IMAGE_REPO} ${IMAGE_TAG}"
  echo ""
elif [[ "${TARGET_ENV}" == "prod" ]]; then
  echo "  Production deployment in progress — monitor carefully!"
  echo "  Rollback if needed:"
  echo "    argocd app rollback ${APP_NAME}"
  echo ""
fi

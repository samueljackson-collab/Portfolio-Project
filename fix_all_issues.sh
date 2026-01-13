#!/bin/bash
#==============================================================================
# AUTO-FIX ALL CODE ISSUES
#==============================================================================
# This script automatically fixes common code issues that cause GitHub checks
# to fail. Run this before pushing to ensure CI passes.
#
# Usage:
#   ./fix_all_issues.sh           # Fix all issues
#   ./fix_all_issues.sh --python  # Fix Python only
#   ./fix_all_issues.sh --js      # Fix JavaScript only
#   ./fix_all_issues.sh --tf      # Fix Terraform only
#
# Requirements:
#   - Python 3.8+
#   - Node.js 18+
#   - Terraform 1.0+
#
# Author: Sam Jackson
# Date: January 2026
#==============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

#==============================================================================
# PYTHON FIXES
#==============================================================================
fix_python() {
    print_header "🐍 Fixing Python Files"

    # Check if Python files exist
    PYTHON_FILES=$(find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" -not -path "./node_modules/*" 2>/dev/null | head -1)

    if [ -z "$PYTHON_FILES" ]; then
        print_warning "No Python files found. Skipping."
        return 0
    fi

    # Install tools if needed
    echo "📦 Installing Python tools..."
    pip install black isort autoflake flake8 bandit safety --quiet

    # Run black formatter
    echo "🔧 Running black formatter..."
    black . --line-length 88 --quiet 2>/dev/null || true

    # Run isort for imports
    echo "🔧 Sorting imports with isort..."
    isort . --profile black --quiet 2>/dev/null || true

    # Remove unused imports
    echo "🔧 Removing unused imports..."
    autoflake --in-place --remove-all-unused-imports --remove-unused-variables --recursive . 2>/dev/null || true

    # Check for remaining issues
    echo "📋 Checking for remaining issues..."
    FLAKE_OUTPUT=$(flake8 . --max-line-length=88 --extend-ignore=E203,W503,E501 --exclude=venv,.venv,node_modules 2>&1 || true)

    if [ -z "$FLAKE_OUTPUT" ]; then
        print_success "All Python checks pass!"
    else
        print_warning "Some Python issues remain:"
        echo "$FLAKE_OUTPUT" | head -10
    fi

    # Security check
    echo "🔒 Running security check..."
    bandit -r . -ll --quiet 2>/dev/null || true
}

#==============================================================================
# JAVASCRIPT/TYPESCRIPT FIXES
#==============================================================================
fix_javascript() {
    print_header "📜 Fixing JavaScript/TypeScript Files"

    # Check if package.json exists
    if [ ! -f "package.json" ]; then
        # Check subdirectories
        if [ -f "frontend/package.json" ]; then
            cd frontend
        else
            print_warning "No package.json found. Skipping JS/TS fixes."
            return 0
        fi
    fi

    # Install dependencies
    echo "📦 Installing dependencies..."
    npm install --silent 2>/dev/null || yarn install --silent 2>/dev/null || true

    # Install dev tools
    echo "📦 Installing linting tools..."
    npm install -D eslint prettier eslint-config-prettier @typescript-eslint/eslint-plugin @typescript-eslint/parser --silent 2>/dev/null || true

    # Create prettier config if not exists
    if [ ! -f ".prettierrc" ] && [ ! -f ".prettierrc.json" ]; then
        echo "📝 Creating .prettierrc..."
        cat > .prettierrc << 'PRETTIER'
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 80,
  "bracketSpacing": true
}
PRETTIER
    fi

    # Run ESLint fix
    echo "🔧 Running ESLint auto-fix..."
    npx eslint . --fix --ext .ts,.tsx,.js,.jsx --quiet 2>/dev/null || true

    # Run Prettier
    echo "🔧 Running Prettier..."
    npx prettier --write "**/*.{ts,tsx,js,jsx,json,css,scss,md}" --log-level error 2>/dev/null || true

    # Type check if TypeScript
    if [ -f "tsconfig.json" ]; then
        echo "🔧 Running TypeScript check..."
        npx tsc --noEmit 2>/dev/null || true
    fi

    print_success "JavaScript/TypeScript fixes applied!"

    # Return to original directory if we changed
    cd - > /dev/null 2>&1 || true
}

#==============================================================================
# TERRAFORM FIXES
#==============================================================================
fix_terraform() {
    print_header "🏗️  Fixing Terraform Files"

    # Find terraform directories
    TF_DIRS=$(find . -name "*.tf" -exec dirname {} \; 2>/dev/null | sort -u)

    if [ -z "$TF_DIRS" ]; then
        print_warning "No Terraform files found. Skipping."
        return 0
    fi

    for dir in $TF_DIRS; do
        echo "📁 Processing: $dir"

        # Format files
        echo "  🔧 Formatting..."
        terraform fmt "$dir" 2>/dev/null || true

        # Validate (if initialized)
        if [ -d "$dir/.terraform" ]; then
            echo "  📋 Validating..."
            (cd "$dir" && terraform validate 2>/dev/null) || true
        fi
    done

    # Run tfsec if available
    if command -v tfsec &> /dev/null; then
        echo "🔒 Running security scan..."
        tfsec . --soft-fail 2>/dev/null | head -20 || true
    fi

    print_success "Terraform fixes applied!"
}

#==============================================================================
# YAML/JSON FIXES
#==============================================================================
fix_yaml_json() {
    print_header "📄 Fixing YAML/JSON Files"

    # Fix YAML indentation (tabs to spaces)
    echo "🔧 Fixing YAML indentation..."
    find . -name "*.yaml" -o -name "*.yml" 2>/dev/null | while read file; do
        if [ -f "$file" ]; then
            sed -i 's/\t/  /g' "$file" 2>/dev/null || true
        fi
    done

    # Validate YAML if yamllint is available
    if command -v yamllint &> /dev/null; then
        echo "📋 Validating YAML..."
        yamllint . -d relaxed 2>/dev/null | head -10 || true
    fi

    # Fix JSON formatting
    echo "🔧 Fixing JSON formatting..."
    find . -name "*.json" -not -path "./node_modules/*" 2>/dev/null | while read file; do
        if [ -f "$file" ]; then
            # Use Python to format JSON
            python3 -c 'import json, sys; path=sys.argv[1];
try:
    with open(path, "r+") as f:
        data = json.load(f)
        f.seek(0)
        f.truncate()
        json.dump(data, f, indent=2)
except (json.JSONDecodeError, IsADirectoryError, UnicodeDecodeError):
    pass # Ignore non-JSON files, directories, or binary files' "$file"
        fi
    done

    print_success "YAML/JSON fixes applied!"
}

#==============================================================================
# DOCKERFILE FIXES
#==============================================================================
fix_dockerfiles() {
    print_header "🐳 Fixing Dockerfiles"

    # Find Dockerfiles
    DOCKERFILES=$(find . -name "Dockerfile*" 2>/dev/null)

    if [ -z "$DOCKERFILES" ]; then
        print_warning "No Dockerfiles found. Skipping."
        return 0
    fi

    # Run hadolint if available
    if command -v hadolint &> /dev/null; then
        echo "📋 Running Dockerfile linter..."
        for dockerfile in $DOCKERFILES; do
            echo "  Checking: $dockerfile"
            hadolint "$dockerfile" 2>/dev/null | head -5 || true
        done
    fi

    print_success "Dockerfile checks complete!"
}

#==============================================================================
# SECURITY FIXES
#==============================================================================
fix_security() {
    print_header "🔒 Security Checks"

    # Check for hardcoded secrets using grep
    echo "🔍 Scanning for potential secrets..."
    SECRETS=$(grep -rn --include="*.py" --include="*.js" --include="*.ts" --include="*.yaml" --include="*.yml" \
        -E "(password|secret|api_key|apikey|token|credential).*=.*['\"][^'\"]+['\"]" . 2>/dev/null | \
        grep -v "example" | grep -v "placeholder" | grep -v "your_" | head -5)

    if [ -n "$SECRETS" ]; then
        print_warning "Potential hardcoded secrets found:"
        echo "$SECRETS"
        echo ""
        echo "Please review and move to environment variables."
    else
        print_success "No obvious hardcoded secrets found."
    fi

    # Check Python dependencies
    if [ -f "requirements.txt" ]; then
        echo "📦 Checking Python dependencies for vulnerabilities..."
        pip install safety --quiet 2>/dev/null || true
        safety check -r requirements.txt 2>/dev/null | head -10 || true
    fi

    # Check npm dependencies
    if [ -f "package.json" ]; then
        echo "📦 Checking npm dependencies..."
        npm audit --production 2>/dev/null | head -10 || true
    fi
}

#==============================================================================
# GIT OPERATIONS
#==============================================================================
commit_fixes() {
    print_header "📝 Committing Fixes"

    # Check if there are changes
    if git diff --quiet && git diff --staged --quiet; then
        print_warning "No changes to commit."
        return 0
    fi

    # Stage all changes
    echo "📁 Staging changes..."
    git add .

    # Show what changed
    echo "📋 Changes to commit:"
    git diff --staged --stat | head -20

    # Commit
    echo ""
    read -p "Commit these fixes? (y/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git commit -m "fix: Auto-fix linting and formatting issues

Applied automatic fixes:
- Python: black, isort, autoflake
- JavaScript/TypeScript: ESLint, Prettier
- Terraform: terraform fmt
- YAML/JSON: indentation fixes

Co-authored-by: CI Bot <ci@example.com>"

        print_success "Changes committed!"

        # Offer to push
        read -p "Push changes? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git push
            print_success "Changes pushed!"
        fi
    else
        print_warning "Commit cancelled. Changes are staged."
    fi
}

#==============================================================================
# MAIN
#==============================================================================
main() {
    print_header "🔧 AUTO-FIX ALL CODE ISSUES"
    echo "This script will automatically fix common code issues."
    echo ""

    # Parse arguments
    FIX_ALL=true
    FIX_PYTHON=false
    FIX_JS=false
    FIX_TF=false
    DO_COMMIT=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --python|-p)
                FIX_ALL=false
                FIX_PYTHON=true
                shift
                ;;
            --js|--javascript|-j)
                FIX_ALL=false
                FIX_JS=true
                shift
                ;;
            --tf|--terraform|-t)
                FIX_ALL=false
                FIX_TF=true
                shift
                ;;
            --commit|-c)
                DO_COMMIT=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --python, -p    Fix Python files only"
                echo "  --js, -j        Fix JavaScript/TypeScript only"
                echo "  --tf, -t        Fix Terraform only"
                echo "  --commit, -c    Commit fixes after applying"
                echo "  --help, -h      Show this help"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    # Run fixes
    if [ "$FIX_ALL" = true ]; then
        fix_python
        fix_javascript
        fix_terraform
        fix_yaml_json
        fix_dockerfiles
        fix_security
    else
        [ "$FIX_PYTHON" = true ] && fix_python
        [ "$FIX_JS" = true ] && fix_javascript
        [ "$FIX_TF" = true ] && fix_terraform
    fi

    # Commit if requested
    if [ "$DO_COMMIT" = true ]; then
        commit_fixes
    fi

    print_header "✅ FIX COMPLETE"
    echo ""
    echo "Next steps:"
    echo "  1. Review the changes: git diff"
    echo "  2. Stage changes: git add ."
    echo "  3. Commit: git commit -m 'fix: Apply auto-fixes'"
    echo "  4. Push: git push"
    echo ""
}

# Run main
main "$@"

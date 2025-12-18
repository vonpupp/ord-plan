#!/bin/bash

# Comprehensive test script for ord-plan
# This is the single place to run all tests and type checking

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to setup environment if needed
setup_environment() {
    print_status $BLUE "🔧 Setting up test environment..."

    cd "$PROJECT_ROOT"

    # Check if virtual environment exists
    if [[ ! -d "venv" ]]; then
        print_status $YELLOW "Creating virtual environment..."
        python -m venv venv
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Install package in development mode if not already installed
    if ! python -c "import ord_plan" >/dev/null 2>&1; then
        print_status $YELLOW "Installing package in development mode..."
        pip install -e . >/dev/null 2>&1
    fi

    # Install testing dependencies
    print_status $YELLOW "Ensuring testing dependencies are installed..."
    pip install pytest mypy types-PyYAML types-croniter types-python-dateutil nox >/dev/null 2>&1

    print_status $GREEN "✅ Environment setup complete"
}

# Function to run syntax checks
run_syntax_checks() {
    print_status $BLUE "🔍 Running syntax checks..."

    cd "$PROJECT_ROOT"

    # Check Python syntax for all Python files
    python_files=$(find . -name "*.py" -not -path "./venv/*" -not -path "./.git/*" -not -path "./.nox/*" -not -path "./site/*")
    syntax_failed=false

    for file in $python_files; do
        if ! python -m py_compile "$file" 2>/dev/null; then
            print_status $RED "❌ Syntax error in $file"
            syntax_failed=true
        fi
    done

    if [[ "$syntax_failed" == false ]]; then
        print_status $GREEN "✅ All syntax checks passed"
    else
        print_status $RED "❌ Syntax checks failed"
        return 1
    fi
}

# Function to run mypy type checking
run_mypy() {
    print_status $BLUE "🔍 Running mypy type checking..."

    cd "$PROJECT_ROOT"
    source venv/bin/activate

    if mypy src/ tests/ --show-error-codes --no-error-summary; then
        print_status $GREEN "✅ mypy type checking passed"
    else
        print_status $RED "❌ mypy type checking failed"
        return 1
    fi
}

# Function to run pytest
run_pytest() {
    print_status $BLUE "🧪 Running pytest tests..."

    cd "$PROJECT_ROOT"
    source venv/bin/activate

    # Run with coverage if available, otherwise just run tests
    if python -c "import pytest_cov" >/dev/null 2>&1; then
        pytest_cmd="pytest --cov=ord_plan --cov-report=term-missing"
    else
        pytest_cmd="pytest"
    fi

    if $pytest_cmd -v; then
        print_status $GREEN "✅ All pytest tests passed"
    else
        print_status $RED "❌ pytest tests failed"
        return 1
    fi
}

# Function to run code style checks
run_style_checks() {
    print_status $BLUE "🎨 Running code style checks..."

    cd "$PROJECT_ROOT"

    # Try ruff if available
    if command_exists ruff; then
        if ruff check . --fix; then
            print_status $GREEN "✅ ruff style checks passed"
        else
            print_status $RED "❌ ruff style checks failed"
            return 1
        fi
    # Try flake8 if available
    elif command_exists flake8; then
        if flake8 .; then
            print_status $GREEN "✅ flake8 style checks passed"
        else
            print_status $RED "❌ flake8 style checks failed"
            return 1
        fi
    else
        print_status $YELLOW "⚠️  No code style checker found (ruff or flake8)"
        print_status $YELLOW "   Install with: pip install ruff  # or flake8"
    fi
}

# Function to run pre-commit checks (black, darglint, flake8, etc.)
run_precommit_checks() {
    print_status $BLUE "🔧 Running pre-commit checks..."

    cd "$PROJECT_ROOT"
    source venv/bin/activate

    # Use pre-commit directly since nox has issues
    if command_exists pre-commit; then
        # Install pre-commit dependencies if needed
        pip install black darglint flake8 flake8-bandit flake8-bugbear flake8-docstrings flake8-rst-docstrings isort pep8-naming pre-commit pre-commit-hooks pyupgrade >/dev/null 2>&1 || true

        if pre-commit run --all-files --hook-stage=manual; then
            print_status $GREEN "✅ pre-commit checks passed"
        else
            print_status $RED "❌ pre-commit checks failed"
            return 1
        fi
    else
        print_status $YELLOW "⚠️  pre-commit not found"
        print_status $YELLOW "   Install with: pip install pre-commit"
        return 1
    fi
}

# Function to run typeguard runtime type checking
run_typeguard_checks() {
    print_status $BLUE "🛡️ Running TypeGuard runtime type checking..."

    cd "$PROJECT_ROOT"
    source venv/bin/activate

    if python -c "import typeguard" >/dev/null 2>&1; then
        if pytest --typeguard-packages=ord_plan; then
            print_status $GREEN "✅ TypeGuard checks passed"
        else
            print_status $RED "❌ TypeGuard checks failed"
            return 1
        fi
    else
        print_status $YELLOW "⚠️  typeguard not found, skipping TypeGuard checks"
        print_status $YELLOW "   Install with: pip install typeguard"
    fi
}

# Function to run xdoctest (doctests in examples)
run_xdoctest() {
    print_status $BLUE "📚 Running xdoctest..."

    cd "$PROJECT_ROOT"
    source venv/bin/activate

    if python -c "import xdoctest" >/dev/null 2>&1; then
        if python -m xdoctest ord_plan --command=all; then
            print_status $GREEN "✅ xdoctest passed"
        else
            print_status $RED "❌ xdoctest failed"
            return 1
        fi
    else
        print_status $YELLOW "⚠️  xdoctest not found, skipping xdoctest"
        print_status $YELLOW "   Install with: pip install xdoctest"
    fi
}

# Function to run docs build test
run_docs_build() {
    print_status $BLUE "📖 Running documentation build test..."

    cd "$PROJECT_ROOT"
    source venv/bin/activate

    if python -c "import sphinx" >/dev/null 2>&1; then
        if sphinx-build -b html docs docs/_build; then
            print_status $GREEN "✅ Documentation build passed"
        else
            print_status $RED "❌ Documentation build failed"
            return 1
        fi
    else
        print_status $YELLOW "⚠️  sphinx not found, skipping docs build"
        print_status $YELLOW "   Install with: pip install sphinx"
    fi
}

# Function to run safety dependency security check
run_safety_checks() {
    print_status $BLUE "🔒 Running Safety dependency security check..."

    cd "$PROJECT_ROOT"
    source venv/bin/activate

    if python -c "import safety" >/dev/null 2>&1; then
        if poetry export --format=requirements.txt --with=dev --without-hashes | safety check --stdin; then
            print_status $GREEN "✅ Safety checks passed"
        else
            print_status $RED "❌ Safety checks failed"
            return 1
        fi
    else
        print_status $YELLOW "⚠️  safety not found, skipping safety checks"
        print_status $YELLOW "   Install with: pip install safety"
    fi
}

# Function to run security checks
run_security_checks() {
    print_status $BLUE "🔒 Running security checks..."

    cd "$PROJECT_ROOT"
    source venv/bin/activate

    # Try bandit if available
    if python -c "import bandit" >/dev/null 2>&1; then
        if bandit -r src/ -f json -o bandit-report.json >/dev/null 2>&1; then
            print_status $GREEN "✅ bandit security checks passed"
        else
            print_status $YELLOW "⚠️  bandit found potential security issues (see bandit-report.json)"
        fi
    else
        print_status $YELLOW "⚠️  bandit not available for security checking"
        print_status $YELLOW "   Install with: pip install bandit"
    fi
}

# Function to run integration tests specifically
run_integration_tests() {
    print_status $BLUE "🔗 Running integration tests..."

    cd "$PROJECT_ROOT"
    source venv/bin/activate

    if pytest tests/integration/ -v; then
        print_status $GREEN "✅ Integration tests passed"
    else
        print_status $RED "❌ Integration tests failed"
        return 1
    fi
}

# Function to run unit tests specifically
run_unit_tests() {
    print_status $BLUE "🔬 Running unit tests..."

    cd "$PROJECT_ROOT"
    source venv/bin/activate

    if pytest tests/unit/ -v; then
        print_status $GREEN "✅ Unit tests passed"
    else
        print_status $RED "❌ Unit tests failed"
        return 1
    fi
}

# Function to show help
show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Comprehensive test runner for ord-plan project (matches GitHub Actions CI).

OPTIONS:
    all              Run all tests and checks (default)
    syntax           Run syntax checks only
    mypy             Run mypy type checking only
    pytest           Run pytest only
    style            Run code style checks only
    security         Run security checks only
    pre-commit       Run pre-commit hooks (black, darglint, flake8, etc.)
    typeguard        Run TypeGuard runtime type checking
    xdoctest         Run xdoctest (doctests)
    docs-build       Test documentation build
    safety           Run Safety dependency security check
    unit             Run unit tests only
    integration      Run integration tests only
    setup            Setup test environment only
    help             Show this help message

EXAMPLES:
    $0                # Run all tests and checks (matches CI)
    $0 pytest         # Run pytest only
    $0 unit           # Run unit tests only
    $0 syntax mypy    # Run syntax and type checks only
    $0 pre-commit     # Run pre-commit hooks only

All tests and checks must pass before code should be considered ready for commit.
EOF
}

# Main function
main() {
    local tests_to_run=()
    local all_tests=false

    # Parse arguments
    if [[ $# -eq 0 ]]; then
        tests_to_run=("pre-commit" "mypy" "tests" "xdoctest" "docs-build" "safety")
        all_tests=true
    else
        for arg in "$@"; do
            case "$arg" in
                "all")
                    tests_to_run=("pre-commit" "mypy" "tests" "typeguard" "xdoctest" "docs-build" "safety")
                    all_tests=true
                    ;;
                "syntax")
                    tests_to_run+=("syntax")
                    ;;
                "mypy")
                    tests_to_run+=("mypy")
                    ;;
                "pytest"|"tests")
                    tests_to_run+=("pytest")
                    ;;
                "style")
                    tests_to_run+=("style")
                    ;;
                "security")
                    tests_to_run+=("security")
                    ;;
                "pre-commit")
                    tests_to_run+=("pre-commit")
                    ;;
                "typeguard")
                    tests_to_run+=("typeguard")
                    ;;
                "xdoctest")
                    tests_to_run+=("xdoctest")
                    ;;
                "docs-build")
                    tests_to_run+=("docs-build")
                    ;;
                "safety")
                    tests_to_run+=("safety")
                    ;;
                "unit")
                    tests_to_run+=("unit")
                    ;;
                "integration")
                    tests_to_run+=("integration")
                    ;;
                "setup")
                    setup_environment
                    exit 0
                    ;;
                "help"|"-h"|"--help")
                    show_help
                    exit 0
                    ;;
                *)
                    print_status $RED "❌ Unknown option: $arg"
                    show_help
                    exit 1
                    ;;
            esac
        done
    fi

    # Always setup environment first
    setup_environment

    # Track overall success
    local overall_success=true

    # Run requested tests
    for test in "${tests_to_run[@]}"; do
        print_status $BLUE "\n" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        print_status $BLUE "🚀 Running: $test"

        case "$test" in
            "syntax")
                run_syntax_checks || overall_success=false
                ;;
            "mypy")
                run_mypy || overall_success=false
                ;;
            "pytest"|"tests")
                run_pytest || overall_success=false
                ;;
            "style")
                run_style_checks || overall_success=false
                ;;
            "security")
                run_security_checks || overall_success=false
                ;;
            "pre-commit")
                run_precommit_checks || overall_success=false
                ;;
            "typeguard")
                run_typeguard_checks || overall_success=false
                ;;
            "xdoctest")
                run_xdoctest || overall_success=false
                ;;
            "docs-build")
                run_docs_build || overall_success=false
                ;;
            "safety")
                run_safety_checks || overall_success=false
                ;;
            "unit")
                run_unit_tests || overall_success=false
                ;;
            "integration")
                run_integration_tests || overall_success=false
                ;;
        esac
    done

    # Final summary
    print_status $BLUE "\n" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [[ "$overall_success" == true ]]; then
        print_status $GREEN "🎉 ALL TESTS AND CHECKS PASSED!"
        print_status $GREEN "   Code is ready for commit ✅"
        exit 0
    else
        print_status $RED "❌ SOME TESTS OR CHECKS FAILED!"
        print_status $RED "   Please fix the issues before committing"
        exit 1
    fi
}

# Run main function with all arguments
main "$@"

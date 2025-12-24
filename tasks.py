#!/usr/bin/env python3
"""Fabric tasks for ord-plan project.

This module provides Fabric tasks for running tests, linting, and other
development operations with proper task structure and individual entry points.
"""

import subprocess
import sys
from pathlib import Path

from invoke import task

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"


def setup_python_path():
    """Add src directory to Python path."""
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))


def run_command(c, cmd, description=""):
    """Run a shell command with description."""
    print(f"🚀 {description}...")
    result = c.run(cmd, hide=False, warn=True)
    if result.return_code != 0:
        print(f"❌ {description} failed with exit code {result.return_code}")
        if result.stderr:
            print(f"STDERR:\n{result.stderr}")
        return False
    print(f"✅ {description} completed!")
    return True


# Main Fabric task definitions
@task
def pytest(c):
    """Run pytest tests."""
    setup_python_path()
    return run_command(
        c,
        (
            "uv run pytest tests/ -v --cov=ord_plan --cov-report=term-missing "
            "-W ignore::DeprecationWarning"
        ),
        "Running pytest tests",
    )


@task
def test_unit(c):
    """Run unit tests only."""
    setup_python_path()
    return run_command(c, "uv run pytest tests/unit/ -v", "Running unit tests")


@task
def test_integration(c):
    """Run integration tests only."""
    setup_python_path()
    return run_command(
        c, "uv run pytest tests/integration/ -v", "Running integration tests"
    )


@task
def test_contract(c):
    """Run contract tests only."""
    setup_python_path()
    return run_command(c, "uv run pytest tests/contract/ -v", "Running contract tests")


@task
def lint(c):
    """Run code linting checks."""
    setup_python_path()
    print("🎨 Running linting checks...")

    # Run individual linting tasks
    checks = [black, isort, flake8, mypy, darglint]
    for check in checks:
        if not check(c):
            print(f"❌ {check.__name__} check failed!")
            return False

    print("✅ All linting checks passed!")
    return True


@task
def style(c):
    """Run all style and formatting checks."""
    setup_python_path()
    print("🎨 Running style checks...")

    # Run individual style checks
    checks = [black, isort, flake8, mypy, darglint]
    for check in checks:
        if not check(c):
            print(f"❌ {check.__name__} check failed!")
            return False

    print("✅ All style checks passed!")
    return True


@task
def pre_commit(c):
    """Run pre-commit hooks on all files."""
    setup_python_path()
    return run_command(
        c, "uv run pre-commit run --all-files", "Running pre-commit hooks"
    )


@task
def pre_commit_install(c):
    """Install pre-commit hooks."""
    setup_python_path()
    return run_command(c, "uv run pre-commit install", "Installing pre-commit hooks")


@task
def gitlint_install(c):
    """Install gitlint commit-msg hook."""
    setup_python_path()
    return run_command(c, "uv run gitlint install-hook", "Installing gitlint hook")


@task
def security(c):
    """Run security checks."""
    setup_python_path()
    return run_command(c, "uv run safety check", "Running security checks")


@task
def mypy(c):
    """Run type checking."""
    setup_python_path()
    return run_command(
        c, "uv run mypy src/ --ignore-missing-imports", "Running type checking"
    )


@task
def black(c):
    """Run Black formatting check."""
    setup_python_path()
    return run_command(
        c, "uv run black --check src/ tests/", "Running Black formatting check"
    )


@task
def isort(c):
    """Run import sorting check."""
    setup_python_path()
    return run_command(
        c, "uv run isort --check-only src/ tests/", "Running import sorting check"
    )


@task
def flake8(c):
    """Run Flake8 linting."""
    setup_python_path()
    return run_command(
        c,
        "uv run flake8 src/ tests/",
        "Running Flake8 linting",
    )


@task
def darglint(c):
    """Run docstring linting."""
    setup_python_path()
    return run_command(
        c,
        'uv run darglint --ignore-raise "FileNotFoundError,PermissionError,OSError,BadParameter" src/',
        "Running docstring linting",
    )


@task
def docs(c):
    """Build documentation."""
    setup_python_path()
    return run_command(
        c, "sphinx-build -b html docs/ docs/_build/", "Building documentation"
    )


@task
def docs_serve(c):
    """Serve documentation locally."""
    setup_python_path()
    return run_command(
        c,
        "sphinx-autobuild -b html docs/ docs/_build/ --host 0.0.0.0 --port 8000",
        "Serving documentation",
    )


@task
def clean(c):
    """Clean build artifacts and cache."""
    setup_python_path()
    print("🧹 Cleaning...")

    commands = [
        "find . -type d -name '__pycache__' -exec rm -rf {} +",
        "find . -type f -name '*.pyc' -delete",
        "rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/",
        "rm -rf docs/_build/",
    ]

    for cmd in commands:
        subprocess.run(cmd, shell=True, check=False)

    print("✅ Clean completed!")


@task
def install_deps(c):
    """Install all development dependencies."""
    setup_python_path()
    print("📦 Installing development dependencies...")

    commands = [
        "pip install fabric==3.2.2 invoke==2.2.0",
        "pip install pytest pytest-cov black isort flake8 mypy darglint safety",
        "pip install sphinx sphinx-rtd-theme myst-parser",
    ]

    for cmd in commands:
        if not run_command(c, cmd, f"Installing {cmd}"):
            return False

    print("✅ All dependencies installed successfully!")
    return True


@task
def workflow_logs(c, run_id=None):
    """Show logs from the last GitHub Actions workflow run.

    Options:
        run_id (str): Specific workflow run ID to view (default: most recent run)
    """
    setup_python_path()

    if not run_id:
        print("📋 Fetching the most recent workflow run ID...")
        result = c.run(
            "gh run list --limit 1 --json databaseId --jq '.[0].databaseId'",
            hide=True,
            warn=True,
        )
        if result.return_code != 0:
            print(f"❌ Failed to fetch workflow run ID")
            if result.stderr:
                print(f"STDERR:\n{result.stderr}")
            return False
        run_id = result.stdout.strip()
        if not run_id:
            print("❌ No workflow runs found")
            return False

    print(f"📋 Showing logs for workflow run: {run_id}")
    cmd = f"gh run view {run_id} --log"
    result = c.run(cmd, hide=False, warn=True)
    if result.return_code != 0:
        print(f"❌ Failed to retrieve workflow logs")
        if result.stderr:
            print(f"STDERR:\n{result.stderr}")
        return False
    return True


@task
def help(c):
    """Show usage examples and task categories."""
    setup_python_path()
    print("🚀 Invoke Tasks Usage Guide\n")

    print("📋 TASK CATEGORIES:\n")

    print("🔧 INDIVIDUAL CHECKS:")
    print("  invoke black          # Just Black formatting")
    print("  invoke isort          # Just import sorting")
    print("  invoke flake8         # Just Flake8 linting")
    print("  invoke mypy           # Just type checking")
    print("  invoke darglint       # Just docstring linting")
    print("  invoke security       # Just security checks")
    print("  invoke pre-commit     # Run all pre-commit hooks")
    print("  invoke pre-commit-install # Install pre-commit hooks")
    print("  invoke gitlint-install # Install gitlint commit-msg hook")
    print()

    print("🧪 SPECIFIC TEST TYPES:")
    print("  invoke test-unit      # Unit tests only")
    print("  invoke test-integration # Integration tests only")
    print("  invoke test-contract   # Contract tests only")
    print("  invoke pytest         # All tests (with coverage)")
    print()

    print("📦 COMPOSITE CHECKS:")
    print("  invoke lint           # All linting checks")
    print("                        # (black, isort, flake8, mypy, darglint)")
    print("  invoke style          # All style checks")
    print("                        # (black, isort, flake8, mypy, darglint)")
    print("  invoke pre-commit     # All pre-commit hooks (alternative to lint/style)")
    print("  invoke all            # All checks (tests, linting, security)")
    print("  invoke all --verbose  # All checks with detailed error output")
    print("  invoke all --use-pre-commit  # All checks using pre-commit hooks")
    print()

    print("🛠️  UTILITIES:")
    print("  invoke clean          # Clean build artifacts and cache")
    print("  invoke install-deps   # Install development dependencies")
    print("  invoke pre-commit-install # Install pre-commit hooks")
    print("  invoke gitlint-install # Install gitlint commit-msg hook")
    print("  invoke docs           # Build documentation")
    print("  invoke docs-serve     # Serve documentation locally")
    print("  invoke workflow-logs  # Show logs from last GitHub Actions run")
    print()

    print("💡 QUICK EXAMPLES:")
    print("  invoke help           # Show this help")
    print("  invoke --list         # List all available tasks")
    print("  invoke black && invoke flake8  # Run specific checks in sequence")
    print("  invoke lint            # Run all linting checks")
    print("  invoke pre-commit      # Run pre-commit hooks (alternative)")
    print("  invoke test-unit       # Run only unit tests")
    print("  invoke all             # Run everything")
    print("  invoke all --verbose    # Run everything with detailed output")


@task
def all(c, verbose=False, use_pre_commit=False):
    """Run all checks: tests, linting, security, and docs.

    Options:
        verbose (bool): Show detailed output for each section (default: False)
        use_pre_commit (bool): Use pre-commit hooks instead of individual linting tasks (default: False)
    """
    setup_python_path()

    def section(title, check_func, quiet_desc):
        """Helper to run a section with appropriate verbosity."""
        print(f"\n{title}")
        print("-" * 50)

        if verbose:
            success = check_func(c)
        else:
            # Run with suppressed output for clean separation
            result = c.run(check_func.__name__, hide=True, warn=True)
            success = result.return_code == 0

        if success:
            print("✅ PASSED")
        else:
            section_name = title.split(":")[1].strip()
            print(f"❌ {section_name} FAILED")
            if verbose:
                print("Run with --verbose for detailed error output")
            return False
        return True

    print("\n" + "=" * 80)
    print("🚀 COMPREHENSIVE TESTING SUITE")
    print("=" * 80)

    # Choose linting approach based on use_pre_commit flag
    if use_pre_commit:
        sections = [
            ("🧪 SECTION: TEST SUITE", pytest, "Running pytest with coverage"),
            ("🔧 SECTION: PRE-COMMIT HOOKS", pre_commit, "Running pre-commit hooks"),
            ("🔒 SECTION: SECURITY SCAN", security, "Running security scan"),
        ]
    else:
        sections = [
            ("🧪 SECTION: TEST SUITE", pytest, "Running pytest with coverage"),
            ("🔍 SECTION: LINTING CHECKS", lint, "Running all linting checks"),
            ("🎨 SECTION: STYLE VALIDATION", style, "Running all style checks"),
            ("🔒 SECTION: SECURITY SCAN", security, "Running security scan"),
            ("📝 SECTION: TYPE CHECKING", mypy, "Running type checking"),
        ]

    for title, check_func, desc in sections:
        if verbose:
            print(f"\n🚀 {desc}...")
        else:
            print()

        if not section(title, check_func, desc):
            print(f"\n{'=' * 80}")
            print("🚨 TESTING SUITE FAILED")
            print("=" * 80)
            print("Run with: invoke all --verbose for detailed error output")
            return False

    # Final success message
    print(f"\n{'=' * 80}")
    print("🎉 ALL SECTIONS PASSED SUCCESSFULLY!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    # Setup path when run as script
    setup_python_path()

    # Simple command line interface for backward compatibility
    if len(sys.argv) < 2:
        print("Usage: python tasks.py <task> or invoke <task>")
        print("\nAvailable tasks:")
        print("Run 'invoke --list' to see all available tasks")
        sys.exit(1)

    task_name = sys.argv[1]
    import tasks

    if hasattr(tasks, task_name):
        # Create a mock context for direct execution
        from invoke import Context

        mock_ctx = Context()
        task_func = getattr(tasks, task_name)
        success = task_func(mock_ctx)
        sys.exit(0 if success else 1)
    else:
        print(f"❌ Unknown task: {task_name}")
        print("Run 'invoke --list' to see all available tasks")
        sys.exit(1)

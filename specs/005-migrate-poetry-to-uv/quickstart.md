# Quickstart: Poetry to UV Migration Guide

**Feature**: 005-migrate-poetry-to-uv | **Date**: 2025-12-23

## Overview

This guide helps developers transition from Poetry to UV for the ord-plan project. The migration preserves all existing functionality while replacing Poetry with UV as the dependency management tool.

## Installation

### Quick Start with UV

```bash
# Clone repository
git clone https://github.com/vonpupp/ord-plan.git
cd ord-plan

# Install UV (if not already installed)
pipx install uv

# Install project in development mode
uv pip install -e ".[dev]"
```

### Verify Installation

```bash
# Check UV version
uv --version

# Run tests to verify installation
invoke pytest

# Run linting
invoke lint
```

## Development Workflow

### Using Invoke Commands

All invoke commands work the same as before, but now use UV internally:

```bash
# Run all tests
invoke pytest

# Run specific test suites
invoke test-unit
invoke test-integration
invoke test-contract

# Run all linting checks
invoke lint

# Run individual linting tools
invoke mypy
invoke black
invoke isort
invoke flake8
invoke darglint

# Run pre-commit hooks
invoke pre-commit

# Install pre-commit hooks
invoke pre-commit-install
```

### Using Nox Sessions

Nox sessions are still available and now use UV:

```bash
# List available sessions
nox --list-sessions

# Run specific sessions
nox -s tests
nox -s mypy
nox -s pre-commit
nox -s docs-build
```

### Running the CLI Directly

```bash
# Generate org-mode schedule
uv run ord-plan generate --input events.yaml --output schedule.org

# Generate JSON output
uv run ord-plan generate --input events.yaml --output schedule.json --format json

# Interactive mode
uv run ord-plan
```

## Migration Differences

### Poetry vs UV Command Reference

| What you did with Poetry | How to do it with UV |
| ------------------------ | ------------------- |
| `poetry install` | `uv pip install -e .` |
| `poetry install --with dev` | `uv pip install -e ".[dev]"` |
| `poetry run pytest` | `uv run pytest` or `invoke pytest` |
| `poetry run black` | `uv run black` or `invoke black` |
| `poetry run mypy` | `uv run mypy` or `invoke mypy` |
| `poetry build` | `uv build` |
| `poetry add <package>` | `uv pip install <package>` |
| `poetry shell` | Not needed; use `uv run` for commands |

### Pre-commit Hooks

Pre-commit hooks now use UV:

```bash
# Run all hooks
invoke pre-commit

# Or run directly
uv run pre-commit run --all-files

# Install hooks
invoke pre-commit-install
```

## Cleaning Up Poetry

### Optional: Remove Poetry Virtual Environments

After verifying UV works, you can clean up Poetry environments:

```bash
# List Poetry virtual environments
poetry env list --full-path

# Remove all Poetry virtual environments
poetry env remove --all

# Remove Poetry cache
rm -rf ~/.cache/pypoetry/

# Uninstall Poetry (optional)
pipx uninstall poetry
```

**Note**: This is optional. You can keep Poetry installed; it won't interfere with UV.

## Troubleshooting

### Issue: Command not found

```bash
# Ensure UV is installed and in PATH
which uv
uv --version

# If not found, install with pipx
pipx install uv
pipx ensurepath
```

### Issue: Import errors

```bash
# Reinstall with dev dependencies
uv pip install -e ".[dev]"

# Verify installation
uv pip list
```

### Issue: Tests fail

```bash
# Check UV version (requires Python 3.8+)
uv --version

# Reinstall dependencies
uv pip install -e ".[dev]"

# Run tests with verbose output
invoke pytest -v
```

### Issue: Nox sessions fail

```bash
# Verify nox installation
nox --version

# Ensure nox-poetry is not installed
pipx uninstall nox-poetry  # If present

# Run nox with verbose output
nox -s tests -vv
```

## CI/CD Changes

GitHub Actions workflows now use UV:

- **Tests workflow**: UV installed via pipx; nox-poetry removed
- **Release workflow**: UV used for building packages; version detection via Python script

No action needed; these changes are automatic in the repo.

## Documentation Updates

All project documentation now references UV instead of Poetry:

- **README.md**: UV installation instructions
- **CONTRIBUTING.md**: UV development setup
- **AGENTS.md**: UV listed in active technologies

## Getting Help

If you encounter issues:

1. Check the [UV documentation](https://docs.astral.sh/uv/)
2. Review the [feature specification](/specs/005-migrate-poetry-to-uv/spec.md)
3. Check GitHub Actions for CI/CD issues
4. Run `invoke help` for available commands

## Next Steps

1. Install UV: `pipx install uv`
2. Install the project: `uv pip install -e ".[dev]"`
3. Run tests: `invoke pytest`
4. Optionally clean up Poetry: See "Cleaning Up Poetry" section above

## Rollback

If you need to rollback to Poetry (not recommended):

```bash
# Checkout files from git
git checkout .

# Reinstall Poetry
pipx install poetry
poetry install

# Run tests
poetry run pytest
```

**Note**: The repository no longer supports Poetry after migration. Rollback is for emergency recovery only.
